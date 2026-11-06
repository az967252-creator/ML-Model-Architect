---
group_id: "03"
name: "Gradient Boosting"
---

> ⚠️ **WARNING: This file is a summary/index.**
> You MUST use your MCP search tools to read the actual paper before making a decision.
> See CONSTITUTION Part F.

# Group 03 — Gradient Boosting

## 1. Overview
Boosted trees: XGBoost, LightGBM, CatBoost. SOTA on tabular.

## 2. Family Members
XGBoost, LightGBM, CatBoost

## 3. Strengths
- Top performance on tabular
- Handles nonlinear interactions
- Native missing-value handling

## 4. Weaknesses
- Requires careful tuning
- Prone to overfitting on noisy data

## 5. Recommended Baseline
XGBoost (learning_rate=0.1, n_estimators=200)

## 6. Key Hyperparameters
`learning_rate (0.01-0.3), n_estimators (100-2000), max_depth`

## 7. References


## 8. Direct Source Access (MCP Required)
> You MUST use MCP to search for the DOI and read the full text.


## References
- Chen, T., & Guestrin, C. (2016). XGBoost. KDD. (DOI: 10.1145/2939672.2939785)
- Prokhorenkova, L., et al. (2018). CatBoost. NeurIPS. (DOI: 10.48550/arXiv.1706.09516)
