# Benchmark: With vs. Without ML Model Architect

This document provides concrete, measurable evidence of how the framework changes AI behavior. 

## The Results (Actuals from `case-study-churn`)

| Metric | Without Framework | With ML Model Architect | Delta |
|--------|-------------------|-------------------------|-------|
| **Questions asked before coding** | 0 | 7 | +7 |
| **Verified academic citations** | 0 | 4 (Breiman, XGBoost, etc.) | +4 |
| **Baseline comparison** | None | Logistic Regression first | Yes |
| **Data Leakage checks** | 0 | 3 (Fit on train only, Pipeline) | +3 |
| **Decision Logging** | 0 | 12 entries in `DECISIONS.md` | +12 |
| **Model Selected** | Gradient Boosting (Blindly) | Logistic Regression (Based on CV) | Data-Driven |
| **Actual CV Score (F1)** | Overfit (Unknown) | 0.3704 (Verified via 5-fold CV) | Accurate |

## The Qualitative Difference

**Standard AI Agent (Without):**
> *User:* "Build a churn model."
> *Agent:* "Here is a Python script using XGBoost with default parameters. It gets 99% accuracy on the training data."
> *(Result: Massive data leakage, no business context, unverified assumptions).*

**ML Model Architect (With):**
> *User:* "Build a churn model."
> *Agent:* "Let's start Stage 1. What is the exact definition of churn here? What is the cost of a False Positive vs. a False Negative?"
> *(Later...)* "I recommend Gradient Boosting based on Chen & Guestrin (2016). Let me verify this DOI via MCP... Now, I will build a Pipeline to ensure no preprocessing leakage, and evaluate using Nested Cross-Validation."
