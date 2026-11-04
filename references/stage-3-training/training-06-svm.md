---
group_id: "06"
name: "SVM"
---

> ⚠️ **WARNING: This file is a summary/index.**
> You MUST use your MCP search tools to read the actual paper before making a decision.
> See CONSTITUTION Part F.

# Training — SVM

## 1. Data Preparation
Scaling REQUIRED (zero mean, unit variance).

## 2. Hyperparameter Search
`C (1e-3 to 1e3), gamma (1e-4 to 1), kernel`

## 3. Common Pitfalls
- Scaling omitted: Apply StandardScaler
- Gamma too high: Overfitting
- Large datasets: Use LinearSVC
