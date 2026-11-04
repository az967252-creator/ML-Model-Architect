# Decision Ledger — Car Price Prediction

| # | Stage | Type | Question | Options | Chosen | Reason | Reference | decided_by | Date |
|---|-------|------|----------|---------|--------|--------|-----------|------------|------|
| 1 | 1 | framing | What is the target? | A) Price B) Depreciation Rate | A | Absolute price is the primary business metric. | N/A (Business context) | user | 2026-11-04 |
| 2 | 2 | technique | Which algorithm family? | A) Linear B) Gradient Boosting | B | Data has non-linear interactions (age x mileage). | 10.1145/2939672.2939785 | user | 2026-11-04 |
| 3 | 3 | parameter | What is the max_depth? | A) 3 B) 6 C) 10 | A | To prevent overfitting on small synthetic data. | 10.1145/2939672.2939785 | user (guided) | 2026-11-04 |
