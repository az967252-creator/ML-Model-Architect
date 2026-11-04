---
group_id: "08"
name: "Naive Bayes"
---

> ⚠️ **WARNING: This file is a summary/index.**
> You MUST use your MCP search tools to read the actual paper before making a decision.
> See CONSTITUTION Part F.

# Training — Naive Bayes

## 1. Data Preparation
Scaling for GaussianNB. CountVectorizer for text.

## 2. Hyperparameter Search
`alpha (1e-3 to 10), var_smoothing`

## 3. Common Pitfalls
- Independence violation: Lazy NB
- Poor calibration: Empirical-Bayes
- Noise: Noise-robust tuning
