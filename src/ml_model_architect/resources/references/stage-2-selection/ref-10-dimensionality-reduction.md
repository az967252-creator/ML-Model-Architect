---
group_id: "10"
name: "Dimensionality Reduction"
---

> ⚠️ **WARNING: This file is a summary/index.**
> You MUST use your MCP search tools to read the actual paper before making a decision.
> See CONSTITUTION Part F.

# Group 10 — Dimensionality Reduction

## 1. Overview
PCA, t-SNE, UMAP for reducing feature space.

## 2. Family Members
PCA, t-SNE, UMAP, MDS

## 3. Strengths
- PCA fast and linear
- t-SNE preserves local
- UMAP faster than t-SNE

## 4. Weaknesses
- t-SNE/UMAP distort global distances
- UMAP initialization-sensitive

## 5. Recommended Baseline
PCA (n_components=0.95) (heuristic, no source)

## 6. Key Hyperparameters
n_components (2-50), perplexity (5-50) (heuristic, no source)


## 7. References


## 8. Direct Source Access (MCP Required)
> You MUST use MCP to search for the DOI and read the full text.


## References
- van der Maaten, L., & Hinton, G. (2008). Visualizing Data using t-SNE. JMLR. (DOI: https://www.jmlr.org/papers/volume9/vandermaaten08a/vandermaaten08a.pdf)
