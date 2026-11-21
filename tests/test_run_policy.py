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
    make_read_only,
    unlock_plan
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

    def test_tamper_manifest_detection(self):
        lock_plan(self.plan_path)
        # Attempt to tamper with the plan manifest
        make_writable(self.plan_path)
        with open(self.plan_path, "a", encoding="utf-8") as f:
            f.write("\n ")
        self.assertFalse(verify_plan(self.plan_path))

    def test_tamper_lock_detection(self):
        lock_plan(self.plan_path)
        lock_path = os.path.join(self.test_dir, "PLAN.lock")
        make_writable(lock_path)
        with open(lock_path, "w", encoding="utf-8") as f:
            f.write("0" * 64 + "\n")
        self.assertFalse(verify_plan(self.plan_path))

    def test_delete_lock_detection(self):
        lock_plan(self.plan_path)
        lock_path = os.path.join(self.test_dir, "PLAN.lock")
        make_writable(lock_path)
        os.remove(lock_path)
        self.assertFalse(verify_plan(self.plan_path))

    def test_unlock_without_env_var_fails(self):
        lock_plan(self.plan_path)
        if "MLA_ALLOW_UNLOCK" in os.environ:
            del os.environ["MLA_ALLOW_UNLOCK"]
        with self.assertRaises(SystemExit) as ctx:
            unlock_plan(self.plan_path)
        self.assertEqual(ctx.exception.code, 1)

    def test_unlock_with_env_var_succeeds_and_logs(self):
        # Create DECISIONS.md
        ledger_path = os.path.join(self.test_dir, "DECISIONS.md")
        with open(ledger_path, "w", encoding="utf-8") as f:
            f.write("# Decision Ledger\n")

        lock_plan(self.plan_path)
        os.environ["MLA_ALLOW_UNLOCK"] = "1"
        try:
            unlock_plan(self.plan_path)
            with open(ledger_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertIn("PLAN_UNLOCKED", content)
        finally:
            del os.environ["MLA_ALLOW_UNLOCK"]

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

    def test_single_sklearn_pipeline_pass(self):
        engine = PolicyEngine(self.plan_path, base_dir=self.test_dir)
        pipe_file = os.path.join(self.test_dir, "pipe_valid.py")
        code = (
            "from sklearn.pipeline import Pipeline\n"
            "from sklearn.preprocessing import StandardScaler\n"
            "from sklearn.linear_model import LogisticRegression\n"
            "from sklearn.model_selection import train_test_split\n"
            "X_tr, X_te, y_tr, y_te = train_test_split(X, y)\n"
            "pipeline = Pipeline([('scaler', StandardScaler()), ('clf', LogisticRegression())])\n"
            "pipeline.fit(X_tr, y_tr)\n"
        )
        with open(pipe_file, "w", encoding="utf-8") as f:
            f.write(code)
        passed, msg = engine.evaluate_assertion("is_single_sklearn_pipeline('pipe_valid.py')")
        self.assertTrue(passed, msg)

    def test_single_sklearn_pipeline_gaming_comment(self):
        engine = PolicyEngine(self.plan_path, base_dir=self.test_dir)
        fake_file = os.path.join(self.test_dir, "pipe_comment.py")
        code = (
            "# Pipeline([('scaler', StandardScaler())])\n"
            "# pipeline.fit(X_train, y_train)\n"
            "x = 10\n"
        )
        with open(fake_file, "w", encoding="utf-8") as f:
            f.write(code)
        passed, msg = engine.evaluate_assertion("is_single_sklearn_pipeline('pipe_comment.py')")
        self.assertFalse(passed, "Comment with Pipeline() must fail single pipeline check")

    def test_single_sklearn_pipeline_data_leakage(self):
        engine = PolicyEngine(self.plan_path, base_dir=self.test_dir)
        leak_file = os.path.join(self.test_dir, "pipe_leak.py")
        code = (
            "from sklearn.preprocessing import StandardScaler\n"
            "from sklearn.model_selection import train_test_split\n"
            "from sklearn.pipeline import Pipeline\n"
            "scaler = StandardScaler()\n"
            "scaler.fit(X)\n"  # Leakage: fitting before split!
            "X_tr, X_te, y_tr, y_te = train_test_split(X, y)\n"
            "pipeline = Pipeline([('s', scaler)])\n"
            "pipeline.fit(X_tr, y_tr)\n"
        )
        with open(leak_file, "w", encoding="utf-8") as f:
            f.write(code)
        passed, msg = engine.evaluate_assertion("is_single_sklearn_pipeline('pipe_leak.py')")
        self.assertFalse(passed, "Transformer fit before train_test_split must trigger leakage failure")

    def test_cv_folds_logged_pass_and_gaming(self):
        engine = PolicyEngine(self.plan_path, base_dir=self.test_dir)
        metrics_file = os.path.join(self.test_dir, "metrics.json")

        # Gaming: no metrics.json file exists
        passed, msg = engine.evaluate_assertion("cv_folds_logged(5)")
        self.assertFalse(passed)

        # Write valid metrics.json
        valid_metrics = {
            "model": "LogisticRegression",
            "fold_scores": [0.85, 0.86, 0.84, 0.87, 0.85],
            "n_splits": 5,
            "seed": 42
        }
        with open(metrics_file, "w", encoding="utf-8") as f:
            json.dump(valid_metrics, f)

        passed, msg = engine.evaluate_assertion("cv_folds_logged(5)")
        self.assertTrue(passed, msg)

        # Gaming: wrong number of folds
        passed, msg = engine.evaluate_assertion("cv_folds_logged(10)")
        self.assertFalse(passed)

    def test_1se_rule_applied_pass_and_gaming(self):
        engine = PolicyEngine(self.plan_path, base_dir=self.test_dir)
        metrics_file = os.path.join(self.test_dir, "metrics.json")
        eval_report_file = os.path.join(self.test_dir, "EVALUATION-REPORT.md")

        # Gaming: Fake 1-SE text without metrics
        with open(eval_report_file, "w", encoding="utf-8") as f:
            f.write("# Evaluation Report\n**Selected Model**: Linear Regression\n1-SE rule verified.\n")
        passed, msg = engine.evaluate_assertion("assert_1se_rule_applied()")
        self.assertFalse(passed, "Fake 1-SE text without valid metrics.json must fail")

        # Pass case: Candidate models with 1-SE selection
        with open(eval_report_file, "w", encoding="utf-8") as f:
            f.write("# Evaluation Report — RMSE\n**Selected Model**: Linear Regression\n1-SE rule verified.\n")
        metrics_data = {
            "model": "Linear Regression",
            "fold_scores": [2330.0, 2340.0, 2335.0, 2332.0, 2338.0],
            "n_splits": 5,
            "seed": 42,
            "candidates": {
                "Linear Regression": {
                    "complexity": 1,
                    "fold_scores": [2330.0, 2340.0, 2335.0, 2332.0, 2338.0]
                },
                "Gradient Boosting": {
                    "complexity": 2,
                    "fold_scores": [2360.0, 2355.0, 2362.0, 2358.0, 2365.0]
                }
            }
        }
        with open(metrics_file, "w", encoding="utf-8") as f:
            json.dump(metrics_data, f)

        # Pass: Selected Linear Regression (simplest within 1-SE)
        passed, msg = engine.evaluate_assertion("assert_1se_rule_applied()")
        self.assertTrue(passed, msg)

        # Gaming: Select Gradient Boosting (higher complexity and worse RMSE)
        with open(eval_report_file, "w", encoding="utf-8") as f:
            f.write("# Evaluation Report — RMSE\n**Selected Model**: Gradient Boosting\n")
        passed, msg = engine.evaluate_assertion("assert_1se_rule_applied()")
        self.assertFalse(passed, "Selecting wrong model violating 1-SE must fail")

    def test_decision_logged_in_ledger_pass_and_gaming(self):
        engine = PolicyEngine(self.plan_path, base_dir=self.test_dir)
        ledger_path = os.path.join(self.test_dir, "DECISIONS.md")

        # Gaming: missing ledger
        passed, msg = engine.evaluate_assertion("decision_logged_in_ledger('DECISIONS.md')")
        self.assertFalse(passed)

        # Gaming: empty ledger with only headers
        with open(ledger_path, "w", encoding="utf-8") as f:
            f.write("| # | Stage | Type | Question | Options | Chosen | Reason | Reference | decided_by | Date |\n|---|---|---|---|---|---|---|---|---|---|\n")
        passed, msg = engine.evaluate_assertion("decision_logged_in_ledger('DECISIONS.md')")
        self.assertFalse(passed)

        # Pass: ledger with valid row
        with open(ledger_path, "a", encoding="utf-8") as f:
            f.write("| 1 | 3 | parameter | Param Q | a | b | Valid reason with twenty characters | 10.1145/2939672.2939785 @ Sec 3.1 | user | 2026-11-04 |\n")
        passed, msg = engine.evaluate_assertion("decision_logged_in_ledger('DECISIONS.md')")
        self.assertTrue(passed, msg)

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
