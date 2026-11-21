"""
Naive scripted baseline: Telecom customer churn.
Failure Mode: Preprocessing leakage across cross-validation folds.
Imputes and scales data before CV loop, producing over-optimistic evaluation.
"""

import time
import numpy as np
import pandas as pd
from sklearn.model_selection import KFold, cross_val_score
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import f1_score


def measure_p99_latency_ms(model, sample, n_repeats: int = 100) -> float:
    latencies = []
    for _ in range(n_repeats):
        t_start = time.perf_counter()
        _ = model.predict(sample)
        latencies.append((time.perf_counter() - t_start) * 1000)
    return float(np.percentile(latencies, 99))


def run_naive_churn(df: pd.DataFrame) -> dict:
    X = df.drop(columns=["churn"])
    y = df["churn"]

    # One-hot encode without ColumnTransformer
    X_num = X[["tenure", "monthly_charges", "total_charges"]]
    X_cat = pd.get_dummies(X[["contract", "internet_service"]], drop_first=True)

    # LEAKAGE: Scaler fit on the full dataset before KFold cross-validation
    scaler = StandardScaler()
    X_num_scaled = pd.DataFrame(scaler.fit_transform(X_num), columns=X_num.columns)
    X_prepared = pd.concat([X_num_scaled, X_cat], axis=1)

    # Standard non-stratified KFold (fails class ratio maintenance)
    kf = KFold(n_splits=5, shuffle=False)
    model = HistGradientBoostingClassifier(random_state=42)

    cv_scores = cross_val_score(model, X_prepared, y, cv=kf, scoring="f1")
    cv_mean = float(cv_scores.mean())
    cv_se = float(cv_scores.std(ddof=1) / np.sqrt(5))

    t0 = time.perf_counter()
    model.fit(X_prepared, y)
    fit_time_ms = (time.perf_counter() - t0) * 1000

    latencies = []
    for _ in range(100):
        sample = X_prepared.iloc[:1]
        t_start = time.perf_counter()
        _ = model.predict(sample)
        latencies.append((time.perf_counter() - t_start) * 1000)
    p99_latency_ms = float(np.percentile(latencies, 99))

    return {
        "chosen_model": "HistGradientBoosting (Non-stratified, Leaked CV)",
        "failure_mode": "Cross-Fold Preprocessing Leakage (Scaler fit before KFold; non-stratified split)",
        "cv_f1": round(cv_mean, 4),
        "cv_se": round(cv_se, 4),
        "fit_time_ms": round(fit_time_ms, 2),
        "p99_latency_ms": round(p99_latency_ms, 2),
        "data_leakage": True,
        "violated_rule": "Stage 4 Evaluation Gate / B7 Empirical Validation",
    }
