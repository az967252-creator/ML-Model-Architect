#!/usr/bin/env python3
"""
Telecom Customer Churn Prediction — Reference Pipeline
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
from sklearn.metrics import f1_score, roc_auc_score

def generate_synthetic_churn_data(n_samples=2000, random_state=42):
    """Generates realistic synthetic telecom subscriber churn data."""
    rng = np.random.RandomState(random_state)
    tenure = rng.randint(1, 72, size=n_samples)
    monthly_charges = rng.uniform(20.0, 120.0, size=n_samples)
    total_charges = tenure * monthly_charges * rng.uniform(0.9, 1.1, size=n_samples)
    contract = rng.choice(["Month-to-month", "One year", "Two year"], size=n_samples, p=[0.55, 0.25, 0.20])
    internet_service = rng.choice(["DSL", "Fiber optic", "No"], size=n_samples, p=[0.4, 0.4, 0.2])

    contract_prob = {"Month-to-month": 0.40, "One year": 0.12, "Two year": 0.03}
    base_prob = np.array([contract_prob[c] for c in contract])
    charge_factor = (monthly_charges - 20.0) / 100.0 * 0.20
    tenure_discount = (tenure / 72.0) * 0.15
    churn_prob = np.clip(base_prob + charge_factor - tenure_discount, 0.02, 0.95)

    churn = rng.binomial(1, churn_prob)

    return pd.DataFrame({
        "tenure": tenure,
        "monthly_charges": monthly_charges,
        "total_charges": total_charges,
        "contract": contract,
        "internet_service": internet_service,
        "churn": churn
    })

def build_pipeline(classifier):
    """Builds a single scikit-learn pipeline to guarantee zero data leakage."""
    num_features = ["tenure", "monthly_charges", "total_charges"]
    cat_features = ["contract", "internet_service"]

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
    print("📞 Telecom Customer Churn — Pipeline & 1-SE Validation")
    print("=" * 60)

    df = generate_synthetic_churn_data()
    X = df.drop(columns=["churn"])
    y = df["churn"]

    # Strict Stratified Train/Test split: 80% train, 20% test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f"Dataset shape: {df.shape} | Churn rate: {y.mean():.2%}")
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    # 1. Baseline: Logistic Regression
    baseline_pipe = build_pipeline(LogisticRegression(max_iter=1000, random_state=42))
    baseline_scores = cross_val_score(baseline_pipe, X_train, y_train, cv=cv, scoring="f1")
    base_mean = baseline_scores.mean()
    base_se = baseline_scores.std() / np.sqrt(len(baseline_scores))
    print(f"\n📊 Baseline (Logistic Regression):")
    print(f"   5-Fold CV F1: {base_mean:.4f} ± {base_se:.4f} (SE)")

    # 2. Candidate: Gradient Boosting
    candidate_pipe = build_pipeline(HistGradientBoostingClassifier(random_state=42))
    candidate_scores = cross_val_score(candidate_pipe, X_train, y_train, cv=cv, scoring="f1")
    cand_mean = candidate_scores.mean()
    cand_se = candidate_scores.std() / np.sqrt(len(candidate_scores))
    print(f"\n🚀 Candidate (Gradient Boosting):")
    print(f"   5-Fold CV F1: {cand_mean:.4f} ± {cand_se:.4f} (SE)")

    # 3. 1-SE Rule Evaluation (Hastie et al. 2009 / Constitution G3)
    print("\n⚖️ 1-SE Model Selection Rule:")
    diff = cand_mean - base_mean
    if diff > cand_se:
        print(f"   ✅ Candidate outperforms Baseline beyond 1-SE threshold (Diff={diff:.4f} > SE={cand_se:.4f}).")
        print("   -> Selecting Candidate (Gradient Boosting).")
        best_pipe = candidate_pipe
    else:
        print(f"   ℹ️ Candidate score within 1-SE of Baseline. Selecting simpler model per Occam's razor.")
        best_pipe = baseline_pipe

    # 4. Final Holdout Evaluation
    best_pipe.fit(X_train, y_train)
    y_pred = best_pipe.predict(X_test)
    y_prob = best_pipe.predict_proba(X_test)[:, 1]
    test_f1 = f1_score(y_test, y_pred)
    test_auc = roc_auc_score(y_test, y_prob)

    print(f"\n🎯 Final Holdout Test F1 Score: {test_f1:.4f} | ROC-AUC: {test_auc:.4f}")
    print("=" * 60)

if __name__ == "__main__":
    main()
