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
alpha (1e-3 to 10), var_smoothing (1e-12 to 1e-6) (heuristic, no source)


## 3. Common Pitfalls
- Independence violation: Lazy NB
- Poor calibration: Empirical-Bayes
- Noise: Noise-robust tuning


## 8. Direct Source Access (MCP Required)
> You MUST use MCP to search for the DOI and read the full text.


## References
- Domingos, P., & Pazzani, M. (1997). On the Optimality of the Simple Bayesian Classifier. Machine Learning. (DOI: 10.1023/A:1007413511361)
