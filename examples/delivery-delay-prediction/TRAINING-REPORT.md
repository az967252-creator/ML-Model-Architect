# Training Report — Delivery Delay Prediction

## Configuration
- Group ID: 03
- Seed: 42
- Environment: Python 3.10, XGBoost 2.0

## Data Preparation
| Step | Decision | Reference |
|------|----------|-----------|
| Scaling | Not required for trees. | N/A |
| Imbalance | scale_pos_weight=2.5 | 10.1145/2939672.2939785 |

## Hyperparameter Search
- Strategy: Optuna TPE
- Budget: 50 trials

## Best Run
- Run ID: xgb_run_45
- Params: learning_rate=0.05, max_depth=6, n_estimators=500
- Validation metrics: F1 = 0.82
