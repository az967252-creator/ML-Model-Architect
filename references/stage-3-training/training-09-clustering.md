---
group_id: "09"
name: "Clustering"
---

> ⚠️ **WARNING: This file is a summary/index.**
> You MUST use your MCP search tools to read the actual paper before making a decision.
> See CONSTITUTION Part F.

# Training — Clustering

## 1. Data Preparation
Scaling REQUIRED for K-Means/GMM.

## 2. Hyperparameter Search
`n_clusters (2-20), eps (percentile), min_samples`

## 3. Common Pitfalls
- Unknown k: GMM with AIC/BIC
- Non-spherical: Switch to GMM
- Noise: Use HDBSCAN
