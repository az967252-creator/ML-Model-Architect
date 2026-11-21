#!/usr/bin/env python3
"""
Financial Anomaly Detection — Reference Implementation
Stage 3 & 4 Isolation Forest vs Statistical Baseline with Leak-Free Pipeline.
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import IsolationForest
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler
from sklearn.metrics import classification_report, roc_auc_score, precision_recall_fscore_support, average_precision_score

def generate_financial_transactions(n_samples=3000, contamination=0.03, random_state=42):
    """Generates synthetic banking transaction stream with subtle anomalies."""
    rng = np.random.RandomState(random_state)
    n_anomalies = int(n_samples * contamination)
    n_normal = n_samples - n_anomalies

    # Normal transactions: typical spending
    normal_amounts = rng.lognormal(mean=3.5, sigma=0.8, size=n_normal)
    normal_hour = rng.normal(loc=14, scale=3, size=n_normal) % 24
    normal_freq = rng.poisson(lam=2, size=n_normal)

    # Anomalies: sudden spikes, abnormal hours, rapid transaction burst
    fraud_amounts = rng.uniform(low=800, high=5000, size=n_anomalies)
    fraud_hour = rng.uniform(low=1, high=4, size=n_anomalies)
    fraud_freq = rng.poisson(lam=12, size=n_anomalies)

    amounts = np.concatenate([normal_amounts, fraud_amounts])
    hours = np.concatenate([normal_hour, fraud_hour])
    freqs = np.concatenate([normal_freq, fraud_freq])
    labels = np.array([0] * n_normal + [1] * n_anomalies)

    # Shuffle
    indices = rng.permutation(n_samples)
    df = pd.DataFrame({
        "amount": amounts[indices],
        "hour_of_day": hours[indices],
        "daily_txn_freq": freqs[indices],
        "is_fraud": labels[indices]
    })
    return df

def main():
    print("=" * 60)
    print("💳 Financial Anomaly Detection — Isolation Forest vs Baseline")
    print("=" * 60)

    df = generate_financial_transactions()
    X = df.drop(columns=["is_fraud"])
    y = df["is_fraud"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    print(f"Transactions: {df.shape[0]} | Contamination: {y.mean():.2%}")

    # 1. Baseline: Statistical Z-Score on transaction amount
    print("\n📊 Baseline: Univariate Z-Score Threshold (|z| > 3.0)")
    mean_val = X_train["amount"].mean()
    std_val = X_train["amount"].std()
    z_scores_test = np.abs((X_test["amount"] - mean_val) / std_val)
    baseline_pred = (z_scores_test > 3.0).astype(int)
    p_b, r_b, f1_b, _ = precision_recall_fscore_support(y_test, baseline_pred, average="binary", zero_division=0)
    pr_auc_b = float(average_precision_score(y_test, z_scores_test))
    roc_b = float(roc_auc_score(y_test, z_scores_test))
    print(f"   Baseline F1: {f1_b:.4f} | Precision: {p_b:.4f} | Recall: {r_b:.4f} | PR-AUC: {pr_auc_b:.4f} | ROC-AUC: {roc_b:.4f}")

    # 2. Candidate: Multivariate Isolation Forest in single Pipeline
    print("\n🌲 Candidate: Isolation Forest with RobustScaler Pipeline")
    pipeline = Pipeline([
        ("scaler", RobustScaler()),
        ("detector", IsolationForest(n_estimators=100, contamination="auto", random_state=42))
    ])

    pipeline.fit(X_train)
    # IsolationForest returns -1 for outlier, 1 for inlier
    raw_pred = pipeline.predict(X_test)
    candidate_pred = (raw_pred == -1).astype(int)
    scores = -pipeline.decision_function(X_test)

    p_c, r_c, f1_c, _ = precision_recall_fscore_support(y_test, candidate_pred, average="binary", zero_division=0)
    roc_c = float(roc_auc_score(y_test, scores))
    pr_auc_c = float(average_precision_score(y_test, scores))
    print(f"   Candidate F1: {f1_c:.4f} | Precision: {p_c:.4f} | Recall: {r_c:.4f} | PR-AUC: {pr_auc_c:.4f} | ROC-AUC: {roc_c:.4f}")

    # 3. Decision (Parsimony Rule: Baseline wins ties on PR-AUC within 1e-3)
    print("\n⚖️ Empirical Evaluation Decision:")
    diff_pr = pr_auc_c - pr_auc_b
    if diff_pr <= 1e-3:
        print(f"   Baseline Selected: Z-Score PR-AUC ({pr_auc_b:.4f}) ties IF ({pr_auc_c:.4f}); simpler baseline chosen per 1-SE parsimony")
        print("   -> Selecting Baseline: Statistical Z-Score (|z| > 3.0).")
    else:
        print(f"   Candidate Selected: Isolation Forest PR-AUC ({pr_auc_c:.4f}) exceeds baseline ({pr_auc_b:.4f}) by > 1e-3")
        print("   -> Selecting Candidate: Isolation Forest.")

    print("=" * 60)

if __name__ == "__main__":
    main()
