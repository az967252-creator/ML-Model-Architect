# ML Model Architect — Audit Defect Remediation Tracking

This document tracks the remediation of 15 verified engineering and architectural defects in `ML-Model-Architect (v1.0.0rc1)` and subsequent Round 2 hardening items (R1 through R6) in `v1.0.0rc2`.

---

## Round 2 Remediation Summary (rc2)

| Item | Focus Domain | Status | Commit | Primary Files Changed | Proving Tests / Evidence |
|:---:|:---|:---:|:---:|:---|:---|
| **R1** | Single Source of Truth & Clean Wheel | [x] Completed | `afb8133` | `src/ml_model_architect/`, `scripts/*.py`, `pyproject.toml`, `.github/workflows/verify.yml` | `tests/test_cli.py`, CI job `wheel-smoke-test` (isolated venv installation + CLI smoke checks) |
| **R2** | Remove Claims Contradicted by Data | [x] Completed | `9ae1a83` | `benchmarks/results.json`, `docs/BENCHMARK.md`, `README.md`, `scripts/render_benchmark_md.py` | `tests/test_benchmarks.py::TestBenchmarks::test_readme_numbers_match_results_json` |
| **R3** | Dataflow AST Leakage Detector | [x] Completed | `c57b146` | `src/ml_model_architect/policy.py`, `tests/test_run_policy.py` | `tests/test_run_policy.py::TestLeakageDetectorAST` (7 tests: aliases, inline calls, SelectKBest, fillna, target encoding, helpers) |
| **R4** | Ledger & Plan Lock Hardening | [x] Completed | `1ea23c8` | `src/ml_model_architect/enforcer.py`, `src/ml_model_architect/locker.py`, `trusted_domains.yaml` | `tests/test_enforce.py` (locator regex, technical promotion, tier B scoping), `tests/test_run_policy.py` (`verify_plan_git`) |
| **R5** | Scanner Resource Exhaustion / DoS | [x] Completed | `01660c8` | `src/ml_model_architect/scanner.py`, `tests/test_scan_sandbox_extra.py` | `tests/test_scan_sandbox_extra.py::TestDoSAttacks` (sleep, large range, array multiplication, dynamic joblib) |
| **R6** | Test Suite Honesty & Limitations | [x] Completed | `0d5a891` | `tests/test_lock_plan.py`, `docs/BEHAVIORAL_TESTS.md`, `README.md`, `docs/AUDIT-FIXES.md` | `tests/test_lock_plan.py` (9 real unit tests), README Known Limitations honesty disclaimer |

---

## Round 3 Final Polish Summary

| Item | Focus Domain | Status | Primary Files Changed | Proving Tests / Evidence |
|:---:|:---|:---:|:---|:---|
| **1** | README Rigor & Claims | [x] Completed | `README.md` | Rigor matrix removes ungrounded percentages; claims bounded to CI verification; naive scripted baseline nomenclature |
| **2** | Financial Anomaly Parsimony Selection | [x] Completed | `benchmarks/run_benchmarks.py`, `benchmarks/results.json`, `docs/BENCHMARK.md`, `README.md` | When Z-score ties IF (PR-AUC 1.0000), baseline selected per 1-SE rule; `tests/test_benchmarks.py::TestBenchmarks::test_results_json_structure` |
| **3** | Citation Traceability & Verification | [x] Completed | `references/references_to_verify.yaml`, `README.md`, `docs/BENCHMARK.md`, `tests/test_benchmarks.py` | Mapped HistGradientBoosting to Ke et al. (2017), Z-Score to Ruff et al. (2021); `tests/test_benchmarks.py::TestBenchmarks::test_every_cited_reference_in_table_exists_in_yaml` |
| **4** | Unified Latency Measurement & Ranges | [x] Completed | `benchmarks/latency_util.py`, `benchmarks/run_benchmarks.py`, `benchmarks/unconstrained_agent/*.py`, `README.md` | Single `measure_p99_latency_ms` with warm-up cycles; README expresses timing as ranges with host hardware note |
| **5** | Scanner > 1e8 & While Loop Bounding | [x] Completed | `src/ml_model_architect/scanner.py`, `tests/test_scan_sandbox_extra.py` | Blocks >1e8 in range/arange/zeros/ones/mult; flags non-constant while loops without break/counter; `tests/test_scan_sandbox_extra.py` (4 passed, 51 subtests) |
| **6** | Leakage Detection Tuple & Container Support | [x] Completed | `src/ml_model_architect/policy.py`, `tests/test_run_policy.py` | Unpacks tuples, tracks list/dict-held transformers; `tests/test_run_policy.py` (3 new tests, 27 passed) |
| **7** | Ledger Zero Technical Decisions Guard | [x] Completed | `src/ml_model_architect/enforcer.py`, `src/ml_model_architect/cli.py`, `tests/test_enforce.py` | Exits non-zero on 0 technical decisions unless `--allow-empty`; `tests/test_enforce.py` (34 passed) |
| **8** | CI Hardening & Docker Smoke Job | [x] Completed | `.github/workflows/verify.yml`, `docs/AUDIT-FIXES.md` | Removed `\|\| true` from behavioral runner; added `docker-smoke` job; resolved pending status |

---

## Remediation Status Summary (Round 1 & Round 2)

| Issue # | Component / Domain | Phase | Status | Target Description | Verifying Test / Reference |
|:---:|:---|:---:|:---:|:---|:---|
| **1** | Enforcement Engine | Phase 2a / R3 | [x] Completed | Real AST policy assertions, single-pipeline check, metrics.json schema validation, dataflow leakage AST visitor | [test_run_policy.py:L14](file:///tests/test_run_policy.py#L14) |
| **2** | Sandbox Scanner | Phase 1 / R5 | [x] Completed | Fail-closed scanner, comprehensive AST bypass defenses, allowlist-by-function, resource exhaustion bounds | [test_scan_sandbox_extra.py:L1](file:///tests/test_scan_sandbox_extra.py#L1) |
| **3** | Docker Sandbox | Phase 1 | [x] Completed | Pinned dependencies, `_allowed.py` shared sync, runtime security flags (`--pids-limit`, `--read-only`, `--network none`) | `docker/Dockerfile.sandbox`, `scripts/run_docker_sandbox.py` |
| **4** | Decision Ledger | Phase 2b / R4 | [x] Completed | Closed type taxonomy, reason length check (>=20 chars), `--max-heuristic-ratio`, strict DOI locators, Tier B scoping | [test_enforce.py:L14](file:///tests/test_enforce.py#L14) |
| **5** | Plan Lock Engine | Phase 2c / R4 / R6 | [x] Completed | Cryptographic plan locking, CRLF invariance, git-anchored tamper verification (`--verify-git`), real unit tests | [test_lock_plan.py:L1](file:///tests/test_lock_plan.py#L1) |
| **6** | DOI Verification | Phase 2d | [x] Completed | Remove verify=False, derive peer review from registry, 365d exception expiry, strict CI retry | [test_verify.py:L1](file:///tests/test_verify.py#L1), [test_verify_dois_extra.py:L1](file:///tests/test_verify_dois_extra.py#L1) |
| **7** | Empirical Benchmarks | Phase 5 / R2 | [x] Completed | Real OpenML benchmark runner, measured p99 latency & fit times, results.json parity check | [test_benchmarks.py:L14](file:///tests/test_benchmarks.py#L14) |
| **8** | Reference Examples | Phase 5 / R2 | [x] Completed | Naive baseline comparison, model naming consistency (HistGradientBoosting), dynamic evaluation reports | [test_enforce.py:L310](file:///tests/test_enforce.py#L310) |
| **9** | Reference Catalog | Phase 4a | [x] Completed | Non-empty catalog claims, >=2 refs per group, sourced hyperparameters, lint script | `scripts/lint_references.py`, [test_docs_consistency.py:L1](file:///tests/test_docs_consistency.py#L1) |
| **10** | Decision Tree Scope | Phase 4b | [x] Completed | Preprocessing Level 1 task, explicit tabular/time-series scope bounding | `references/stage-02-technique-selection/` |
| **11** | Security Claims | Phase 1 / R6 | [x] Completed | Clarify AST tripwire vs. Docker isolation boundary in README, honest threat model | [README.md:L686](file:///README.md#L686) |
| **12** | Constitution Alignment | Phase 4c / R4 | [x] Completed | A1 vs Skill 2 suggested options, B3/B8 Tier A/B source governance, 35 monotonic rules | [test_docs_consistency.py:L40](file:///tests/test_docs_consistency.py#L40) |
| **13** | Test Suite & CI | Phase 3 / R6 | [x] Completed | Behavioral scenario harness, modular 1-SE rule, pinned CI actions, Python 3.11-3.13 matrix | [test_1se_rule.py:L1](file:///tests/test_1se_rule.py#L1), [test_evaluator_logic.py:L1](file:///tests/test_evaluator_logic.py#L1) |
| **14** | Secondary Tooling | Phase 6 | [x] Completed | Hardened executive_summary, pre_mortem, generate_diagram, red_team, app.py, local_knowledge | [test_tools.py:L1](file:///tests/test_tools.py#L1) |
| **15** | Package Restructuring | Phase 7 / R1 | [x] Completed | `src/ml_model_architect/`, importlib.resources, `mla init`, clean venv wheel smoke test | [test_cli.py:L1](file:///tests/test_cli.py#L1) |

---

## Detailed Round 2 Execution Log

### Item R1: Single Source of Truth + Working Wheel
- **Problem**: 8 duplicate modules in `scripts/` diverged from `src/ml_model_architect/`. Wheel missing skills/references package data.
- **Remediation**:
  1. Converted all `scripts/*.py` into transparent 1-line forwarding shims importing from `src.ml_model_architect.*`.
  2. Fixed all internal imports to package-relative in `src/ml_model_architect/`.
  3. Packaged skills, references, templates, and constitution into `src/ml_model_architect/resources/` via `package_data` and `MANIFEST.in`.
  4. Added `wheel-smoke-test` job in `.github/workflows/verify.yml` building wheel and verifying `mla --version`, `mla init`, `mla scan`, `mla enforce`, and `mla status` in a clean virtual environment without repo on `sys.path`.
- **Commit**: `afb8133`
- **Proving Test**: `tests/test_cli.py` (6 passed).

### Item R2: Remove Claims Contradicted by Data
- **Problem**: README claimed "85% lower latency" and "85% compute overhead" without measurement. Labeled baseline "Unconstrained LLM Agent" when it was scripted. Oracle contamination in IsolationForest.
- **Remediation**:
  1. Replaced ungrounded percentages with measured fit-times (8.1ms vs 138.1ms) and p99 latencies (5.1ms vs 5.7ms).
  2. Renamed baseline to "Naive scripted baseline" throughout `results.json`, `BENCHMARK.md`, and `README.md`.
  3. Replaced "zero loss in generalization" with exact holdout RMSE delta ($\Delta = 108.57$).
  4. Changed `IsolationForest(contamination=0.03)` to `contamination='auto'` and reported PR-AUC (1.0000) and ROC-AUC (1.0000) honestly.
  5. Deleted redundant root `BENCHMARK.md` (preserved canonical `docs/BENCHMARK.md`).
  6. Fixed "XGBoost" delivery delay typo to "HistGradientBoosting".
- **Commit**: `9ae1a83`
- **Proving Test**: `tests/test_benchmarks.py::TestBenchmarks::test_readme_numbers_match_results_json` (PASSED).

### Item R3: Dataflow AST Leakage Detector
- **Problem**: Leakage checker used fragile string matching that missed aliases (`import ... as RS`), inline instantiations (`StandardScaler().fit_transform(X)`), and pandas pre-split statistics.
- **Remediation**:
  1. Implemented dataflow AST visitor tracking transformer instances across variable assignments, aliased imports, and inline calls.
  2. Flagged pre-split `.fit()` and `.fit_transform()` before `train_test_split`.
  3. Flagged pandas `.fillna(mean/median)`, `.groupby().transform()`, and manual standardization `(X - X.mean()) / X.std()`.
  4. Scanned helper functions defined in the script for isolated leakage operations.
  5. Softened doc wording to "static leakage heuristics".
- **Commit**: `c57b146`
- **Proving Test**: `tests/test_run_policy.py::TestLeakageDetectorAST` (7 tests, all PASSED).

### Item R4: Ledger & Lock Hardening
- **Problem**: Locators accepted any string with `@`. Non-technical rows mentioning algorithms bypassed technical reference rules. Local plan locks were vulnerable to silent tampering.
- **Remediation**:
  1. Required strict locator regex `(?:Sec|Section|p\.|page|Table|Fig|Figure|Eq|Theorem)\b` in `enforcer.py`.
  2. If `data`, `framing`, or `other` rows mention algorithms, models, hyperparameters, or metrics, they are promoted to technical decisions and required to have peer-reviewed literature citations.
  3. Scoped `trusted_domains.yaml` to `tier: B`: rejected for `technique`, `parameter`, `metric` and allowed only for `deployment` and `threshold`.
  4. Added `verify_plan(..., check_git=True)` comparing lock hash to `git show HEAD:<manifest_rel_path>`.
  5. Added git-verified plan lock step in `.github/workflows/verify.yml`.
- **Commit**: `1ea23c8`
- **Proving Test**: `tests/test_enforce.py` (3 new tests) & `tests/test_run_policy.py::TestLockPlan::test_verify_plan_git_committed` (all PASSED).

### Item R5: Scanner DoS Residuals
- **Problem**: Static scanner did not guard against CPU/memory exhaustion attacks (large `range()`, unbounded list multiplication, long `sleep()`, dynamic model deserialization).
- **Remediation**:
  1. Flagged `time.sleep()` with non-literal or literal > 10s.
  2. Flagged `range()` / `np.arange()` with literal > 10**7.
  3. Flagged list/array multiplication `[...] * N` with factor > 10**8.
  4. Flagged non-literal path arguments in `joblib.load()` and `skops.io.load()`.
  5. Clarified that static AST is a tripwire, and Docker container isolation is the true execution boundary.
- **Commit**: `01660c8`
- **Proving Test**: `tests/test_scan_sandbox_extra.py::TestDoSAttacks` (6 test methods, 44 subtests, all PASSED).

### Item R6: Test Suite Honesty & Limitations
- **Problem**: `tests/test_lock_plan.py` only subclassed tests from another file without own tests. Behavioral test table was empty. README lacked explicit per-check limitation disclaimers.
- **Remediation**:
  1. Converted `tests/test_lock_plan.py` into 9 independent unit tests covering CRLF invariance, lock creation, tampering, deletion, schema errors, and unlock authorization.
  2. Completed sign-off table in `docs/BEHAVIORAL_TESTS.md` and added automated scheduled run step in `.github/workflows/verify.yml` with API key secrets.
  3. Expanded `README.md` "Known Limitations and Threat Model" documenting exact operational boundaries of the AST scanner, leakage heuristics, plan locking, ledger enforcer, and DOI verifier.
- **Commit**: In progress (R6)
- **Proving Test**: `tests/test_lock_plan.py` (9 tests, all PASSED), `tests/test_evaluator_logic.py` (8 scenarios, all PASSED).
