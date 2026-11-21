import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ["README.md", "docs/GETTING_STARTED.md", ".github/SECURITY.md"]


class TestMcpIsPinned(unittest.TestCase):
    def test_every_mcp_command_pins_a_version(self):
        checked = 0
        for name in DOCS:
            for n, line in enumerate((ROOT / name).read_text(encoding="utf-8").splitlines(), 1):
                is_command = '"args"' in line or "mcp add" in line
                if is_command and "openresearch-mcp" in line:
                    checked += 1
                    self.assertRegex(line, r"openresearch-mcp@\d+\.\d+\.\d+", f"{name}:{n} is not pinned")
        self.assertGreaterEqual(checked, 5)


class TestReadmeFiles(unittest.TestCase):
    def test_scripts_named_in_readme_exist(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        for path in sorted(set(re.findall(r"\b(scripts/[A-Za-z0-9_]+\.py)\b", text))):
            self.assertTrue((ROOT / path).exists(), f"README mentions missing file {path}")


class TestConstitutionRuleCount(unittest.TestCase):
    def test_constitution_has_35_rules_monotonic(self):
        sys.path.insert(0, str(ROOT))
        from scripts.count_rules import parse_rules, validate_rules

        parsed = parse_rules(ROOT / "_constitution" / "CONSTITUTION.md")
        self.assertEqual(parsed["total"], 35, f"Expected 35 rules, found {parsed['total']}")
        errors = validate_rules(parsed, expected_total=35)
        self.assertEqual(errors, [], f"Rule validation errors: {errors}")

    def test_count_rules_script_exit_code_zero(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "count_rules.py")],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )
        self.assertEqual(result.returncode, 0, f"count_rules.py failed: {result.stderr}")
        self.assertIn("Total Rules Counted: 35 (Expected: 35)", result.stdout)

    def test_readme_declares_35_rules(self):
        readme_text = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("35 constitutional articles", readme_text)
        self.assertIn("All 35 rules", readme_text)
        self.assertIn("35 rules partitioned into seven constitutional parts", readme_text)
        self.assertNotIn("26 rules", readme_text)
        self.assertNotIn("26 constitutional articles", readme_text)


if __name__ == "__main__":
    unittest.main()
