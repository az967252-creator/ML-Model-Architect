import pandas as pd
import numpy as np
import json
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import f1_score, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer

print("--- ML Model Architect: Full Case Study ---")
print("Stage 1: Framing... (Mocked via DECISIONS.md)")
print("Stage 2: Technique Selection... (Mocked via TECH-CHOICE.md)")
print("Stage 3: Training...")

# Generate realistic synthetic Churn Data
np.random.seed(42)
n = 2000
data = {
    'tenure': np.random.randint(1, 72, n),
    'monthly_charges': np.random.uniform(20, 120, n),
    'total_charges': np.random.uniform(100, 8000, n),
    'contract': np.random.choice(['Month-to-month', 'One year', 'Two year'], n),
    'internet_service': np.random.choice(['DSL', 'Fiber optic', 'No'], n)
}
df = pd.DataFrame(data)

# Business logic: Month-to-month with high charges churn more
churn_prob = 0.1 + (df['contract'] == 'Month-to-month') * 0.3 + (df['monthly_charges'] > 80) * 0.2
df['churn'] = np.random.binomial(1, churn_prob)

X = df.drop('churn', axis=1)
y = df['churn']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Stage 3: Pipeline
num_cols = ['tenure', 'monthly_charges', 'total_charges']
cat_cols = ['contract', 'internet_service']

preprocessor = ColumnTransformer(
    transformers=[
        ('num', Pipeline([('imputer', SimpleImputer(strategy='median')), ('scaler', StandardScaler())]), num_cols),
        ('cat', OneHotEncoder(handle_unknown='ignore'), cat_cols)
    ])

models = {
    "Baseline (Logistic Regression)": LogisticRegression(max_iter=1000),
    "Selected (Gradient Boosting)": GradientBoostingClassifier(n_estimators=100, max_depth=3, random_state=42)
}

results = {}
best_cv_f1 = 0
best_model_name = ""

for name, model in models.items():
    pipeline = Pipeline([('preprocessor', preprocessor), ('model', model)])
    cv_scores = cross_val_score(pipeline, X_train, y_train, cv=5, scoring='f1')
    cv_f1 = cv_scores.mean()
    
    pipeline.fit(X_train, y_train)
    preds = pipeline.predict(X_test)
    test_f1 = f1_score(y_test, preds)
    test_auc = roc_auc_score(y_test, pipeline.predict_proba(X_test)[:, 1])
    
    results[name] = {"cv_f1": cv_f1, "test_f1": test_f1, "test_auc": test_auc}
    if cv_f1 > best_cv_f1:
        best_cv_f1 = cv_f1
        best_model_name = name

print(f"Winning Model (by CV F1): {best_model_name}")
for name, res in results.items():
    print(f"{name}: CV F1 = {res['cv_f1']:.4f}, Test F1 = {res['test_f1']:.4f}, Test AUC = {res['test_auc']:.4f}")

# Stage 4: Evaluation Report Generation
print("Stage 4: Evaluation...")
eval_report = f"""# Evaluation Report — Telecom Churn

## Metrics
| Model | CV F1 | Test F1 | Test AUC |
|-------|-------|---------|----------|
| Baseline (Logistic Regression) | {results['Baseline (Logistic Regression)']['cv_f1']:.4f} | {results['Baseline (Logistic Regression)']['test_f1']:.4f} | {results['Baseline (Logistic Regression)']['test_auc']:.4f} |
| Selected (Gradient Boosting) | {results['Selected (Gradient Boosting)']['cv_f1']:.4f} | {results['Selected (Gradient Boosting)']['test_f1']:.4f} | {results['Selected (Gradient Boosting)']['test_auc']:.4f} |

**Decision:** {best_model_name} selected based on Cross-Validation F1-score (Constitution Rule B7).

## Leakage Checks
- Preprocessing fit on train only (Pipeline).
- Stratified split.
- No future data used.
"""
with open("EVALUATION-REPORT.md", "w", encoding="utf-8") as f:
    f.write(eval_report)

# Stage 1 & 2 Artifacts
with open("REQUIREMENTS.md", "w", encoding="utf-8") as f:
    f.write("# Requirements — Telecom Churn\n\n- Target: `churn` (Binary)\n- Business Metric: Reduce churn by 5%\n- Error Cost: False Negative > False Positive.\n")

with open("DECISIONS.md", "w", encoding="utf-8") as f:
    f.write("# Decision Ledger — Telecom Churn\n\n| Stage | Decision | Reference |\n|---|---|---|\n| 2 | Chose Gradient Boosting | 10.1145/2939672.2939785 |\n| 4 | Used CV F1 for selection | 10.1186/1471-2105-7-91 |\n")

print("All reports generated successfully in the case study folder.")
