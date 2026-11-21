"""
tests/test_examples.py - Validate the 4 reference projects.

Verifies:
- All 4 reference examples pass all policy gates (ALL_STEPS_COMPLETED).
- All metrics.json files conform to _shared/metrics.schema.json.
- Cryptographic locks match manifest hashes.
"""

import json
import unittest
from pathlib import Path
import jsonschema

from scripts.run_policy import PolicyEngine

ROOT = Path(__file__).resolve().parent.parent
EXAMPLE_DIRS = [
    ROOT / "examples" / "car-price-prediction",
    ROOT / "examples" / "delivery-delay-prediction",
    ROOT / "examples" / "financial-anomaly-detection",
    ROOT / "examples" / "case-study-churn",
]


class TestExamplesPolicyCompliance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        schema_path = ROOT / "_shared" / "metrics.schema.json"
        with open(schema_path, "r", encoding="utf-8") as f:
            cls.metrics_schema = json.load(f)

    def test_all_examples_complete_all_policy_steps(self):
        for ex_dir in EXAMPLE_DIRS:
            manifest_path = ex_dir / "PLAN.manifest.json"
            self.assertTrue(manifest_path.exists(), f"Missing manifest in {ex_dir}")
            engine = PolicyEngine(manifest_path, base_dir=ex_dir)
            self.assertTrue(engine.verify_integrity(), f"Integrity check failed for {manifest_path}")

            summary = engine.get_status()
            self.assertEqual(
                summary["current_active_step"],
                "ALL_STEPS_COMPLETED",
                f"Project {ex_dir.name} is not ALL_STEPS_COMPLETED: {summary}",
            )

    def test_example_metrics_schema_validity(self):
        for ex_dir in EXAMPLE_DIRS:
            metrics_file = ex_dir / "metrics.json"
            if not metrics_file.exists():
                continue
            with open(metrics_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            jsonschema.validate(instance=data, schema=self.metrics_schema)

    def test_disclaimer_exists_and_accurate(self):
        disclaimer = ROOT / "examples" / "DISCLAIMER.md"
        self.assertTrue(disclaimer.exists())
        text = disclaimer.read_text(encoding="utf-8")
        self.assertIn("deterministic synthetic datasets", text)
        self.assertIn("car-price-prediction", text)
        self.assertIn("delivery-delay-prediction", text)
        self.assertIn("financial-anomaly-detection", text)
        self.assertIn("case-study-churn", text)


if __name__ == "__main__":
    unittest.main()
