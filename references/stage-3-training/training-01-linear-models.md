---
group_id: "01"
name: "Linear Models"
---

> ⚠️ **WARNING: This file is a summary/index.**
> You MUST use your MCP search tools to read the actual paper before making a decision.
> See CONSTITUTION Part F.

# Training — Linear Models

## 1. Data Preparation
Scaling REQUIRED (StandardScaler)

## 2. Hyperparameter Search
`C (1e-4 to 1e3), penalty (l1/l2), solver`

## 3. Common Pitfalls
- Overfitting: Increase regularization
- Outliers: Use RobustScaler
- Non-linear: Check partial dependence
