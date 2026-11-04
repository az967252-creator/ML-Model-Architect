#!/usr/bin/env python3
import sys, difflib, re, requests, yaml
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
# CHANGE THIS TO YOUR ACTUAL EMAIL
HDR = {"User-Agent": "ML-Model-Architect-verifier/1.0 (mailto:az967252@users.noreply.github.com)"}
norm = lambda s: re.sub(r"[^a-z0-9 ]", "", (s or "").lower())

def check(ref):
    # Handle explicit exceptions
    if "exception" in ref and ref["exception"]:
        return ("EXCEPTION", ref["exception"])
        
    doi, title, year = ref["doi_or_url"], ref.get("title", ""), ref.get("year", 0)
    
    if not doi.startswith("10."):
        try:
            r = requests.head(doi, headers=HDR, timeout=15, allow_redirects=True)
            return ("OK_URL", "") if r.status_code < 400 else ("FAIL_URL_DEAD", r.status_code)
        except Exception as e:
            return ("FAIL_URL_DEAD", str(e))
            
    # Try Crossref
    try:
        r = requests.get(f"https://api.crossref.org/works/{quote(doi)}", headers=HDR, timeout=15)
        
        if r.status_code == 404:
            # Fallback to DataCite (handles arXiv/Zenodo)
            d = requests.get(f"https://api.datacite.org/dois/{quote(doi)}", headers=HDR, timeout=15)
            if d.status_code == 200:
                t = d.json()["data"]["attributes"]["titles"][0]["title"]
                y = d.json()["data"]["attributes"].get("publicationYear", 0)
            else:
                return ("FAIL_NOT_FOUND", "Not in Crossref or DataCite")
        elif r.status_code != 200:
            return ("WARN_HTTP_ERROR", r.status_code)
        else:
            m = r.json()["message"]
            # Combine title and subtitle
            t1 = (m.get("title") or [""])[0]
            t2 = (m.get("subtitle") or [""])[0]
            t = f"{t1} {t2}".strip()
            y = ((m.get("issued") or {}).get("date-parts") or [[None]])[0][0]
            
        # Compare Titles
        a, b = norm(t), norm(title)
        sim = max(
            difflib.SequenceMatcher(None, a, b).ratio(),
            1.0 if a and (a in b or b in a) else 0.0
        )
        
        if sim < 0.8: 
            return ("FAIL_TITLE_MISMATCH", f"crossref: {t!r}")
        if y and abs(y - year) > 1: 
            return ("FAIL_YEAR_MISMATCH", f"crossref: {y}, yaml: {year}")
        return ("OK", "")
        
    except Exception as e:
        return ("WARN_ERROR", str(e))

def main():
    try:
        data = yaml.safe_load((ROOT / "references_to_verify.yaml").read_text(encoding="utf-8"))
    except Exception as e:
        print(f"Failed to read YAML: {e}")
        sys.exit(1)

    fails = 0
    warns = 0
    
    print(f"{'GROUP':<8} {'STATUS':<24} {'REFERENCE'}")
    print("-" * 80)
    
    for g in data["groups"]:
        for ref in g["refs"]:
            status, note = check(ref)
            print(f"[{g['id']:<5}] {status:<24} {ref['doi_or_url']} {note}")
            
            if status.startswith("FAIL"): 
                fails += 1
            elif status.startswith("WARN"): 
                warns += 1
                
    print("-" * 80)
    print(f"Total FAILs: {fails} | Total WARNs: {warns}")
    
    if fails > 0:
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()
