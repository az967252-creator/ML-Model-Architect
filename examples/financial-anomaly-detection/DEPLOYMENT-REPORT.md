# Deployment Report — Financial Anomaly Detection

## Strategy
- Chosen: Blue-Green Deployment
- Rationale: Must have instant rollback if False Positive rate spikes and blocks valid customers.

## Monitoring
| Metric type | Metric | Threshold | Reference |
|-------------|--------|-----------|-----------|
| Performance | False Positive Rate | > 2% | N/A |
| Data Drift | PSI on Transaction Amount | > 0.25 | N/A |

## Rollback Plan
- Command: Switch traffic back to Green environment.
- Condition: FP rate > 3% for 15 minutes.
