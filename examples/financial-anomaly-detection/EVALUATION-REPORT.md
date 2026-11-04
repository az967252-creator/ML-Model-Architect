# Evaluation Report — Financial Anomaly Detection

## Metrics
| Metric | Value | 95% CI | Reference | Baseline |
|--------|-------|--------|-----------|----------|
| AUPRC | 0.88 | [0.85, 0.91] | 10.1109/ICDM.2008.17 | 0.60 |
| Recall | 0.85 | [0.82, 0.88] | 10.1109/ICDM.2008.17 | 0.55 |

## Validation Protocol
- Time-based split (due to temporal nature of transactions).

## Leakage Checks
| Check | Status |
|-------|--------|
| Selection | Passed |
| Preprocessing | Passed |
| Temporal | Passed (No future data) |
