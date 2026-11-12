---
group_id: "01"
name: "Linear Models"
---

> ⚠️ **WARNING: This file is a summary/index.**
> You MUST use your MCP search tools to read the actual paper before making a decision.
> See CONSTITUTION Part F.

# Evaluation — Linear Models

## 1. Metrics
F1, ROC-AUC, Brier Score / MAE, RMSE

## 2. Validation Protocol
KFold 5-fold

## 3. Problem Catalog
- Overfitting | Increase regularization
- Outliers | Use RobustScaler
- Non-linear | Check partial dependence


## 8. Direct Source Access (MCP Required)
> You MUST use MCP to search for the DOI and read the full text.


## References
- Hastie, T., et al. (2009). The Elements of Statistical Learning (Ch. 3). Springer. (DOI: 10.1007/978-0-387-84858-7)
- Zou, H., & Hastie, T. (2005). Regularization and variable selection via the elastic net. JRSS-B. (DOI: 10.1111/j.1467-9868.2005.00503.x)

## 4. Out of Scope
- Imbalance handling: Not applicable for regression.
- Missing values: Handled in the Pipeline (Imputer).
