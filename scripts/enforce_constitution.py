#!/usr/bin/env python3
import sys
import re
import yaml
from pathlib import Path
from urllib.parse import urlparse

ALLOWED_TOKENS = {"heuristic", "reference-gap", "n/a (business context)"}

def is_trusted_url(url, whitelist):
    try:
        hostname = urlparse(url).hostname
        if not hostname: return False
        return any(hostname == d or hostname.endswith('.' + d) for d in whitelist)
    except Exception:
        return False

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
        print("❌ ERROR: Ledger table is missing required headers.")
        sys.exit(1)

    violations = 0
    wl_path = Path(__file__).parent.parent / "trusted_domains.yaml"
    whitelist = []
    if wl_path.exists():
        whitelist = yaml.safe_load(wl_path.read_text(encoding="utf-8")).get("domains", [])

    for line in lines[1:]:
        cols = [c.strip() for c in line.split("|")[1:-1]]
        if len(cols) < len(headers): 
            print(f"❌ VIOLATION: Malformed row: {line[:30]}...")
            violations += 1
            continue
            
        dec_type = cols[type_idx].lower()
        question = cols[q_idx]
        ref = cols[ref_idx]
        
        if dec_type in ["technique", "parameter", "threshold", "deployment", "metric", "evaluation"]:
            if not ref or ref.lower() in ALLOWED_TOKENS:
                continue
                
            if "10." in ref:
                # Just check format, not network (verify_dois handles network)
                doi_match = re.search(r'10\.\d{4,9}/[^\s|]+', ref)
                if not doi_match:
                    print(f"❌ INVALID DOI FORMAT: Decision '{question}' -> {ref}")
                    violations += 1
            elif "http" in ref.lower():
                if not is_trusted_url(ref, whitelist):
                    print(f"❌ UNTRUSTED URL: Decision '{question}' cites {ref}")
                    violations += 1
            else:
                print(f"❌ INVALID REFERENCE: Decision '{question}' ref is neither DOI, trusted URL, nor token.")
                violations += 1
                
    if violations == 0:
        print("✅ All technical decisions have valid reference formats.")
    else:
        print(f"\n⚠️ Found {violations} violations.")
        sys.exit(1)

if __name__ == "__main__":
    enforce(sys.argv[1] if len(sys.argv) > 1 else "examples/delivery-delay-prediction/DECISIONS.md")
