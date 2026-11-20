#!/usr/bin/env python3
"""
run_policy.py - Deterministic Execution Engine and Run Policy Runner.
Enforces that AI agent adheres to the locked plan without deviation, skipping, or tampering.
"""

import sys
import os
import re
import ast
import json
from typing import List, Tuple

# Try importing lock_plan helpers
try:
    from scripts.lock_plan import verify_plan, validate_plan_schema
except ImportError:
    # When running directly from scripts directory
    from lock_plan import verify_plan, validate_plan_schema

try:
    from scripts.scan_sandbox import Scanner
except ImportError:
    try:
        from scan_sandbox import Scanner
    except ImportError:
        Scanner = None

class PolicyEngine:
    def __init__(self, plan_path: str, base_dir: str = "."):
        self.plan_path = plan_path
        self.base_dir = os.path.abspath(base_dir)
        self.data = validate_plan_schema(plan_path)

    def verify_integrity(self) -> bool:
        """Verifies that plan is not tampered with."""
        return verify_plan(self.plan_path)

    def resolve_path(self, rel_path: str) -> str:
        """Resolves path relative to base directory."""
        if os.path.isabs(rel_path):
            return rel_path
        return os.path.normpath(os.path.join(self.base_dir, rel_path))

    def evaluate_assertion(self, assertion_str: str) -> Tuple[bool, str]:
        """
        Parses and evaluates deterministic programmatic assertions.
        Supported assertions:
        - file_exists('path')
        - ast_scanner_passed('path')
        - is_single_sklearn_pipeline('path')
        - cv_folds_logged(N)
        - assert_1se_rule_applied()
        - decision_logged_in_ledger('path')
        """
        assertion_str = assertion_str.strip()

        # file_exists('path')
        m_file = re.match(r"^file_exists\(['\"](.*?)['\"]\)$", assertion_str)
        if m_file:
            path = self.resolve_path(m_file.group(1))
            if os.path.exists(path):
                return True, f"File exists: {m_file.group(1)}"
            return False, f"File does NOT exist: {m_file.group(1)} (resolved: {path})"

        # ast_scanner_passed('path')
        m_ast = re.match(r"^ast_scanner_passed\(['\"](.*?)['\"]\)$", assertion_str)
        if m_ast:
            path = self.resolve_path(m_ast.group(1))
            if not os.path.exists(path):
                return False, f"Cannot scan missing file: {m_ast.group(1)}"
            if Scanner is None:
                return False, "AST Scanner module could not be imported."
            try:
                with open(path, "r", encoding="utf-8") as f:
                    source = f.read()
                tree = ast.parse(source, filename=path)
                scanner = Scanner(filename=path)
                scanner.visit(tree)
                if scanner.violations:
                    return False, f"AST Scanner found {len(scanner.violations)} violation(s) in {m_ast.group(1)}: {scanner.violations}"
                return True, f"AST Scanner passed for {m_ast.group(1)}"
            except Exception as e:
                return False, f"AST Scanner parsing error in {m_ast.group(1)}: {e}"

        # is_single_sklearn_pipeline('path')
        m_pipe = re.match(r"^is_single_sklearn_pipeline\(['\"](.*?)['\"]\)$", assertion_str)
        if m_pipe:
            path = self.resolve_path(m_pipe.group(1))
            if not os.path.exists(path):
                return False, f"Cannot check pipeline: file missing {m_pipe.group(1)}"
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                tree = ast.parse(content, filename=path)
                has_pipeline_import = False
                has_pipeline_call = False
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        if node.module and "pipeline" in node.module:
                            for alias in node.names:
                                if alias.name in ["Pipeline", "make_pipeline"]:
                                    has_pipeline_import = True
                    elif isinstance(node, ast.Call):
                        if isinstance(node.func, ast.Name) and node.func.id in ["Pipeline", "make_pipeline"]:
                            has_pipeline_call = True
                        elif isinstance(node.func, ast.Attribute) and node.func.attr in ["Pipeline", "make_pipeline"]:
                            has_pipeline_call = True

                if has_pipeline_import or has_pipeline_call or "Pipeline(" in content or "make_pipeline(" in content:
                    return True, f"Verified scikit-learn Pipeline construction in {m_pipe.group(1)}"
                return False, f"No scikit-learn Pipeline usage detected in {m_pipe.group(1)}"
            except Exception as e:
                return False, f"Error inspecting pipeline AST in {m_pipe.group(1)}: {e}"

        # cv_folds_logged(N)
        m_cv = re.match(r"^cv_folds_logged\((\d+)\)$", assertion_str)
        if m_cv:
            expected_folds = m_cv.group(1)
            # Scan files in sandbox or project for cv=N or n_splits=N
            found = False
            for root, _, files in os.walk(self.resolve_path("sandbox")):
                for f in files:
                    if f.endswith(".py"):
                        with open(os.path.join(root, f), "r", encoding="utf-8", errors="ignore") as pyf:
                            code = pyf.read()
                            if f"cv={expected_folds}" in code or f"n_splits={expected_folds}" in code:
                                found = True
                                break
            if found:
                return True, f"Cross-validation with {expected_folds} folds confirmed."
            return False, f"Cross-validation with {expected_folds} folds not detected in sandbox code."

        # assert_1se_rule_applied()
        if assertion_str == "assert_1se_rule_applied()":
            # Check EVALUATION-REPORT.md or DECISIONS.md or sandbox
            for candidate in ["EVALUATION-REPORT.md", "DECISIONS.md"]:
                cand_path = self.resolve_path(candidate)
                if os.path.exists(cand_path):
                    with open(cand_path, "r", encoding="utf-8", errors="ignore") as f:
                        txt = f.read()
                        if "1-SE" in txt or "one standard error" in txt.lower():
                            return True, f"1-SE rule verified in {candidate}"
            return False, "1-SE rule application not found in EVALUATION-REPORT.md or DECISIONS.md"

        # decision_logged_in_ledger('path')
        m_dec = re.match(r"^decision_logged_in_ledger\(['\"](.*?)['\"]\)$", assertion_str)
        if m_dec:
            path = self.resolve_path(m_dec.group(1))
            if not os.path.exists(path):
                return False, f"Ledger file missing: {m_dec.group(1)}"
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            rows = [line for line in content.splitlines() if line.strip().startswith("|") and "---" not in line and "Stage" not in line]
            if len(rows) > 0:
                return True, f"Decision ledger contains {len(rows)} decision entries."
            return False, f"Decision ledger {m_dec.group(1)} has no recorded decision rows."

        # Fallback unknown assertion
        return False, f"Unknown assertion predicate: {assertion_str}"

    def check_step(self, step_id: str, check_post: bool = True) -> Tuple[bool, List[str]]:
        """Evaluates assertions for a given step."""
        dag = self.data["execution_dag"]
        step = next((s for s in dag if s["step_id"] == step_id), None)
        if not step:
            return False, [f"Step '{step_id}' not found in execution DAG."]

        logs = []
        all_passed = True

        # Pre-conditions
        for prec in step.get("pre_conditions", []):
            passed, msg = self.evaluate_assertion(prec)
            logs.append(f"  [PRE-CONDITION] {'✅' if passed else '❌'} {msg}")
            if not passed:
                all_passed = False

        if check_post:
            for postc in step.get("post_assertions", []):
                passed, msg = self.evaluate_assertion(postc)
                logs.append(f"  [POST-ASSERTION] {'✅' if passed else '❌'} {msg}")
                if not passed:
                    all_passed = False

        return all_passed, logs

    def get_status(self) -> dict:
        """Returns step-by-step evaluation status across the entire DAG."""
        dag = self.data["execution_dag"]
        status_report = []
        current_active_step = None
        for step in dag:
            step_id = step["step_id"]
            ok, logs = self.check_step(step_id, check_post=True)
            status_report.append({
                "step_id": step_id,
                "stage": step.get("stage"),
                "passed": ok,
                "logs": logs
            })
            if not ok and current_active_step is None:
                current_active_step = step_id

        return {
            "project_id": self.data.get("project_id"),
            "current_active_step": current_active_step or "ALL_STEPS_COMPLETED",
            "steps": status_report
        }

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage:")
        print("  run_policy.py verify <plan_file>")
        print("  run_policy.py check-step <plan_file> <step_id>")
        print("  run_policy.py status <plan_file>")
        sys.exit(1)

    cmd = sys.argv[1]
    plan_path = sys.argv[2]

    try:
        engine = PolicyEngine(plan_path)

        if cmd == "verify":
            ok = engine.verify_integrity()
            sys.exit(0 if ok else 1)

        elif cmd == "check-step":
            if len(sys.argv) < 4:
                print("Error: step_id required for check-step command.")
                sys.exit(1)
            # First ensure plan is intact
            if not engine.verify_integrity():
                sys.exit(2)
            step_id = sys.argv[3]
            ok, logs = engine.check_step(step_id)
            print(f"Step '{step_id}' Check Results:")
            for l in logs:
                print(l)
            sys.exit(0 if ok else 1)

        elif cmd == "status":
            if not engine.verify_integrity():
                sys.exit(2)
            status = engine.get_status()
            print(f"==================================================")
            print(f" Project: {status['project_id']}")
            print(f" Active Step: {status['current_active_step']}")
            print(f"==================================================")
            for s in status["steps"]:
                mark = "✅" if s["passed"] else "⏳"
                print(f"{mark} Stage {s['stage']}: {s['step_id']}")
                for l in s["logs"]:
                    print(f"    {l}")
            all_done = status["current_active_step"] == "ALL_STEPS_COMPLETED"
            sys.exit(0 if all_done else 1)

        else:
            print(f"Unknown command: {cmd}")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Policy Engine Error: {e}", file=sys.stderr)
        sys.exit(1)
