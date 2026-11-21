# Decision Ledger — Car Price Prediction

| # | Stage | Type | Question | Options | Chosen | Reason | Reference | decided_by | Date |
|---|-------|------|----------|---------|--------|--------|-----------|------------|------|
| 1 | 1 | framing | What is the target? | A) Price B) Depreciation Rate | A | Absolute price is the primary business metric. | N/A (Business context) | user | 2026-11-04 |
| 2 | 2 | technique | Which algorithm family? | A) Linear B) Gradient Boosting | B | Data has non-linear interactions (age x mileage). We will validate with CV. | 10.1145/2939672.2939785 @ Sec 3.1 | user | 2026-11-04 |
| 3 | 3 | parameter | What is the max_depth? | A) 3 B) 6 C) 10 | A | To prevent overfitting on moderate sample size. | 10.1145/2939672.2939785 @ Sec 4.1 | user (guided) | 2026-11-04 |
| 4 | 4 | evaluation | Which validation metric? | A) RMSE B) MAE | A | RMSE penalizes large pricing errors heavily in secondary vehicle market. | 10.1007/978-0-387-84858-7 @ Sec 3.2 | user | 2026-11-04 |

<!-- MANIFEST_SHA256: 850aae185d09e14a5550168d21f9c6e63fa6a2733ad50cc3230c0d30c6be201b -->
