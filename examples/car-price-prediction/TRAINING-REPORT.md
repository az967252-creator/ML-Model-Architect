# Training Report — Car Price Prediction

## Configuration
- Group ID: 03
- Seed: 42
- Environment: Python 3.10, scikit-learn 1.2

## Data Preparation
- Preprocessing wrapped inside `ColumnTransformer` within the Pipeline (No Leakage).

## Experiment Results
| Model | CV RMSE | Test RMSE |
|-------|---------|-----------|
| Linear Regression | 2333.97 | 2303.08 |
| Gradient Boosting | 2360.57 | 2198.66 |

**Winning Model:** Linear Regression (CV RMSE: 2333.97)
