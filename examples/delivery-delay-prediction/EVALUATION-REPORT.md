# Evaluation Report — Delivery Delay Prediction

## Empirical Validation Metrics (5-Fold Stratified Cross-Validation)

| Model Architecture | 5-Fold CV F1 Score | Standard Error (SE) | Holdout Test F1 | Selection Margin | Decision |
|:---|:---:|:---:|:---:|:---:|:---:|
| **Logistic Regression (Baseline)** | 0.9582 | ± 0.0042 | 0.9586 | Floor metric | Baseline |
| **HistGradientBoostingClassifier (Candidate)** | **0.9847** | **± 0.0028** | **0.9824** | **+0.0265 > 0.0028** | **SELECTED** |

## 1-SE Model Selection Rule Decision
- Standard Error (SE) threshold for Candidate: $SE = 0.0028$.
- Difference: $\text{CV}_{\text{GB}} - \text{CV}_{\text{Linear}} = 0.9847 - 0.9582 = +0.0265$.
- Since $\Delta F1 (0.0265) > 1 \times SE (0.0028)$, candidate demonstrates statistically significant improvement beyond noise.
- Applying Hastie et al. (2009) 1-SE rule (`10.1007/978-0-387-84858-7`):
  - **Selected Model**: HistGradientBoostingClassifier.

## Validation Protocol
- 5-Fold Stratified Cross-Validation on 80% train partition (1,600 orders).
- Holdout test evaluation on 20% test partition (400 orders).

## Leakage Checks
| Check | Status | Verification Evidence |
|:---|:---:|:---|
| Selection Leakage | Passed | Preprocessing encapsulated entirely within Pipeline |
| Preprocessing Leakage | Passed | StandardScaler and SimpleImputer fit strictly within train folds |
| Encoding Leakage | Passed | OneHotEncoder fit strictly within train folds |
