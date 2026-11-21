---
group_id: "03"
name: "Gradient Boosting"
---

> ⚠️ **WARNING: This file is a summary/index.**
> You MUST use your MCP search tools to read the actual paper before making a decision.
> See CONSTITUTION Part F.

# Evaluation — Gradient Boosting

## 1. Metrics
- Classification: F1, PR-AUC, ROC-AUC (10.1186/1471-2105-7-91 @ Sec 2)
- Regression: MAE, RMSE (10.1007/978-0-387-84858-7 @ Sec 3.2)

## 2. Validation Protocol
- K-Fold (5-fold) Cross-Validation or Repeated Stratified K-Fold (10.1186/1471-2105-7-91 @ Sec 3)
- 1-SE Model Complexity Rule (10.1007/978-0-387-84858-7 @ Sec 7.10)

## 3. Problem Catalog
| Problem / Symptom | Recommended Mitigation | Reference Anchor |
|---|---|---|
| LightGBM/XGBoost overfitting on small samples | Restrict `max_depth` (3-6) and raise `min_child_weight` | 10.1145/2939672.2939785 @ Sec 4.1 |
| Unintended feature dominance / accuracy drop | Enforce monotonic constraints or tune `colsample_bytree` | 10.1145/2939672.2939785 @ Sec 3.2 |
| High memory consumption on high-cardinality features | Use histogram binning or CatBoost native categorical encoding | 10.48550/arXiv.1706.09516 @ Sec 2 |
| Sensitivity to label noise | Prefer Huber loss or reduce learning_rate (heuristic) | 10.1007/978-0-387-84858-7 @ Sec 10.6 |

## 4. Implementation Constraints
- For classification with class imbalance: utilize `scale_pos_weight` in XGBoost/LightGBM (10.1145/2939672.2939785 @ Sec 3.1) or focal loss.
- Missing values: Handled natively by tree branching (10.1145/2939672.2939785 @ Sec 3.4) or in the Pipeline via `SimpleImputer`.

## 5. Direct Source Access (MCP Required)
> You MUST use MCP to search for the DOI and read the full text.

## 6. References
- Chen, T., & Guestrin, C. (2016). XGBoost: A Scalable Tree Boosting System. KDD. (DOI: 10.1145/2939672.2939785)
- Prokhorenkova, L., et al. (2018). CatBoost: unbiased boosting with categorical features. NeurIPS. (DOI: 10.48550/arXiv.1706.09516)
- Hastie, T., et al. (2009). The Elements of Statistical Learning. Springer. (DOI: 10.1007/978-0-387-84858-7)
- Varma, S., & Simon, R. (2006). Bias in error estimation when using cross-validation. (DOI: 10.1186/1471-2105-7-91)
