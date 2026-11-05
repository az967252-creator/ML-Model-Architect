# Evaluation Report — Delivery Delay Prediction

## Metrics
| Metric | Value | 95% CI | Reference | Baseline |
|--------|-------|--------|-----------|----------|
| F1 Score | 0.82 | [0.79, 0.85] | 10.1145/2939672.2939785 | 0.65 |
| PR-AUC | 0.84 | [0.81, 0.87] | 10.1145/2939672.2939785 | 0.60 |

## Validation Protocol
- Nested CV: Yes, 5-fold.

## Leakage Checks
| Check | Status |
|-------|--------|
| Selection | Passed |
| Preprocessing | Passed (Pipeline used) |
| Temporal | Passed (TimeSeriesSplit) |
