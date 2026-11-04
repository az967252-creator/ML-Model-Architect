import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import json

# 1. Generate Synthetic Data
np.random.seed(42)
n = 1000
data = {
    'age': np.random.randint(1, 15, n),
    'mileage': np.random.randint(10000, 200000, n),
    'engine_size': np.random.uniform(1.0, 4.0, n),
    'brand': np.random.choice(['A', 'B', 'C'], n)
}
df = pd.DataFrame(data)
df['price'] = 50000 - (df['age'] * 1500) - (df['mileage'] * 0.1) + (df['engine_size'] * 5000) + np.random.normal(0, 2000, n)
df = pd.get_dummies(df, columns=['brand'], drop_first=True)

X = df.drop('price', axis=1)
y = df['price']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 2. Pipeline (As per Constitution B1)
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('model', GradientBoostingRegressor(n_estimators=100, max_depth=3, random_state=42))
])

pipeline.fit(X_train, y_train)
preds = pipeline.predict(X_test)
rmse = np.sqrt(mean_squared_error(y_test, preds))

print(f"Model trained successfully. RMSE: {rmse:.2f}")
