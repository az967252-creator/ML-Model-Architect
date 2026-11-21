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
| Shadow | Ground truth is delayed; compare outputs without user impact | 10.5555/2969239.2969316 @ Sec 4 |
| Canary | Gradual rollout of a risky new model | https://research.google/pubs/pub48551/ @ Sec 3 |
| Blue-Green | High-risk switchover with instant rollback | 10.1145/3097983.3098021 @ Sec 3.2 |

## 2. Monitoring Layers
| Layer | Metric | Threshold |
|-------|--------|-----------|
| Data Drift | KS test per feature (heuristic), PSI on output (heuristic) | PSI > 0.2 (heuristic) |
| Performance | Label-dependent KPIs (F1, MAE) | Drop > 5% (heuristic) |
| System Health | Latency, error rate, throughput | p99 > 50ms (heuristic) |
| Business | Cost saved, revenue impact | Deficit > 2% (heuristic) |

## 3. Retraining Policies
Framework: Retrain / Alert / Rollback — a state machine giving each response a trigger and an associated cost (Gama et al., 2014; 10.1145/2523813 @ Sec 3).

## 4. Quality Gate
- New model must beat current on held-out set (Varma & Simon, 2006; 10.1186/1471-2105-7-91 @ Sec 2).
- Two-stage canary before promotion (heuristic).
- One-command rollback (10.5555/2969239.2969316 @ Sec 4).

## 5. Problem Catalog (Production)
| Problem | Solution | Source Reference |
|---------|----------|------------------|
| Silent degradation | Continuous monitoring of label-dependent & label-independent metrics | 10.1145/2523813 @ Sec 3 |
| Calendar-based retraining only | Data-driven drift triggers | 10.1145/2523813 @ Sec 4 |
| Unnecessary retraining | Hybrid drift detection (data distribution + performance) | 10.48550/arXiv.1810.11953 @ Sec 2 |
| Late drift detection | Enhanced adversarial drift detection or ADWIN | 10.1145/2523813 @ Sec 3.2 |
| Silent regression on deploy | Quality Gate + two-stage canary | https://research.google/pubs/pub48551/ @ Sec 3 |
| No rollback plan | Blue-Green or Canary with one-command rollback | 10.5555/2969239.2969316 @ Sec 4 |
| Delayed labels | Shadow Deployment | 10.5555/2969239.2969316 @ Sec 4 |
| Feature drift | KS per feature vs training distribution, PSI on output | https://research.google/pubs/pub48551/ @ Sec 2 |
| Audit gap | Unified logging + model lineage | 10.1145/3097983.3098021 @ Sec 3 |
| High retraining cost | Evaluate incremental learning vs periodic retrain | 10.1145/2523813 @ Sec 5 |

## 6. References (Verified)
- Sculley, D. et al. (2015). Hidden Technical Debt in Machine Learning Systems. NeurIPS. (DOI: 10.5555/2969239.2969316)
- Gama, J. et al. (2014). A survey on concept drift adaptation. ACM Computing Surveys. (DOI: 10.1145/2523813)
- Breck, E. et al. (2019). Data Validation for Machine Learning. MLSys. (URL: https://research.google/pubs/pub48551/)
- Baylor, D. et al. (2017). TFX: A TensorFlow-Based Production-Scale Machine Learning Platform. KDD. (DOI: 10.1145/3097983.3098021)
- Rabanser, S. et al. (2019). Failing Loudly: An Empirical Study of Methods for Detecting Dataset Shift. NeurIPS. (DOI: 10.48550/arXiv.1810.11953)

## 7. Direct Source Access (MCP Required)
> You MUST use MCP to search for the DOI and read the full text.
