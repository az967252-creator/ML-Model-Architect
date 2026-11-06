#!/usr/bin/env python3
import sys
import re
import requests
from pathlib import Path

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
    
    violations = 0
    for line in lines[1:]:
        cols = [c.strip() for c in line.split("|")[1:-1]]
        if len(cols) < 8: 
            print(f"❌ VIOLATION: Malformed row.")
            violations += 1
            continue
            
        dec_id, dec_type, question, ref = cols[0], cols[2].lower(), cols[3], cols[7]
        
        if dec_type in ["technique", "parameter", "threshold", "deployment", "metric", "evaluation"]:
            if not ref or ref.lower() in ["none", "n/a", "-", "n/a (empirical)"]:
                print(f"❌ VIOLATION: Decision #{dec_id} has no valid reference.")
                violations += 1
            elif "10." in ref:
                doi_match = re.search(r'10\.\d{4,9}/[^\s|]+', ref)
                if doi_match:
                    doi_to_check = doi_match.group(0).strip(")")
                    status = check_doi(doi_to_check)
                    if status == "FAKE":
                        print(f"❌ FAKE DOI: Decision #{dec_id} cites {doi_to_check}")
                        violations += 1
                    elif status == "NETWORK_ERROR":
                        print(f"⚠️ WARNING: Network error while checking {doi_to_check} for Decision #{dec_id}.")
                else:
                    print(f"❌ INVALID DOI FORMAT: Decision #{dec_id} -> {ref}")
                    violations += 1
            elif "http" not in ref.lower() and "reference-gap" not in ref.lower():
                print(f"❌ VIOLATION: Decision #{dec_id} reference is just text: {ref}")
                violations += 1
                
    if violations == 0:
        print("✅ All technical decisions have real, verified DOIs.")
    else:
        print(f"\n⚠️ Found {violations} violations.")
        sys.exit(1)

if __name__ == "__main__":
    enforce(sys.argv[1] if len(sys.argv) > 1 else "examples/delivery-delay-prediction/DECISIONS.md")
