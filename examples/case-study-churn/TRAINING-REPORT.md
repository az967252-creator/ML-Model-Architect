# Training Report — Telecom Customer Churn Prediction

## Configuration
- Group ID: 03 (Gradient Boosting) & 01 (Linear Models)
- Seed: 42
- Framework: scikit-learn Pipeline (zero leakage guarantee)

## Data Preparation
| Feature / Step | Transformation | Handling |
|----------------|----------------|----------|
| `tenure`, `monthly_charges`, `total_charges` | StandardScaler | Median Imputation |
| `contract`, `internet_service` | OneHotEncoder(ignore_unknown) | Most Frequent Imputation |

## Cross-Validation Setup
- Protocol: 5-Fold Stratified Cross-Validation
- Folds: 5 (fit on train folds only)
- Target: `churn` (Binary 0/1)

## Model Comparison
- Baseline: Logistic Regression (max_iter=1000)
- Candidate: Gradient Boosting Classifier (HistGradientBoosting, max_depth=3)
