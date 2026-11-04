#!/usr/bin/env python3
import os
import sys
import re

SANDBOX_DIR = os.path.join(os.path.dirname(__file__), '..', 'sandbox')

# Dangerous patterns that could indicate Prompt Injection
DANGEROUS_PATTERNS = [
    r'\bos\.system\b',
    r'\bsubprocess\b',
    r'\beval\b',
    r'\bexec\b',
    r'\brequests\.',
    r'\burllib\b',
    r'\bsocket\b',
    r'\bboto3\b',
    r'\bopen\s*\(\s*[\'"]~', # Accessing home directory
    r'\brm\s+-rf\b'
]

def scan_file(filepath):
    violations = []
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for i, line in enumerate(lines, 1):
            for pattern in DANGEROUS_PATTERNS:
                if re.search(pattern, line):
                    violations.append((i, line.strip(), pattern))
    return violations

def main():
    if not os.path.exists(SANDBOX_DIR):
        print("✅ Sandbox is clean (directory not found).")
        sys.exit(0)

    print("🔍 Scanning sandbox for malicious code...")
    has_violations = False

    for root, _, files in os.walk(SANDBOX_DIR):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                violations = scan_file(filepath)
                if violations:
                    has_violations = True
                    print(f"\n🚨 WARNING: Dangerous code found in {file}:")
                    for line_num, code, pattern in violations:
                        print(f"  Line {line_num}: {code}")
                        print(f"  Matched rule: {pattern}")

    if has_violations:
        print("\n❌ SCAN FAILED. Do not execute this code. Review it manually.")
        sys.exit(1)
    else:
        print("\n✅ SCAN PASSED. No obvious malicious patterns found. Please still review manually.")
        sys.exit(0)

if __name__ == "__main__":
    main()
