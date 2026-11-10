import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ["README.md", "GETTING_STARTED.md", "SECURITY.md"]


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


if __name__ == "__main__":
    unittest.main()
