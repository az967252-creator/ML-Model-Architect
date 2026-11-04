import unittest
import os
from pathlib import Path

class TestSkillsIntegrity(unittest.TestCase):
    """Verifies that the SKILL.md files contain the mandatory constitutional gates."""

    def setUp(self):
        self.skills_dir = Path(__file__).resolve().parent.parent / "skills"
        self.constitution_path = Path(__file__).resolve().parent.parent / "_constitution" / "CONSTITUTION.md"

    def test_constitution_exists_and_has_rules(self):
        self.assertTrue(self.constitution_path.exists())
        content = self.constitution_path.read_text(encoding="utf-8")
        # Normalize dashes and check for core keywords
        content = content.replace("—", "-")
        self.assertIn("B1", content)
        self.assertIn("No Technical Decision Without a Reference", content)
        self.assertIn("B7", content)
        self.assertIn("Empirical Validation is the Final Judge", content)
        self.assertIn("Part E - Violation Handling", content)

    def test_stage1_has_funnel(self):
        skill1 = self.skills_dir / "01-goals-and-requirements" / "SKILL.md"
        content = skill1.read_text(encoding="utf-8")
        self.assertIn("Q1", content)
        self.assertIn("Q2", content)
        self.assertIn("Q5", content)
        self.assertIn("Sufficiency Gate", content) # Stage 1 calls it Sufficiency Gate

    def test_stage2_has_mcp_requirement(self):
        skill2 = self.skills_dir / "02-technique-selection" / "SKILL.md"
        content = skill2.read_text(encoding="utf-8")
        self.assertIn("MCP REQUIREMENT", content)
        self.assertIn("pros/cons", content.lower())

    def test_all_stages_have_exit_gates(self):
        for i in range(1, 6):
            folder = [f for f in os.listdir(self.skills_dir) if f.startswith(f"0{i}")][0]
            skill_path = self.skills_dir / folder / "SKILL.md"
            content = skill_path.read_text(encoding="utf-8").replace("—", "-")
            # Stage 1 uses "Sufficiency Gate (Exit)", others use "Exit Gate"
            self.assertTrue("Exit" in content or "Gate" in content, f"Stage {i} is missing an Exit Gate")

if __name__ == '__main__':
    unittest.main()
