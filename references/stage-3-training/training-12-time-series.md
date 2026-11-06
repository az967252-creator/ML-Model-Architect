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
p/d/q (0-5), lag_window (1-30), hidden_size (16-256) [Source: 10.1098/rsta.2020.0209]


## 3. Common Pitfalls
- Temporal leakage: Enforce TimeSeriesSplit
- Complex patterns: TFT or TCN
- MAPE with zeros: MASE


## 8. Direct Source Access (MCP Required)
> You MUST use MCP to search for the DOI and read the full text.


## References
- Lim, B., & Zohren, S. (2021). Time-series forecasting with deep learning: a survey. Phil. Trans. R. Soc. A. (DOI: 10.1098/rsta.2020.0209)
