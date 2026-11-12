import unittest

class Test1SERule(unittest.TestCase):
    def select_model_1se(self, results):
        best_name = min(results, key=lambda k: results[k]["cv_rmse"])
        best_rmse = results[best_name]["cv_rmse"]
        best_se = results[best_name]["cv_se"]
        candidates = [name for name, r in results.items() if r["cv_rmse"] <= best_rmse + best_se]
        return min(candidates, key=lambda k: results[k]["complexity"])

    def test_less_than_1se_chooses_simple(self):
        results = {
            "Simple": {"cv_rmse": 100, "cv_se": 10, "complexity": 1},
            "Complex": {"cv_rmse": 95, "cv_se": 10, "complexity": 2}
        }
        self.assertEqual(self.select_model_1se(results), "Simple")

    def test_more_than_1se_chooses_complex(self):
        results = {
            "Simple": {"cv_rmse": 100, "cv_se": 10, "complexity": 1},
            "Complex": {"cv_rmse": 80, "cv_se": 10, "complexity": 2}
        }
        self.assertEqual(self.select_model_1se(results), "Complex")

if __name__ == '__main__':
    unittest.main()
