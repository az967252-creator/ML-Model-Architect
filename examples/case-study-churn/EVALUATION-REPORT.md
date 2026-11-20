# Evaluation Report — Telecom Customer Churn Prediction

## Metrics
| Model | 5-Fold CV F1 | Test F1 | Test ROC-AUC | Reference |
|-------|--------------|---------|--------------|-----------|
| Baseline (Logistic Regression) | ~0.72 | 0.73 | 0.81 | 10.1007/978-0-387-84858-7 |
| Candidate (Gradient Boosting) | ~0.82 | 0.83 | 0.89 | 10.1145/2939672.2939785 |

## 1-SE Model Selection Rule
- Standard Error (SE) on CV folds computed per Hastie et al. (2009) (`10.1007/978-0-387-84858-7`).
- Candidate Gradient Boosting exceeds Baseline by more than 1-SE threshold.
- **Decision:** Select Gradient Boosting Classifier for deployment.

## Leakage Checks
| Check | Status | Evidence |
|-------|--------|----------|
| Preprocessing Leakage | Passed | All scalers & encoders fit strictly within train folds via Pipeline |
| Target Leakage | Passed | No future billing information included |
| Stratification | Passed | StratifiedKFold maintains class ratio across splits |
