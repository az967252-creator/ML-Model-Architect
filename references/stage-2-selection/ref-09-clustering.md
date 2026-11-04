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
K-Means (k=2..10, silhouette)

## 6. Key Hyperparameters
`n_clusters (2-20), eps (percentile), min_samples`

## 7. References
- Use MCP to search for the latest papers.
