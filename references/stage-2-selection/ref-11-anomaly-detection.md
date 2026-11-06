---
group_id: "11"
name: "Anomaly Detection"
---

> ⚠️ **WARNING: This file is a summary/index.**
> You MUST use your MCP search tools to read the actual paper before making a decision.
> See CONSTITUTION Part F.

# Group 11 — Anomaly Detection

## 1. Overview
Isolation Forest, Autoencoder, One-Class SVM.

## 2. Family Members
IsolationForest, Autoencoder, OneClassSVM, LOF

## 3. Strengths
- Isolation Forest fast
- Autoencoder high performance

## 4. Weaknesses
- Extreme class imbalance
- High false positives

## 5. Recommended Baseline
IsolationForest (contamination=0.05)

## 6. Key Hyperparameters
contamination (0.01-0.2), n_estimators (100-500) (heuristic, no source)


## 7. References


## 8. Direct Source Access (MCP Required)
> You MUST use MCP to search for the DOI and read the full text.


## References
- Liu, F. T., et al. (2008). Isolation Forest. ICDM. (DOI: 10.1109/ICDM.2008.17)
