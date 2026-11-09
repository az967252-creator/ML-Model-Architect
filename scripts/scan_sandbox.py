#!/usr/bin/env python3
"""First-line static scan of AI-generated code in sandbox/ (rule F4).

This is an ALLOWLIST check: a script may only import the modules listed in
ALLOWED_IMPORTS, may not use dynamic-execution builtins, and may not contain
string literals that look like absolute paths, parent-directory paths or URLs.

It is a filter, NOT a security boundary. Run the code itself in an isolated
container (see sandbox/README.md) -- static analysis cannot catch everything.

Usage: python scripts/scan_sandbox.py [directory]   (default: ../sandbox)
Exit code: 0 = clean, 1 = violations found.
"""
import ast
import json
import os
import sys

ALLOWED_IMPORTS = {
    # numerics / data
    "numpy", "pandas", "scipy", "statsmodels",
    # ML
    "sklearn", "xgboost", "lightgbm", "catboost", "torch", "tensorflow", "keras",
    "optuna", "mlflow", "shap", "joblib", "imblearn", "umap", "hdbscan", "tabpfn",
    # plotting
    "matplotlib", "seaborn",
    # pure-python stdlib helpers
    "__future__", "abc", "argparse", "bisect", "collections", "copy", "csv", "dataclasses",
    "datetime", "decimal", "enum", "fractions", "functools", "heapq", "itertools", "json",
    "logging", "math", "numbers", "operator", "random", "re", "statistics", "string",
    "textwrap", "time", "typing", "warnings",
}
BANNED_CALLS = {"eval", "exec", "compile", "__import__", "getattr", "setattr", "delattr",
                "globals", "locals", "breakpoint"}
BANNED_NAMES = {"__builtins__"}
BANNED_ATTRS = {"__import__", "__builtins__", "__globals__", "__subclasses__", "__bases__",
                "__mro__", "__code__", "__loader__", "__spec__", "__getattribute__"}
PLAIN_EXTENSIONS = {".md", ".txt", ".csv", ".json", ".yaml", ".yml", ".png", ".gitkeep"}


class Visitor(ast.NodeVisitor):
    def __init__(self):
        self.violations = []

    def flag(self, node, msg):
        self.violations.append((getattr(node, "lineno", 0), msg))

    def visit_Import(self, node):
        for alias in node.names:
            if alias.name.split(".")[0] not in ALLOWED_IMPORTS:
                self.flag(node, f"import not allowed: {alias.name}")

    def visit_ImportFrom(self, node):
        if node.level:
            self.flag(node, "relative import not allowed")
        elif (node.module or "").split(".")[0] not in ALLOWED_IMPORTS:
            self.flag(node, f"import not allowed: {node.module}")

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id in BANNED_CALLS:
            self.flag(node, f"banned builtin: {node.func.id}()")
        self.generic_visit(node)

    def visit_Name(self, node):
        if node.id in BANNED_NAMES:
            self.flag(node, f"banned name: {node.id}")

    def visit_Attribute(self, node):
        if node.attr in BANNED_ATTRS:
            self.flag(node, f"banned attribute: .{node.attr}")
        self.generic_visit(node)

    def visit_Expr(self, node):
        # docstrings / bare strings are not executed: skip the literal check for them
        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            return
        self.generic_visit(node)

    def visit_Constant(self, node):
        s = node.value
        if not isinstance(s, str) or len(s) < 2:
            return
        parts = s.replace("\\", "/").split("/")
        if s.startswith(("/", "~")) or ".." in parts or "://" in s:
            self.flag(node, f"suspicious path/URL literal: {s[:40]!r}")


def scan_source(source, filename="<string>"):
    """Return [(lineno, message)] for a piece of Python source."""
    try:
        tree = ast.parse(source, filename=filename)
    except SyntaxError as e:
        return [(e.lineno or 0, f"syntax error: {e.msg}")]
    v = Visitor()
    v.visit(tree)
    return sorted(v.violations)


def scan_file(path):
    ext = os.path.splitext(path)[1].lower()
    base = os.path.basename(path)
    if ext == ".py":
        with open(path, encoding="utf-8") as f:
            return scan_source(f.read(), path)
    if ext == ".ipynb":
        try:
            with open(path, encoding="utf-8") as f:
                nb = json.load(f)
            code = "\n".join("".join(c.get("source", [])) for c in nb.get("cells", [])
                             if c.get("cell_type") == "code")
        except (ValueError, OSError) as e:
            return [(0, f"unreadable notebook: {e}")]
        return scan_source(code, path)
    if ext in PLAIN_EXTENSIONS or base in PLAIN_EXTENSIONS:
        return []
    return [(0, f"file type not allowed in sandbox: {base}")]


def scan_dir(directory):
    """Return {relative_path: [(lineno, message), ...]} for every offending file."""
    found = {}
    for root, _, files in os.walk(directory):
        for name in sorted(files):
            path = os.path.join(root, name)
            problems = scan_file(path)
            if problems:
                found[os.path.relpath(path, directory)] = problems
    return found


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    directory = argv[0] if argv else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sandbox")
    if not os.path.isdir(directory):
        print("✅ Nothing to scan (sandbox directory not found).")
        return 0
    found = scan_dir(directory)
    for path, problems in found.items():
        print(f"🚨 {path}")
        for lineno, msg in problems:
            print(f"   line {lineno}: {msg}")
    if found:
        print("\n❌ SCAN FAILED. Do not run these files.")
        return 1
    print("✅ SCAN PASSED (static filter only -- still run the code in an isolated container).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
