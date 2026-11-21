import unittest
import os
import sys
import tempfile
import shutil
import json
from pathlib import Path

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
        os.environ["MLA_ALLOW_UNLOCK"] = "1"
        try:
            main(["plan", "lock", self.plan_path])
            main(["plan", "unlock", self.plan_path])
            with open(self.plan_path, "a", encoding="utf-8") as f:
                f.write("\n")
        finally:
            os.environ.pop("MLA_ALLOW_UNLOCK", None)

    def test_cli_init_command(self):
        proj_dir = Path(self.test_dir) / "new_test_proj"
        ret = main(["init", str(proj_dir)])
        self.assertEqual(ret, 0)
        self.assertTrue((proj_dir / "REQUIREMENTS.md").exists())
        self.assertTrue((proj_dir / "TECH-CHOICE.md").exists())
        self.assertTrue((proj_dir / "DECISIONS.md").exists())
        self.assertTrue((proj_dir / "PLAN.manifest.json").exists())
        self.assertTrue((proj_dir / "PLAN.lock").exists())
        # R1 scaffolding verification:
        self.assertTrue((proj_dir / "_constitution" / "CONSTITUTION.md").exists())
        self.assertTrue((proj_dir / "skills" / "01-goals-and-requirements" / "SKILL.md").exists())
        self.assertTrue((proj_dir / "references" / "references_to_verify.yaml").exists())
        self.assertTrue((proj_dir / "sandbox" / "example_task.py").exists())
        self.assertTrue((proj_dir / ".cursorrules").exists())
        self.assertTrue((proj_dir / ".cursor" / "mcp.json").exists())
        self.assertTrue((proj_dir / ".github" / "copilot-instructions.md").exists())
        self.assertTrue((proj_dir / ".antigravity" / "rules.md").exists())

    def test_cli_status_command(self):
        ex_manifest = "examples/car-price-prediction/PLAN.manifest.json"
        with self.assertRaises(SystemExit) as cm:
            main(["status", ex_manifest])
        self.assertEqual(cm.exception.code, 0)

    def test_cli_scan_clean_file(self):
        clean_file = Path(self.test_dir) / "clean_code.py"
        clean_file.write_text("import numpy as np\nx = np.array([1, 2, 3])\n", encoding="utf-8")
        ret = main(["scan", str(clean_file)])
        self.assertEqual(ret, 0)


if __name__ == "__main__":
    unittest.main()
