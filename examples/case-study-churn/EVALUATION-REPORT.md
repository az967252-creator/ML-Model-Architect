# Evaluation Report — Telecom Customer Churn Prediction

## Empirical Validation Metrics (5-Fold Stratified Cross-Validation)

| Model Architecture | 5-Fold CV F1 Score | Standard Error (SE = Std/√5) | Holdout Test F1 | Holdout ROC-AUC | Selection Margin | Decision |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Logistic Regression (Baseline)** | 0.3924 | ± 0.0178 | 0.4103 | 0.6210 | Floor metric | Baseline |
| **HistGradientBoostingClassifier (Candidate)** | **0.4140** | **± 0.0133** | **0.4017** | **0.6589** | **+0.0216 > 0.0133** | **SELECTED (1-SE Rule)** |

## 1-SE Model Selection Rule Decision
- Standard Error (SE) on candidate cross-validation folds: $SE = 0.0133$.
- Candidate HistGradientBoostingClassifier exceeds baseline by $\Delta F1 = 0.0216 > 0.0133$.
- Applying Hastie et al. (2009) 1-SE rule (`10.1007/978-0-387-84858-7`):
  - **Selected Model**: HistGradientBoostingClassifier.

## Validation Protocol
- 5-Fold Stratified Cross-Validation on 80% train partition (1,600 accounts).
- Holdout test evaluation on 20% test partition (400 accounts).

## Leakage Checks
| Check | Status | Verification Evidence |
|:---|:---:|:---|
| Preprocessing Leakage | Passed | All scalers and imputers fit strictly within train folds via Pipeline |
| Target Leakage | Passed | No future billing or churn status information accessible |
| Stratification | Passed | StratifiedKFold maintains class ratio across splits |
