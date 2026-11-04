#!/usr/bin/env python3
"""
enforce_constitution.py - Verifies that every decision in DECISIONS.md has a reference.
Usage: python scripts/enforce_constitution.py projects/my-project/DECISIONS.md
"""
import sys
import re
from pathlib import Path

def enforce(filepath):
    if not Path(filepath).exists():
        print(f"ERROR: {filepath} not found.")
        sys.exit(1)

    content = Path(filepath).read_text(encoding="utf-8")
    
    lines = [line for line in content.split("\n") if line.strip().startswith("|") and "---" not in line]
    
    if not lines:
        print("No decisions found in the ledger.")
        return

    violations = 0
    for i, line in enumerate(lines[1:], start=2):
        cols = [c.strip() for c in line.split("|")[1:-1]]
        if len(cols) < 8:
            continue
            
        decision_id = cols[0]
        question = cols[3]
        reference = cols[7]
        
        if not reference or reference.lower() in ["none", "n/a", "-"]:
            print(f"❌ VIOLATION (Rule B1): Decision #{decision_id} ('{question}') has no reference anchor.")
            violations += 1
            
    if violations == 0:
        print("✅ Constitution Enforced: All decisions have reference anchors.")
    else:
        print(f"\n⚠️ Found {violations} violations. Please fix them before proceeding.")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/enforce_constitution.py <path_to_DECISIONS.md>")
        sys.exit(1)
    enforce(sys.argv[1])
