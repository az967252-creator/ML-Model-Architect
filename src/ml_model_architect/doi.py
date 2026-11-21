#!/usr/bin/env python3
"""Verify every reference in references_to_verify.yaml (rule B4: references must be real).

Per reference it checks: policy (source_type / peer review), then that the DOI exists
(Crossref, then DataCite), and that title and year match the registry.

Usage: python scripts/verify_dois.py [--strict] [--check-md]
  --strict    warnings (network problems) also fail the run
  --check-md  also fail if a DOI is cited in references/stage-*/*.md but missing from the YAML
"""
import datetime
import difflib
import re
import sys
import time
from pathlib import Path
from urllib.parse import quote, urlparse

import requests
import yaml

ROOT = Path(__file__).resolve().parent.parent.parent
HDR = {"User-Agent": "ML-Model-Architect-verifier/1.0 (mailto:az967252@users.noreply.github.com)"}
norm = lambda s: re.sub(r"[^a-z0-9 ]", "", (s or "").lower())

ALLOWED_SOURCE_TYPES = {"journal", "conference", "book"}
PEER_REVIEW_REQUIRED = {"journal", "conference"}   # books may be foundational, un-reviewed texts
PEER_REVIEWED_CROSSREF_TYPES = {"journal-article", "proceedings-article", "book-chapter"}
RETRY_DELAYS = (2, 5)                              # seconds to wait between attempts (3 attempts)
DOI_RE = re.compile(r"10\.\d{4,9}/[^\s)|,;<>]+")


def load_whitelist(path=None):
    """Return a list of (host, path_prefix) rules from trusted_domains.yaml."""
    if path:
        path = Path(path)
    else:
        path = ROOT / "references" / "trusted_domains.yaml"
        if not path.exists():
            path = Path(__file__).resolve().parent / "resources" / "references" / "trusted_domains.yaml"
        if not path.exists():
            path = ROOT / "trusted_domains.yaml"
    if not path.exists():
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    rules = []
    for entry in data.get("domains", []):
        if isinstance(entry, dict):
            raw_entry = entry.get("domain", entry.get("url", ""))
        else:
            raw_entry = str(entry)
        raw_entry = re.sub(r"^https?://", "", raw_entry.strip().lower())
        host, _, rest = raw_entry.partition("/")
        host = host.removeprefix("www.")
        prefix = "/" + rest.strip("/") if rest.strip("/") else ""
        if host:
            rules.append((host, prefix))
    return rules


def is_trusted_url(url, rules):
    """True if the URL's real hostname (and path, when the rule has one) is whitelisted."""
    try:
        parsed = urlparse(url)
    except ValueError:
        return False
    host = (parsed.hostname or "").lower().removeprefix("www.")
    if parsed.scheme not in ("http", "https") or not host:
        return False
    path = parsed.path or "/"
    for rule_host, prefix in rules:
        if host == rule_host or host.endswith("." + rule_host):
            if not prefix or path == prefix or path.startswith(prefix + "/"):
                return True
    return False


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
    if error is not None:
        raise error
    raise RuntimeError(f"Failed to fetch {url}")


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


def check(ref, whitelist=None):
    doi, title, year = ref["doi_or_url"], ref.get("title", "").strip(), ref.get("year", 0)
    
    if not title:
        return ("FAIL_MISSING_TITLE", "Title is required in YAML")

    if "exception" in ref and ref["exception"]:
        if not ref.get("verified_by") or not ref.get("verified_date") or not ref.get("evidence_url"):
            return ("FAIL_INCOMPLETE_EXCEPTION", "Exception lacks verified_by, verified_date, or evidence_url")
        
        # Expiry check (<= 365 days)
        try:
            v_date = datetime.date.fromisoformat(str(ref["verified_date"]))
            days_old = (datetime.date.today() - v_date).days
            if days_old > 365:
                return ("FAIL_EXCEPTION_EXPIRED", f"Exception verified on {ref['verified_date']} has expired ({days_old} days > 365 days)")
        except Exception as e:
            return ("FAIL_INCOMPLETE_EXCEPTION", f"Invalid verified_date: {e}")

        # Evidence URL domain whitelist check
        rules = load_whitelist() if whitelist is None else whitelist
        if not is_trusted_url(ref["evidence_url"], rules):
            return ("FAIL_UNTRUSTED_EVIDENCE_URL", f"Evidence URL {ref['evidence_url']} is not on a trusted domain")

        try:
            er = http_get(ref["evidence_url"], timeout=10, allow_redirects=True)
            if er.status_code >= 400:
                return ("FAIL_DEAD_EVIDENCE_URL", f"HTTP {er.status_code} for {ref['evidence_url']}")
        except Exception as e:
            return ("WARN_NETWORK_ERROR", str(e))
        return ("EXCEPTION", ref["exception"])
        
    if not doi.startswith("10."):
        try:
            r = http_get(doi, timeout=15, allow_redirects=True)
            if r.status_code >= 400:
                r = requests.head(doi, headers=HDR, timeout=15, allow_redirects=True)
            return ("OK_URL", "") if r.status_code < 400 else ("FAIL_URL_DEAD", str(r.status_code))
        except Exception as e:
            return ("WARN_NETWORK_ERROR", str(e))
            
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
                return ("WARN_HTTP_ERROR", str(d.status_code))
        elif r.status_code != 200:
            return ("WARN_HTTP_ERROR", str(r.status_code))
        else:
            m = r.json()["message"]
            t1 = (m.get("title") or [""])[0]
            t2 = (m.get("subtitle") or [""])[0]
            t = f"{t1} {t2}".strip()
            y = ((m.get("issued") or {}).get("date-parts") or [[None]])[0][0]

            # Cross-check peer review status against Crossref type
            cr_type = (m.get("type") or "").lower()
            claimed_pr = ref.get("claimed_peer_reviewed")
            if claimed_pr is True and cr_type and cr_type not in PEER_REVIEWED_CROSSREF_TYPES:
                return ("FAIL_NOT_PEER_REVIEWED", f"Crossref reports type {cr_type!r}, which is not peer-reviewed")
            
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
    strict = "--strict" in argv
    check_md = "--check-md" in argv
    ref_file = ROOT / "references" / "references_to_verify.yaml"
    if not ref_file.exists():
        ref_file = ROOT / "references_to_verify.yaml"
    data = yaml.safe_load(ref_file.read_text(encoding="utf-8"))
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


def verify_dois(strict: bool = False, check_markdown: bool = False) -> int:
    """Programmatic entry point for DOI verification."""
    args = []
    if strict:
        args.append("--strict")
    if check_markdown:
        args.append("--check-md")
    return main(args)


if __name__ == "__main__":
    sys.exit(main())
