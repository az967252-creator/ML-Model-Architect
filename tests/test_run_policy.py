import unittest
import os
import json
import tempfile
import shutil
from scripts.lock_plan import (
    lock_plan,
    verify_plan,
    validate_plan_schema,
    compute_sha256,
    make_writable,
    make_read_only
)
from scripts.run_policy import PolicyEngine

SAMPLE_PLAN = {
    "plan_version": "1.0.0",
    "project_id": "test-project",
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

class TestLockPlan(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.plan_path = os.path.join(self.test_dir, "PLAN.manifest.json")
        with open(self.plan_path, "w", encoding="utf-8") as f:
            json.dump(SAMPLE_PLAN, f, indent=2)

    def tearDown(self):
        make_writable(self.plan_path)
        lock_path = os.path.join(self.test_dir, "PLAN.lock")
        if os.path.exists(lock_path):
            make_writable(lock_path)
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_lock_and_verify(self):
        sha = lock_plan(self.plan_path)
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "PLAN.lock")))
        self.assertTrue(verify_plan(self.plan_path))

    def test_tamper_detection(self):
        lock_plan(self.plan_path)
        # Attempt to tamper with the plan manifest
        make_writable(self.plan_path)
        with open(self.plan_path, "a", encoding="utf-8") as f:
            f.write("\n ")
        self.assertFalse(verify_plan(self.plan_path))

    def test_invalid_schema_missing_fields(self):
        invalid_path = os.path.join(self.test_dir, "invalid.json")
        with open(invalid_path, "w", encoding="utf-8") as f:
            json.dump({"plan_version": "1.0.0"}, f)
        with self.assertRaises(ValueError):
            validate_plan_schema(invalid_path)

class TestPolicyEngine(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.plan_path = os.path.join(self.test_dir, "PLAN.manifest.json")
        with open(self.plan_path, "w", encoding="utf-8") as f:
            json.dump(SAMPLE_PLAN, f, indent=2)
        lock_plan(self.plan_path)

    def tearDown(self):
        make_writable(self.plan_path)
        lock_path = os.path.join(self.test_dir, "PLAN.lock")
        if os.path.exists(lock_path):
            make_writable(lock_path)
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_assertions_evaluation(self):
        engine = PolicyEngine(self.plan_path, base_dir=self.test_dir)
        self.assertTrue(engine.verify_integrity())

        # Pre-condition fails because input.txt does not exist
        passed, msg = engine.evaluate_assertion("file_exists('input.txt')")
        self.assertFalse(passed)

        # Create input.txt and re-check
        with open(os.path.join(self.test_dir, "input.txt"), "w") as f:
            f.write("data")
        passed, msg = engine.evaluate_assertion("file_exists('input.txt')")
        self.assertTrue(passed)

    def test_ast_scanner_evaluation(self):
        engine = PolicyEngine(self.plan_path, base_dir=self.test_dir)
        clean_file = os.path.join(self.test_dir, "clean.py")
        with open(clean_file, "w", encoding="utf-8") as f:
            f.write("import numpy as np\nx = np.array([1, 2, 3])\n")
        passed, msg = engine.evaluate_assertion("ast_scanner_passed('clean.py')")
        self.assertTrue(passed)

        bad_file = os.path.join(self.test_dir, "bad.py")
        with open(bad_file, "w", encoding="utf-8") as f:
            f.write("import os\nos.system('echo test')\n")
        passed, msg = engine.evaluate_assertion("ast_scanner_passed('bad.py')")
        self.assertFalse(passed)

    def test_step_check(self):
        engine = PolicyEngine(self.plan_path, base_dir=self.test_dir)
        # Create input.txt and output.txt
        with open(os.path.join(self.test_dir, "input.txt"), "w") as f:
            f.write("data")
        with open(os.path.join(self.test_dir, "output.txt"), "w") as f:
            f.write("result")

        ok, logs = engine.check_step("STEP_01")
        self.assertTrue(ok)

if __name__ == "__main__":
    unittest.main()
