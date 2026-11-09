#!/usr/bin/env python3
import ast
import os
import sys

SANDBOX_DIR = os.path.join(os.path.dirname(__file__), '..', 'sandbox')

class SandboxVisitor(ast.NodeVisitor):
    def __init__(self):
        self.violations = []
        self.banned_imports = {'os', 'subprocess', 'socket', 'pickle', 'ctypes', 'urllib', 'requests', 'boto3'}

    def visit_Import(self, node):
        for alias in node.names:
            if alias.name.split('.')[0] in self.banned_imports:
                self.violations.append((node.lineno, f"Banned import: {alias.name}"))
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module and node.module.split('.')[0] in self.banned_imports:
            self.violations.append((node.lineno, f"Banned import: {node.module}"))
        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            if node.func.id in {'eval', 'exec', '__import__', 'compile'}:
                self.violations.append((node.lineno, f"Banned function: {node.func.id}"))
        self.generic_visit(node)

def scan_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        tree = ast.parse(f.read(), filename=filepath)
    visitor = SandboxVisitor()
    visitor.visit(tree)
    return visitor.violations

def main():
    if not os.path.exists(SANDBOX_DIR):
        print("✅ Sandbox is clean (directory not found).")
        sys.exit(0)
        
    has_violations = False
    for root, _, files in os.walk(SANDBOX_DIR):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    violations = scan_file(filepath)
                    if violations:
                        has_violations = True
                        print(f"🚨 WARNING in {file}:")
                        for line_num, msg in violations:
                            print(f"  Line {line_num}: {msg}")
                except SyntaxError:
                    print(f"🚨 SYNTAX ERROR in {file}. Blocking execution.")
                    has_violations = True
                    
    if has_violations:
        print("\n❌ SCAN FAILED. Blocking execution.")
        sys.exit(1)
    print("\n✅ SCAN PASSED.")
    sys.exit(0)

if __name__ == "__main__":
    main()
