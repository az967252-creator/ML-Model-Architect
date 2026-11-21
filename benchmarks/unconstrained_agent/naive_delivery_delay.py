"""
Naive unconstrained agent: Delivery delay prediction.
Failure Mode: Preprocessing and Target Data Leakage.
Scales and imputes on full dataset BEFORE train_test_split, leaking test distribution.
"""

import time
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import f1_score


def run_naive_delivery_delay(df: pd.DataFrame) -> dict:
    X = df.drop(columns=["delayed"])
    y = df["delayed"]

    # LEAKAGE BUG: Scaling numerical features before splitting!
    num_cols = ["distance_km", "package_weight_kg", "courier_experience_months"]
    scaler = StandardScaler()
    X_leaked = X.copy()
    X_leaked[num_cols] = scaler.fit_transform(X[num_cols])  # Leaked fit on entire dataset!

    # Dummy encoding
    X_leaked = pd.get_dummies(X_leaked, drop_first=True)

    X_train, X_test, y_train, y_test = train_test_split(
        X_leaked, y, test_size=0.2, random_state=42
    )

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
    test_f1 = float(f1_score(y_test, preds))

    return {
        "chosen_model": "Logistic Regression (Leaked Preprocessing)",
        "failure_mode": "Data Leakage (StandardScaler fitted across full dataset before split)",
        "test_f1": round(test_f1, 4),
        "fit_time_ms": round(fit_time_ms, 2),
        "p99_latency_ms": round(p99_latency_ms, 2),
        "data_leakage": True,
        "violated_rule": "G1 / Stage 3 Leakage Gate (Missing Pipeline Boundary)",
    }
