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
C (1e-3 to 1e3), gamma (1e-4 to 1), kernel (rbf/linear/poly) (heuristic, no source)


## 3. Common Pitfalls
- Scaling omitted: Apply StandardScaler
- Gamma too high: Overfitting
- Large datasets: Use LinearSVC


## 8. Direct Source Access (MCP Required)
> You MUST use MCP to search for the DOI and read the full text.


## References
- Cortes, C., & Vapnik, V. (1995). Support-vector networks. Machine Learning. (DOI: 10.1007/BF00994018)
