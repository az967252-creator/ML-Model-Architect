#!/usr/bin/env python3
"""
Delivery Delay Prediction — Reference Implementation
Stage 3 & 4 Training and Evaluation with Zero Data Leakage and 1-SE Rule.
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.metrics import f1_score, classification_report

def generate_synthetic_delivery_data(n_samples=2000, random_state=42):
    """Generates synthetic delivery logistics data."""
    rng = np.random.RandomState(random_state)
    distance_km = rng.exponential(scale=10.0, size=n_samples) + 1.0
    package_weight_kg = rng.gamma(shape=2.0, scale=2.5, size=n_samples)
    traffic_level = rng.choice(["low", "medium", "high", "congested"], size=n_samples, p=[0.4, 0.3, 0.2, 0.1])
    weather = rng.choice(["clear", "rain", "storm"], size=n_samples, p=[0.7, 0.2, 0.1])
    courier_experience_months = rng.randint(1, 60, size=n_samples)

    # Delay probability based on physical features
    traffic_mult = {"low": 1.0, "medium": 1.5, "high": 2.2, "congested": 3.5}
    weather_mult = {"clear": 1.0, "rain": 1.6, "storm": 2.8}

    traffic_factor = np.array([traffic_mult[t] for t in traffic_level])
    weather_factor = np.array([weather_mult[w] for w in weather])

    base_time = (distance_km * 3.0 * traffic_factor * weather_factor) - (courier_experience_months * 0.2)
    # Binary target: Delay > 45 minutes
    delay = (base_time > 45.0).astype(int)

    df = pd.DataFrame({
        "distance_km": distance_km,
        "package_weight_kg": package_weight_kg,
        "traffic_level": traffic_level,
        "weather": weather,
        "courier_experience_months": courier_experience_months,
        "delayed": delay
    })
    return df

def build_pipeline(classifier):
    """Builds a single scikit-learn pipeline to guarantee zero data leakage."""
    num_features = ["distance_km", "package_weight_kg", "courier_experience_months"]
    cat_features = ["traffic_level", "weather"]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", Pipeline([
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler())
            ]), num_features),
            ("cat", Pipeline([
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
            ]), cat_features)
        ]
    )

    return Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", classifier)
    ])

def main():
    print("=" * 60)
    print("🚚 Delivery Delay Prediction — Pipeline & 1-SE Validation")
    print("=" * 60)

    df = generate_synthetic_delivery_data()
    X = df.drop(columns=["delayed"])
    y = df["delayed"]

    # Strict Train/Test split: 80% train, 20% test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f"Dataset shape: {df.shape} | Churn/Delay rate: {y.mean():.2%}")
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    # 1. Baseline: Logistic Regression
    baseline_pipe = build_pipeline(LogisticRegression(max_iter=1000, random_state=42))
    baseline_scores = cross_val_score(baseline_pipe, X_train, y_train, cv=cv, scoring="f1")
    base_mean = baseline_scores.mean()
    base_se = baseline_scores.std() / np.sqrt(len(baseline_scores))
    print(f"\n📊 Baseline (Logistic Regression):")
    print(f"   5-Fold CV F1: {base_mean:.4f} ± {base_se:.4f} (SE)")

    # 2. Candidate: Gradient Boosting (HistGradientBoosting)
    candidate_pipe = build_pipeline(HistGradientBoostingClassifier(random_state=42))
    candidate_scores = cross_val_score(candidate_pipe, X_train, y_train, cv=cv, scoring="f1")
    cand_mean = candidate_scores.mean()
    cand_se = candidate_scores.std() / np.sqrt(len(candidate_scores))
    print(f"\n🚀 Candidate (Gradient Boosting):")
    print(f"   5-Fold CV F1: {cand_mean:.4f} ± {cand_se:.4f} (SE)")

    # 3. 1-SE Rule Evaluation (Constitution Rule B7 / Stage 2 Exit)
    print("\n⚖️ 1-SE Model Selection Rule:")
    diff = cand_mean - base_mean
    if diff > cand_se:
        print(f"   ✅ Candidate outperforms Baseline beyond 1-SE threshold (Diff={diff:.4f} > SE={cand_se:.4f}).")
        print("   -> Selecting Candidate (Gradient Boosting).")
        best_pipe = candidate_pipe
    else:
        print(f"   ℹ️ Candidate within 1-SE of Baseline. Selecting simpler model per Occam's razor.")
        best_pipe = baseline_pipe

    # 4. Final Holdout Evaluation
    best_pipe.fit(X_train, y_train)
    y_pred = best_pipe.predict(X_test)
    test_f1 = f1_score(y_test, y_pred)
    print(f"\n🎯 Final Holdout Test F1 Score: {test_f1:.4f}")
    print("=" * 60)

if __name__ == "__main__":
    main()
