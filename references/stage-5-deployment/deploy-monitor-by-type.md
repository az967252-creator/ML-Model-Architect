---
stage: 5
type: deployment-reference
scope: by-task-type
---

> ⚠️ **WARNING: This file is a summary/index.**
> You MUST use your MCP search tools to read the actual paper before making a decision.
> See CONSTITUTION Part F.
# Deployment & Monitoring — By Task Type

## Classification
- Drift focus: class distribution (predicted positive rate).
- Alert: predicted positive rate deviates >20% from training.
- Metric: F1 on labeled samples, AUPRC.

## Regression
- Drift focus: prediction mean and variance.
- Alert: MAE increase >15% over baseline.
- Metric: MAE, RMSE, MAPE.

## Time Series
- Drift focus: seasonality shift, regime change.
- Alert: forecast error (MASE) exceeds 1.5x training MASE.
- Retraining: include recent windows; respect TimeSeriesSplit.

## Anomaly Detection
- Drift focus: anomaly rate, false positive rate.
- Alert: FP rate doubles from baseline.
- Metric: AUPRC, detection delay.

## Clustering
- Drift focus: cluster population shift, silhouette drop.
- Alert: Silhouette drop >0.1.
- Retraining: only when assignment loses meaning (documented).
