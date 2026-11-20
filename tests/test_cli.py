import unittest
import os
import sys
import tempfile
import shutil
import json
from scripts.cli import main
from scripts.lock_plan import make_writable

SAMPLE_PLAN = {
    "plan_version": "1.0.0",
    "project_id": "test-cli",
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

class TestCLI(unittest.TestCase):
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

    def test_cli_help(self):
        with self.assertRaises(SystemExit) as cm:
            main(["--help"])
        self.assertEqual(cm.exception.code, 0)

    def test_cli_plan_lock_and_verify(self):
        # Lock plan
        main(["plan", "lock", self.plan_path])
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "PLAN.lock")))

        # Verify plan
        with self.assertRaises(SystemExit) as cm:
            main(["plan", "verify", self.plan_path])
        self.assertEqual(cm.exception.code, 0)

    def test_cli_plan_unlock(self):
        main(["plan", "lock", self.plan_path])
        main(["plan", "unlock", self.plan_path])
        # Should be writable now
        with open(self.plan_path, "a", encoding="utf-8") as f:
            f.write("\n")

if __name__ == "__main__":
    unittest.main()
