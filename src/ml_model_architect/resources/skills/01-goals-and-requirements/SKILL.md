---
name: goals-and-requirements
description: "Convert a vague request into complete goals + requirements through a dynamic MCQ engine."
version: "2.0.0"
stage: 1
requires: CONSTITUTION.md
outputs: REQUIREMENTS.md
---

# Stage 1 — Goals & Requirements

## Scope
- In: goals + requirements extraction.
- Out: plan, tech selection, code, algorithm choice.

## Part A — Knowledge State (11 items)

| # | Item | State |
|---|------|-------|
| 1 | The pain | |
| 2 | The decision | |
| 3 | Output user | |
| 4 | Business goal & success | |
| 5 | What is predicted (what, unit, moment) | |
| 6 | Historical labeled cases | |
| 7 | Error cost (which is worse?) | |
| 8 | Current process | |
| 9 | Constraints | |
| 10 | Volume & cadence | |
| 11 | Stakeholders | |

States: unknown / pending / clarifying / confirmed / blocked / delegated.

Dependencies:
- 6 requires 5
- 10 requires 2
- 7 requires 2
- 9 requires 4

Never ask a question whose dependencies are unresolved.

## Part B — Sequential Opening Funnel (5 questions)

### Q1 — Seed (Items 1 + preliminary goal)
Question: "إيه اللي عايز المودل يساعدك فيه؟"
Format:
  A) أتوقع حاجة هتحصل (مبيعات، إلغاء، تأخر)
  B) أكتشف حاجة غريبة (fraud، عيب، شذوذ)
  C) أقسّم عملاء/منتجات لمجموعات
  D) أرتّب/أرشّح حاجة (recommendations)
  E) خيار تاني (اكتبه)
  F) مش عارف

Reflect back in one sentence. Confirm before proceeding.

### Q2 — Decision (Items 2 + 3)
Derived from Q1. Options generated from Q1 context.

### Q3 — Current process (Item 8)
Derived from Q2.

### Q4 — The change (Item 4 part 1)
Derived from Q3.

### Q5 — Success metric (Item 4 part 2)
Must produce a number + timeframe.

After Q5: items 1,2,3,4,8 are confirmed. Gap Analyzer takes over.

## Part C — Dynamic Question Loop

1. Scan items, filter unknowns whose dependencies are resolved.
2. Rank by criticality, then impact, then readiness.
3. Pick the single top candidate.
4. Generate the question. It MUST:
   - Reference something the user already said.
   - Open a specific downstream decision.
   - Be plain business language.
   - Be ONE question.

Question format:
  Why now: <one line: which decision this unblocks>
  Question: <the question>
    A) <option> (<examples>)
    B) <option> (<examples>)
    C) <option> (<examples>)
    D) <option> (<examples>)
    E) خيار تاني (اكتبه)
    F) مش عارف

Options must be generated dynamically from context. Never marked as recommended.

## Part D — Vague Answer Protocol
1. Reflect what you understood literally.
2. If "not exactly": split into 2-3 concrete sub-questions.
3. If still vague: offer Options Forcing format.
4. Never interpret "as best you can".

## Part E — "مش عارف" Protocol
Present 3 concrete scenarios. Each shows:
- What it looks like in reality.
- What it implies for the model.

Ask user to pick one, or say "مش عارف" again (then mark pending).
When they pick: record as decided_by = user (guided).

## Part F — Refusal Protocol (3 strikes)
- Strikes 1-2: re-ask simpler with examples.
- Strike 3: present 3 options + recommendation + delegate option.
- If delegated: record as user (delegated).
- Never auto-fill silently.

## Part G — Requirements Inference

For each goal, run the 18-requirement catalog internally.
6 groups: Data, Decision, Outputs, Success, Constraints, Errors.

Each requirement classified as:
- Confirmed (user said it) -> show for quick confirmation.
- Needs question -> ask.
- Not applicable -> skip.

Display grouped under each goal. Shared requirements shown once.

## Part H — Conflict Handling
If a requirement contradicts a goal:
- STOP.
- Consult with 3 options: change goal / change requirement / pause.
- Never silently adjust the goal.

## Part I — Sufficiency Gate (Exit)

- [ ] All 11 items confirmed or delegated.
- [ ] Item 5 precise (what, unit, moment).
- [ ] Item 4 has measurable business metric + target + timeframe.
- [ ] Item 7 states which error is worse.
- [ ] Item 6 gives volume + location.
- [ ] Item 10 states required speed.
- [ ] Every item in Decision Ledger.
- [ ] User explicitly approved REQUIREMENTS.md.

If any check fails: do not write the file. Return to the loop.

## Part J — Hard Rules

1. One question at a time (after funnel).
2. Reflect every answer before confirming.
3. Never write REQUIREMENTS.md before the gate passes.
4. Never state a decision before the user picked it.
5. Never use ML terms unless the user used them first.
6. Always precede consultations with a "why now" line.
7. When in doubt, ask.
