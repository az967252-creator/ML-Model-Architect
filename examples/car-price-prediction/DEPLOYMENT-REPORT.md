# Deployment Report — Car Price Prediction

## Strategy
- Chosen: Direct Synchronous Serving (REST API / Microservice)
- Latency target: < 15ms p99 on CPU
- Artifact: Scikit-learn Pipeline (preprocessing + model) exported via skops / joblib

## Monitoring & Drift Detection
| Metric Type | Monitoring Method | Threshold | Reference |
|-------------|-------------------|-----------|-----------|
| Data Drift | Population Stability Index (PSI) on `mileage` and `age` | PSI > 0.2 | N/A |
| Prediction Drift | Kolmogorov-Smirnov test on predicted price distribution | p-value < 0.05 | N/A |
| Performance | Rolling Mean Absolute Error (MAE) vs confirmed sales price | > 15% increase | N/A |

## Rollback Plan
- Fallback to 이전 Linear Regression weights or mean baseline if latency > 50ms or PSI > 0.25.
