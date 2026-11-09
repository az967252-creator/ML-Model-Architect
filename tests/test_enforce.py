import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts")))
import enforce_constitution as ec  # noqa: E402

HEADER = ("| # | Stage | Type | Question | Options | Chosen | Reason | Reference | decided_by | Date |\n"
          "|---|---|---|---|---|---|---|---|---|---|\n")
RULES = [("arxiv.org", ""), ("uber.com", "/blog/engineering")]


def ledger(*rows):
    body = ""
    for i, (typ, ref) in enumerate(rows, 1):
        body += f"| {i} | 3 | {typ} | q{i} | a | b | r | {ref} | user | d |\n"
    return HEADER + body


def run(text, **kw):
    kw.setdefault("whitelist", RULES)
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write(text)
    try:
        return ec.enforce(f.name, **kw)
    finally:
        os.unlink(f.name)


class TestReferences(unittest.TestCase):
    def test_valid_doi_format(self):
        self.assertEqual(run(ledger(("parameter", "10.1145/2939672.2939785"))), 0)

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
        self.assertEqual(run(ledger(("scope", "none"))), 0)

    def test_arxiv_doi_not_truncated(self):
        seen = []
        run(ledger(("parameter", "10.48550/arXiv.2610.18935")), online=True,
            doi_checker=lambda d: seen.append(d) or "OK")
        self.assertEqual(seen, ["10.48550/arXiv.2610.18935"])

    def test_arxiv_id_converted_to_doi(self):
        seen = []
        run(ledger(("parameter", "arXiv:2611.02251")), online=True,
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


class TestOnline(unittest.TestCase):
    def test_fake_doi_fails(self):
        self.assertEqual(run(ledger(("parameter", "10.1234/fake")), online=True,
                             doi_checker=lambda d: "FAKE"), 1)

    def test_network_error_is_incomplete_not_ok(self):
        self.assertEqual(run(ledger(("parameter", "10.1145/2939672.2939785")), online=True,
                             doi_checker=lambda d: "NETWORK_ERROR"), 2)

    def test_allow_offline(self):
        self.assertEqual(run(ledger(("parameter", "10.1145/2939672.2939785")), online=True,
                             allow_offline=True, doi_checker=lambda d: "NETWORK_ERROR"), 0)

    def test_ok_doi_online(self):
        self.assertEqual(run(ledger(("parameter", "10.1145/2939672.2939785")), online=True,
                             doi_checker=lambda d: "OK"), 0)

    def test_offline_mode_makes_no_network_call(self):
        def boom(_):
            raise AssertionError("network used")
        self.assertEqual(run(ledger(("parameter", "10.1145/2939672.2939785")), doi_checker=boom), 0)


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
