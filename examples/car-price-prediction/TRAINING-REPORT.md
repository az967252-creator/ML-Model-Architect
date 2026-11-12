# Training Report — Car Price Prediction (Synthetic Demo)

## Configuration
- Group ID: 03
- Seed: 42
- Environment: Python 3.10, scikit-learn 1.2

## Data Preparation
- Preprocessing wrapped inside `ColumnTransformer` within the Pipeline (No Leakage).

## Experiment Results (5-Fold CV)
| Model | CV RMSE (Mean +/- Std) | Test RMSE |
|-------|------------------------|-----------|
| Dummy (Mean Baseline) | 12148.19 +/- 333.36 | 12223.19 |
| Linear Regression | 2333.97 +/- 75.06 | 2303.08 |
| Gradient Boosting | 2360.57 +/- 61.44 | 2198.66 |

**Winning Model:** Linear Regression (CV RMSE: 2333.97)
