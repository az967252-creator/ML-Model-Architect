# Evaluation Report — Car Price Prediction

## Metrics
| Model | 5-Fold CV RMSE | SE (Std/√5) | Holdout Test RMSE | Reference |
|-------|----------------|-------------|-------------------|-----------|
| Dummy (Mean Baseline) | 12,148.19 | ± 149.08 | 12,223.19 | Foundational |
| Linear Regression (Baseline) | 2,333.97 | ± 33.57 | 2,303.08 | Foundational |
| Gradient Boosting (Candidate) | 2,360.57 | ± 27.48 | 2,198.66 | 10.1145/2939672.2939785 |

## Validation Protocol
- 5-Fold Cross-Validation on 80% train partition (800 rows).
- Holdout test evaluation on 20% test partition (200 rows).

## 1-SE Model Selection Rule Decision
- Standard Error (SE) threshold for Linear Regression: 33.57.
- Gradient Boosting CV RMSE (2360.57) does not outperform Linear Regression CV RMSE (2333.97).
- Applying Hastie et al. (2009) 1-SE rule (10.1007/978-0-387-84858-7):
  - **Selected Model**: **Linear Regression** (simpler, faster, robust generalization, lowest CV error).

## Leakage Checks
| Check | Status |
|-------|--------|
| Selection Leakage | Passed (preprocessing within Pipeline) |
| Feature Scaling | Passed (StandardScaler fitted only on train fold) |
| Encoding Leakage | Passed (OneHotEncoder fitted only on train fold) |
