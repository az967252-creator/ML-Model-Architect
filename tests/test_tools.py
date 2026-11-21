"""
tests/test_tools.py - Unit test suite for secondary tooling.

Covers:
  - scripts/executive_summary.py
  - scripts/pre_mortem.py
  - scripts/generate_diagram.py
  - scripts/red_team.py
  - app.py
  - mcp_server/local_knowledge.py
  - scripts/pdf_to_markdown.py
"""

import os
import tempfile
import unittest
from pathlib import Path

from scripts.executive_summary import generate_executive_summary
from scripts.pre_mortem import generate_premortem
from scripts.generate_diagram import generate_mermaid_diagram, is_valid_mermaid
from scripts.red_team import red_team_review
from mcp_server.local_knowledge import KnowledgeBase
from scripts.pdf_to_markdown import convert_pdfs

ROOT = Path(__file__).resolve().parent.parent


class TestExecutiveSummary(unittest.TestCase):
    def test_executive_summary_real_example(self):
        project_dir = ROOT / "examples" / "car-price-prediction"
        summary = generate_executive_summary(project_dir)
        self.assertIn("# Executive Summary — car-price-prediction", summary)
        self.assertIn("Linear Regression", summary)
        self.assertIn("Rigor Score", summary)
        self.assertNotIn("Our AI agent was tasked with solving a critical business problem.", summary)

    def test_executive_summary_missing_fails_closed(self):
        with self.assertRaises(FileNotFoundError):
            generate_executive_summary(Path("non_existent_project_dir_12345"))


class TestPreMortem(unittest.TestCase):
    def test_premortem_real_example(self):
        dec_file = ROOT / "examples" / "delivery-delay-prediction" / "DECISIONS.md"
        report = generate_premortem(dec_file)
        self.assertIn("# Pre-Mortem Risk Analysis", report)
        self.assertIn("Scenario", report)
        self.assertIn("Mandated Mitigation", report)

    def test_premortem_missing_fails_closed(self):
        with self.assertRaises(FileNotFoundError):
            generate_premortem(Path("non_existent_decisions.md"))

    def test_premortem_empty_fails_closed(self):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
            f.write("# Empty Decisions\n\nNo table here.")
            temp_path = Path(f.name)
        try:
            with self.assertRaises(ValueError):
                generate_premortem(temp_path)
        finally:
            if temp_path.exists():
                temp_path.unlink()


class TestGenerateDiagram(unittest.TestCase):
    def test_generate_diagram_valid_mermaid(self):
        dec_file = ROOT / "examples" / "financial-anomaly-detection" / "DECISIONS.md"
        diagram = generate_mermaid_diagram(dec_file)
        self.assertTrue(is_valid_mermaid(diagram))
        self.assertIn("flowchart TD", diagram)
        self.assertIn("step_1", diagram)

    def test_generate_diagram_missing_fails_closed(self):
        with self.assertRaises(FileNotFoundError):
            generate_mermaid_diagram(Path("non_existent_dec.md"))


class TestRedTeam(unittest.TestCase):
    def test_red_team_rule_based(self):
        dec_file = ROOT / "examples" / "delivery-delay-prediction" / "DECISIONS.md"
        res = red_team_review(dec_file, deep=False)
        self.assertIn("total_decisions_reviewed", res)
        self.assertGreater(res["total_decisions_reviewed"], 0)

    def test_red_team_deep_fails_closed_missing_key(self):
        dec_file = ROOT / "examples" / "delivery-delay-prediction" / "DECISIONS.md"
        # Temporarily wipe env
        old_gemini = os.environ.pop("GEMINI_API_KEY", None)
        old_openai = os.environ.pop("OPENAI_API_KEY", None)
        try:
            with self.assertRaises(PermissionError):
                red_team_review(dec_file, deep=True, api_key_env="NON_EXISTENT_KEY_ENV_VAR")
        finally:
            if old_gemini:
                os.environ["GEMINI_API_KEY"] = old_gemini
            if old_openai:
                os.environ["OPENAI_API_KEY"] = old_openai

    def test_red_team_deep_mocked_llm(self):
        dec_file = ROOT / "examples" / "delivery-delay-prediction" / "DECISIONS.md"
        os.environ["MOCK_API_KEY"] = "mock_key_value"

        def mock_client(prompt, key):
            return [{"persona": "MLOps", "critique": "Test critique from mock.", "severity": "HIGH"}]

        try:
            res = red_team_review(dec_file, deep=True, api_key_env="MOCK_API_KEY", model_client=mock_client)
            self.assertEqual(len(res["deep_critiques"]), 1)
            self.assertEqual(res["deep_critiques"][0]["persona"], "MLOps")
        finally:
            os.environ.pop("MOCK_API_KEY", None)


class TestDashboardImport(unittest.TestCase):
    def test_app_imports_cleanly(self):
        import app
        self.assertTrue(hasattr(app, "run_dashboard"))


class TestLocalKnowledgeBase(unittest.TestCase):
    def test_knowledge_base_indexing_and_search(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            doc_file = tmp_path / "sample_ref.md"
            doc_file.write_text(
                "# Sample Reference\n\nGradient boosting builds an additive model of trees sequentially to minimize loss.",
                encoding="utf-8",
            )
            kb = KnowledgeBase(collection_name="test_collection")
            indexed_count = kb.index_directory(tmp_path)
            self.assertGreaterEqual(indexed_count, 1)

            results = kb.search("additive trees sequential", top_k=1)
            self.assertGreater(len(results), 0)
            self.assertEqual(results[0]["source"], "sample_ref.md")


class TestPdfToMarkdown(unittest.TestCase):
    def test_pdf_to_markdown_missing_dir_fails_closed(self):
        ret = convert_pdfs(Path("non_existent_pdf_directory_12345"), Path("dummy_out"))
        self.assertEqual(ret, 1)

    def test_pdf_to_markdown_empty_dir(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            ret = convert_pdfs(Path(tmp_dir), Path(tmp_dir) / "out")
            self.assertEqual(ret, 0)

    def test_pdf_to_markdown_with_mock_converter(self):
        class MockResult:
            class MockDoc:
                def export_to_markdown(self):
                    return "# Converted Content\n\nExtracted text from PDF."
            document = MockDoc()

        class MockConverter:
            def convert(self, path):
                return MockResult()

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            pdf_file = tmp_path / "paper.pdf"
            pdf_file.write_bytes(b"%PDF-1.4 dummy pdf content")
            out_dir = tmp_path / "out"
            ret = convert_pdfs(tmp_path, out_dir, converter=MockConverter())
            self.assertEqual(ret, 0)
            converted_md = out_dir / "paper.md"
            self.assertTrue(converted_md.exists())
            self.assertIn("Converted Content", converted_md.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
