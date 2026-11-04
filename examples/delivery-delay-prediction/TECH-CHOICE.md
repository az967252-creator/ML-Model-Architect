# Technique Choice — Delivery Delay Prediction

## Selected Family
- Family: Gradient Boosting
- Group ID: 03
- Reference: references/stage-2-selection/ref-03-gradient-boosting.md

## Sub-Algorithm
- Selected: XGBoost

## Baseline
- Method: Logistic Regression (to establish a floor)

## Transition Criterion
- Move to complex model if Baseline F1 < 0.70.
