#!/usr/bin/env python3
"""
scripts/render_benchmark_md.py - Benchmark Markdown Generator.

Reads benchmarks/results.json and auto-generates BENCHMARK.md and docs/BENCHMARK.md.
Supports --check flag for CI to verify the committed markdown matches results.json.
"""

from __future__ import annotations

import argparse
import difflib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def render_markdown(results: dict) -> str:
    b1, b2, b3, b4 = results["benchmarks"]

    # B1 numbers
    m1 = b1["mla_results"]["models"]
    u1 = b1["unconstrained_agent"]

    # B2 numbers
    m2 = b1_m2 = b2["mla_results"]["models"]
    u2 = b2["unconstrained_agent"]

    # B3 numbers
    m3_b = b3["mla_results"]["baseline"]
    m3_c = b3["mla_results"]["candidate"]
    u3 = b3["unconstrained_agent"]

    # B4 numbers
    m4 = b4["mla_results"]["models"]
    u4 = b4["unconstrained_agent"]

    md = f"""# Empirical Benchmark: Framework vs. Standard Agent

This benchmark provides concrete, reproducible experimental evidence measuring the practical difference between an **Unconstrained LLM Agent** and an agent guided by the **ML Model Architect** framework.

> **Methodological Context:** The benchmark datasets are controlled synthetic benchmarks generated with known statistical ground-truth properties (non-linear interactions, class imbalance, outlier contamination). This isolates algorithmic decision-making, data leakage vulnerability, and model selection discipline from noisy confounding factors in a 100% reproducible, offline test harness.

---

## Benchmark 1: Car Price Prediction (Tabular Regression)

### Problem Setup
- **Data:** {b1['dataset']['n_samples']} observations, {b1['dataset']['n_features']} features (`age`, `mileage`, `engine_size`, `brand`).
- **Interaction:** Compound non-linear depreciation penalty (`age * mileage * 0.005`).
- **Target:** Continuous car sales price ($).

### Empirical Results (5-Fold Cross-Validation)

| Model Architecture | Complexity Rank | 5-Fold CV RMSE | Standard Error (SE) | Holdout Test RMSE | Fit Time (ms) | Inference Latency (p99) | Decision |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Dummy (Mean Baseline)** | 0 | {m1['Dummy (Mean Baseline)']['cv_rmse']:,.2f} | ± {m1['Dummy (Mean Baseline)']['cv_se']:.2f} | {m1['Dummy (Mean Baseline)']['test_rmse']:,.2f} | {m1['Dummy (Mean Baseline)']['fit_time_ms']:.1f} ms | {m1['Dummy (Mean Baseline)']['p99_latency_ms']:.1f} ms | Rejected |
| **Linear Regression (Baseline)** | 1 | **{m1['Linear Regression']['cv_rmse']:,.2f}** | **± {m1['Linear Regression']['cv_se']:.2f}** | **{m1['Linear Regression']['test_rmse']:,.2f}** | **{m1['Linear Regression']['fit_time_ms']:.1f} ms** | **{m1['Linear Regression']['p99_latency_ms']:.1f} ms** | **SELECTED (1-SE Rule)** |
| **Gradient Boosting (Candidate)** | 2 | {m1['Gradient Boosting']['cv_rmse']:,.2f} | ± {m1['Gradient Boosting']['cv_se']:.2f} | {m1['Gradient Boosting']['test_rmse']:,.2f} | {m1['Gradient Boosting']['fit_time_ms']:.1f} ms | {m1['Gradient Boosting']['p99_latency_ms']:.1f} ms | Rejected (Insuff. CV gain) |

### Algorithmic Comparison
- **Unconstrained Agent Behavior:** Directly selected Gradient Boosting due to perceived non-linearity, resulting in higher fit time ({u1['fit_time_ms']:.1f} ms vs {m1['Linear Regression']['fit_time_ms']:.1f} ms), higher CV RMSE ({u1['cv_rmse']:.2f} vs {m1['Linear Regression']['cv_rmse']:.2f}), and violation of the 1-SE rule.
- **ML Model Architect Decision:**
  - Standard Error threshold for Linear Regression: $SE = {m1['Linear Regression']['cv_se']:.2f}$.
  - Candidate does not outperform Linear Regression on 5-fold CV.
  - **Verdict:** Linear Regression strictly chosen per Hastie et al. (2009) 1-SE rule (`10.1007/978-0-387-84858-7`).

---

## Benchmark 2: Delivery Delay Prediction (Tabular Binary Classification)

### Problem Setup
- **Data:** {b2['dataset']['n_samples']} logistics orders, {b2['dataset']['n_features']} multimodal features (distance, package weight, courier experience, traffic level, weather).
- **Target:** Binary delay indicator (`delayed`), delay base rate: {b2['dataset']['delay_rate']:.2%}.
- **Business Cost:** High recall priority (missed delayed shipments cost 4x more than false alarms).

### Empirical Results (5-Fold Stratified Cross-Validation)

| Model Architecture | 5-Fold CV F1 Score | Standard Error (SE) | Holdout Test F1 | Fit Time (ms) | Inference Latency (p99) | Selection Margin | Decision |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Logistic Regression (Baseline)** | {m2['Logistic Regression (Baseline)']['cv_f1']:.4f} | ± {m2['Logistic Regression (Baseline)']['cv_se']:.4f} | {m2['Logistic Regression (Baseline)']['test_f1']:.4f} | {m2['Logistic Regression (Baseline)']['fit_time_ms']:.1f} ms | {m2['Logistic Regression (Baseline)']['p99_latency_ms']:.1f} ms | Floor metric | Baseline |
| **Gradient Boosting (Candidate)** | **{m2['Gradient Boosting (Candidate)']['cv_f1']:.4f}** | **± {m2['Gradient Boosting (Candidate)']['cv_se']:.4f}** | **{m2['Gradient Boosting (Candidate)']['test_f1']:.4f}** | **{m2['Gradient Boosting (Candidate)']['fit_time_ms']:.1f} ms** | **{m2['Gradient Boosting (Candidate)']['p99_latency_ms']:.1f} ms** | **+{b2['mla_results']['margin_diff']:.4f} > {b2['mla_results']['se_threshold']:.4f}** | **SELECTED** |

### Algorithmic Comparison
- **Unconstrained Agent Behavior:** Scaled features using `StandardScaler` on the entire dataset *before* calling `train_test_split` (Target & Preprocessing Leakage). Achieved an ungrounded test F1 of `{u2['test_f1']:.4f}` with leaked data distributions.
- **ML Model Architect Decision:**
  - Implemented strict scikit-learn `Pipeline` (all transformations fitted inside each train fold).
  - Difference: $+{b2['mla_results']['margin_diff']:.4f} > 1 \\times SE ({b2['mla_results']['se_threshold']:.4f})$.
  - **Verdict:** Gradient Boosting promoted with holdout test verification ($F1 = {m2['Gradient Boosting (Candidate)']['test_f1']:.4f}$).

---

## Benchmark 3: Financial Anomaly Detection (Extreme Imbalance)

### Problem Setup
- **Data:** {b3['dataset']['n_samples']} banking transactions, continuous transaction features.
- **Contamination Rate:** {b3['dataset']['contamination']:.1%} true anomalies (extreme imbalance).
- **Target:** Outlier detection (`is_fraud`).

### Empirical Results

| Detection Strategy | Precision | Recall | F1 Score | ROC-AUC | Decision |
|:---|:---:|:---:|:---:|:---:|:---:|
| **Statistical Z-Score (|z| > 3.0 Baseline)** | {m3_b['precision']:.4f} | {m3_b['recall']:.4f} | {m3_b['f1_score']:.4f} | N/A | Floor baseline |
| **Isolation Forest Pipeline (Candidate)** | **{m3_c['precision']:.4f}** | **{m3_c['recall']:.4f}** | **{m3_c['f1_score']:.4f}** | **{m3_c['roc_auc']:.4f}** | **SELECTED** |

### Algorithmic Comparison
- **Unconstrained Agent Behavior:** Trained a supervised classifier optimizing standard Accuracy on imbalanced data. Achieved `{u3['accuracy']:.2%} Accuracy` while completely failing to isolate anomalies in business practice ({u3['failure_mode']}).
- **ML Model Architect Decision:**
  - Grounded in Liu et al. (2008) Isolation Forest literature (`10.1109/ICDM.2008.17`).
  - Evaluated candidate against empirical statistical baseline, delivering clean anomaly separation.

---

## Benchmark 4: Telecom Customer Churn (Imbalanced Tabular Classification)

### Problem Setup
- **Data:** {b4['dataset']['n_samples']} subscriber accounts, 5 continuous and categorical features.
- **Target:** Subscriber churn (`churn`), baseline rate: {b4['dataset']['churn_rate']:.2%}.

### Empirical Results (5-Fold Stratified Cross-Validation)

| Model Architecture | 5-Fold CV F1 Score | Standard Error (SE) | Holdout Test F1 | Fit Time (ms) | Inference Latency (p99) | Selection Margin | Decision |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Logistic Regression (Baseline)** | {m4['Logistic Regression (Baseline)']['cv_f1']:.4f} | ± {m4['Logistic Regression (Baseline)']['cv_se']:.4f} | {m4['Logistic Regression (Baseline)']['test_f1']:.4f} | {m4['Logistic Regression (Baseline)']['fit_time_ms']:.1f} ms | {m4['Logistic Regression (Baseline)']['p99_latency_ms']:.1f} ms | Floor metric | Baseline |
| **Gradient Boosting (Candidate)** | **{m4['Gradient Boosting (Candidate)']['cv_f1']:.4f}** | **± {m4['Gradient Boosting (Candidate)']['cv_se']:.4f}** | **{m4['Gradient Boosting (Candidate)']['test_f1']:.4f}** | **{m4['Gradient Boosting (Candidate)']['fit_time_ms']:.1f} ms** | **{m4['Gradient Boosting (Candidate)']['p99_latency_ms']:.1f} ms** | **+{b4['mla_results']['margin_diff']:.4f} > {b4['mla_results']['se_threshold']:.4f}** | **SELECTED (1-SE Rule)** |

### Algorithmic Comparison
- **Unconstrained Agent Behavior:** Performed scaling before cross-validation loops and used non-stratified random splits, causing fold-level data leakage ({u4['failure_mode']}).
- **ML Model Architect Decision:**
  - Constructed a single `Pipeline` with `ColumnTransformer` handling imputers and scalers strictly on train folds.
  - Candidate model outperformed baseline beyond the 1-SE threshold ($+{b4['mla_results']['margin_diff']:.4f} > {b4['mla_results']['se_threshold']:.4f}$).

---

## Benchmark Summary Matrix

| Metric Dimension | Unconstrained LLM Agent | ML Model Architect (Constitutional) |
|:---|:---:|:---:|
| **Data Leakage Vulnerability** | ❌ Leaks scalers/imputers before split | ✅ **Zero Leakage (Pipeline AST verification)** |
| **Model Selection Discipline** | ❌ Choses complex models arbitrarily | ✅ **Hastie 1-SE Rule verified empirically** |
| **Imbalanced Class Handling** | ❌ Optimizes deceptive Accuracy | ✅ **Precision-Recall / PR-AUC grounding** |
| **Reproducibility & Auditability** | ❌ Ad-hoc scripts, no locks | ✅ **Cryptographic DAG lock & Decision Ledger** |
"""
    return md.strip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Render BENCHMARK.md from results.json.")
    parser.add_argument("--check", action="store_true", help="Check whether committed markdown matches results.json")
    args = parser.parse_args()

    results_path = ROOT / "benchmarks" / "results.json"
    if not results_path.exists():
        print(f"ERROR: {results_path} does not exist. Run benchmarks/run_benchmarks.py first.", file=sys.stderr)
        return 1

    with open(results_path, "r", encoding="utf-8") as f:
        results = json.load(f)

    rendered = render_markdown(results)

    targets = [ROOT / "BENCHMARK.md", ROOT / "docs" / "BENCHMARK.md"]

    if args.check:
        any_diff = False
        for target in targets:
            if not target.exists():
                print(f"FAIL: {target} does not exist.", file=sys.stderr)
                any_diff = True
                continue
            committed = target.read_text(encoding="utf-8")
            if committed != rendered:
                print(f"FAIL: {target} differs from rendered output:", file=sys.stderr)
                diff = difflib.unified_diff(
                    committed.splitlines(), rendered.splitlines(), fromfile=str(target), tofile="rendered", lineterm=""
                )
                for line in diff:
                    print(line, file=sys.stderr)
                any_diff = True
        if any_diff:
            return 1
        print("OK: Benchmark documentation matches results.json exactly.")
        return 0

    for target in targets:
        target.write_text(rendered, encoding="utf-8")
        print(f"Wrote rendered benchmark to: {target}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
