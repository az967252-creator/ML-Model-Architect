---
group_id: "11"
name: "Anomaly Detection"
---

> ⚠️ **WARNING: This file is a summary/index.**
> You MUST use your MCP search tools to read the actual paper before making a decision.
> See CONSTITUTION Part F.

# Evaluation — Anomaly Detection

## 1. Metrics
Precision, Recall, F1, AUPRC, AUC-PR

## 2. Validation Protocol
Time-based split if temporal. AUC-PR over ROC.

## 3. Problem Catalog
- IF fails on complex | Autoencoder
- High false negatives | Hybrid
- Unlabeled anomalies | Unsupervised AE
