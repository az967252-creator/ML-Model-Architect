#!/usr/bin/env python3
import sys, difflib, re, requests, yaml
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
HDR = {"User-Agent": "ML-Model-Architect-verifier/1.0 (mailto:test@example.com)"}
norm = lambda s: re.sub(r"[^a-z0-9 ]", "", (s or "").lower())

def check(ref):
    doi, title, year = ref["doi_or_url"], ref.get("title", ""), ref.get("year", 0)
    if not doi.startswith("10."):
        try:
            r = requests.head(doi, headers=HDR, timeout=15, allow_redirects=True)
            return ("OK_URL", "") if r.status_code < 400 else ("URL_DEAD", r.status_code)
        except Exception as e:
            return ("URL_DEAD", str(e))
            
    try:
        r = requests.get(f"https://api.crossref.org/works/{quote(doi)}", headers=HDR, timeout=15)
        if r.status_code == 404:
            d = requests.head(f"https://doi.org/{quote(doi)}", headers=HDR, timeout=15, allow_redirects=False)
            return ("REGISTERED_NOT_CROSSREF", "title unchecked") if d.status_code in (301, 302, 303) else ("NOT_FOUND", "")
        if r.status_code != 200:
            return ("HTTP_ERROR", r.status_code)
            
        m = r.json()["message"]
        t = (m.get("title") or [""])[0]
        y = ((m.get("issued") or {}).get("date-parts") or [[None]])[0][0]
        sim = difflib.SequenceMatcher(None, norm(t), norm(title)).ratio()
        if sim < 0.8:   return ("TITLE_MISMATCH", f"crossref: {t!r}")
        if y and abs(y - year) > 1: return ("YEAR_MISMATCH", f"crossref: {y}, yaml: {year}")
        return ("OK", "")
    except Exception as e:
        return ("ERROR", str(e))

def main():
    try:
        data = yaml.safe_load((ROOT / "references_to_verify.yaml").read_text(encoding="utf-8"))
    except Exception as e:
        print(f"Failed to read YAML: {e}")
        sys.exit(1)

    bad = 0
    for g in data["groups"]:
        for ref in g["refs"]:
            status, note = check(ref)
            print(f"[{g['id']}] {status:24} {ref['doi_or_url']} {note}")
            if status in ("TITLE_MISMATCH", "YEAR_MISMATCH", "NOT_FOUND", "URL_DEAD", "ERROR"):
                bad += 1
    sys.exit(1 if bad else 0)

if __name__ == "__main__":
    main()
