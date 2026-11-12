# Training Report — Car Price Prediction (Synthetic Demo)

## Configuration
- Group ID: 03
- Seed: 42
- Environment: Python 3.10, scikit-learn 1.2

## Data Preparation
- Preprocessing wrapped inside `ColumnTransformer` within the Pipeline (No Leakage).

## Experiment Results (5-Fold CV)
| Model | Complexity | CV RMSE (Mean +/- Std) | Test RMSE |
|-------|------------|------------------------|-----------|
| Dummy (Mean Baseline) | 0 | 12148.19 +/- 333.36 | 12223.19 |
| Linear Regression | 1 | 2333.97 +/- 75.06 | 2303.08 |
| Gradient Boosting | 2 | 2360.57 +/- 61.44 | 2198.66 |

**Selection Logic (1-SE Rule):**
The best CV RMSE was 2333.97 (Linear Regression). The standard error was 33.57.
Models within 1 standard error of the best were: Linear Regression, Gradient Boosting.
The simplest model among these candidates was selected: **Linear Regression**.

*Note: While Gradient Boosting had a lower Test RMSE, the cross-validation difference is not statistically significant (within 1 Standard Error).*
