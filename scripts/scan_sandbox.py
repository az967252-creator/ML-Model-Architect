#!/usr/bin/env python3
"""
scripts/scan_sandbox.py - Static AST security tripwire analyzer for sandbox code.
Enforces Constitution Rules F4 and F4.1.
Fail-closed on missing/empty directories, blocks dynamic evaluation, non-literal I/O paths,
unbounded loops, and unauthorized filesystem writes.
"""

import ast
import argparse
import os
import re
import sys

# Attempt import of allowed packages from shared module
try:
    from scripts._allowed import ALLOWED_IMPORTS
except ImportError:
    try:
        from _allowed import ALLOWED_IMPORTS
    except ImportError:
        ALLOWED_IMPORTS = {
            "numpy", "pandas", "sklearn", "scipy", "joblib", "xgboost",
            "lightgbm", "catboost", "matplotlib", "seaborn", "skops",
            "optuna", "mlflow", "json", "math", "statistics", "time", "datetime"
        }

SANDBOX_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sandbox"))

class SandboxVisitor(ast.NodeVisitor):
    def __init__(self, filename=None):
        self.filename = filename
        self.violations = []
        self.allowed_imports = set(ALLOWED_IMPORTS)
        self.banned_names = {
            "eval", "exec", "__import__", "compile", "open", "getattr", "setattr",
            "delattr", "globals", "locals", "vars", "breakpoint", "input", "__builtins__"
        }
        self.banned_attrs = {
            "os", "sys", "subprocess", "shutil", "socket", "system", "popen", "importlib",
            "read_pickle", "to_pickle", "fetch_openml", "load_dataset", "fromhex",
            "read_clipboard", "ctypeslib"
        }
        self.allowed_dunders = {"__name__", "__len__", "__init__"}
        
        # Function-level allowlist for I/O
        self.ALLOWED_READ_IO = {"read_csv", "read_json", "load"}
        self.ALLOWED_WRITE_IO = {"to_csv", "to_json", "savefig", "save", "savez", "savetxt"}
        self.BANNED_IO = {
            "read_pickle", "to_pickle", "read_parquet", "to_parquet", "read_excel",
            "to_excel", "read_table", "read_html", "read_xml", "read_clipboard",
            "fromfile", "tofile"
        }

    def visit_Import(self, node):
        for alias in node.names:
            root_mod = alias.name.split(".")[0]
            if root_mod not in self.allowed_imports:
                self.violations.append((node.lineno, f"Untrusted import: {alias.name}"))
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.level:
            self.violations.append((node.lineno, "Relative import not allowed"))
        if node.module:
            root_mod = node.module.split(".")[0]
            if root_mod not in self.allowed_imports:
                self.violations.append((node.lineno, f"Untrusted import: {node.module}"))
        for alias in node.names:
            if alias.name == "*":
                self.violations.append((node.lineno, "Star-imports ('from ... import *') are forbidden"))
            elif alias.name in self.banned_attrs or alias.name in self.banned_names:
                self.violations.append((node.lineno, f"Banned name imported: {alias.name}"))
            elif alias.name.startswith("fetch_"):
                self.violations.append((node.lineno, f"Dataset downloader imported: {alias.name}"))
            elif alias.name in {"ctypeslib", "read_clipboard"}:
                self.violations.append((node.lineno, f"Banned utility imported: {alias.name}"))
        self.generic_visit(node)

    def visit_Name(self, node):
        if node.id in self.banned_names:
            self.violations.append((node.lineno, f"Banned name: {node.id}"))
        elif node.id == "ctypeslib":
            self.violations.append((node.lineno, "ctypeslib usage forbidden"))
        elif node.id.startswith("fetch_"):
            self.violations.append((node.lineno, f"Dataset downloader forbidden: {node.id}"))
        self.generic_visit(node)

    def visit_Attribute(self, node):
        a = node.attr
        if (a.startswith("__") and a.endswith("__") and a not in self.allowed_dunders) or a in self.banned_attrs:
            self.violations.append((node.lineno, f"Banned attribute: {a}"))
        elif a in {"eval", "query"}:
            if isinstance(node.value, ast.Name) and node.value.id in {"pd", "pandas"}:
                self.violations.append((node.lineno, f"Dynamic eval/query forbidden: {a}"))
        elif a == "ctypeslib":
            self.violations.append((node.lineno, "ctypeslib usage forbidden"))
        elif a.startswith("fetch_"):
            self.violations.append((node.lineno, f"Dataset downloader forbidden: {a}"))
        elif a == "read_clipboard":
            self.violations.append((node.lineno, "read_clipboard forbidden"))
        elif a == "use" and isinstance(node.value, ast.Name) and node.value.id in {"matplotlib", "plt"}:
            self.violations.append((node.lineno, "matplotlib.use forbidden"))
        self.generic_visit(node)

    def visit_While(self, node):
        # Detect unbounded infinite loops (while True / while 1 without break)
        is_truthy = False
        if isinstance(node.test, ast.Constant) and bool(node.test.value) is True:
            is_truthy = True
        elif isinstance(node.test, ast.Name) and node.test.id == "True":
            is_truthy = True
        if is_truthy:
            has_break = any(isinstance(n, ast.Break) for n in ast.walk(node))
            if not has_break:
                self.violations.append((node.lineno, "Unbounded infinite loop without break"))
        self.generic_visit(node)

    def visit_Call(self, node):
        # 1. Attribute call checks
        if isinstance(node.func, ast.Attribute):
            attr = node.func.attr
            # Check dynamic eval/query calls (e.g. pd.eval, df.eval, df.query)
            if attr in {"eval", "query"}:
                # PyTorch model.eval() takes 0 arguments; pandas eval/query takes arguments
                if attr == "query" or (attr == "eval" and (node.args or node.keywords)):
                    self.violations.append((node.lineno, f"Dynamic eval/query forbidden: {attr}"))
                elif isinstance(node.func.value, ast.Name) and node.func.value.id in {"pd", "pandas"}:
                    self.violations.append((node.lineno, f"Dynamic eval/query forbidden: {attr}"))
            
            # Check matplotlib.use
            if attr == "use" and isinstance(node.func.value, ast.Name) and node.func.value.id in {"matplotlib", "plt"}:
                self.violations.append((node.lineno, "matplotlib.use forbidden"))

            # Check dataset downloaders
            if attr.startswith("fetch_"):
                self.violations.append((node.lineno, f"Dataset downloader forbidden: {attr}"))

            # Check banned I/O methods
            if attr in self.BANNED_IO:
                self.violations.append((node.lineno, f"Banned I/O method: {attr}"))
            elif attr in (self.ALLOWED_READ_IO | self.ALLOWED_WRITE_IO):
                path_arg = None
                if node.args:
                    path_arg = node.args[0]
                else:
                    for kw in node.keywords:
                        if kw.arg in {"path", "filepath_or_buffer", "fname", "file", "fname_or_buf", "filename"}:
                            path_arg = kw.value
                            break
                if path_arg is not None:
                    # Require literal string
                    if not (isinstance(path_arg, ast.Constant) and isinstance(path_arg.value, str)):
                        self.violations.append((node.lineno, f"I/O path must be a literal relative string: {attr}"))
                    else:
                        val = path_arg.value
                        # Check URL or absolute path
                        if "://" in val or val.startswith(("/", "\\", "~")) or re.match(r"^[A-Za-z]:[\\/]", val):
                            self.violations.append((node.lineno, f"I/O call with URL/absolute path: {val[:25]}"))
                        # Check path traversal
                        if "../" in val or "..\\" in val or ".." in val.replace("\\", "/").split("/"):
                            self.violations.append((node.lineno, f"Path traversal forbidden: {val[:25]}"))
                        # Check write boundary: writes must be to sandbox/out/ or out/
                        if attr in self.ALLOWED_WRITE_IO:
                            norm = os.path.normpath(val).replace("\\", "/")
                            if not (norm.startswith("out/") or norm == "out" or norm.startswith("sandbox/out/") or norm.startswith("./out/")):
                                self.violations.append((node.lineno, f"Write call outside sandbox/out/ directory: {val}"))

        # 2. Standalone call checks
        elif isinstance(node.func, ast.Name):
            if node.func.id.startswith("fetch_"):
                self.violations.append((node.lineno, f"Dataset downloader forbidden: {node.func.id}"))

        self.generic_visit(node)

    def visit_keyword(self, node):
        if node.arg is None:
            self.violations.append((node.value.lineno, "**kwargs unpacking is not allowed"))
        elif node.arg == "allow_pickle" and not (isinstance(node.value, ast.Constant) and node.value.value is False):
            self.violations.append((node.value.lineno, "allow_pickle must be the literal False"))
        self.generic_visit(node)

    def visit_Constant(self, node):
        if isinstance(node.value, str):
            if "../" in node.value or "..\\" in node.value:
                self.violations.append((node.lineno, f"Suspicious path traversal: {node.value[:20]}..."))
        self.generic_visit(node)

# Alias for external tools importing Scanner
Scanner = SandboxVisitor

def scan_code(code, filename="<string>"):
    """Parses and checks code string for security violations."""
    try:
        tree = ast.parse(code, filename=filename)
        visitor = SandboxVisitor(filename=filename)
        visitor.visit(tree)
        return visitor.violations
    except SyntaxError as e:
        return [(e.lineno or 0, f"SyntaxError in file: {e.msg}")]

def scan_file(filepath):
    """Scans an individual file on disk."""
    if os.path.islink(filepath):
        return [(0, f"Symlink detected: {filepath}")]
    ext = os.path.splitext(filepath)[1].lower()
    if ext in {".sh", ".bash", ".ps1", ".so", ".pyc"}:
        return [(0, f"Dangerous file type: {filepath}")]
    if ext != ".py":
        if ext not in {".csv", ".json", ".yaml", ".yml", ".txt", ".parquet", ".md"}:
            return [(0, f"Unrecognized file type: {filepath}")]
        return []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return scan_code(content, filepath)
    except Exception as e:
        return [(0, f"Failed to read file {filepath}: {e}")]

def scan_directory(directory):
    """Scan all python files in a directory and return {filepath: violations}."""
    dir_path = Path(directory)
    if not dir_path.exists() or not dir_path.is_dir():
        raise FileNotFoundError(f"Directory not found: {directory}")
    results = {}
    py_files = sorted(dir_path.glob("**/*.py"))
    for py_file in py_files:
        results[str(py_file)] = scan_file(str(py_file))
    return results

def main(argv=None):
    parser = argparse.ArgumentParser(description="AST Sandbox Code Security Scanner")
    parser.add_argument("paths", nargs="*", default=None, help="File(s) or directory(ies) to scan (defaults to sandbox/)")
    args = parser.parse_args(argv)

    targets = args.paths if args.paths else [SANDBOX_DIR]
    
    files_to_scan = []
    for target in targets:
        if not os.path.exists(target):
            print(f"🚨 REJECTED: Target path does not exist: {target}", file=sys.stderr)
            sys.exit(1)
        if os.path.isfile(target):
            files_to_scan.append(target)
        elif os.path.isdir(target):
            dir_py_files = []
            for root, _, files in os.walk(target, followlinks=False):
                for f in files:
                    full_p = os.path.join(root, f)
                    if f.endswith(".py") or os.path.islink(full_p):
                        dir_py_files.append(full_p)
            if not dir_py_files:
                print(f"🚨 REJECTED: Sandbox directory contains no .py files: {target}", file=sys.stderr)
                sys.exit(1)
            files_to_scan.extend(dir_py_files)

    has_violations = False
    for filepath in files_to_scan:
        violations = scan_file(filepath)
        if violations:
            has_violations = True
            print(f"🚨 WARNING in {filepath}:", file=sys.stderr)
            for line, msg in violations:
                print(f"  Line {line}: {msg}", file=sys.stderr)

    if has_violations:
        sys.exit(1)
    print("\n✅ SCAN PASSED. (Tripwire only. Use Docker for true isolation).")
    sys.exit(0)

if __name__ == "__main__":
    main()
