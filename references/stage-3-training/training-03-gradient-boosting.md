---
group_id: "03"
name: "Gradient Boosting"
---

> ⚠️ **WARNING: This file is a summary/index.**
> You MUST use your MCP search tools to read the actual paper before making a decision.
> See CONSTITUTION Part F.

# Training — Gradient Boosting

## 1. Data Preparation
CatBoost native categorical. Early stopping MANDATORY.

## 2. Hyperparameter Search
learning_rate (0.01-0.3), n_estimators (100-2000), max_depth (3-10), subsample (0.6-1.0) [Source: 10.1145/2939672.2939785]


## 3. Common Pitfalls
- LightGBM overfitting: Enforce max_depth
- Accuracy drop: Relax monotonicity
- High memory: Prefer LightGBM


## 8. Direct Source Access (MCP Required)
> You MUST use MCP to search for the DOI and read the full text.


## References
- Chen, T., & Guestrin, C. (2016). XGBoost. KDD. (DOI: 10.1145/2939672.2939785)
- Prokhorenkova, L., et al. (2018). CatBoost. NeurIPS. (DOI: 10.48550/arXiv.1706.09516)
