---
group_id: "04"
name: "Neural Networks"
---

> ⚠️ **WARNING: This file is a summary/index.**
> You MUST use your MCP search tools to read the actual paper before making a decision.
> See CONSTITUTION Part F.

# Evaluation — Neural Networks

## 1. Metrics
F1, ROC-AUC / MAE, RMSE + Brier

## 2. Validation Protocol
StratifiedKFold + Hold-out mandatory

## 3. Problem Catalog
- Unstable convergence | Dropout
- NaN divergence | Check loss stability
- Slow training | Multi-fidelity
