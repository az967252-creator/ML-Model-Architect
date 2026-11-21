"""
tests/test_benchmarks.py - Test benchmark runner and markdown rendering integrity.
"""

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class TestBenchmarks(unittest.TestCase):
    def test_results_json_structure(self):
        results_file = ROOT / "benchmarks" / "results.json"
        self.assertTrue(results_file.exists(), "benchmarks/results.json must exist")

        with open(results_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertIn("benchmarks", data)
        self.assertEqual(len(data["benchmarks"]), 4)
        for b in data["benchmarks"]:
            self.assertIn("benchmark_id", b)
            self.assertIn("mla_results", b)
            self.assertIn("naive_baseline", b)
            self.assertFalse(b["mla_results"]["leakage_detected"])

        # Validate BENCH-03 has no oracle contamination
        b3 = data["benchmarks"][2]
        self.assertEqual(b3["benchmark_id"], "BENCH-03")
        cand_name = b3["mla_results"]["candidate"]["name"]
        self.assertIn("auto", cand_name, "Candidate IsolationForest must not use oracle contamination")
        self.assertIn("pr_auc", b3["mla_results"]["candidate"])

    def test_readme_numbers_match_results_json(self):
        results_file = ROOT / "benchmarks" / "results.json"
        with open(results_file, "r", encoding="utf-8") as f:
            results = json.load(f)

        readme_text = (ROOT / "README.md").read_text(encoding="utf-8")
        b1, b2, b3, b4 = results["benchmarks"]
        m1 = b1["mla_results"]["models"]
        m2 = b2["mla_results"]["models"]

        # 1. Honest metrics presence
        self.assertIn(f"{m1['Linear Regression']['cv_rmse']:,.2f}", readme_text)
        self.assertIn(f"{m1['Linear Regression']['test_rmse']:,.2f}", readme_text)
        self.assertIn(f"{m1['Gradient Boosting']['cv_rmse']:,.2f}", readme_text)
        self.assertIn(f"{m2['Gradient Boosting (Candidate)']['test_f1']:.4f}", readme_text)
        self.assertIn("Naive Scripted Baseline", readme_text)

        # 2. Honest claims: prohibited ungrounded exaggerations must NOT be present
        self.assertNotIn("85% lower latency", readme_text)
        self.assertNotIn("85% compute overhead", readme_text)
        self.assertNotIn("zero loss in generalization", readme_text)
        self.assertNotIn("7 root files", readme_text)
        self.assertNotIn("79 Unit Tests", readme_text)

    def test_render_benchmark_md_check(self):
        cmd = [sys.executable, str(ROOT / "scripts" / "render_benchmark_md.py"), "--check"]
        res = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
        self.assertEqual(res.returncode, 0, f"render_benchmark_md.py --check failed: {res.stderr}\n{res.stdout}")
        self.assertIn("OK: Benchmark documentation", res.stdout)

    def test_every_cited_reference_in_table_exists_in_yaml(self):
        import yaml
        yaml_path = ROOT / "references" / "references_to_verify.yaml"
        with open(yaml_path, "r", encoding="utf-8") as f:
            ref_data = yaml.safe_load(f)
        all_citations = " ".join(r["citation"] for g in ref_data["groups"] for r in g["refs"])

        # Check references cited in benchmark table
        self.assertIn("Ke, G., et al. (2017)", all_citations)
        self.assertIn("Hastie, T., et al. (2009)", all_citations)
        self.assertIn("Ruff, L., et al. (2021)", all_citations)


if __name__ == "__main__":
    unittest.main()
