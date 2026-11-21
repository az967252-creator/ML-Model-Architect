# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0-rc.2] - 2026-11-21

### Added
- **Packaging & `src/` Layout**:
  - Restructured architecture into standard `src/ml_model_architect/` package layout.
  - Added unified `mla` CLI with `init`, `scan`, `verify`, `status`, `lock`, `enforce`, and `verify-dois` subcommands.
  - Added `mla init <project_name>` scaffolding command with automatic cryptographic plan locking.
  - Integrated `importlib.resources` for bundled constitutions, templates, schemas, and catalog references.
- **Empirical Benchmarks & Unconstrained Agent Baselines**:
  - Added `benchmarks/run_benchmarks.py` evaluating 4 end-to-end tasks with latency tracking via `time.perf_counter()`.
  - Added `benchmarks/unconstrained_agent/` demonstrating real failure modes (data leakage, 1-SE violations, imbalanced metric collapse).
  - Added `scripts/render_benchmark_md.py` auto-generating `BENCHMARK.md` verified by test suites.
- **Reference Catalog Expansion & Two-Tier Source Governance**:
  - Populated all 12 reference catalogs (`ref-01` to `ref-12`) with verified claims, source DOIs, locators, and statuses.
  - Guaranteed $\ge 2$ verified references per catalog group.
  - Added `scripts/lint_references.py` enforcing anchor citations or `(heuristic)` tags on all hyperparameters.
  - Formalized Tier A (primary academic peer-reviewed) vs. Tier B (trusted industry engineering for operational patterns).
- **Secondary Tools Hardening**:
  - Grounded `scripts/executive_summary.py` on real project artifacts and metrics.
  - Hardened `scripts/pre_mortem.py` with multi-scenario failure mode analysis and constitutional mitigations.
  - Validated Mermaid syntax generator in `scripts/generate_diagram.py`.
  - Added fail-closed `--deep` LLM evaluation mode in `scripts/red_team.py`.
  - Renamed `scripts/verify_references.py` to `scripts/pdf_to_markdown.py`.
- **Expanded Test Coverage**:
  - Expanded test suite from 79 to 137 tests (plus 32 subtests) across 15 test modules.

### Security & Compliance
- **AST Scanner Tripwire & Sandbox Containment**:
  - Fail-closed execution on missing or empty sandbox directories.
  - Blocked dynamic eval (`pd.eval`, `DataFrame.eval`, `DataFrame.query`), `ctypeslib`, `fetch_*`, `read_clipboard`, star-imports, unbounded loops, non-literal paths, and out-of-bounds writes.
  - Docker container hardened with `--pids-limit 100`, `--security-opt no-new-privileges`, `--user 1000`, 600s wall-clock timeout, and separate writable output mount.
  - Clarified AST scan as a tripwire and Docker as the isolation boundary in documentation.
- **Policy Engine & Ledger Enforcement**:
  - AST verification for single scikit-learn Pipeline construction and pre-split data leakage detection.
  - Strict schema validation for `metrics.json`.
  - Closed decision taxonomy with minimum character length checks and `--max-heuristic-ratio` thresholds.
  - Removed agent `--unlock` CLI option without explicit `MLA_ALLOW_UNLOCK=1` guard.
- **DOI Verification**:
  - Removed `verify=False` and warning suppression; derived peer review from Crossref/DataCite metadata registries.

## [1.0.0-rc.1] - 2026-11-20

### Added
- **Deterministic Run Policy & Immutable Plan (Constitution Part G)**:
  - Added `_shared/TEMPLATE-PLAN-MANIFEST.json` for deterministic execution DAGs with strict pre-conditions and post-assertions.
  - Added `scripts/lock_plan.py` for SHA-256 cryptographic locking and OS read-only permission enforcement.
  - Added `scripts/run_policy.py` for evaluating assertion predicates (`ast_scanner_passed`, `is_single_sklearn_pipeline`, `cv_folds_logged`, `assert_1se_rule_applied`).
  - Added unit test suite `tests/test_run_policy.py` covering plan locking, integrity verification, and tamper detection.
- **Streamlit Dashboard (`app.py`)**:
  - Interactive dashboard visualizing decision ledgers, training reports, pre-mortem analysis, and Rigor Score metrics.
- **Local MCP Knowledge Server (`mcp_server/local_knowledge.py`)**:
  - FastMCP server powered by ChromaDB and Sentence-Transformers for semantic retrieval of verified literature.
- **Model Selection & 1-SE Rule**:
  - Implementation and unit testing for the One Standard Error rule (`test_1se_rule.py`) ensuring parsimonious model selection.
- **Risk Analysis Tools**:
  - Added `scripts/red_team.py` and `scripts/pre_mortem.py` for automated vulnerability and deployment risk reviews.

### Security & Hardening
- **AST Scanner Hardening (`scripts/scan_sandbox.py`)**:
  - Blocked `fromhex` string obfuscation.
  - Blocked untrusted `from-import` statements.
  - Enforced `allow_pickle=False` literal restriction on NumPy calls.
  - Secured file I/O operations against URL or absolute path traversal.
  - Added comprehensive bypass test coverage (`tests/test_scan_sandbox_extra.py`).

## [0.2.0] - 2026-11-04

### Added
- Replaced all fake/blog references in `references_to_verify.yaml` with foundational papers (Breiman, XGBoost, etc.).
- Added `GETTING_STARTED.md` and `CONTRIBUTING.md`.
- Added `enforce_constitution.py` (later renamed).

### Fixed
- Fixed the DOI duplication bug (`10.1145/3767726`).
- Fixed broken Markdown tree in README.

## [0.1.0] - 2026-11-04

### Added
- Initial release with 5 stages (`skills/`), templates (`_shared/`), and the Constitution.
