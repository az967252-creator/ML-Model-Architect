---
name: building-and-training
description: "Build and train following the training reference for the selected group. Every decision anchored to a verified source."
version: "2.0.0"
stage: 3
requires: CONSTITUTION.md
inputs: TECH-CHOICE.md (with group_id), REQUIREMENTS.md
outputs: TRAINING-REPORT.md
---

# Stage 3 — Building & Training

## Input Gate

> **MCP REQUIREMENT:** Before setting hyperparameters, use your MCP tool to read the actual training paper for this algorithm (e.g., XGBoost paper).

TECH-CHOICE.md must exist with group_id set (01-12). If missing: STOP.

## Part A — Load (Lazy)
- _shared/TEMPLATE-TRAINING-REPORT.md
- references/stage-3-training/training-<group_id>.md ONLY
- Do NOT load other training files.

## Part B — Reference-Driven Workflow

Every technical decision must find its anchor in the training reference.
If missing: escalate per Constitution B2.

Steps:
1. Data Preparation: scaling, encoding, missing values, imbalance.
2. Training Setup: split strategy, CV, early stopping, seeds.
3. Hyperparameter Search: space from reference, user approves, run Optuna.
4. Experiment Tracking: MLflow (params, metrics, artifacts, seeds, env).
5. Stopping Criteria: early stopping patience from reference.
6. Common Pitfalls Check: walk through the reference's pitfalls section.

## Part C — Pipeline Mandatory

All transforms inside a single Pipeline. Fit on train only. No exceptions.

## Part D — Reference Gap

If a decision has no anchor: STOP.
Present "الفراغ المرجعي: <description>".
Record as deferred in DECISIONS.md.
Never invent.

## Part E — Exit Gate

- [ ] Pipeline complete and runnable.
- [ ] No leakage (all fits on train only).
- [ ] Best run logged with artifacts.
- [ ] Config file exists.
- [ ] Training report written.
- [ ] Every decision has a citation or reference-gap record.
- [ ] User approved.
