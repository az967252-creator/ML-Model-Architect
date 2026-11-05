---
name: deployment-and-monitoring
description: "Deploy with a referenced strategy and set up referenced monitoring + retraining policy."
version: "2.0.0"
stage: 5
requires: CONSTITUTION.md
inputs: EVALUATION-REPORT.md, group_id
outputs: DEPLOYMENT-REPORT.md
---

# Stage 5 — Deployment & Monitoring

## Input Gate
EVALUATION-REPORT.md must exist and be user-approved.

## Part A — Load (Lazy)
- _shared/TEMPLATE-DEPLOYMENT-REPORT.md
- references/stage-5-deployment/deploy-monitor-common.md
- references/stage-5-deployment/deploy-monitor-by-type.md (filtered)

## Part B — Reference-Driven Deployment

1. Strategy selection (Shadow / Canary / Blue-Green)
   From deployment reference.
   Shadow is mandatory when labels are delayed.

2. Monitoring metrics
   - Data Drift (KS / PSI)
   - Performance (label-dependent KPIs)
   - System Health (latency, errors)
   - Business Metrics
   Every metric with a reference.

3. Alert thresholds
   From reference.

4. Retraining policy
   Retrain / Alert / Rollback framework.
   From the "Retrain, Alert, or Rollback" reference.

5. Rollback plan
   One-command rollback mandatory.

6. Quality Gate
   New model must beat current on a held-out set before promotion.
   Every retrained model must pass a two-stage canary.

## Part C — Problem Catalog (Production)

Use the 10-problem catalog from the deployment reference.
No invention. Every proposed solution must have a citation.

## Part D — Exit Gate

- [ ] Deployment strategy chosen with reference.
- [ ] Rollback plan documented.
- [ ] Monitoring metrics defined with references.
- [ ] Alert thresholds defined with references.
- [ ] Retraining policy defined with reference.
- [ ] Model lineage + unified logging enabled.
- [ ] User approved DEPLOYMENT-REPORT.md.
