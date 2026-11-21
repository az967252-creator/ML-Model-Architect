import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
SCRIPTS = ROOT / "scripts"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

try:
    import ml_model_architect.enforcer as ec
except ImportError:
    import enforce_constitution as ec  # type: ignore # noqa: E402

HEADER = ("| # | Stage | Type | Question | Options | Chosen | Reason | Reference | decided_by | Date |\n"
          "|---|---|---|---|---|---|---|---|---|---|\n")
RULES = [("arxiv.org", ""), ("uber.com", "/blog/engineering")]


def ledger(*rows):
    body = ""
    for i, (typ, ref) in enumerate(rows, 1):
        body += f"| {i} | 3 | {typ} | q{i} | a | b | Valid technical reasoning that exceeds twenty characters | {ref} | user | d |\n"
    return HEADER + body


def run(text, **kw):
    kw.setdefault("whitelist", RULES)
    kw.setdefault("max_heuristic_ratio", 1.0)
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write(text)
    try:
        return ec.enforce(f.name, **kw)
    finally:
        os.unlink(f.name)


class TestReferences(unittest.TestCase):
    def test_valid_doi_format(self):
        self.assertEqual(run(ledger(("parameter", "10.1145/2939672.2939785 @ Sec 3.1"))), 0)

    def test_missing_locator_rejected(self):
        self.assertEqual(run(ledger(("parameter", "10.1145/2939672.2939785"))), 1)

    def test_locator_arbitrary_at_rejected(self):
        # '@ arbitrary_text' without Sec/Section/p./page/Table/Fig/Eq/Theorem must be rejected
        self.assertEqual(run(ledger(("parameter", "10.1145/2939672.2939785 @ mynotes"))), 1)
        self.assertEqual(run(ledger(("parameter", "10.1145/2939672.2939785 @ random"))), 1)
        # Proper locator formats must pass
        self.assertEqual(run(ledger(("parameter", "10.1145/2939672.2939785 @ Sec 3.1"))), 0)
        self.assertEqual(run(ledger(("parameter", "10.1145/2939672.2939785 @ Table 2"))), 0)
        self.assertEqual(run(ledger(("parameter", "10.1145/2939672.2939785 @ Eq 4"))), 0)
        self.assertEqual(run(ledger(("parameter", "10.1145/2939672.2939785 @ Theorem 1"))), 0)

    def test_data_framing_with_model_or_hyperparam_treated_as_technical(self):
        # A row marked as 'data' or 'framing' choosing XGBoost without reference fails
        disguised = HEADER + "| 1 | 1 | data | Which input features? | A) raw B) processed | XGBoost | Valid technical reasoning exceeding twenty characters | none | user | d |\n"
        self.assertEqual(run(disguised), 1)

        # Disguised with hyperparameter name
        disguised_param = HEADER + "| 1 | 1 | framing | Feature scale? | A) minmax B) standard | learning_rate | Valid technical reasoning exceeding twenty characters | none | user | d |\n"
        self.assertEqual(run(disguised_param), 1)

        # Disguised with metric name
        disguised_metric = HEADER + "| 1 | 1 | other | Business metric? | A) acc B) f1 | F1-Score | Valid technical reasoning exceeding twenty characters | none | user | d |\n"
        self.assertEqual(run(disguised_metric), 1)

        # Truly non-technical data row without model names passes when accompanied by valid technical decision
        clean_data = (
            HEADER
            + "| 1 | 1 | data | Customer region column? | A) US B) EU | US | Valid business reasoning exceeding twenty characters | none | user | d |\n"
            + "| 2 | 2 | technique | Model family? | A) Linear B) Trees | A | Linear regression for simple baseline interpretation | 10.1145/2939672.2939785 @ Sec 3.1 | user | d |\n"
        )
        self.assertEqual(run(clean_data), 0)

    def test_allowed_tokens(self):
        for tok in ("heuristic", "reference-gap", "N/A (Business context)"):
            self.assertEqual(run(ledger(("parameter", tok))), 0, tok)

    def test_free_text_rejected(self):
        self.assertEqual(run(ledger(("parameter", "from my memory"))), 1)

    def test_na_empirical_rejected(self):
        self.assertEqual(run(ledger(("parameter", "N/A (Empirical)"))), 1)

    def test_version_number_is_not_a_doi(self):
        self.assertEqual(run(ledger(("parameter", "version 10.5 of my notes"))), 1)

    def test_all_technical_types_are_checked(self):
        for typ in ("technique", "parameter", "threshold", "deployment", "metric", "evaluation", "Parameter"):
            self.assertEqual(run(ledger((typ, "none"))), 1, typ)

    def test_non_technical_type_not_checked(self):
        # Non-technical row (data) does not require a valid DOI, as long as a technical row exists
        text = ledger(("data", "none"), ("technique", "10.1145/2939672.2939785 @ Sec 3.1"))
        self.assertEqual(run(text), 0)

    def test_zero_technical_decisions_fails_without_flag(self):
        # Zero technical decisions exits with code 1
        text = ledger(("data", "none"))
        self.assertEqual(run(text, allow_empty=False), 1)

    def test_zero_technical_decisions_passes_with_allow_empty(self):
        # Zero technical decisions exits with code 0 when allow_empty=True
        text = ledger(("data", "none"))
        self.assertEqual(run(text, allow_empty=True), 0)

    def test_unknown_type_misc_rejected(self):
        self.assertEqual(run(ledger(("misc", "none"))), 1)

    def test_framing_short_reason_rejected(self):
        short_reason = "| 1 | 1 | framing | q1 | a | b | short | N/A (Business context) | user | d |\n"
        self.assertEqual(run(HEADER + short_reason), 1)

    def test_heuristic_ratio_exceeded(self):
        # 1 heuristic out of 2 technical = 50% > 40%
        text = ledger(
            ("parameter", "heuristic"),
            ("technique", "10.1145/2939672.2939785 @ Sec 3.1")
        )
        self.assertEqual(run(text, max_heuristic_ratio=0.4), 1)

    def test_heuristic_ratio_within_limit(self):
        # 1 heuristic out of 3 technical = 33.3% <= 40%
        text = ledger(
            ("parameter", "heuristic"),
            ("technique", "10.1145/2939672.2939785 @ Sec 3.1"),
            ("parameter", "10.1145/2939672.2939785 @ Sec 4.1")
        )
        self.assertEqual(run(text, max_heuristic_ratio=0.4), 0)

    def test_arxiv_doi_not_truncated(self):
        seen = []
        run(ledger(("parameter", "10.48550/arXiv.2610.18935 @ Sec 1")), online=True,
            doi_checker=lambda d: seen.append(d) or "OK")
        self.assertEqual(seen, ["10.48550/arXiv.2610.18935"])

    def test_arxiv_id_converted_to_doi(self):
        seen = []
        run(ledger(("parameter", "arXiv:2611.02251 @ Sec 1")), online=True,
            doi_checker=lambda d: seen.append(d) or "OK")
        self.assertEqual(seen, ["10.48550/arXiv.2611.02251"])


class TestUrls(unittest.TestCase):
    def test_trusted_url(self):
        self.assertEqual(run(ledger(("parameter", "https://arxiv.org/abs/2611.02251"))), 0)
        self.assertEqual(run(ledger(("parameter", "https://www.arxiv.org/abs/1"))), 0)

    def test_lookalike_domains_rejected(self):
        for url in ("https://arxiv.org.evil.example/x", "https://notarxiv.org/x",
                    "https://evil.example/arxiv.org", "ftp://arxiv.org/x"):
            self.assertEqual(run(ledger(("parameter", url))), 1, url)

    def test_path_rule_is_respected(self):
        self.assertEqual(run(ledger(("parameter", "https://www.uber.com/blog/engineering/foo"))), 0)
        self.assertEqual(run(ledger(("parameter", "https://www.uber.com/careers"))), 1)
        self.assertEqual(run(ledger(("parameter", "https://www.uber.com/blog/engineering-evil"))), 1)

    def test_random_blog_rejected(self):
        self.assertEqual(run(ledger(("parameter", "https://myblog.example/post"))), 1)

    def test_tier_b_rejected_for_technique_allowed_for_deployment(self):
        tier_b_rules = [("arxiv.org", "", "B"), ("uber.com", "/blog/engineering", "B")]
        # Technique row referencing Tier B -> REJECTED
        self.assertEqual(run(ledger(("technique", "https://arxiv.org/abs/2611.02251")), whitelist=tier_b_rules), 1)
        # Parameter row referencing Tier B -> REJECTED
        self.assertEqual(run(ledger(("parameter", "https://arxiv.org/abs/2611.02251")), whitelist=tier_b_rules), 1)
        # Deployment row referencing Tier B -> ALLOWED
        self.assertEqual(run(ledger(("deployment", "https://uber.com/blog/engineering/canary")), whitelist=tier_b_rules), 0)
        # Threshold row referencing Tier B -> ALLOWED
        self.assertEqual(run(ledger(("threshold", "https://uber.com/blog/engineering/drift")), whitelist=tier_b_rules), 0)


class TestOnline(unittest.TestCase):
    def test_fake_doi_fails(self):
        self.assertEqual(run(ledger(("parameter", "10.1234/fake @ Sec 1")), online=True,
                             doi_checker=lambda d: "FAKE"), 1)

    def test_network_error_is_incomplete_not_ok(self):
        self.assertEqual(run(ledger(("parameter", "10.1145/2939672.2939785 @ Sec 3.1")), online=True,
                             doi_checker=lambda d: "NETWORK_ERROR"), 2)

    def test_allow_offline(self):
        self.assertEqual(run(ledger(("parameter", "10.1145/2939672.2939785 @ Sec 3.1")), online=True,
                             allow_offline=True, doi_checker=lambda d: "NETWORK_ERROR"), 0)

    def test_ok_doi_online(self):
        self.assertEqual(run(ledger(("parameter", "10.1145/2939672.2939785 @ Sec 3.1")), online=True,
                             doi_checker=lambda d: "OK"), 0)

    def test_offline_mode_makes_no_network_call(self):
        def boom(_):
            raise AssertionError("network used")
        self.assertEqual(run(ledger(("parameter", "10.1145/2939672.2939785 @ Sec 3.1")), doi_checker=boom), 0)


class TestParsing(unittest.TestCase):
    def test_malformed_row_is_a_violation(self):
        self.assertEqual(run(ledger(("parameter", "heuristic")) + "| 9 | 3 | parameter | broken |\n"), 1)

    def test_cell_containing_dashes_is_not_dropped(self):
        text = ledger(("parameter", "heuristic")).replace("| q1 |", "| why --- not? |")
        self.assertEqual(run(text.replace("heuristic", "free text")), 1)

    def test_missing_table_fails(self):
        self.assertEqual(run("no table here"), 1)

    def test_other_tables_are_ignored(self):
        extra = "\n\n| Source | Reason |\n|---|---|\n| blog | not peer reviewed |\n"
        self.assertEqual(run(ledger(("parameter", "heuristic")) + extra), 0)

    def test_missing_file(self):
        self.assertEqual(ec.enforce("/nonexistent/DECISIONS.md"), 1)


class TestRealExamples(unittest.TestCase):
    def test_every_example_ledger_is_valid(self):
        root = os.path.join(os.path.dirname(__file__), "..", "examples")
        found = 0
        for name in sorted(os.listdir(root)):
            path = os.path.join(root, name, "DECISIONS.md")
            if os.path.exists(path):
                found += 1
                self.assertEqual(ec.enforce(path, whitelist=ec.load_whitelist()), 0, path)
        self.assertGreaterEqual(found, 3)


if __name__ == "__main__":
    unittest.main()
