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
            self.assertIn("unconstrained_agent", b)
            self.assertFalse(b["mla_results"]["leakage_detected"])

    def test_render_benchmark_md_check(self):
        cmd = [sys.executable, str(ROOT / "scripts" / "render_benchmark_md.py"), "--check"]
        res = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
        self.assertEqual(res.returncode, 0, f"render_benchmark_md.py --check failed: {res.stderr}")
        self.assertIn("OK: Benchmark documentation matches results.json exactly.", res.stdout)


if __name__ == "__main__":
    unittest.main()
