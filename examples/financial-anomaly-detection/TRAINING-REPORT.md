# Training Report — Financial Anomaly Detection

## Configuration
- Group ID: 11
- Seed: 42

## Data Preparation
| Step | Decision | Reference |
|------|----------|-----------|
| Scaling | Required for Autoencoders, not for Isolation Forest. | 10.1109/ICDM.2008.17 |

## Best Run
- Run ID: if_run_01
- Params: contamination=0.01, n_estimators=100
- Validation metrics: AUPRC = 0.88
