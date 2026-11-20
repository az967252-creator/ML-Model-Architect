# Requirements — Telecom Customer Churn Prediction

## Goals
### Goal 1: Predict Customer Churn
- What: Predict if an active telecom subscriber will cancel their contract within the next 30 days.
- Decision supported: Retention marketing team initiates targeted retention offers (discount or contract upgrade).
- Success metric: Reduce annual customer churn by 5% and preserve $250k in Annual Recurring Revenue.
- Error cost: False Negative is worse than False Positive (losing an existing customer costs ~5x more than giving an unnecessary discount).

## Requirements
- Data: Historical billing and CRM subscriber records (tenure, monthly charges, total charges, contract type, internet service).
- Volume & Cadence: Monthly batch scoring for 100k active subscribers.
- Constraints: Latency < 100ms per prediction, CPU-only inference environment.

## Handoff to Stage 2
- Task type: Binary Classification
- Data nature: Tabular (Mixed numerical & categorical)
- Priority: Balanced (Accuracy prioritized while maintaining interpretability for retention triggers)
- Data size: Medium (10k-100k rows)
