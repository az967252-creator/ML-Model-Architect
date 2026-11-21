"""
scripts/_allowed.py - Unified source of truth for allowed sandbox packages and imports.
Kept in sync between scripts/scan_sandbox.py and docker/Dockerfile.sandbox.
"""

# Pinned package versions for Dockerfile.sandbox and virtual environments
ALLOWED_PACKAGES = {
    "numpy": "2.2.3",
    "pandas": "2.2.3",
    "scikit-learn": "1.6.1",
    "scipy": "1.15.2",
    "joblib": "1.4.2",
    "xgboost": "2.1.4",
    "lightgbm": "4.6.0",
    "catboost": "1.2.7",
    "matplotlib": "3.10.1",
    "seaborn": "0.13.2",
    "skops": "0.10.0",
    "optuna": "4.2.1",
    "mlflow": "2.20.3",
}

# Module root names permitted for import in the sandbox
ALLOWED_IMPORTS = {
    "numpy",
    "pandas",
    "sklearn",
    "scipy",
    "joblib",
    "xgboost",
    "lightgbm",
    "catboost",
    "matplotlib",
    "seaborn",
    "skops",
    "optuna",
    "mlflow",
    "json",
    "math",
    "statistics",
    "time",
    "datetime",
}
