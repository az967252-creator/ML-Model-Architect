# Training Report — Car Price Prediction

## Configuration
- Group ID: 03
- Seed: 42
- Environment: Python 3.10, scikit-learn 1.2

## Data Preparation
| Step | Decision | Reference |
|------|----------|-----------|
| Scaling | StandardScaler (inside Pipeline). | 10.1007/978-0-387-84858-7 |
| Encoding | One-Hot Encoding for 'brand'. | 10.1007/978-0-387-84858-7 |

## Best Run
- Run ID: xgb_run_01
- Params: learning_rate=0.1, max_depth=3, n_estimators=100
- Validation metrics: RMSE = 1985.42
