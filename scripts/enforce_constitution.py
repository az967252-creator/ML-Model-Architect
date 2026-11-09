#!/usr/bin/env python3
import sys
import re
import requests
import yaml
from pathlib import Path
from urllib.parse import urlparse

ALLOWED_TOKENS = {"heuristic", "reference-gap", "n/a (business context)"}

def check_doi(doi):
    clean_doi = doi.strip()
    try:
        r = requests.get(f"https://api.crossref.org/works/{clean_doi}", timeout=10)
        if r.status_code == 200: return "OK"
        d = requests.get(f"https://api.datacite.org/dois/{clean_doi}", timeout=10)
        if d.status_code == 200: return "OK"
        return "FAKE"
    except requests.exceptions.RequestException:
        return "NETWORK_ERROR"

def enforce(filepath):
    if not Path(filepath).exists():
        print(f"ERROR: {filepath} not found.")
        sys.exit(1)

    content = Path(filepath).read_text(encoding="utf-8")
    lines = [line for line in content.split("\n") if line.strip().startswith("|") and "---" not in line]
    
    if len(lines) < 2:
        print("No valid table found.")
        return

    headers = [h.strip().lower() for h in lines[0].split("|")[1:-1]]
    try:
        id_idx = headers.index("stage")
        type_idx = headers.index("type")
        q_idx = headers.index("question")
        ref_idx = headers.index("reference")
    except ValueError:
        print("❌ ERROR: Ledger table is missing required headers (Stage, Type, Question, Reference).")
        sys.exit(1)

    violations = 0
    for line in lines[1:]:
        cols = [c.strip() for c in line.split("|")[1:-1]]
        if len(cols) < len(headers): continue
            
        dec_id = cols[id_idx]
        dec_type = cols[type_idx].lower()
        question = cols[q_idx]
        ref = cols[ref_idx]
        
        if dec_type in ["technique", "parameter", "threshold", "deployment", "metric", "evaluation"]:
            if not ref or ref.lower() in ALLOWED_TOKENS:
                continue
                
            if "10." in ref:
                doi_match = re.search(r'10\.\d{4,9}/[^\s|]+', ref)
                if doi_match:
                    doi_to_check = doi_match.group(0).strip(")")
                    status = check_doi(doi_to_check)
                    if status == "FAKE":
                        print(f"❌ FAKE DOI: Decision '{question}' cites {doi_to_check}")
                        violations += 1
                    elif status == "NETWORK_ERROR":
                        print(f"⚠️ WARNING: Network error checking DOI for '{question}'.")
                else:
                    print(f"❌ INVALID DOI FORMAT: Decision '{question}' -> {ref}")
                    violations += 1
            elif "http" in ref.lower():
                wl_path = Path(__file__).parent.parent / "trusted_domains.yaml"
                if wl_path.exists():
                    whitelist = yaml.safe_load(wl_path.read_text(encoding="utf-8"))["domains"]
                    domain = urlparse(ref).netloc
                    if not any(d in domain for d in whitelist):
                        print(f"❌ UNTRUSTED URL: Decision '{question}' cites {domain}")
                        violations += 1
            else:
                print(f"❌ INVALID REFERENCE: Decision '{question}' reference is neither DOI, trusted URL, nor allowed token.")
                violations += 1
                
    if violations == 0:
        print("✅ All technical decisions have valid references or allowed heuristics.")
    else:
        print(f"\n⚠️ Found {violations} violations.")
        sys.exit(1)

if __name__ == "__main__":
    enforce(sys.argv[1] if len(sys.argv) > 1 else "examples/delivery-delay-prediction/DECISIONS.md")
