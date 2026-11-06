# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - 2026-11-04

### Added
- **Case Study:** Added `examples/case-study-churn/` with a real ML pipeline using Cross-Validation.
- **Benchmark:** Added `BENCHMARK.md` showing the measurable difference (0 questions vs 7) between standard AI and the framework.
- **CI/CD:** Added `.github/workflows/verify.yml` to run DOI verification on every push.
- **Tests:** Added `test_skills.py` (structural integrity) and `test_verify.py` (mocked API tests).
- **OSS Standards:** Added `SECURITY.md`, `CODE_OF_CONDUCT.md`, and `CHANGELOG.md`.

### Changed
- **Philosophy:** Replaced "The Reference Is the Judge" with "The Reference guides, the Experiment decides" (Rule B7).

- **Reference Validator:** Refactored `verify_dois.py` to use Crossref and DataCite fallbacks, checking titles and years.

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
