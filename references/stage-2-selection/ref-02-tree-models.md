---
group_id: "02"
name: "Tree Models"
---

> ⚠️ **WARNING: This file is a summary/index.**
> You MUST use your MCP search tools to read the actual paper before making a decision.
> See CONSTITUTION Part F.

# Group 02 — Tree Models

## 1. Overview
Decision trees and ensembles (Random Forest). Robust to noise.

## 2. Family Members
DecisionTree, RandomForest, ExtraTrees

## 3. Strengths
- Robust to outliers
- Handles nonlinear interactions
- Provides feature importance

## 4. Weaknesses
- RF inference slower than linear
- Memory-heavy on large data

## 5. Recommended Baseline
RandomForestClassifier (n_estimators=100-300)

## 6. Key Hyperparameters
`n_estimators (100-1000), max_depth (5-30), min_samples_leaf`

## 7. References
- Use MCP to search for the latest papers.


## 8. Direct Source Access (MCP Required)
> You MUST use MCP to search for the DOI and read the full text.


## References
- Breiman, L. (2001). Random Forests. Machine Learning. (DOI: 10.1023/A:1010933404324)
