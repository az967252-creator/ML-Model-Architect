# Deployment Report — Delivery Delay Prediction

## Strategy
- Chosen: Shadow Deployment
- Rationale: Ground truth (actual delivery) is delayed by 3-5 days. We cannot use Canary.

## Monitoring
| Metric type | Metric | Threshold | Reference |
|-------------|--------|-----------|-----------|
| Data Drift | PSI on Weather Data | > 0.2 | N/A |
| Performance | F1 Score | Drop below 0.75 | N/A |

## Rollback Plan
- Command: kubectl rollout undo deployment/delay-predictor
- Condition: F1 drops below 0.70 for 3 consecutive days.
