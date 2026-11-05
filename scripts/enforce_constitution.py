#!/usr/bin/env python3
import sys
from pathlib import Path
import requests

def check_doi(doi):
    if "arxiv" in doi.lower():
        doi = doi.lower().replace("arxiv.", "").replace("arxiv:", "")
    try:
        # Try Crossref
        r = requests.get(f"https://api.crossref.org/works/{doi}", timeout=10)
        if r.status_code == 200: return True
        # Fallback to DataCite
        d = requests.get(f"https://api.datacite.org/dois/{doi}", timeout=10)
        return d.status_code == 200
    except:
        return False

def enforce(filepath):
    if not Path(filepath).exists():
        print(f"ERROR: {filepath} not found.")
        sys.exit(1)

    content = Path(filepath).read_text(encoding="utf-8")
    lines = [line for line in content.split("\n") if line.strip().startswith("|") and "---" not in line]
    
    if not lines:
        print("No decisions found.")
        return

    violations = 0
    for line in lines[1:]:
        cols = [c.strip() for c in line.split("|")[1:-1]]
        if len(cols) < 8: 
            print(f"❌ VIOLATION: Malformed row (less than 8 columns): {line[:50]}...")
            violations += 1
            continue
            
        dec_id, dec_type, question, ref = cols[0], cols[2].lower(), cols[3], cols[7]
        
        if dec_type in ["technique", "parameter", "threshold", "deployment"]:
            if not ref or ref.lower() in ["none", "n/a", "-", "n/a (empirical)"] or "memory" in ref.lower():
                print(f"❌ VIOLATION: Decision #{dec_id} has no valid reference.")
                violations += 1
            elif "10." in ref:
                doi_match = re.search(r'10\.\d{4,9}/[^\s]+', ref)
                if doi_match:
                    if not check_doi(doi_match.group(0)):
                        print(f"❌ FAKE DOI: Decision #{dec_id} cites {doi_match.group(0)}")
                        violations += 1
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
