# Decision Ledger — Financial Anomaly Detection

| # | Stage | Type | Question | Options | Chosen | Reason | Reference | decided_by | Date |
|---|-------|------|----------|---------|--------|--------|-----------|------------|------|
| 1 | 1 | framing | What is the target? | A) Fraud > $100 B) Fraud > $1000 | A | Catch small frauds before they escalate into systematic losses. | N/A (Business context) | user | 2026-11-04 |
| 2 | 1 | framing | Which error is worse? | A) False Positive B) False Negative | B | Blocking a valid transaction is annoying, but letting fraud through costs money. | N/A (Business context) | user | 2026-11-04 |
| 3 | 2 | technique | Which algorithm family? | A) Isolation Forest B) Autoencoder | A | High speed required for real-time transactions. | 10.1109/ICDM.2008.17 @ Sec 3 | user | 2026-11-04 |
| 4 | 3 | parameter | Contamination parameter? | A) 0.01 B) 0.05 C) 0.1 | A | We expect very few anomalies in baseline data (<1%). | 10.1109/ICDM.2008.17 @ Sec 4 | user (guided) | 2026-11-04 |

<!-- MANIFEST_SHA256: a7d9188a2b2fa8e3ba952c41e2bd55711aa9b4f03982c66467188acf4118a70f -->
