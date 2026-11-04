import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add scripts directory to path so we can import verify_dois
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts')))
import verify_dois

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
        # Mock the API to return a 500 error
        mock_get.return_value = MagicMock(status_code=500)
        
        ref = {"doi_or_url": "10.1234/5678", "title": "Some Title", "year": 2020}
        status, note = verify_dois.check(ref)
        
        # The check function should return WARN_HTTP_ERROR
        self.assertEqual(status, "WARN_HTTP_ERROR")

    @patch('requests.get')
    def test_valid_paper(self, mock_get):
        # Mock a successful Crossref response
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

if __name__ == '__main__':
    unittest.main()