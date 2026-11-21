# Methodological Context and Dataset Disclaimer

This directory contains four complete end-to-end reference projects designed to demonstrate the **ML Model Architect** governance framework:
1. `car-price-prediction` (Tabular Regression)
2. `delivery-delay-prediction` (Tabular Binary Classification)
3. `financial-anomaly-detection` (Unsupervised Outlier Detection with Extreme Imbalance)
4. `case-study-churn` (Imbalanced Telecom Customer Churn)

## Synthetic Controlled Datasets

The datasets in these examples are **deterministic synthetic datasets** generated with known statistical ground-truth properties:
- `car-price-prediction`: Ground-truth compound non-linear depreciation interactions (`age * mileage * 0.005`).
- `delivery-delay-prediction`: Multimodal logistics factors with known traffic and weather multipliers.
- `financial-anomaly-detection`: Exact 3.0% anomaly injection via lognormal and uniform burst distributions.
- `case-study-churn`: Known non-linear tenure and contract churn distributions.

Using controlled synthetic datasets isolates algorithmic decision-making, data leakage vulnerability, and model selection discipline from noisy real-world confounders, and guarantees that the test suite and execution engine run 100% offline without external network dependencies.

## Dynamic Verification & Real Execution

Every example project includes runnable Python code (`train.py`) that executes in under two seconds.
All reports (`TRAINING-REPORT.md`, `EVALUATION-REPORT.md`, `metrics.json`) reflect empirical outputs generated directly by `train.py` and are cryptographically verified by the policy engine (`scripts/run_policy.py`).
