---
group_id: "12"
name: "Time Series"
---

> ⚠️ **WARNING: This file is a summary/index.**
> You MUST use your MCP search tools to read the actual paper before making a decision.
> See CONSTITUTION Part F.

# Training — Time Series

## 1. Data Preparation
Scaling for deep models. Create lag features.

## 2. Hyperparameter Search
`p/d/q (0-5), lag_window (1-30), hidden_size`

## 3. Common Pitfalls
- Temporal leakage: Enforce TimeSeriesSplit
- Complex patterns: TFT or TCN
- MAPE with zeros: MASE
