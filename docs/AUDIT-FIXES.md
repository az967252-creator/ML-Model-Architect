# ML Model Architect — Audit Defect Remediation Tracking

This document tracks the remediation of 15 verified engineering and architectural defects in `ML-Model-Architect (v1.0.0rc1)` as part of the `fix/audit-2026-11` audit cycle.

## Remediation Status Summary

| Issue # | Component / Domain | Phase | Status | Target Description |
|:---:|:---|:---:|:---:|:---|
| **1** | Enforcement Engine | Phase 2a | [x] Completed | Real AST policy assertions, single-pipeline check, metrics.json schema validation |
| **2** | Sandbox Scanner | Phase 1 | [x] Completed | Fail-closed scanner, comprehensive AST bypass defenses, allowlist-by-function |
| **3** | Docker Sandbox | Phase 1 | [x] Completed | Pinned dependencies, `_allowed.py` shared sync, runtime security flags, timeout |
| **4** | Decision Ledger | Phase 2b | [x] Completed | Closed type taxonomy, reason length check, `--max-heuristic-ratio`, DOI locators |
| **5** | Plan Lock Engine | Phase 2c | [x] Completed | Remove `--unlock` from agent CLI, ledger manifest hash, default base_dir to manifest dir |
| **6** | DOI Verification | Phase 2d | [x] Completed | Remove verify=False, derive peer review from registry, 365d exception expiry, strict CI |
| **7** | Empirical Benchmarks | Phase 5 | [x] Completed | Real OpenML/UCI benchmark script, latency measurements, remove ungrounded claims |
| **8** | Reference Examples | Phase 5 | [x] Completed | Naive agent comparison, model naming consistency, dynamic evaluation reports |
| **9** | Reference Catalog | Phase 4a | [x] Completed | Non-empty catalog claims, >=2 refs per group, sourced hyperparameters, lint script |
| **10** | Decision Tree Scope | Phase 4b | [x] Completed | Preprocessing Level 1 task, explicit tabular/time-series scope bounding |
| **11** | Security Claims | Phase 1 | [x] Completed | Clarify AST tripwire vs. Docker isolation boundary in README and docs |
| **12** | Constitution Alignment | Phase 4c | [x] Completed | A1 vs Skill 2 suggested options, B3/B8 Tier A/B sources, consistent rule numbering |
| **13** | Test Suite & CI | Phase 3 | [x] Completed | Behavioral scenario harness, modular 1-SE rule, pinned CI actions, Python 3.11-3.13 matrix |
| **14** | Secondary Tooling | Phase 6 | [x] Completed | Audit executive_summary, pre_mortem, generate_diagram, red_team, app.py, local_knowledge |
| **15** | Package Restructuring | Phase 7 | [x] Completed | `src/ml_model_architect/`, importlib.resources, `mla init`, wheel smoke test |

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
- [x] Phase 2a: Real AST policy assertions in `scripts/run_policy.py` & `_shared/metrics.schema.json`.
- [x] Phase 2b: Closed ledger taxonomy, reason length, heuristic ratio, and locators in `scripts/enforce_constitution.py`.
- [x] Phase 2c: Cryptographic plan locking hardening in `scripts/lock_plan.py`.
- [x] Phase 2d: DOI verification rigor in `scripts/verify_dois.py`.

### Phase 3: Tests & CI Modernization (Issue 13, CI part of 12)
- [x] Behavioral evaluation harness (`tests/behavioral/run_scenarios.py`).
- [x] Modular 1-SE rule in `scripts/model_selection.py`.
- [x] Split requirements files (`requirements.txt`, `requirements-mcp.txt`, `requirements-dashboard.txt`).
- [x] Commit-SHA pinned GitHub Actions & Dependabot configuration.
- [x] CI matrix for Python 3.11, 3.12, 3.13 (`requires-python >=3.11`).
- [x] SOTA workflow fix with 30-day cutoff and PR guard.

### Phase 4: References, Decision Tree & Constitution (Issues 9, 10, 12)
- [x] Populate `references/catalog/` with verified claims and locators.
- [x] Sourced hyperparameter ranges and `scripts/lint_references.py`.
- [x] Stage 2 Decision Tree Level-1 Preprocessing & scope bounding.
- [x] Two-tier source governance (Tier A vs. Tier B) in `trusted_domains.yaml`.
- [x] Renumber constitutional articles and synchronize `scripts/count_rules.py`.

### Phase 5: Empirical Benchmarks & Examples (Issues 7, 8)
- [x] Public dataset benchmark runner (`benchmarks/run_benchmarks.py`).
- [x] Honest latency measurement and `benchmarks/results.json`.
- [x] Scripted naive baseline comparison (`benchmarks/unconstrained_agent/`).
- [x] Auto-rendered benchmark tables (`scripts/render_benchmark_md.py`).
- [x] Updated `examples/DISCLAIMER.md` and dynamic evaluation reports.

### Phase 6: Secondary Tools Hardening (Issue 14)
- [x] Hardened `executive_summary.py`, `pre_mortem.py`, `generate_diagram.py`, `red_team.py`.
- [x] Streamlit dashboard error handling & relative paths in `app.py`.
- [x] MCP local knowledge indexing & fallback in `mcp_server/local_knowledge.py`.
- [x] Renamed `scripts/verify_references.py` to `scripts/pdf_to_markdown.py`.
- [x] Comprehensive test coverage in `tests/test_tools.py`.

### Phase 7: Packaging & Developer Experience (Issue 15)
- [x] Restructure into `src/ml_model_architect/` package layout.
- [x] Resource resolution via `importlib.resources`.
- [x] `mla init <project>` scaffolding command.
- [x] Wheel distribution build, validation, and smoke tests.
- [x] Backward-compatibility CLI and script shims.

### Phase 8: Documentation Sync & Verification
- [x] Synchronize README, GETTING_STARTED, CHANGELOG (`v1.0.0-rc.2`).
- [x] Full test suite, benchmark suite, and bypass verification execution.
- [x] Final remediation verification matrix.
