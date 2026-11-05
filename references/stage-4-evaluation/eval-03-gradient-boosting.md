---
group_id: "03"
name: "Gradient Boosting"
---

> ⚠️ **WARNING: This file is a summary/index.**
> You MUST use your MCP search tools to read the actual paper before making a decision.
> See CONSTITUTION Part F.

# Evaluation — Gradient Boosting

## 1. Metrics
F1, PR-AUC, ROC-AUC / MAE, RMSE

## 2. Validation Protocol
StratifiedKFold 5-fold + Nested CV

## 3. Problem Catalog
- LightGBM overfitting | Enforce max_depth
- Accuracy drop | Relax monotonicity
- High memory | Prefer LightGBM


## 8. Direct Source Access (MCP Required)
> You MUST use MCP to search for the DOI and read the full text.


## References
- Chen, T., & Guestrin, C. (2016). XGBoost. KDD. (DOI: 10.1145/2939672.2939785)
- Prokhorenkova, L., et al. (2018). CatBoost. NeurIPS. (DOI: 10.48550/arXiv.1706.09516)
