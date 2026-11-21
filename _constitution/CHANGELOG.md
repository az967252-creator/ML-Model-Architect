# Constitution Changelog

All notable changes to the ML Model Architect Constitution are documented in this file.

## [1.4.0] - 2026-11-21
- **Rule A1**: Permitted candidate options A/B/C to be generated heuristically during exploration if explicitly tagged with `(heuristic)`, requiring verified grounding for the final adopted decision.
- **Rules B3 & B8**: Formalized two-tier source rigor gate:
  - **Tier A (Rule B3)**: Peer-reviewed primary academic literature (Crossref/DataCite) required for all algorithmic selections, loss functions, and metrics.
  - **Tier B (Rule B8)**: Trusted industry engineering domains (`references/trusted_domains.yaml`) permitted exclusively for operational/deployment patterns (Canary, Shadow, drift monitoring).
- **Rule Numbering & Monotonic Organization**:
  - Enforced strict monotonic rule numbering across all 7 parts: A1–A5, B1–B9, C1–C6, D1–D5, E1, F1–F5, G1–G4 (total 35 formal governance rules).
  - Part C: Moved C6 (Red Team Token Economics) into Part C.
  - Part D: Numbered stage transition gates as explicit rules D1–D5.
  - Part E: Formalized violation handling protocol as explicit rule E1.
  - Part F: Consolidated AST pre-scan and Docker isolation under F4; web content data boundary as F5.

## [1.3.0] - 2026-11-20
- **Part G (Deterministic Execution & Immutable Plan Policy)**: Added G1 (Immutable DAG manifest), G2 (Grounded ReAct loop), G3 (Empirical 1-SE override), G4 (Zero skipped steps).
- **Part F**: Added F4.1 AST pre-scan and C6 token controls.

## [1.2.0] - 2026-11-15
- **Part F**: Added MCP search protocols (F1–F5).
- **Part B**: Added B7 (Empirical Validation) and B8 (Zero-Paywall Whitelist).

## [1.0.0] - 2026-11-04
- Initial formalization of Parts A, B, C, D, E.
