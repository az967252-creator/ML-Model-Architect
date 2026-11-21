# Decision Ledger — Delivery Delay Prediction

| # | Stage | Type | Question | Options | Chosen | Reason | Reference | decided_by | Date |
|---|-------|------|----------|---------|--------|--------|-----------|------------|------|
| 1 | 1 | framing | What is the target? | A) Delay > 1 day B) Delay > 3 days | A | Covers 90% of business pain and customer inquiries. | N/A (Business context) | user | 2026-11-04 |
| 2 | 1 | framing | Which error is worse? | A) False Positive B) False Negative | A | Sending an apology email for no reason is cheap compared to unexpected delivery delays. | N/A (Business context) | user | 2026-11-04 |
| 3 | 2 | technique | Which algorithm family? | A) Linear B) XGBoost | B | Data is tabular, non-linear, accuracy is prioritized. | 10.1145/2939672.2939785 @ Sec 3.1 | user | 2026-11-04 |
| 4 | 3 | parameter | Max depth for XGBoost? | A) 3 B) 6 C) 10 | B | XGBoost paper recommends 6 for standard tabular. | 10.1145/2939672.2939785 @ Sec 4.1 | user (guided) | 2026-11-04 |

<!-- MANIFEST_SHA256: 848e89f7248daaab2a9f65963c7677cb1e2d8118fd54f5db4388208dac65d576 -->
