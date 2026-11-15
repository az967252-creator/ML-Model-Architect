import ast
import os
import sys

SANDBOX_DIR = os.path.join(os.path.dirname(__file__), '..', 'sandbox')

class SandboxVisitor(ast.NodeVisitor):
    def __init__(self):
        self.violations = []
        self.allowed_imports = {
            'pandas', 'numpy', 'sklearn', 'xgboost', 'lightgbm', 'catboost', 
            'matplotlib', 'seaborn', 'json', 'math', 'statistics', 'time', 
            'datetime', 'skops'
        }
        self.banned_names = {
            'eval', 'exec', '__import__', 'compile', 'open', 'getattr', 'setattr', 
            'delattr', 'globals', 'locals', 'vars', 'breakpoint', 'input', '__builtins__'
        }
        self.banned_attrs = {
            'os', 'sys', 'subprocess', 'shutil', 'socket', 'system', 'popen', 'importlib',
            'read_pickle', 'to_pickle', 'fetch_openml', 'load_dataset', 'fromhex'
        }
        self.allowed_dunders = {'__name__', '__len__', '__init__'}

    def visit_Import(self, node):
        for alias in node.names:
            if alias.name.split('.')[0] not in self.allowed_imports:
                self.violations.append((node.lineno, f"Untrusted import: {alias.name}"))
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.level:
            self.violations.append((node.lineno, "Relative import not allowed"))
        if node.module and node.module.split('.')[0] not in self.allowed_imports:
            self.violations.append((node.lineno, f"Untrusted import: {node.module}"))
        self.generic_visit(node)

    def visit_Name(self, node):
        if node.id in self.banned_names:
            self.violations.append((node.lineno, f"Banned name: {node.id}"))
        self.generic_visit(node)

    def visit_Attribute(self, node):
        a = node.attr
        if (a.startswith('__') and a.endswith('__') and a not in self.allowed_dunders) or a in self.banned_attrs:
            self.violations.append((node.lineno, f"Banned attribute: {a}"))
        self.generic_visit(node)

    def visit_keyword(self, node):
        if node.arg == 'allow_pickle' and isinstance(node.value, ast.Constant) and node.value.value is True:
            self.violations.append((node.value.lineno, "allow_pickle=True is not allowed"))
        self.generic_visit(node)
        
    def visit_Constant(self, node):
        if isinstance(node.value, str):
            if '../' in node.value or '..\\' in node.value:
                self.violations.append((node.lineno, f"Suspicious path traversal: {node.value[:20]}..."))
        self.generic_visit(node)

def scan_code(code, filename):
    try:
        tree = ast.parse(code, filename=filename)
        visitor = SandboxVisitor()
        visitor.visit(tree)
        return visitor.violations
    except SyntaxError:
        return [(0, "SyntaxError in file")]

def main():
    if not os.path.exists(SANDBOX_DIR):
        print("✅ Sandbox clean.")
        sys.exit(0)
        
    has_violations = False
    for root, dirs, files in os.walk(SANDBOX_DIR, followlinks=False):
        for file in files:
            filepath = os.path.join(root, file)
            
            if os.path.islink(filepath):
                print(f"🚨 REJECTED: Symlink detected: {file}")
                has_violations = True
                continue
                
            ext = os.path.splitext(file)[1].lower()
            if ext == '.sh' or ext in {'.bash', '.ps1', '.so', '.pyc'}:
                print(f"🚨 REJECTED: Dangerous file type: {file}")
                has_violations = True
            elif ext == '.py':
                with open(filepath, 'r', encoding='utf-8') as f:
                    v = scan_code(f.read(), file)
                    if v:
                        has_violations = True
                        print(f"🚨 WARNING in {file}:")
                        for line, msg in v: print(f"  Line {line}: {msg}")
            elif ext not in {'.csv', '.json', '.yaml', '.yml', '.txt', '.parquet'}:
                print(f"🚨 REJECTED: Unrecognized file type: {file}")
                has_violations = True
                    
    if has_violations:
        sys.exit(1)
    print("\n✅ SCAN PASSED. (Tripwire only. Use Docker for true isolation).")
    sys.exit(0)

if __name__ == "__main__":
    main()
