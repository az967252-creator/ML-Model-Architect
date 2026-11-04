---
group_id: "05"
name: "Tabular Foundation Models"
---

> ⚠️ **WARNING: This file is a summary/index.**
> You MUST use your MCP search tools to read the actual paper before making a decision.
> See CONSTITUTION Part F.

# Group 05 — Tabular Foundation Models

## 1. Overview
TabPFN and successors. Prior-fitted networks for small/medium data.

## 2. Family Members
TabPFN, TabPFN-2, TabPFN-3

## 3. Strengths
- Outperforms XGBoost on small/medium
- No tuning needed

## 4. Weaknesses
- Slow inference
- Sensitive to context size
- No native interpretability

## 5. Recommended Baseline
TabPFNClassifier/Regressor (default)

## 6. Key Hyperparameters
`n_estimators (1-32), context_size (512-1024)`

## 7. References
- Use MCP to search for the latest papers.
