---
group_id: "08"
name: "Naive Bayes"
---

> ⚠️ **WARNING: This file is a summary/index.**
> You MUST use your MCP search tools to read the actual paper before making a decision.
> See CONSTITUTION Part F.

# Group 08 — Naive Bayes

## 1. Overview
Naive Bayes classifiers (Gaussian, Multinomial).

## 2. Family Members
GaussianNB, MultinomialNB, BernoulliNB

## 3. Strengths
- Extremely fast
- Strong on sparse data

## 4. Weaknesses
- Independence assumption rarely holds
- Poor calibration

## 5. Recommended Baseline
GaussianNB (continuous) or MultinomialNB (counts)

## 6. Key Hyperparameters
`alpha (1e-3 to 10), var_smoothing`

## 7. References
- Use MCP to search for the latest papers.


## 8. Direct Source Access (MCP Required)
> You MUST use MCP to search for the DOI and read the full text.


## References
- Domingos, P., & Pazzani, M. (1997). On the Optimality of the Simple Bayesian Classifier. Machine Learning. (DOI: 10.1023/A:1007413511361)
