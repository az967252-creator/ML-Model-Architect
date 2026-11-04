---
name: technique-selection
description: "5-level decision tree from task type to algorithm family. Every option carries pros/cons + reference anchor."
version: "2.0.0"
stage: 2
requires: CONSTITUTION.md
inputs: REQUIREMENTS.md
outputs: TECH-CHOICE.md
---

# Stage 2 — Technique Selection

## Input Gate

> **MCP REQUIREMENT:** Before selecting any family, use your MCP tool (OpenAlex/arXiv) to read the actual paper for the chosen group.

REQUIREMENTS.md must exist and pass Stage 1 exit gate.
If not: STOP with message "المرحلة 1 مش مكتملة".

## Part A — The 5-Level Tree

Level 1: Task type
  Classification / Regression / Clustering / Anomaly / Time Series

Level 2: Data nature
  Tabular / Text / Image / Sequential

Level 3: Priority (from Stage 1 constraints)
  Interpretability first / Accuracy first / Balanced

Level 4: Data size
  Small (<10k) / Medium (10k-100k) / Large (>100k)

Level 5: 2-3 candidate families

At each level: one MCQ. Options generated from accumulated state.

## Part B — Option Display Format (mandatory)

  Why now: <one line>
  Question: <the question>

    A) <name>
       Strengths: <list>
       Weaknesses: <list>
       Best for: <when this wins>
       Reference: ref-XX

    B) ...
    C) ...

    D) خيار تاني (اكتبه)
    E) مش عارف

Rules:
- 3-4 options + "خيار تاني" + "مش عارف".
- No option without pros/cons.
- No option without reference anchor (or explicit "لا يوجد مرجع").
- No "recommended" label.

## Part C — Lazy Reference Loading

- Load references/stage-2-selection/ref-00-index.md first (cheap).
- Load ref-XX-<slug>.md ONLY when the user reaches that group.
- If user asks for more depth: offer to summarize the full reference file.

## Part D — Exclusion Transparency

For each excluded family, show one line:
  "استبعدنا <family> لأن <reason from Stage 1 constraints>."

## Part E — After Family Selection

1. If sub-algorithms exist, load that reference and present second MCQ
   with the same format.
2. Ask about the baseline: "نبدأ بـ <simplest> كـ baseline؟"
3. Ask about transition criterion: "لو الـ baseline حقق أقل من X%
   من مقياس النجاح، ننتقل للعائلة الأعقد؟"
4. Record all in DECISIONS.md.

## Part F — Exit Gate

- [ ] Family selected + group_id recorded.
- [ ] Sub-algorithm selected (if applicable).
- [ ] Baseline selected.
- [ ] Transition criterion agreed.
- [ ] Every option had pros/cons + reference anchor.
- [ ] User explicitly approved TECH-CHOICE.md.
