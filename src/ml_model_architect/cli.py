#!/usr/bin/env python3
"""
src/ml_model_architect/cli.py - Unified Command-Line Interface for ML Model Architect (`mla`).

Available commands:
  mla init <project_name>                                Scaffold and lock a new constitutional project
  mla scan [path]                                        Run AST tripwire scan on sandbox code
  mla verify [--manifest path] [--step ID]               Verify cryptographic integrity or step assertions
  mla status [--manifest path]                           Check progress against execution DAG
  mla lock <manifest>                                    Cryptographically lock a plan manifest
  mla enforce <ledger> [--online] [--max-heuristic-ratio R]
                                                         Validate constitutional decision ledger
  mla verify-dois [--strict] [--check-md]                Check DOI citations against Crossref/DataCite
  mla dashboard                                          Launch Streamlit audit dashboard
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

from .__version__ import __version__
from .locker import lock_plan, verify_plan, unlock_plan, make_writable
from .policy import PolicyEngine
from .scanner import scan_file, scan_directory
from .enforcer import enforce as enforce_constitution
from .doi import verify_dois
from .resources import get_resource_text


def cmd_init(args):
    """Scaffold a new disciplined ML engineering project."""
    project_dir = Path(args.project_name)
    if project_dir.exists() and any(project_dir.iterdir()):
        print(f"ERROR: Destination directory '{project_dir}' already exists and is not empty.", file=sys.stderr)
        sys.exit(1)

    project_dir.mkdir(parents=True, exist_ok=True)
    project_id = project_dir.name

    # 1. REQUIREMENTS.md
    req_text = get_resource_text("TEMPLATE-REQUIREMENTS.md")
    (project_dir / "REQUIREMENTS.md").write_text(req_text, encoding="utf-8")

    # 2. TECH-CHOICE.md
    tech_text = get_resource_text("TEMPLATE-TECH-CHOICE.md")
    (project_dir / "TECH-CHOICE.md").write_text(tech_text, encoding="utf-8")

    # 3. DECISIONS.md
    dec_text = get_resource_text("TEMPLATE-DECISION-LEDGER.md")
    (project_dir / "DECISIONS.md").write_text(dec_text, encoding="utf-8")

    # 4. PLAN.manifest.json
    plan_template = get_resource_text("TEMPLATE-PLAN-MANIFEST.json")
    try:
        plan_data = json.loads(plan_template)
        plan_data["project_id"] = project_id
        plan_path = project_dir / "PLAN.manifest.json"
        with open(plan_path, "w", encoding="utf-8") as f:
            json.dump(plan_data, f, indent=2)
    except Exception as e:
        print(f"ERROR creating PLAN.manifest.json: {e}", file=sys.stderr)
        sys.exit(1)

    # 5. Cryptographically lock the plan
    try:
        lock_plan(str(plan_path))
    except Exception as e:
        print(f"ERROR locking plan manifest: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"✅ Successfully initialized project: {project_dir}")
    print("📁 Scaffolded files:")
    print("   - REQUIREMENTS.md")
    print("   - TECH-CHOICE.md")
    print("   - DECISIONS.md")
    print("   - PLAN.manifest.json")
    print("   - PLAN.lock")
    print(f"🔒 Plan cryptographically locked and registered. Ready for Stage 1 execution.")
    return 0


def cmd_scan(args):
    target = Path(args.path) if args.path else Path("sandbox")
    if not target.exists():
        print(f"ERROR: Target path does not exist: {target}", file=sys.stderr)
        sys.exit(1)

    if target.is_file():
        violations = scan_file(target)
        if violations:
            print(f"❌ AST scan failed for {target}: {len(violations)} violation(s):")
            for line, v in violations:
                print(f"   Line {line}: {v}")
            sys.exit(1)
        print(f"✅ AST scan passed: {target}")
        return 0
    else:
        results = scan_directory(target)
        if not results:
            print(f"ERROR: No python files found to scan in {target}", file=sys.stderr)
            sys.exit(1)
        total_violations = sum(len(v) for v in results.values())
        if total_violations > 0:
            print(f"❌ AST scan failed: {total_violations} violation(s) found across {len(results)} file(s).")
            for f, viols in results.items():
                if viols:
                    print(f"  {f}:")
                    for line, v in viols:
                        print(f"    Line {line}: {v}")
            sys.exit(1)
        print(f"✅ AST scan passed: All {len(results)} files in {target} clean.")
        return 0


def cmd_verify(args):
    manifest = Path(args.manifest) if args.manifest else Path("PLAN.manifest.json")
    if not manifest.exists():
        print(f"ERROR: Manifest not found: {manifest}", file=sys.stderr)
        sys.exit(1)

    engine = PolicyEngine(manifest)
    if not engine.verify_integrity():
        print("❌ Integrity check failed: manifest does not match cryptographic lock.", file=sys.stderr)
        sys.exit(2)

    if args.step:
        ok, logs = engine.check_step(args.step)
        print(f"Step '{args.step}' Verification:")
        for log in logs:
            print(log)
        sys.exit(0 if ok else 1)
    else:
        print(f"✅ [INTEGRITY OK] {manifest} matches cryptographic lock.")
        return 0


def cmd_status(args):
    manifest = Path(args.manifest) if args.manifest else Path("PLAN.manifest.json")
    if not manifest.exists():
        print(f"ERROR: Manifest not found: {manifest}", file=sys.stderr)
        sys.exit(1)

    engine = PolicyEngine(manifest)
    if not engine.verify_integrity():
        sys.exit(2)

    status = engine.get_status()
    print("==================================================")
    print(f" Project: {status['project_id']}")
    print(f" Active Step: {status['current_active_step']}")
    print("==================================================")
    for s in status["steps"]:
        mark = "✅" if s["passed"] else "⏳"
        print(f"{mark} Stage {s['stage']}: {s['step_id']}")
        for l in s["logs"]:
            print(f"    {l}")
    all_done = status["current_active_step"] == "ALL_STEPS_COMPLETED"
    sys.exit(0 if all_done else 1)


def cmd_lock(args):
    manifest = args.manifest
    lock_plan(manifest)


def cmd_enforce(args):
    ledger = args.ledger or "DECISIONS.md"
    exit_code = enforce_constitution(
        ledger,
        online=args.online,
        allow_offline=not args.online,
        max_heuristic_ratio=args.max_heuristic_ratio,
    )
    sys.exit(exit_code)


def cmd_verify_dois(args):
    ret = verify_dois(
        strict=args.strict,
        check_markdown=args.check_md,
    )
    sys.exit(ret)


def cmd_dashboard(args):
    app_path = Path(__file__).resolve().parent.parent.parent / "app.py"
    subprocess.run(["streamlit", "run", str(app_path)])


def cmd_plan_legacy(args):
    action = args.action
    plan_path = args.plan_file or "PLAN.manifest.json"
    if action == "lock":
        lock_plan(plan_path)
    elif action == "verify":
        ok = verify_plan(plan_path)
        sys.exit(0 if ok else 1)
    elif action == "unlock":
        unlock_plan(plan_path)
    elif action == "check-step":
        if not args.step_id:
            print("Error: --step-id is required for check-step.", file=sys.stderr)
            sys.exit(1)
        engine = PolicyEngine(plan_path)
        if not engine.verify_integrity():
            sys.exit(2)
        ok, logs = engine.check_step(args.step_id)
        print(f"Step '{args.step_id}' Verification:")
        for log in logs:
            print(log)
        sys.exit(0 if ok else 1)


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(
        prog="mla",
        description="ML Model Architect — A strict, reference-driven framework for disciplined ML engineering."
    )
    parser.add_argument("-v", "--version", action="version", version=f"ML Model Architect v{__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # init
    p_init = subparsers.add_parser("init", help="Scaffold a new project workspace.")
    p_init.add_argument("project_name", help="Directory name for the new project")
    p_init.set_defaults(func=cmd_init)

    # scan
    p_scan = subparsers.add_parser("scan", help="Run AST static tripwire analysis on sandbox code.")
    p_scan.add_argument("path", nargs="?", default="sandbox", help="Target file or directory to scan (default: sandbox)")
    p_scan.set_defaults(func=cmd_scan)

    # verify
    p_verify = subparsers.add_parser("verify", help="Verify plan integrity or execute step assertions.")
    p_verify.add_argument("--manifest", default="PLAN.manifest.json", help="Path to PLAN.manifest.json")
    p_verify.add_argument("--step", help="Step ID to assert")
    p_verify.set_defaults(func=cmd_verify)

    # status
    p_status = subparsers.add_parser("status", help="Display execution DAG step completion status.")
    p_status.add_argument("manifest", nargs="?", default="PLAN.manifest.json", help="Path to PLAN.manifest.json")
    p_status.set_defaults(func=cmd_status)

    # lock
    p_lock = subparsers.add_parser("lock", help="Cryptographically lock a plan manifest.")
    p_lock.add_argument("manifest", help="Path to PLAN.manifest.json to lock")
    p_lock.set_defaults(func=cmd_lock)

    # enforce
    p_enforce = subparsers.add_parser("enforce", help="Validate decision ledger against constitutional rules.")
    p_enforce.add_argument("ledger", nargs="?", default="DECISIONS.md", help="Path to DECISIONS.md")
    p_enforce.add_argument("--online", action="store_true", help="Perform live Crossref DOI lookups")
    p_enforce.add_argument("--max-heuristic-ratio", type=float, default=0.4, help="Max allowed heuristic/reference-gap ratio")
    p_enforce.set_defaults(func=cmd_enforce)

    # verify-dois
    p_doi = subparsers.add_parser("verify-dois", help="Validate literature citations against Crossref and DataCite.")
    p_doi.add_argument("--strict", action="store_true", help="Fail if any DOI cannot be verified live")
    p_doi.add_argument("--check-md", action="store_true", help="Scan reference markdown files for uncataloged DOIs")
    p_doi.set_defaults(func=cmd_verify_dois)

    # dashboard
    p_dash = subparsers.add_parser("dashboard", help="Launch interactive Streamlit dashboard.")
    p_dash.set_defaults(func=cmd_dashboard)

    # legacy plan command for backwards compatibility
    p_plan = subparsers.add_parser("plan", help="Manage and verify deterministic plan manifest (legacy).")
    p_plan.add_argument("action", choices=["lock", "verify", "unlock", "check-step"], help="Action to perform")
    p_plan.add_argument("plan_file", nargs="?", default="PLAN.manifest.json", help="Path to plan")
    p_plan.add_argument("--step-id", help="Step ID to check")
    p_plan.set_defaults(func=cmd_plan_legacy)

    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
