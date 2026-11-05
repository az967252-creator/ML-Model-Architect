import os, sys, re
SANDBOX_DIR = os.path.join(os.path.dirname(__file__), '..', 'sandbox')
DANGEROUS_PATTERNS = [
    r'\bos\.system\b', r'\bsubprocess\b', r'\b__import__\b', 
    r'\bpickle\b', r'\bctypes\b', r'\brequests\.', r'\burllib\b', 
    r'\bsocket\b', r'\bboto3\b', r'\brm\s+-rf\b'
]
# Regex to catch eval() but ignore model.eval() or df.eval()
EVAL_PATTERN = r'(?<![\.\w])eval\s*\('

def scan_file(filepath):
    violations = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f.readlines(), 1):
            for pattern in DANGEROUS_PATTERNS:
                if re.search(pattern, line):
                    violations.append((i, line.strip(), pattern))
            if re.search(EVAL_PATTERN, line):
                violations.append((i, line.strip(), "eval()"))
    return violations

def main():
    if not os.path.exists(SANDBOX_DIR):
        print("✅ Sandbox is clean.")
        sys.exit(0)
    has_violations = False
    for root, _, files in os.walk(SANDBOX_DIR):
        for file in files:
            if file.endswith('.py') or file.endswith('.sh'):
                violations = scan_file(os.path.join(root, file))
                if violations:
                    has_violations = True
                    print(f"🚨 WARNING in {file}:")
                    for line_num, code, pattern in violations:
                        print(f"  Line {line_num}: {code}")
    if has_violations:
        print("\n❌ SCAN FAILED.")
        sys.exit(1)
    print("\n✅ SCAN PASSED.")
    sys.exit(0)

if __name__ == "__main__":
    main()
