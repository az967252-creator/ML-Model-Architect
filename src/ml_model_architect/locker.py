#!/usr/bin/env python3
"""
lock_plan.py - Cryptographic locking and immutability enforcement for PLAN.manifest.json.
Enforces Constitution Part G: Deterministic Execution & Immutable Plan Policy.

SECURITY NOTICE: Local file locking provides TAMPER-EVIDENT protection (detects drift,
parameter modifications, and accidental edits via SHA-256 and read-only attributes).
Local file permissions are NOT tamper-proof against deliberate host collusion by an agent
with full host OS write privileges unless backed by committed git history (git show HEAD:<path>)
and hardened container isolation.
"""

import sys
import os
import re
import json
import hashlib
import stat
import subprocess
from datetime import datetime, timezone

REQUIRED_FIELDS = ["plan_version", "project_id", "client_grounding", "execution_dag"]
STEP_REQUIRED_FIELDS = ["step_id", "stage", "action_type", "pre_conditions", "post_assertions"]

MANIFEST_HASH_PATTERN = re.compile(r"<!--\s*MANIFEST_SHA256:\s*([a-f0-9]{64})\s*-->", re.IGNORECASE)

def compute_sha256(filepath: str) -> str:
    """Computes SHA-256 hash of a file with normalized line endings for cross-platform determinism."""
    with open(filepath, "rb") as f:
        content = f.read()
    # Normalize CRLF to LF so hashes are invariant across Windows, macOS, and Linux
    normalized = content.replace(b"\r\n", b"\n")
    return hashlib.sha256(normalized).hexdigest()

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

def get_lock_path(filepath: str) -> str:
    """Derives lock file path from manifest file path."""
    if filepath.endswith(".manifest.json"):
        lock_path = filepath.replace(".manifest.json", ".lock")
    else:
        lock_path = f"{filepath}.lock"
    return lock_path

def sync_hash_to_ledger(filepath: str, file_hash: str):
    """Stores manifest hash inside DECISIONS.md if present in the same directory."""
    manifest_dir = os.path.dirname(os.path.abspath(filepath))
    ledger_path = os.path.join(manifest_dir, "DECISIONS.md")
    if not os.path.exists(ledger_path):
        return

    try:
        make_writable(ledger_path)
        with open(ledger_path, "r", encoding="utf-8") as f:
            content = f.read()

        hash_line = f"<!-- MANIFEST_SHA256: {file_hash} -->"
        if MANIFEST_HASH_PATTERN.search(content):
            new_content = MANIFEST_HASH_PATTERN.sub(hash_line, content)
        else:
            new_content = content.rstrip() + f"\n\n{hash_line}\n"

        with open(ledger_path, "w", encoding="utf-8") as f:
            f.write(new_content)
    except Exception as e:
        print(f"Warning: Could not record manifest hash in ledger {ledger_path}: {e}", file=sys.stderr)

def log_unlock_to_ledger(filepath: str):
    """Logs an unlock event to DECISIONS.md."""
    manifest_dir = os.path.dirname(os.path.abspath(filepath))
    ledger_path = os.path.join(manifest_dir, "DECISIONS.md")
    if not os.path.exists(ledger_path):
        return

    try:
        make_writable(ledger_path)
        ts = datetime.now(timezone.utc).isoformat()
        unlock_entry = f"\n<!-- PLAN_UNLOCKED: timestamp={ts}, manifest={os.path.basename(filepath)} -->\n"
        with open(ledger_path, "a", encoding="utf-8") as f:
            f.write(unlock_entry)
    except Exception as e:
        print(f"Warning: Could not log unlock to ledger {ledger_path}: {e}", file=sys.stderr)

def lock_plan(filepath: str) -> str:
    """Validates schema, computes hash, writes .lock file, updates ledger, and sets read-only."""
    validate_plan_schema(filepath)
    file_hash = compute_sha256(filepath)
    lock_path = get_lock_path(filepath)

    # Make writable temporarily if it was previously locked
    if os.path.exists(lock_path):
        make_writable(lock_path)

    with open(lock_path, "w", encoding="utf-8") as f:
        f.write(file_hash + "\n")

    sync_hash_to_ledger(filepath, file_hash)

    make_read_only(lock_path)
    make_read_only(filepath)

    print(f"🔒 [LOCKED] Plan successfully validated and locked.")
    print(f"   Manifest: {filepath}")
    print(f"   Lock file: {lock_path}")
    print(f"   SHA-256:  {file_hash}")
    return file_hash

def verify_plan_in_git(filepath: str, actual_hash: str) -> bool:
    """Verifies that the manifest hash matches the committed PLAN.lock in git HEAD."""
    try:
        manifest_dir = os.path.dirname(os.path.abspath(filepath))
        lock_path = get_lock_path(filepath)
        # Find relative path from git repo root
        res = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, cwd=manifest_dir)
        if res.returncode != 0:
            return True  # Not in a git repo, skip git check
        git_root = res.stdout.strip()
        rel_lock_path = os.path.relpath(lock_path, git_root).replace("\\", "/")

        # Check git show HEAD:<path>
        show_res = subprocess.run(["git", "show", f"HEAD:{rel_lock_path}"], capture_output=True, text=True, cwd=git_root)
        if show_res.returncode != 0:
            # File might not yet be committed to HEAD or is newly created
            return True
        committed_hash = show_res.stdout.strip()
        if committed_hash != actual_hash:
            print(f"🚨 [FATAL GIT TAMPER DETECTED] Committed git lock ({committed_hash[:12]}...) does not match manifest hash ({actual_hash[:12]}...)!", file=sys.stderr)
            return False
        print(f"✅ [GIT INTEGRITY OK] Plan matches committed git HEAD ({committed_hash[:12]}...).")
        return True
    except Exception as e:
        print(f"Warning: Could not verify against git HEAD: {e}", file=sys.stderr)
        return True


def verify_plan(filepath: str, check_git: bool = False) -> bool:
    """Verifies that the plan file matches its cryptographic lock, ledger record, and optionally git HEAD."""
    lock_path = get_lock_path(filepath)

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

    # Check ledger manifest hash if DECISIONS.md exists
    manifest_dir = os.path.dirname(os.path.abspath(filepath))
    ledger_path = os.path.join(manifest_dir, "DECISIONS.md")
    if os.path.exists(ledger_path):
        with open(ledger_path, "r", encoding="utf-8") as f:
            ledger_text = f.read()
        m = MANIFEST_HASH_PATTERN.search(ledger_text)
        if m:
            ledger_hash = m.group(1).strip()
            if ledger_hash != actual_hash:
                print(f"🚨 [FATAL TAMPER DETECTED] DECISIONS.md contains manifest hash {ledger_hash}, which does not match actual {actual_hash}!", file=sys.stderr)
                return False

    # Verify against committed git HEAD if requested or in CI
    if check_git or os.environ.get("MLA_VERIFY_GIT") == "1":
        if not verify_plan_in_git(filepath, actual_hash):
            return False

    print(f"✅ [INTEGRITY OK] Plan matches cryptographic lock ({actual_hash[:12]}...).")
    return True

def unlock_plan(filepath: str):
    """Unlocks a plan manifest if authorized via MLA_ALLOW_UNLOCK=1."""
    if os.environ.get("MLA_ALLOW_UNLOCK") != "1":
        print("❌ [ACCESS DENIED] Unlocking plans is restricted. Set MLA_ALLOW_UNLOCK=1 to authorize.", file=sys.stderr)
        sys.exit(1)

    make_writable(filepath)
    lock_path = get_lock_path(filepath)
    if os.path.exists(lock_path):
        make_writable(lock_path)

    log_unlock_to_ledger(filepath)
    print(f"🔓 [UNLOCKED] {filepath} is now writable.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: lock_plan.py [--verify|--verify-git|--unlock] <path_to_plan.json>")
        sys.exit(1)

    flag = None
    target_path = sys.argv[1]
    if target_path in ["--verify", "--verify-git", "--unlock"]:
        flag = target_path
        if len(sys.argv) < 3:
            print(f"Usage: lock_plan.py {flag} <path_to_plan.json>")
            sys.exit(1)
        target_path = sys.argv[2]

    try:
        if flag == "--verify":
            ok = verify_plan(target_path)
            sys.exit(0 if ok else 1)
        elif flag == "--verify-git":
            ok = verify_plan(target_path, check_git=True)
            sys.exit(0 if ok else 1)
        elif flag == "--unlock":
            unlock_plan(target_path)
            sys.exit(0)
        else:
            lock_plan(target_path)
            sys.exit(0)
    except Exception as err:
        print(f"❌ [ERROR] {err}", file=sys.stderr)
        sys.exit(1)
