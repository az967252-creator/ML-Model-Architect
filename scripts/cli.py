#!/usr/bin/env python3
"""
cli.py - Unified Command-Line Interface for ML Model Architect (ml-architect / mla).
"""

import sys
import os
import argparse
import subprocess

VERSION = "1.0.0-rc.1"

def cmd_plan(args):
    plan_path = args.plan_file or "PLAN.manifest.json"
    action = args.action

    if action == "lock":
        from scripts.lock_plan import lock_plan
        lock_plan(plan_path)
    elif action == "verify":
        from scripts.lock_plan import verify_plan
        ok = verify_plan(plan_path)
        sys.exit(0 if ok else 1)
    elif action == "unlock":
        from scripts.lock_plan import make_writable
        make_writable(plan_path)
        lock_path = plan_path.replace(".manifest.json", ".lock")
        if os.path.exists(lock_path):
            make_writable(lock_path)
        print(f"🔓 [UNLOCKED] {plan_path} is now writable.")
    elif action == "check-step":
        if not args.step_id:
            print("Error: --step-id is required for check-step.", file=sys.stderr)
            sys.exit(1)
        from scripts.run_policy import PolicyEngine
        engine = PolicyEngine(plan_path)
        if not engine.verify_integrity():
            sys.exit(2)
        ok, logs = engine.check_step(args.step_id)
        print(f"Step '{args.step_id}' Verification:")
        for log in logs:
            print(log)
        sys.exit(0 if ok else 1)
    else:
        print(f"Unknown plan action: {action}")
        sys.exit(1)

def cmd_status(args):
    plan_path = args.plan_file or "PLAN.manifest.json"
    from scripts.run_policy import PolicyEngine
    engine = PolicyEngine(plan_path)
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

def cmd_scan(args):
    from scripts.scan_sandbox import main as scan_main
    scan_main()

def cmd_enforce(args):
    from scripts.enforce_constitution import enforce
    decisions_path = args.file or "DECISIONS.md"
    exit_code = enforce(decisions_path, online=args.online, allow_offline=args.allow_offline)
    sys.exit(exit_code)

def cmd_verify_dois(args):
    from scripts.verify_dois import main as verify_main
    sys.exit(verify_main())

def cmd_dashboard(args):
    app_path = os.path.join(os.path.dirname(__file__), "..", "app.py")
    subprocess.run(["streamlit", "run", app_path])

def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="ml-architect",
        description="ML Model Architect — A strict, reference-driven framework for disciplined ML engineering."
    )
    parser.add_argument("-v", "--version", action="version", version=f"ML Model Architect v{VERSION}")

    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # plan command
    p_plan = subparsers.add_parser("plan", help="Manage and verify deterministic plan manifest.")
    p_plan.add_argument("action", choices=["lock", "verify", "unlock", "check-step"], help="Action to perform on plan.")
    p_plan.add_argument("plan_file", nargs="?", default="PLAN.manifest.json", help="Path to PLAN.manifest.json")
    p_plan.add_argument("--step-id", help="Step ID to check (required for check-step).")
    p_plan.set_defaults(func=cmd_plan)

    # status command
    p_status = subparsers.add_parser("status", help="Display execution status across all DAG steps.")
    p_status.add_argument("plan_file", nargs="?", default="PLAN.manifest.json", help="Path to PLAN.manifest.json")
    p_status.set_defaults(func=cmd_status)

    # scan command
    p_scan = subparsers.add_parser("scan", help="Scan sandbox code for AST security violations.")
    p_scan.set_defaults(func=cmd_scan)

    # enforce command
    p_enforce = subparsers.add_parser("enforce", help="Validate DECISIONS.md against the Constitution.")
    p_enforce.add_argument("file", nargs="?", default="DECISIONS.md", help="Path to DECISIONS.md")
    p_enforce.add_argument("--online", action="store_true", help="Perform online DOI existence checks.")
    p_enforce.add_argument("--allow-offline", action="store_true", help="Allow offline mode without network fails.")
    p_enforce.set_defaults(func=cmd_enforce)

    # verify-dois command
    p_dois = subparsers.add_parser("verify-dois", help="Verify all references in references_to_verify.yaml.")
    p_dois.set_defaults(func=cmd_verify_dois)

    # dashboard command
    p_dash = subparsers.add_parser("dashboard", help="Launch Streamlit visualization dashboard.")
    p_dash.set_defaults(func=cmd_dashboard)

    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        sys.exit(0)

    args.func(args)

if __name__ == "__main__":
    main()
