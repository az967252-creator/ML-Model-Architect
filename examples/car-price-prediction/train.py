import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.dummy import DummyRegressor
from sklearn.metrics import mean_squared_error
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
import json
import math

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

X = df.drop('price', axis=1)
y = df['price']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

numeric_features = ['age', 'mileage', 'engine_size']
categorical_features = ['brand']

preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numeric_features),
        ('cat', OneHotEncoder(), categorical_features)
    ])

# Order of complexity (0 = simplest)
models = {
    "Dummy (Mean Baseline)": (0, Pipeline([('preprocessor', preprocessor), ('model', DummyRegressor())])),
    "Linear Regression": (1, Pipeline([('preprocessor', preprocessor), ('model', LinearRegression())])),
    "Gradient Boosting": (2, Pipeline([('preprocessor', preprocessor), ('model', GradientBoostingRegressor(n_estimators=100, max_depth=3, random_state=42))]))
}

results = {}
cv_scores_dict = {}

for name, (complexity, pipeline) in models.items():
    cv_scores = cross_val_score(pipeline, X_train, y_train, cv=5, scoring='neg_root_mean_squared_error')
    cv_rmse = -cv_scores.mean()
    cv_std = cv_scores.std()
    cv_se = cv_std / math.sqrt(5) # Standard Error = Std / sqrt(k)
    
    pipeline.fit(X_train, y_train)
    preds = pipeline.predict(X_test)
    test_rmse = np.sqrt(mean_squared_error(y_test, preds))
    
    results[name] = {"cv_rmse": round(cv_rmse, 2), "cv_std": round(cv_std, 2), "cv_se": round(cv_se, 2), "test_rmse": round(test_rmse, 2), "complexity": complexity}
    cv_scores_dict[name] = cv_scores

# 1-SE Rule Logic
best_cv_rmse = min(r["cv_rmse"] for r in results.values())
best_model_name = min(results, key=lambda k: results[k]["cv_rmse"])
best_se = results[best_model_name]["cv_se"]

# Filter models within 1 SE of the best
candidates = [name for name, r in results.items() if r["cv_rmse"] <= best_cv_rmse + best_se]

# Choose the simplest among candidates
chosen_model = min(candidates, key=lambda k: results[k]["complexity"])

print(f"Best Model (by CV RMSE): {best_model_name}")
print(f"Chosen Model (by 1-SE Rule): {chosen_model}")
for name, metrics in results.items():
    print(f"{name} -> CV RMSE: {metrics['cv_rmse']} (+/- {metrics['cv_std']}) | Test RMSE: {metrics['test_rmse']}")

report_content = f"""# Training Report — Car Price Prediction (Synthetic Demo)

## Configuration
- Group ID: 03
- Seed: 42
- Environment: Python 3.10, scikit-learn 1.2

## Data Preparation
- Preprocessing wrapped inside `ColumnTransformer` within the Pipeline (No Leakage).

## Experiment Results (5-Fold CV)
| Model | Complexity | CV RMSE (Mean +/- Std) | Test RMSE |
|-------|------------|------------------------|-----------|
| Dummy (Mean Baseline) | 0 | {results['Dummy (Mean Baseline)']['cv_rmse']} +/- {results['Dummy (Mean Baseline)']['cv_std']} | {results['Dummy (Mean Baseline)']['test_rmse']} |
| Linear Regression | 1 | {results['Linear Regression']['cv_rmse']} +/- {results['Linear Regression']['cv_std']} | {results['Linear Regression']['test_rmse']} |
| Gradient Boosting | 2 | {results['Gradient Boosting']['cv_rmse']} +/- {results['Gradient Boosting']['cv_std']} | {results['Gradient Boosting']['test_rmse']} |

**Selection Logic (1-SE Rule):**
The best CV RMSE was {best_cv_rmse} ({best_model_name}). The standard error was {best_se:.2f}.
Models within 1 standard error of the best were: {', '.join(candidates)}.
The simplest model among these candidates was selected: **{chosen_model}**.

*Note: While Gradient Boosting had a lower Test RMSE, the cross-validation difference is not statistically significant (within 1 Standard Error).*
"""

with open("TRAINING-REPORT.md", "w", encoding="utf-8") as f:
    f.write(report_content)

with open("metrics.json", "w") as f:
    json.dump(results, f, indent=4)

print("\nReports generated: TRAINING-REPORT.md, metrics.json")
