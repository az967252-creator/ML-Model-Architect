"""
Naive unconstrained agent: Financial anomaly detection.
Failure Mode: Metric Misalignment on Imbalanced Data.
Optimizes standard Accuracy with supervised classifier on 3% imbalanced data, predicting all normal.
"""

import time
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_recall_fscore_support


def run_naive_anomaly(df: pd.DataFrame) -> dict:
    X = df.drop(columns=["is_fraud"])
    y = df["is_fraud"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42
    )

    # Supervised model optimizing accuracy without class re-weighting
    model = LogisticRegression(max_iter=1000, random_state=42)

    t0 = time.perf_counter()
    model.fit(X_train, y_train)
    fit_time_ms = (time.perf_counter() - t0) * 1000

    latencies = []
    for _ in range(100):
        sample = X_test.iloc[:1]
        t_start = time.perf_counter()
        _ = model.predict(sample)
        latencies.append((time.perf_counter() - t_start) * 1000)
    p99_latency_ms = float(np.percentile(latencies, 99))

    preds = model.predict(X_test)
    acc = float(accuracy_score(y_test, preds))
    prec, rec, f1, _ = precision_recall_fscore_support(y_test, preds, average="binary", zero_division=0)

    return {
        "chosen_model": "Logistic Regression (Accuracy Metric)",
        "failure_mode": "Metric Misalignment (97% accuracy achieved by predicting 'normal', missing anomalies)",
        "accuracy": round(acc, 4),
        "precision": round(float(prec), 4),
        "recall": round(float(rec), 4),
        "f1_score": round(float(f1), 4),
        "fit_time_ms": round(fit_time_ms, 2),
        "p99_latency_ms": round(p99_latency_ms, 2),
        "data_leakage": False,
        "violated_rule": "B1 / Stage 1 Framing Gate (Imbalanced metric selection)",
    }
