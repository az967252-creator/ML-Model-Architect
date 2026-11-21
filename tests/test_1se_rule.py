import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts")))
from model_selection import select_1se_model, compute_1se_from_folds


class Test1SERule(unittest.TestCase):
    def test_less_than_1se_chooses_simple(self):
        results = {
            "Simple": {"cv_rmse": 100, "cv_se": 10, "complexity": 1},
            "Complex": {"cv_rmse": 95, "cv_se": 10, "complexity": 2}
        }
        self.assertEqual(select_1se_model(results, is_error=True), "Simple")

    def test_more_than_1se_chooses_complex(self):
        results = {
            "Simple": {"cv_rmse": 100, "cv_se": 10, "complexity": 1},
            "Complex": {"cv_rmse": 80, "cv_se": 10, "complexity": 2}
        }
        self.assertEqual(select_1se_model(results, is_error=True), "Complex")

    def test_higher_is_better_metric(self):
        # When metric is accuracy/F1 (higher is better)
        results = {
            "Simple": {"cv_score": 0.88, "cv_se": 0.03, "complexity": 1},
            "Complex": {"cv_score": 0.90, "cv_se": 0.03, "complexity": 2}
        }
        # Best is 0.90, threshold = 0.90 - 0.03 = 0.87. 0.88 >= 0.87 -> Simple selected
        self.assertEqual(select_1se_model(results, is_error=False), "Simple")

    def test_compute_1se_from_folds(self):
        folds = [10.0, 12.0, 11.0, 9.0, 13.0]
        mean_val, std_val, se_val = compute_1se_from_folds(folds)
        self.assertAlmostEqual(mean_val, 11.0)
        self.assertGreater(se_val, 0)
        self.assertAlmostEqual(se_val, std_val / (5 ** 0.5))


if __name__ == '__main__':
    unittest.main()
