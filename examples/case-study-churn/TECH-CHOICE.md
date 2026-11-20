# Technique Choice — Telecom Customer Churn Prediction

## Selected Family
- Family: Gradient Boosting & Linear Models
- Group ID: 03 & 01
- References:
  - references/stage-2-selection/ref-03-gradient-boosting.md
  - references/stage-2-selection/ref-01-linear-models.md

## Sub-Algorithms
- Baseline: Logistic Regression (with StandardScaler & OneHotEncoder)
- Candidate: Gradient Boosting Classifier (n_estimators=100, max_depth=3)

## Transition Criterion
- Select Candidate over Baseline only if Candidate CV F1 score outperforms Baseline beyond the 1-SE margin (Hastie et al., 2009).
