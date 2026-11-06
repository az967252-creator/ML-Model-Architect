---
group_id: "04"
name: "Neural Networks"
---

> ⚠️ **WARNING: This file is a summary/index.**
> You MUST use your MCP search tools to read the actual paper before making a decision.
> See CONSTITUTION Part F.

# Training — Neural Networks

## 1. Data Preparation
Scaling REQUIRED. Early stopping MANDATORY.

## 2. Hyperparameter Search
learning_rate (1e-5 to 1e-2), batch_size (32-512), epochs (10-200), dropout (0.0-0.5) (heuristic, no source)


## 3. Common Pitfalls
- Unstable convergence: Dropout
- NaN divergence: Check loss stability
- Slow training: Multi-fidelity


## 8. Direct Source Access (MCP Required)
> You MUST use MCP to search for the DOI and read the full text.


## References
- LeCun, Y., et al. (2015). Deep learning. Nature. (DOI: 10.1038/nature14539)
- Grinsztajn, L., et al. (2022). Why do tree-based models still outperform deep learning on typical tabular data? NeurIPS. (DOI: 10.48550/arXiv.2207.08815)
