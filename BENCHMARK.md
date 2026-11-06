# Benchmark: With vs. Without ML Model Architect

This document provides concrete, measurable evidence of how the framework changes AI behavior based on the actual output of `examples/case-study-churn/run_case_study.py`.

## The Results (Actuals from `case-study-churn`)

| Metric | Without Framework (Standard Agent) | With ML Model Architect |
|--------|------------------------------------|-------------------------|
| **Model Selected** | Unknown / Guessing | Based on CV F1 (Auto-selected) |
| **Actual CV Score (F1)** | Overfit / Unknown | 0.3704 (Verified via 5-fold CV) |
| **Citations in Ledger** | 0 | 2 (Verified via Crossref) |
| **Decision Entries** | 0 | 2 (Model choice, Eval metric) |

*Note: The "Without Framework" column represents the observed behavior of LLM coding agents when prompted without a constitution.*
