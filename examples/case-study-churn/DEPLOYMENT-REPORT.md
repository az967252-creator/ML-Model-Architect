# Deployment Report — Telecom Customer Churn Prediction

## Strategy
- Chosen: Canary Deployment (10% -> 25% -> 50% -> 100%)
- Rationale: Labels become observable within 30-day billing cycle. Canary limits potential retention offer misallocation.

## Monitoring
| Metric Type | Metric | Threshold | Retraining Action |
|-------------|--------|-----------|-------------------|
| Data Drift | PSI (Population Stability Index) on charges & tenure | PSI > 0.20 | Trigger automated drift alert & retraining |
| Performance | Monthly F1 Score | Drops below 0.75 | Fallback to Baseline & investigate feature drift |
| System Health | Prediction Latency (p99) | > 50ms | Scale replica instances |

## Rollback Plan
- One-command rollback: `kubectl rollout undo deployment/churn-predictor`
- Trigger: If False Positive churn prediction exceeds 35% in first 48 hours of rollout.
