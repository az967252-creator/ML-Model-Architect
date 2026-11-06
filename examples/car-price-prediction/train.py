import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
import json
import os

# 1. Generate Synthetic Data with NON-LINEARITY
np.random.seed(42)
n = 1000
data = {
    'age': np.random.randint(1, 15, n),
    'mileage': np.random.randint(10000, 200000, n),
    'engine_size': np.random.uniform(1.0, 4.0, n),
    'brand': np.random.choice(['A', 'B', 'C'], n)
}
df = pd.DataFrame(data)

# TRUE NON-LINEARITY: mileage penalty increases the older the car is (interaction)
interaction_penalty = (df['age'] * df['mileage']) * 0.005
df['price'] = 50000 - (df['age'] * 1500) - (df['mileage'] * 0.1) - interaction_penalty + (df['engine_size'] * 5000) + np.random.normal(0, 2000, n)

# 2. Train/Test Split
X = df.drop('price', axis=1)
y = df['price']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 3. Pipeline with ColumnTransformer (Prevents Leakage)
numeric_features = ['age', 'mileage', 'engine_size']
categorical_features = ['brand']

preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numeric_features),
        ('cat', OneHotEncoder(), categorical_features)
    ])

# 4. Baselines and Models
models = {
    "Linear Regression": Pipeline([
        ('preprocessor', preprocessor),
        ('model', LinearRegression())
    ]),
    "Gradient Boosting": Pipeline([
        ('preprocessor', preprocessor),
        ('model', GradientBoostingRegressor(n_estimators=100, max_depth=3, random_state=42))
    ])
}

results = {}
best_model = None
best_rmse = float('inf')

for name, pipeline in models.items():
    # 5-fold CV
    cv_scores = cross_val_score(pipeline, X_train, y_train, cv=5, scoring='neg_root_mean_squared_error')
    cv_rmse = -cv_scores.mean()
    
    # Fit and Test
    pipeline.fit(X_train, y_train)
    preds = pipeline.predict(X_test)
    test_rmse = np.sqrt(mean_squared_error(y_test, preds))
    
    results[name] = {"cv_rmse": round(cv_rmse, 2), "test_rmse": round(test_rmse, 2)}
    
    # PROPER ML PRACTICE: Model selection must be based on CV score, never on Test score.
    if cv_rmse < best_rmse:
        best_rmse = cv_rmse
        best_model = name

# 5. Output Real Metrics
print(f"Best Model (by CV RMSE): {best_model}")
for name, metrics in results.items():
    print(f"{name} -> CV RMSE: {metrics['cv_rmse']} | Test RMSE: {metrics['test_rmse']}")

# 6. Generate Reports dynamically
report_content = f"""# Training Report — Car Price Prediction

## Configuration
- Group ID: 03
- Seed: 42
- Environment: Python 3.10, scikit-learn 1.2

## Data Preparation
- Preprocessing wrapped inside `ColumnTransformer` within the Pipeline (No Leakage).

## Experiment Results
| Model | CV RMSE | Test RMSE |
|-------|---------|-----------|
| Linear Regression | {results['Linear Regression']['cv_rmse']} | {results['Linear Regression']['test_rmse']} |
| Gradient Boosting | {results['Gradient Boosting']['cv_rmse']} | {results['Gradient Boosting']['test_rmse']} |

**Winning Model:** {best_model} (CV RMSE: {best_rmse:.2f})
"""

with open("TRAINING-REPORT.md", "w", encoding="utf-8") as f:
    f.write(report_content)

with open("metrics.json", "w") as f:
    json.dump(results, f, indent=4)

print("\nReports generated: TRAINING-REPORT.md, metrics.json")
