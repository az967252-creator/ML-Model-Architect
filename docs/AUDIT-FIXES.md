# ML Model Architect — Audit Defect Remediation Tracking

This document tracks the remediation of 15 verified engineering and architectural defects in `ML-Model-Architect (v1.0.0rc1)` as part of the `fix/audit-2026-11` audit cycle.

## Remediation Status Summary

| Issue # | Component / Domain | Phase | Status | Target Description |
|:---:|:---|:---:|:---:|:---|
| **1** | Enforcement Engine | Phase 2a | [ ] Pending | Real AST policy assertions, single-pipeline check, metrics.json schema validation |
| **2** | Sandbox Scanner | Phase 1 | [x] Completed | Fail-closed scanner, comprehensive AST bypass defenses, allowlist-by-function |
| **3** | Docker Sandbox | Phase 1 | [x] Completed | Pinned dependencies, `_allowed.py` shared sync, runtime security flags, timeout |
| **4** | Decision Ledger | Phase 2b | [ ] Pending | Closed type taxonomy, reason length check, `--max-heuristic-ratio`, DOI locators |
| **5** | Plan Lock Engine | Phase 2c | [ ] Pending | Remove `--unlock` from agent CLI, ledger manifest hash, default base_dir to manifest dir |
| **6** | DOI Verification | Phase 2d | [ ] Pending | Remove verify=False, derive peer review from registry, 365d exception expiry, strict CI |
| **7** | Empirical Benchmarks | Phase 5 | [ ] Pending | Real OpenML/UCI benchmark script, latency measurements, remove ungrounded claims |
| **8** | Reference Examples | Phase 5 | [ ] Pending | Naive agent comparison, model naming consistency, dynamic evaluation reports |
| **9** | Reference Catalog | Phase 4a | [ ] Pending | Non-empty catalog claims, >=2 refs per group, sourced hyperparameters, lint script |
| **10** | Decision Tree Scope | Phase 4b | [ ] Pending | Preprocessing Level 1 task, explicit tabular/time-series scope bounding |
| **11** | Security Claims | Phase 1 | [x] Completed | Clarify AST tripwire vs. Docker isolation boundary in README and docs |
| **12** | Constitution Alignment | Phase 4c | [ ] Pending | A1 vs Skill 2 suggested options, B3/B8 Tier A/B sources, consistent rule numbering |
| **13** | Test Suite & CI | Phase 3 | [ ] Pending | Behavioral scenario harness, modular 1-SE rule, pinned CI actions, Python 3.11-3.13 matrix |
| **14** | Secondary Tooling | Phase 6 | [ ] Pending | Audit executive_summary, pre_mortem, generate_diagram, red_team, app.py, local_knowledge |
| **15** | Package Restructuring | Phase 7 | [ ] Pending | `src/ml_model_architect/`, importlib.resources, `mla init`, wheel smoke test |

---

## Phase Execution Log

### Phase 0: Baseline Capture
- [x] Baseline test suite captured (`79 passed` via pytest).
- [x] Baseline outputs captured for all 4 reference projects (`car-price`, `delivery-delay`, `financial-anomaly`, `case-study-churn`) and saved to `/tmp/baseline/`.
- [x] Audit tracking document initialized (`docs/AUDIT-FIXES.md`).

### Phase 1: Sandbox & Scanner (Issues 2, 3, 11)
- [x] Fail-closed scanner on missing/empty sandbox directory.
- [x] Argparse CLI support for scanning arbitrary files/directories.
- [x] AST bypass defenses: `eval`, `query`, `ctypeslib`, `fetch_*`, `matplotlib.use`, `read_clipboard`, star-imports, unbounded loops, non-literal paths, write boundary containment.
- [x] Function-level allowlist for I/O operations.
- [x] Bypass tests in `tests/test_scan_sandbox_extra.py`.
- [x] Dockerfile.sandbox pinned dependencies & shared `scripts/_allowed.py`.
- [x] Container security flags (`--pids-limit`, `--security-opt`, `--user`, timeout, read-only mount with separate `out/`).
- [x] Replace "100% Containment" claims in README/BENCHMARK with tripwire vs. isolation boundary distinction.
- [x] Optuna + MLflow pinned in Docker and project extras.

### Phase 2: Enforcement Engine (Issues 1, 4, 5, 6)
- [ ] Phase 2a: Real AST policy assertions in `scripts/run_policy.py` & `_shared/metrics.schema.json`.
- [ ] Phase 2b: Closed ledger taxonomy, reason length, heuristic ratio, and locators in `scripts/enforce_constitution.py`.
- [ ] Phase 2c: Cryptographic plan locking hardening in `scripts/lock_plan.py`.
- [ ] Phase 2d: DOI verification rigor in `scripts/verify_dois.py`.

### Phase 3: Tests & CI Modernization (Issue 13, CI part of 12)
- [ ] Behavioral evaluation harness (`tests/behavioral/run_scenarios.py`).
- [ ] Modular 1-SE rule in `scripts/model_selection.py`.
- [ ] Split requirements files (`requirements.txt`, `requirements-mcp.txt`, `requirements-dashboard.txt`).
- [ ] Commit-SHA pinned GitHub Actions & Dependabot configuration.
- [ ] CI matrix for Python 3.11, 3.12, 3.13 (`requires-python >=3.11`).
- [ ] SOTA workflow fix with 30-day cutoff and PR guard.

### Phase 4: References, Decision Tree & Constitution (Issues 9, 10, 12)
- [ ] Populate `references/catalog/` with verified claims and locators.
- [ ] Sourced hyperparameter ranges and `scripts/lint_references.py`.
- [ ] Stage 2 Decision Tree Level-1 Preprocessing & scope bounding.
- [ ] Two-tier source governance (Tier A vs. Tier B) in `trusted_domains.yaml`.
- [ ] Renumber constitutional articles and synchronize `scripts/count_rules.py`.

### Phase 5: Empirical Benchmarks & Examples (Issues 7, 8)
- [ ] Public dataset benchmark runner (`benchmarks/run_benchmarks.py`).
- [ ] Honest latency measurement and `benchmarks/results.json`.
- [ ] Scripted naive baseline comparison (`benchmarks/unconstrained_agent/`).
- [ ] Auto-rendered benchmark tables (`scripts/render_benchmark_md.py`).
- [ ] Updated `examples/DISCLAIMER.md` and dynamic evaluation reports.

### Phase 6: Secondary Tools Hardening (Issue 14)
- [ ] Hardened `executive_summary.py`, `pre_mortem.py`, `generate_diagram.py`, `red_team.py`.
- [ ] Streamlit dashboard rigor score alignment in `app.py`.
- [ ] MCP local knowledge indexing in `mcp_server/local_knowledge.py`.
- [ ] Rename `scripts/verify_references.py` to `scripts/pdf_to_markdown.py`.

### Phase 7: Packaging & Developer Experience (Issue 15)
- [ ] Restructure into `src/ml_model_architect/` package layout.
- [ ] Resource resolution via `importlib.resources`.
- [ ] `mla init <project>` scaffolding command.
- [ ] Wheel distribution build, validation, and smoke tests.

### Phase 8: Documentation Sync & Verification
- [ ] Synchronize README, GETTING_STARTED, CHANGELOG (`v1.0.0-rc.2`).
- [ ] Full test suite, benchmark suite, and bypass verification execution.
- [ ] Final remediation verification matrix.
