"""
tests/test_lock_plan.py - Comprehensive unit tests for cryptographic plan locking and immutability.
"""

import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.ml_model_architect.locker import (
    compute_sha256,
    lock_plan,
    verify_plan,
    validate_plan_schema,
    make_writable,
    make_read_only,
    unlock_plan,
    get_lock_path,
)

SAMPLE_PLAN = {
    "plan_version": "1.0.0",
    "project_id": "test-lock-project",
    "client_grounding": {
        "task_type": "binary_classification",
        "target_column": "target",
        "business_metric": "PR-AUC",
        "cost_priority": "high_recall"
    },
    "execution_dag": [
        {
            "step_id": "STEP_01",
            "stage": 3,
            "action_type": "GENERATE_CODE",
            "pre_conditions": ["file_exists('input.txt')"],
            "post_assertions": ["file_exists('output.txt')"]
        }
    ]
}


class TestLockPlanReal(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.plan_path = os.path.join(self.test_dir, "PLAN.manifest.json")
        with open(self.plan_path, "w", encoding="utf-8") as f:
            json.dump(SAMPLE_PLAN, f, indent=2)

    def tearDown(self):
        make_writable(self.plan_path)
        lock_path = get_lock_path(self.plan_path)
        if os.path.exists(lock_path):
            make_writable(lock_path)
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_compute_sha256_crlf_invariance(self):
        f_lf = os.path.join(self.test_dir, "file_lf.txt")
        f_crlf = os.path.join(self.test_dir, "file_crlf.txt")

        with open(f_lf, "wb") as f:
            f.write(b"line1\nline2\nline3\n")
        with open(f_crlf, "wb") as f:
            f.write(b"line1\r\nline2\r\nline3\r\n")

        hash_lf = compute_sha256(f_lf)
        hash_crlf = compute_sha256(f_crlf)
        self.assertEqual(hash_lf, hash_crlf, "SHA-256 must be identical across LF and CRLF line endings")

    def test_lock_and_verify(self):
        file_hash = lock_plan(self.plan_path)
        lock_path = get_lock_path(self.plan_path)
        self.assertTrue(os.path.exists(lock_path))
        with open(lock_path, "r", encoding="utf-8") as f:
            saved_hash = f.read().strip()
        self.assertEqual(file_hash, saved_hash)
        self.assertTrue(verify_plan(self.plan_path))

    def test_tamper_manifest_detection(self):
        lock_plan(self.plan_path)
        make_writable(self.plan_path)
        with open(self.plan_path, "a", encoding="utf-8") as f:
            f.write("\n")
        self.assertFalse(verify_plan(self.plan_path), "Modified manifest must fail verification")

    def test_tamper_lock_detection(self):
        lock_plan(self.plan_path)
        lock_path = get_lock_path(self.plan_path)
        make_writable(lock_path)
        with open(lock_path, "w", encoding="utf-8") as f:
            f.write("0" * 64 + "\n")
        self.assertFalse(verify_plan(self.plan_path), "Modified lock hash must fail verification")

    def test_delete_lock_detection(self):
        lock_plan(self.plan_path)
        lock_path = get_lock_path(self.plan_path)
        make_writable(lock_path)
        os.remove(lock_path)
        self.assertFalse(verify_plan(self.plan_path), "Missing lock file must fail verification")

    def test_invalid_schema_missing_fields(self):
        invalid_plan = {"plan_version": "1.0.0"}
        bad_path = os.path.join(self.test_dir, "bad.manifest.json")
        with open(bad_path, "w", encoding="utf-8") as f:
            json.dump(invalid_plan, f)
        with self.assertRaises(ValueError):
            validate_plan_schema(bad_path)

    def test_unlock_without_env_var_fails(self):
        lock_plan(self.plan_path)
        os.environ.pop("MLA_ALLOW_UNLOCK", None)
        with self.assertRaises(SystemExit) as cm:
            unlock_plan(self.plan_path)
        self.assertEqual(cm.exception.code, 1)

    def test_unlock_with_env_var_succeeds_and_logs(self):
        ledger_path = os.path.join(self.test_dir, "DECISIONS.md")
        with open(ledger_path, "w", encoding="utf-8") as f:
            f.write("# Decision Ledger\n")

        lock_plan(self.plan_path)
        os.environ["MLA_ALLOW_UNLOCK"] = "1"
        try:
            unlock_plan(self.plan_path)
            # Verify writable
            with open(self.plan_path, "a", encoding="utf-8") as f:
                f.write("\n")
            with open(ledger_path, "r", encoding="utf-8") as f:
                ledger_text = f.read()
            self.assertIn("PLAN_UNLOCKED", ledger_text)
        finally:
            os.environ.pop("MLA_ALLOW_UNLOCK", None)

    def test_verify_plan_git_committed(self):
        ex_manifest = str(ROOT / "examples" / "car-price-prediction" / "PLAN.manifest.json")
        self.assertTrue(verify_plan(ex_manifest, check_git=True))


if __name__ == "__main__":
    unittest.main()
