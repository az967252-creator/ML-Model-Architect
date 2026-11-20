#!/usr/bin/env python3
"""
lock_plan.py - Cryptographic locking and immutability enforcement for PLAN.manifest.json.
Enforces Constitution Part G: Deterministic Execution & Immutable Plan Policy.
"""

import sys
import os
import json
import hashlib
import stat

REQUIRED_FIELDS = ["plan_version", "project_id", "client_grounding", "execution_dag"]
STEP_REQUIRED_FIELDS = ["step_id", "stage", "action_type", "pre_conditions", "post_assertions"]

def compute_sha256(filepath: str) -> str:
    """Computes SHA-256 hash of a file."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

def validate_plan_schema(filepath: str) -> dict:
    """Validates the structure and fields of the plan manifest."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Plan file not found: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {filepath}: {e}")

    for field in REQUIRED_FIELDS:
        if field not in data:
            raise ValueError(f"Missing required top-level field: '{field}'")

    dag = data.get("execution_dag")
    if not isinstance(dag, list) or len(dag) == 0:
        raise ValueError("'execution_dag' must be a non-empty list of steps.")

    seen_ids = set()
    for idx, step in enumerate(dag):
        if not isinstance(step, dict):
            raise ValueError(f"Step at index {idx} is not an object.")
        for sfield in STEP_REQUIRED_FIELDS:
            if sfield not in step:
                raise ValueError(f"Step '{step.get('step_id', idx)}' missing required field: '{sfield}'")
        sid = step["step_id"]
        if sid in seen_ids:
            raise ValueError(f"Duplicate step_id found: '{sid}'")
        seen_ids.add(sid)

    return data

def make_read_only(filepath: str):
    """Sets file permission to read-only."""
    try:
        current_mode = os.stat(filepath).st_mode
        os.chmod(filepath, current_mode & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH))
    except Exception as e:
        print(f"Warning: Could not set read-only attribute on {filepath}: {e}", file=sys.stderr)

def make_writable(filepath: str):
    """Restores writable permission."""
    try:
        current_mode = os.stat(filepath).st_mode
        os.chmod(filepath, current_mode | stat.S_IWUSR)
    except Exception as e:
        print(f"Warning: Could not set writable attribute on {filepath}: {e}", file=sys.stderr)

def lock_plan(filepath: str) -> str:
    """Validates schema, computes hash, writes .lock file, and sets read-only."""
    validate_plan_schema(filepath)
    file_hash = compute_sha256(filepath)
    lock_path = f"{filepath}.lock" if not filepath.endswith(".manifest.json") else filepath.replace(".manifest.json", ".lock")
    if lock_path == filepath:
        lock_path = f"{filepath}.lock"

    # Make writable temporarily if it was previously locked
    if os.path.exists(lock_path):
        make_writable(lock_path)

    with open(lock_path, "w", encoding="utf-8") as f:
        f.write(file_hash + "\n")

    make_read_only(lock_path)
    make_read_only(filepath)

    print(f"🔒 [LOCKED] Plan successfully validated and locked.")
    print(f"   Manifest: {filepath}")
    print(f"   Lock file: {lock_path}")
    print(f"   SHA-256:  {file_hash}")
    return file_hash

def verify_plan(filepath: str) -> bool:
    """Verifies that the plan file matches its cryptographic lock."""
    lock_path = f"{filepath}.lock" if not filepath.endswith(".manifest.json") else filepath.replace(".manifest.json", ".lock")
    if lock_path == filepath:
        lock_path = f"{filepath}.lock"

    if not os.path.exists(filepath):
        print(f"❌ [TAMPER/ERROR] Manifest file does not exist: {filepath}", file=sys.stderr)
        return False
    if not os.path.exists(lock_path):
        print(f"❌ [TAMPER/ERROR] Lock file does not exist: {lock_path}", file=sys.stderr)
        return False

    with open(lock_path, "r", encoding="utf-8") as f:
        expected_hash = f.read().strip()

    actual_hash = compute_sha256(filepath)
    if actual_hash != expected_hash:
        print(f"🚨 [FATAL TAMPER DETECTED] Plan manifest has been modified!", file=sys.stderr)
        print(f"   Expected: {expected_hash}", file=sys.stderr)
        print(f"   Actual:   {actual_hash}", file=sys.stderr)
        return False

    print(f"✅ [INTEGRITY OK] Plan matches cryptographic lock ({actual_hash[:12]}...).")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: lock_plan.py [--verify|--unlock] <path_to_plan.json>")
        sys.exit(1)

    flag = None
    target_path = sys.argv[1]
    if target_path in ["--verify", "--unlock"]:
        flag = target_path
        if len(sys.argv) < 3:
            print(f"Usage: lock_plan.py {flag} <path_to_plan.json>")
            sys.exit(1)
        target_path = sys.argv[2]

    try:
        if flag == "--verify":
            ok = verify_plan(target_path)
            sys.exit(0 if ok else 1)
        elif flag == "--unlock":
            make_writable(target_path)
            lock_path = target_path.replace(".manifest.json", ".lock")
            if os.path.exists(lock_path):
                make_writable(lock_path)
            print(f"🔓 [UNLOCKED] {target_path} is now writable.")
            sys.exit(0)
        else:
            lock_plan(target_path)
            sys.exit(0)
    except Exception as err:
        print(f"❌ [ERROR] {err}", file=sys.stderr)
        sys.exit(1)
