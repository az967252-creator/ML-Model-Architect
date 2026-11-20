# Technique Choice — Car Price Prediction

## Selected Family
- Family: Linear Models & Tree Models
- Group ID: 01 & 02
- References:
  - references/stage-2-selection/ref-01-linear-models.md
  - references/stage-2-selection/ref-02-tree-models.md

## Sub-Algorithms
- Baseline: Dummy (Mean Baseline) & Linear Regression with StandardScaler + OneHotEncoder
- Candidate: Gradient Boosting Regressor (n_estimators=100, max_depth=3)

## Transition Criterion
- Select Candidate over Baseline only if Candidate CV RMSE beats Baseline CV RMSE beyond the 1-SE margin (Hastie et al., 2009).
