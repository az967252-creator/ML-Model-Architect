---
group_id: "11"
name: "Anomaly Detection"
---

> ⚠️ **WARNING: This file is a summary/index.**
> You MUST use your MCP search tools to read the actual paper before making a decision.
> See CONSTITUTION Part F.

# Training — Anomaly Detection

## 1. Data Preparation
Scaling for AE/SVM. Handle extreme imbalance.

## 2. Hyperparameter Search
`contamination (0.01-0.2), n_estimators, latent_dim`

## 3. Common Pitfalls
- IF fails on complex: Autoencoder
- High false negatives: Hybrid
- Unlabeled anomalies: Unsupervised AE


## 8. Direct Source Access (MCP Required)
> You MUST use MCP to search for the DOI and read the full text.


## References
- Liu, F. T., et al. (2008). Isolation Forest. ICDM. (DOI: 10.1109/ICDM.2008.17)
