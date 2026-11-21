# Decision Ledger — Telecom Churn

| # | Stage | Type | Question | Options | Chosen | Reason | Reference | decided_by | Date |
|---|-------|------|----------|---------|--------|--------|-----------|------------|------|
| 1 | 1 | framing | What is the business target? | A) Churn in 30 days B) Downgrade tier | A | Churn directly drives customer lifetime revenue loss. | N/A (Business context) | user | 2026-11-09 |
| 2 | 1 | framing | Which error is worse? | A) False Positive B) False Negative | B | Missing a churner loses entire customer; sending unnecessary discount is cheap. | N/A (Business context) | user | 2026-11-09 |
| 3 | 2 | technique | Which algorithm family? | A) Linear B) Gradient Boosting | B | Data contains non-linear interactions between tenure and billing charges. | 10.1145/2939672.2939785 @ Sec 3.1 | user | 2026-11-09 |
| 4 | 3 | parameter | What is tree max_depth? | A) 3 B) 6 C) 10 | A | Prevents overfitting on moderate sample size. | 10.1145/2939672.2939785 @ Sec 4.1 | user (guided) | 2026-11-09 |
| 5 | 4 | evaluation | Which evaluation metric? | A) F1 B) ROC-AUC | A | F1 balances precision and recall on imbalanced churn dataset. | 10.1186/1471-2105-7-91 @ Sec 2 | user | 2026-11-09 |

<!-- MANIFEST_SHA256: 9290124e608f5f07df686588595d7c2b5d585319d3656645abda287cf7589d7c -->
