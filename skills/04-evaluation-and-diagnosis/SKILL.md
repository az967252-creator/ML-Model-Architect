---
name: evaluation-and-diagnosis
description: "Evaluate rigorously, then diagnose any weakness using the group's problem catalog. No invention."
version: "2.0.0"
stage: 4
requires: CONSTITUTION.md
inputs: TRAINING-REPORT.md, group_id, REQUIREMENTS.md
outputs: EVALUATION-REPORT.md
---

# Stage 4 — Evaluation & Diagnosis

## Input Gate

> **MCP REQUIREMENT:** Before diagnosing a problem, use your MCP tool to search OpenAlex for solutions cited in literature.

TRAINING-REPORT.md must exist and be user-approved.

## Part A — Load (Lazy)
- _shared/TEMPLATE-EVALUATION-REPORT.md
- references/stage-4-evaluation/eval-<group_id>.md ONLY

## Part B — Reference-Driven Evaluation

1. Metrics selection
   From Stage 1 business metric + eval reference.

2. Validation protocol
   Nested CV for tuned models (mandatory).
   Time-based split for temporal data (mandatory).

3. Leakage check
   - Selection leakage
   - Preprocessing leakage
   - Temporal leakage

4. Error analysis
   Residuals / confusion matrix / per-segment breakdown.

5. Confidence intervals
   Bootstrap (1000 iterations) or cross-validation folds.

## Part C — Problem Catalog (Reference-Based Diagnosis)

When a metric is weak:
1. Open the problem catalog inside eval-<group_id>.md.
2. Find the symptom that matches.
3. Propose ONLY solutions listed there, each with citation.
4. If no matching solution: STOP, "الفراغ المرجعي".

Forbidden: proposing a fix from "experience".

## Part D — Exit Gate

- [ ] Every metric has a reference anchor.
- [ ] Validation protocol documented.
- [ ] Leakage checks done and documented.
- [ ] Error analysis done.
- [ ] Metrics compared to Stage 1 baseline.
- [ ] CIs computed where possible.
- [ ] User approved EVALUATION-REPORT.md.
