#!/usr/bin/env python3
"""Verify every reference in references_to_verify.yaml (rule B4: references must be real).

Per reference it checks: policy (source_type / peer review), then that the DOI exists
(Crossref, then DataCite), and that title and year match the registry.

Usage: python scripts/verify_dois.py [--strict] [--check-md]
  --strict    warnings (network problems) also fail the run
  --check-md  also fail if a DOI is cited in references/stage-*/*.md but missing from the YAML
"""
import difflib
import re
import sys
import time
from pathlib import Path
from urllib.parse import quote

import requests
import yaml

ROOT = Path(__file__).resolve().parent.parent
HDR = {"User-Agent": "ML-Model-Architect-verifier/1.0 (mailto:az967252@users.noreply.github.com)"}
norm = lambda s: re.sub(r"[^a-z0-9 ]", "", (s or "").lower())

ALLOWED_SOURCE_TYPES = {"journal", "conference", "book"}
PEER_REVIEW_REQUIRED = {"journal", "conference"}   # books may be foundational, un-reviewed texts
RETRY_DELAYS = (2, 5)                              # seconds to wait between attempts (3 attempts)
DOI_RE = re.compile(r"10\.\d{4,9}/[^\s)|,;<>]+")


def http_get(url, **kwargs):
    """requests.get with retries on network errors, HTTP 429 and HTTP 5xx."""
    kwargs.setdefault("headers", HDR)
    response, error = None, None
    for attempt in range(len(RETRY_DELAYS) + 1):
        response, error = None, None
        try:
            response = requests.get(url, **kwargs)
            if response.status_code != 429 and response.status_code < 500:
                return response
        except requests.exceptions.RequestException as e:
            error = e
        if attempt < len(RETRY_DELAYS):
            time.sleep(RETRY_DELAYS[attempt])
    if response is not None:
        return response
    raise error


def check_policy(ref):
    """Rule B3 as code: allowed source type and peer review. Returns (status, note) or None if fine."""
    st = ref.get("source_type")
    if st not in ALLOWED_SOURCE_TYPES:
        return ("FAIL_SOURCE_TYPE", f"source_type {st!r} not allowed; use one of {sorted(ALLOWED_SOURCE_TYPES)}")
    if st in PEER_REVIEW_REQUIRED and ref.get("claimed_peer_reviewed") is not True:
        return ("FAIL_NOT_PEER_REVIEWED", f"{st} reference must have claimed_peer_reviewed: true")
    return None


def md_dois_not_in_yaml(data, root=ROOT):
    """DOIs cited in references/stage-*/*.md that are not listed in the YAML (so never verified)."""
    known = {str(r["doi_or_url"]).lower() for g in data["groups"] for r in g["refs"]}
    missing = {}
    for f in sorted((Path(root) / "references").glob("stage-*/*.md")):
        for m in DOI_RE.findall(f.read_text(encoding="utf-8", errors="replace")):
            doi = m.rstrip(".,;)").lower()
            if doi not in known:
                missing.setdefault(doi, []).append(f.name)
    return missing

def check(ref):
    doi, title, year = ref["doi_or_url"], ref.get("title", "").strip(), ref.get("year", 0)
    
    if not title:
        return ("FAIL_MISSING_TITLE", "Title is required in YAML")

    if "exception" in ref and ref["exception"]:
        if not ref.get("verified_by") or not ref.get("verified_date") or not ref.get("evidence_url"):
            return ("FAIL_INCOMPLETE_EXCEPTION", "Exception lacks verified_by, verified_date, or evidence_url")
        try:
            er = http_get(ref["evidence_url"], timeout=10, allow_redirects=True)
            if er.status_code >= 400:
                return ("FAIL_DEAD_EVIDENCE_URL", f"HTTP {er.status_code} for {ref['evidence_url']}")
        except Exception as e:
            return ("FAIL_DEAD_EVIDENCE_URL", str(e))
        return ("EXCEPTION", ref["exception"])
        
    if not doi.startswith("10."):
        try:
            r = http_get(doi, timeout=15, allow_redirects=True)
            if r.status_code >= 400:
                r = requests.head(doi, headers=HDR, timeout=15, allow_redirects=True)
            return ("OK_URL", "") if r.status_code < 400 else ("FAIL_URL_DEAD", r.status_code)
        except Exception as e:
            return ("FAIL_URL_DEAD", str(e))
            
    try:
        r = http_get(f"https://api.crossref.org/works/{quote(doi)}", timeout=15)
        
        if r.status_code == 404:
            d = http_get(f"https://api.datacite.org/dois/{quote(doi)}", timeout=15)
            if d.status_code == 200:
                t = d.json()["data"]["attributes"]["titles"][0]["title"]
                y = d.json()["data"]["attributes"].get("publicationYear", 0)
            elif d.status_code == 404:
                return ("FAIL_NOT_FOUND", "Not in Crossref or DataCite")
            else:
                return ("WARN_HTTP_ERROR", d.status_code)
        elif r.status_code != 200:
            return ("WARN_HTTP_ERROR", r.status_code)
        else:
            m = r.json()["message"]
            t1 = (m.get("title") or [""])[0]
            t2 = (m.get("subtitle") or [""])[0]
            t = f"{t1} {t2}".strip()
            y = ((m.get("issued") or {}).get("date-parts") or [[None]])[0][0]
            
        a, b = norm(t), norm(title)
        sim = max(
            difflib.SequenceMatcher(None, a, b).ratio(),
            1.0 if a and (a in b or b in a) and min(len(a), len(b)) / max(len(a), len(b)) >= 0.7 else 0.0
        )
        
        if sim < 0.8: 
            return ("FAIL_TITLE_MISMATCH", f"crossref: {t!r}")
        if y and abs(y - year) > 1: 
            return ("FAIL_YEAR_MISMATCH", f"crossref: {y}, yaml: {year}")
        return ("OK", "")
        
    except Exception as e:
        return ("WARN_ERROR", str(e))

def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    strict, check_md = "--strict" in argv, "--check-md" in argv
    data = yaml.safe_load((ROOT / "references_to_verify.yaml").read_text(encoding="utf-8"))
    fails, warns, exceptions = 0, 0, 0

    print(f"{'GROUP':<8} {'STATUS':<24} {'REFERENCE'}")
    print("-" * 80)

    for g in data["groups"]:
        for ref in g["refs"]:
            policy = check_policy(ref)
            status, note = policy if policy else check(ref)
            print(f"[{g['id']:<5}] {status:<24} {ref['doi_or_url']} {note}")

            if status.startswith("FAIL"):
                fails += 1
            elif status.startswith("WARN"):
                warns += 1
            elif status == "EXCEPTION":
                exceptions += 1

    if check_md:
        for doi, files in md_dois_not_in_yaml(data).items():
            print(f"[md   ] FAIL_NOT_IN_YAML         {doi} cited in {', '.join(sorted(set(files)))}")
            fails += 1

    print("-" * 80)
    print(f"Total FAILs: {fails} | Total WARNs: {warns} | Total Exceptions: {exceptions}")
    return 1 if fails > 0 or (strict and warns > 0) else 0


if __name__ == "__main__":
    sys.exit(main())
