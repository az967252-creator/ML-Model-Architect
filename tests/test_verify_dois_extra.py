import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import requests
import yaml

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts")))
import verify_dois  # noqa: E402

verify_dois.RETRY_DELAYS = (0, 0)   # never really sleep in tests
ROOT = Path(__file__).resolve().parent.parent


def resp(code):
    return MagicMock(status_code=code)


class TestRetry(unittest.TestCase):
    @patch("requests.get")
    def test_network_error_then_success(self, get):
        get.side_effect = [requests.exceptions.ConnectionError("x"), resp(200)]
        self.assertEqual(verify_dois.http_get("http://x").status_code, 200)
        self.assertEqual(get.call_count, 2)

    @patch("requests.get")
    def test_429_and_5xx_are_retried(self, get):
        get.side_effect = [resp(429), resp(503), resp(200)]
        self.assertEqual(verify_dois.http_get("http://x").status_code, 200)
        self.assertEqual(get.call_count, 3)

    @patch("requests.get")
    def test_gives_up_after_three_attempts_and_returns_last_response(self, get):
        get.return_value = resp(500)
        self.assertEqual(verify_dois.http_get("http://x").status_code, 500)
        self.assertEqual(get.call_count, 3)

    @patch("requests.get")
    def test_persistent_network_error_is_raised(self, get):
        get.side_effect = requests.exceptions.ConnectionError("down")
        with self.assertRaises(requests.exceptions.ConnectionError):
            verify_dois.http_get("http://x")
        self.assertEqual(get.call_count, 3)

    @patch("requests.get")
    def test_404_is_not_retried(self, get):
        get.return_value = resp(404)
        self.assertEqual(verify_dois.http_get("http://x").status_code, 404)
        self.assertEqual(get.call_count, 1)

    @patch("requests.get")
    def test_check_reports_warning_on_persistent_outage(self, get):
        get.side_effect = requests.exceptions.ConnectionError("down")
        ref = {"doi_or_url": "10.1234/5678", "title": "T", "year": 2020}
        self.assertTrue(verify_dois.check(ref)[0].startswith("WARN"))


class TestRegistries(unittest.TestCase):
    @patch("requests.get")
    def test_datacite_fallback_ok(self, get):
        datacite = MagicMock(status_code=200)
        datacite.json.return_value = {"data": {"attributes": {
            "titles": [{"title": "Attention Is All You Need"}], "publicationYear": 2017}}}
        get.side_effect = [resp(404), datacite]
        ref = {"doi_or_url": "10.48550/arXiv.1706.03762", "title": "Attention Is All You Need", "year": 2017}
        self.assertEqual(verify_dois.check(ref)[0], "OK")

    @patch("requests.get")
    def test_not_in_either_registry(self, get):
        get.side_effect = [resp(404), resp(404)]
        ref = {"doi_or_url": "10.1234/fake", "title": "T", "year": 2020}
        self.assertEqual(verify_dois.check(ref)[0], "FAIL_NOT_FOUND")

    @patch("requests.get")
    def test_datacite_server_error_is_warning_not_fake(self, get):
        get.side_effect = [resp(404), resp(500), resp(500), resp(500)]
        ref = {"doi_or_url": "10.1234/x", "title": "T", "year": 2020}
        self.assertEqual(verify_dois.check(ref)[0], "WARN_HTTP_ERROR")

    @patch("requests.get")
    def test_title_mismatch(self, get):
        ok = MagicMock(status_code=200)
        ok.json.return_value = {"message": {"title": ["Completely Different Paper"],
                                            "issued": {"date-parts": [[2020]]}}}
        get.return_value = ok
        ref = {"doi_or_url": "10.1234/x", "title": "Gradient Boosting Machines", "year": 2020}
        self.assertEqual(verify_dois.check(ref)[0], "FAIL_TITLE_MISMATCH")

    @patch("requests.get")
    def test_url_reference_alive_and_dead(self, get):
        ref = {"doi_or_url": "https://example.org/paper.pdf", "title": "T", "year": 2008}
        get.return_value = resp(200)
        self.assertEqual(verify_dois.check(ref)[0], "OK_URL")
        get.return_value = resp(404)
        self.assertEqual(verify_dois.check(ref)[0], "FAIL_URL_DEAD")


class TestPolicy(unittest.TestCase):
    def test_journal_and_conference_need_peer_review(self):
        for st in ("journal", "conference"):
            self.assertIsNone(verify_dois.check_policy({"source_type": st, "claimed_peer_reviewed": True}))
            self.assertEqual(verify_dois.check_policy({"source_type": st, "claimed_peer_reviewed": False})[0],
                             "FAIL_NOT_PEER_REVIEWED")

    def test_book_is_allowed_without_peer_review(self):
        self.assertIsNone(verify_dois.check_policy({"source_type": "book", "claimed_peer_reviewed": False}))

    def test_blog_course_docs_preprint_and_missing_are_rejected(self):
        for st in ("blog", "course", "docs", "preprint", "", None):
            self.assertEqual(verify_dois.check_policy({"source_type": st, "claimed_peer_reviewed": True})[0],
                             "FAIL_SOURCE_TYPE", st)

    def test_every_reference_in_the_real_yaml_passes_policy(self):
        data = yaml.safe_load((ROOT / "references_to_verify.yaml").read_text(encoding="utf-8"))
        bad = [(r["doi_or_url"], verify_dois.check_policy(r)) for g in data["groups"] for r in g["refs"]
               if verify_dois.check_policy(r)]
        self.assertEqual(bad, [])


class TestMarkdownCheck(unittest.TestCase):
    def make_root(self, md_text):
        tmp = tempfile.TemporaryDirectory()
        stage = Path(tmp.name) / "references" / "stage-2-selection"
        stage.mkdir(parents=True)
        (stage / "ref-01-x.md").write_text(md_text, encoding="utf-8")
        return tmp

    DATA = {"groups": [{"id": "01", "refs": [{"doi_or_url": "10.1145/2939672.2939785"}]}]}

    def test_known_doi_is_fine(self):
        tmp = self.make_root("See 10.1145/2939672.2939785.")
        self.addCleanup(tmp.cleanup)
        self.assertEqual(verify_dois.md_dois_not_in_yaml(self.DATA, tmp.name), {})

    def test_unknown_doi_is_reported_with_file_name(self):
        tmp = self.make_root("See 10.48550/arXiv.2611.02251, and 10.1145/2939672.2939785")
        self.addCleanup(tmp.cleanup)
        self.assertEqual(verify_dois.md_dois_not_in_yaml(self.DATA, tmp.name),
                         {"10.48550/arxiv.2611.02251": ["ref-01-x.md"]})

    def test_doi_case_and_trailing_punctuation_are_ignored(self):
        tmp = self.make_root("(10.1145/2939672.2939785).")
        self.addCleanup(tmp.cleanup)
        self.assertEqual(verify_dois.md_dois_not_in_yaml(self.DATA, tmp.name), {})


class TestMainExitCodes(unittest.TestCase):
    def run_main(self, argv, status):
        with patch.object(verify_dois, "check", return_value=(status, "")):
            with patch.object(verify_dois, "check_policy", return_value=None):
                with patch("builtins.print"):
                    return verify_dois.main(argv)

    def test_ok(self):
        self.assertEqual(self.run_main([], "OK"), 0)

    def test_fail(self):
        self.assertEqual(self.run_main([], "FAIL_NOT_FOUND"), 1)

    def test_warn_only_fails_in_strict_mode(self):
        self.assertEqual(self.run_main([], "WARN_ERROR"), 0)
        self.assertEqual(self.run_main(["--strict"], "WARN_ERROR"), 1)

    def test_policy_failure_fails_even_if_registry_is_fine(self):
        with patch.object(verify_dois, "check", return_value=("OK", "")):
            with patch.object(verify_dois, "check_policy", return_value=("FAIL_SOURCE_TYPE", "x")):
                with patch("builtins.print"):
                    self.assertEqual(verify_dois.main([]), 1)

    def test_script_starts_with_shebang(self):
        first = (ROOT / "scripts" / "verify_dois.py").read_text(encoding="utf-8").splitlines()[0]
        self.assertEqual(first, "#!/usr/bin/env python3")


if __name__ == "__main__":
    unittest.main()
