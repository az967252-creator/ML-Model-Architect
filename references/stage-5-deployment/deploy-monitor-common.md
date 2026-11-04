---
stage: 5
type: deployment-reference
scope: all-groups
---

> ⚠️ **WARNING: This file is a summary/index.**
> You MUST use your MCP search tools to read the actual paper before making a decision.
> See CONSTITUTION Part F.
# Deployment & Monitoring — Common Reference

## 1. Deployment Strategies
| Strategy | When to use | Reference |
|----------|-------------|-----------|
| Shadow | Ground truth is delayed | arXiv:2611.02251 |
| Canary | Gradual rollout of a risky new model | arXiv:2611.02251 |
| Blue-Green | High-risk switchover with instant rollback | arXiv:2611.02251 |

## 2. Monitoring Layers
| Layer | Metric |
|-------|--------|
| Data Drift | KS test per feature, PSI on output |
| Performance | Label-dependent KPIs (F1, MAE) |
| System Health | Latency, error rate, throughput |
| Business | Cost saved, revenue impact |

## 3. Retraining Policies
Framework: Retrain / Alert / Rollback — a state machine giving each
response a trigger and a cost.

## 4. Quality Gate
- New model must beat current on held-out set.
- Two-stage canary before promotion.
- One-command rollback.

## 5. Problem Catalog (Production)
| Problem | Solution |
|---------|----------|
| Silent degradation | Continuous monitoring of both label-dependent and label-independent metrics |
| Calendar-based retraining only | Data-driven triggers |
| Unnecessary retraining | Hybrid drift detection (data + performance) |
| Late drift detection | Enhanced adversarial drift detection or ADWIN |
| Silent regression on deploy | Quality Gate + two-stage canary |
| No rollback plan | Blue-Green or Canary with one-command rollback |
| Delayed labels | Shadow Deployment |
| Feature drift | KS per feature vs training distribution, PSI on output |
| Audit gap | Unified logging + model lineage |
| High retraining cost | Evaluate incremental learning vs periodic retrain |

## 6. References (Verified)
- Sadeghian, A. et al. (2026). Retrain, Alert, or Rollback? A Three-Response Decision Framework for Production ML Under Concept Drift. arXiv:2611.02251. DOI: 10.48550/arXiv.2611.02251
- Hafezi, T. et al. (2026). A Multi-Dimensional Taxonomy and Practical Framework for MLOps Monitoring. IEEE.
- Dasari, S. (2026). When to Retrain: An Empirical Study of Retraining Policies for Streaming ML. arXiv:2608.19488. DOI: 10.48550/arXiv.2608.19488
- Shcherbinin et al. (2026). Adaptive Mechanisms for Model Retraining in Production. Semantic Scholar CorpusID: 286298538.
- KodeKloud. (2026). CI/CD for Machine Learning: Best Practices and Tools.
