#!/usr/bin/env python3
"""
enforce_constitution.py - Verifies DECISIONS.md.
Requires: pip install requests
"""
import sys
import time
from pathlib import Path

try:
    import requests
except ImportError:
    print("Please install requests: pip install requests")
    sys.exit(1)

def check_doi(doi):
    """Pings Crossref API to see if the DOI is real."""
    url = f"https://api.crossref.org/works/{doi}"
    try:
        r = requests.get(url, timeout=10)
        return r.status_code == 200
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
        if len(cols) < 8: continue
            
        dec_id, dec_type, question, ref = cols[0], cols[2].lower(), cols[3], cols[7]
        
        if dec_type in ["technique", "parameter"]:
            if not ref or ref.lower() in ["none", "n/a", "-"]:
                print(f"❌ VIOLATION: Decision #{dec_id} ('{question}') has no reference.")
                violations += 1
            elif "10." in ref:
                doi_match = ref.split("10.")[1].split()[0] if "10." in ref else ""
                full_doi = "10." + doi_match.strip(")")
                print(f"Checking DOI {full_doi} via Crossref...")
                if not check_doi(full_doi):
                    print(f"❌ FAKE DOI: Decision #{dec_id} cites {full_doi} but Crossref rejected it.")
                    violations += 1
                time.sleep(1) # Be polite to API
                
    if violations == 0:
        print("✅ All technical decisions have real, verified DOIs.")
    else:
        print(f"\n⚠️ Found {violations} violations.")

if __name__ == "__main__":
    enforce(sys.argv[1] if len(sys.argv) > 1 else "examples/delivery-delay-prediction/DECISIONS.md")
