# Changelog

All notable changes to this project will be documented in this file.

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
