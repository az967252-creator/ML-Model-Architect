#!/usr/bin/env python3
"""
model_selection.py - Model Selection Utilities implementing the 1-SE Rule.

Implements the One Standard Error (1-SE) rule (Hastie, Tibshirani & Friedman, 2009;
Breiman et al., 1984) for model complexity selection during cross-validation.
"""

import math
from typing import Dict, Any, List, Tuple


def compute_1se_from_folds(fold_scores: List[float]) -> Tuple[float, float, float]:
    """
    Computes (mean, std, se) for cross-validation fold scores.
    Standard Error is SE = std(ddof=1) / sqrt(k).
    """
    n = len(fold_scores)
    if n == 0:
        return 0.0, 0.0, 0.0
    mean_val = sum(fold_scores) / n
    if n > 1:
        variance = sum((x - mean_val) ** 2 for x in fold_scores) / (n - 1)
        std_val = math.sqrt(variance)
        se_val = std_val / math.sqrt(n)
    else:
        std_val = 0.0
        se_val = 0.0
    return mean_val, std_val, se_val


def select_1se_model(results: Dict[str, Dict[str, Any]], is_error: bool = True) -> str:
    """
    Selects the simplest model whose performance is within 1 Standard Error of the best model.

    Parameters:
      results: Dict mapping model_name -> dict containing:
               - 'cv_rmse' or 'cv_score' or 'mean': float
               - 'cv_se' or 'se': float
               - 'complexity': int (lower means simpler)
      is_error: True if lower metric is better (RMSE, MAE, loss),
                False if higher metric is better (Accuracy, F1, ROC-AUC).

    Returns:
      model_name of the selected model.
    """
    if not results:
        raise ValueError("Cannot apply 1-SE rule on empty results dictionary.")

    # Normalize metric values
    parsed = {}
    for name, metrics in results.items():
        if "cv_rmse" in metrics:
            val = metrics["cv_rmse"]
        elif "cv_score" in metrics:
            val = metrics["cv_score"]
        elif "mean" in metrics:
            val = metrics["mean"]
        else:
            raise KeyError(f"Model '{name}' missing 'cv_rmse', 'cv_score', or 'mean'.")

        se = metrics.get("cv_se", metrics.get("se", 0.0))
        complexity = metrics.get("complexity", 1)
        parsed[name] = {"val": val, "se": se, "complexity": complexity}

    if is_error:
        best_name = min(parsed, key=lambda k: parsed[k]["val"])
        best_val = parsed[best_name]["val"]
        best_se = parsed[best_name]["se"]
        threshold = best_val + best_se
        eligible = [k for k, v in parsed.items() if v["val"] <= threshold]
    else:
        best_name = max(parsed, key=lambda k: parsed[k]["val"])
        best_val = parsed[best_name]["val"]
        best_se = parsed[best_name]["se"]
        threshold = best_val - best_se
        eligible = [k for k, v in parsed.items() if v["val"] >= threshold]

    return min(eligible, key=lambda k: parsed[k]["complexity"])
