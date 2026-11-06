---
group_id: "09"
name: "Clustering"
---

> ⚠️ **WARNING: This file is a summary/index.**
> You MUST use your MCP search tools to read the actual paper before making a decision.
> See CONSTITUTION Part F.

# Group 09 — Clustering

## 1. Overview
Unsupervised clustering: K-Means, DBSCAN, GMM.

## 2. Family Members
K-Means, DBSCAN, Hierarchical, GaussianMixture

## 3. Strengths
- K-Means fast and stable
- DBSCAN arbitrary shapes
- GMM probabilistic

## 4. Weaknesses
- K-Means needs k
- DBSCAN sensitive to eps
- Hierarchical O(n^2)

## 5. Recommended Baseline
K-Means (k=2..10, silhouette) (heuristic, no source)

## 6. Key Hyperparameters
n_clusters (2-20), eps (percentile-based), min_samples (3-20) (heuristic, no source)


## 7. References


## 8. Direct Source Access (MCP Required)
> You MUST use MCP to search for the DOI and read the full text.


## References
- Ester, M., et al. (1996). A density-based algorithm for discovering clusters (DBSCAN). KDD. (DOI: 10.5555/3001460.3001507)
