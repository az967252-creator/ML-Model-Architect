---
group_id: "05"
name: "Tabular Foundation Models"
---

> ⚠️ **WARNING: This file is a summary/index.**
> You MUST use your MCP search tools to read the actual paper before making a decision.
> See CONSTITUTION Part F.

# Training — Tabular Foundation Models

## 1. Data Preparation
Built-in preprocessing. No fine-tuning for <1000 rows.

## 2. Hyperparameter Search
`n_estimators (1-32), context_size (512-1024)`

## 3. Common Pitfalls
- No native interpretability: Post-hoc explainers
- Sensitivity: Re-tune context_size
- Slow inference: Only if accuracy > speed


## 8. Direct Source Access (MCP Required)
> You MUST use MCP to search for the DOI and read the full text.
