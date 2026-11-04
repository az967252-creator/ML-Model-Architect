---
group_id: "12"
name: "Time Series"
---

> ⚠️ **WARNING: This file is a summary/index.**
> You MUST use your MCP search tools to read the actual paper before making a decision.
> See CONSTITUTION Part F.

# Evaluation — Time Series

## 1. Metrics
MAE, RMSE, MAPE, sMAPE, MASE, CRPS

## 2. Validation Protocol
TimeSeriesSplit MANDATORY

## 3. Problem Catalog
- Temporal leakage | Enforce TimeSeriesSplit
- Complex patterns | TFT or TCN
- MAPE with zeros | MASE
