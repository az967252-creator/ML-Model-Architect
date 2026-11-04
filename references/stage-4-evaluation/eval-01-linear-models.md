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
StratifiedKFold 5-fold

## 3. Problem Catalog
- Overfitting | Increase regularization
- Outliers | Use RobustScaler
- Non-linear | Check partial dependence
