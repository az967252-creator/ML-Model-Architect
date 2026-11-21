"""
Naive unconstrained agent: Car price regression.
Failure Mode: Premature complexity adoption without 1-SE validation.
Directly selects Gradient Boosting, incurring 6.7x higher latency with worse CV RMSE.
"""

import time
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.metrics import root_mean_squared_error


def run_naive_car_price(df: pd.DataFrame) -> dict:
    X = df.drop("price", axis=1)
    y = df["price"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Naive agent directly builds complex Gradient Boosting model without testing parsimony
    preprocessor = ColumnTransformer([
        ("num", StandardScaler(), ["age", "mileage", "engine_size"]),
        ("cat", OneHotEncoder(drop="first"), ["brand"]),
    ])

    X_train_trans = preprocessor.fit_transform(X_train)
    X_test_trans = preprocessor.transform(X_test)

    model = GradientBoostingRegressor(n_estimators=100, max_depth=3, random_state=42)

    # Measure CV
    cv_scores = cross_val_score(model, X_train_trans, y_train, cv=5, scoring="neg_root_mean_squared_error")
    cv_rmse = float(-cv_scores.mean())
    cv_se = float(cv_scores.std(ddof=1) / np.sqrt(5))

    # Fit and measure latency
    t0 = time.perf_counter()
    model.fit(X_train_trans, y_train)
    fit_time_ms = (time.perf_counter() - t0) * 1000

    # Latency p99 over 100 predictions
    latencies = []
    for _ in range(100):
        sample = X_test_trans[:1]
        t_start = time.perf_counter()
        _ = model.predict(sample)
        latencies.append((time.perf_counter() - t_start) * 1000)
    p99_latency_ms = float(np.percentile(latencies, 99))

    preds = model.predict(X_test_trans)
    test_rmse = float(root_mean_squared_error(y_test, preds))

    return {
        "chosen_model": "Gradient Boosting Regressor",
        "failure_mode": "Overfitting & Complexity Penalty (ignored 1-SE rule; Linear is simpler and better on CV)",
        "cv_rmse": round(cv_rmse, 2),
        "cv_se": round(cv_se, 2),
        "test_rmse": round(test_rmse, 2),
        "fit_time_ms": round(fit_time_ms, 2),
        "p99_latency_ms": round(p99_latency_ms, 2),
        "data_leakage": False,
        "violated_rule": "G3 (Empirical 1-SE Override)",
    }
