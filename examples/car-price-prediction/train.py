import math
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder

# 1. Generate Synthetic Data with NON-LINEARITY
np.random.seed(42)
n = 1000
data = {
    "age": np.random.randint(1, 15, n),
    "mileage": np.random.randint(10000, 200000, n),
    "engine_size": np.random.uniform(1.0, 4.0, n),
    "brand": np.random.choice(["A", "B", "C"], n),
}
df = pd.DataFrame(data)

# TRUE NON-LINEARITY: mileage penalty increases the older the car is (interaction)
interaction_penalty = (df["age"] * df["mileage"]) * 0.005
df["price"] = (
    50000
    - (df["age"] * 1500)
    - (df["mileage"] * 0.1)
    - interaction_penalty
    + (df["engine_size"] * 5000)
    + np.random.normal(0, 2000, n)
)

X = df.drop("price", axis=1)
y = df["price"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

numeric_features = ["age", "mileage", "engine_size"]
categorical_features = ["brand"]

preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), numeric_features),
        ("cat", OneHotEncoder(), categorical_features),
    ]
)

# Single scikit-learn pipeline specification
pipeline = Pipeline([
    ("preprocessor", preprocessor),
    ("model", LinearRegression()),
])

# Fit and evaluate candidate pipeline
cv_scores = cross_val_score(pipeline, X_train, y_train, cv=5, scoring="neg_root_mean_squared_error")
pipeline.fit(X_train, y_train)
preds = pipeline.predict(X_test)
test_rmse = np.sqrt(mean_squared_error(y_test, preds))

print("Linear Regression (Pipeline) -> CV RMSE:", round(-cv_scores.mean(), 2), "Test RMSE:", round(test_rmse, 2))
