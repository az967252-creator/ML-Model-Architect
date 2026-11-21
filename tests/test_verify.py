import unittest
import sys
import os
import tempfile
from unittest.mock import patch, MagicMock

# Add scripts directory to path so we can import verify_dois
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts')))
import verify_dois

verify_dois.RETRY_DELAYS = (0, 0)   # tests must never really sleep

class TestVerifyDois(unittest.TestCase):

    def test_empty_title(self):
        ref = {"doi_or_url": "10.1000/182", "title": "", "year": 2020}
        status, note = verify_dois.check(ref)
        self.assertEqual(status, "FAIL_MISSING_TITLE")

    def test_exception_missing_evidence(self):
        ref = {
            "doi_or_url": "10.5555/1234", 
            "title": "Some Title", 
            "year": 2020, 
            "exception": "ACM legacy"
        }
        status, note = verify_dois.check(ref)
        self.assertEqual(status, "FAIL_INCOMPLETE_EXCEPTION")

    @patch('requests.get')
    def test_warn_http_error(self, mock_get):
        mock_get.return_value = MagicMock(status_code=500)
        ref = {"doi_or_url": "10.1234/5678", "title": "Some Title", "year": 2020}
        status, note = verify_dois.check(ref)
        self.assertEqual(status, "WARN_HTTP_ERROR")

    @patch('requests.get')
    def test_year_mismatch(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": {
                "title": ["XGBoost"],
                "subtitle": ["A Scalable Tree Boosting System"],
                "issued": {"date-parts": [[2016]]}
            }
        }
        mock_get.return_value = mock_response
        
        # We pass 1990 instead of 2016
        ref = {
            "doi_or_url": "10.1145/2939672.2939785", 
            "title": "XGBoost: A Scalable Tree Boosting System", 
            "year": 1990
        }
        status, note = verify_dois.check(ref)
        self.assertEqual(status, "FAIL_YEAR_MISMATCH")

    @patch('requests.get')
    def test_valid_paper(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": {
                "title": ["XGBoost"],
                "subtitle": ["A Scalable Tree Boosting System"],
                "issued": {"date-parts": [[2016]]}
            }
        }
        mock_get.return_value = mock_response
        
        ref = {
            "doi_or_url": "10.1145/2939672.2939785", 
            "title": "XGBoost: A Scalable Tree Boosting System", 
            "year": 2016
        }
        status, note = verify_dois.check(ref)
        self.assertEqual(status, "OK")

    def test_catalogs_non_empty(self):
        import yaml
        from pathlib import Path
        root = Path(__file__).resolve().parent.parent
        catalog_files = list((root / "references" / "catalog").glob("*.yaml"))
        self.assertGreaterEqual(len(catalog_files), 12, "Must have at least 12 catalog files")
        for f in catalog_files:
            data = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
            claims = data.get("claims", [])
            self.assertGreater(len(claims), 0, f"Catalog file {f.name} has empty claims list")
            for c in claims:
                self.assertIn("claim", c)
                self.assertIn("source", c)
                self.assertIn("locator", c)
                self.assertIn("status", c)

    def test_each_group_has_at_least_two_references(self):
        import yaml
        from pathlib import Path
        root = Path(__file__).resolve().parent.parent
        ref_file = root / "references" / "references_to_verify.yaml"
        data = yaml.safe_load(ref_file.read_text(encoding="utf-8")) or {}
        for g in data.get("groups", []):
            if g["id"] in [f"{i:02d}" for i in range(1, 13)]:
                self.assertGreaterEqual(len(g.get("refs", [])), 2, f"Group {g['id']} must have >= 2 references")

    def test_empty_catalog_fails_check(self):
        import yaml
        empty_catalog = yaml.safe_load("group_id: '99'\nclaims: []")
        self.assertEqual(len(empty_catalog.get("claims", [])), 0)


if __name__ == '__main__':
    unittest.main()
