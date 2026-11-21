"""
sandbox/example_task.py - Canonical reference sandbox training task.
Conforms strictly to Constitution Part F (Sandboxed Execution & Allowlist I/O).
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

# 1. Deterministic synthetic data
X = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0], [7.0, 8.0]])
y = np.array([0, 0, 1, 1])

# 2. Fit model
clf = LogisticRegression()
clf.fit(X, y)
score = float(clf.score(X, y))

# 3. Export metrics to allowlisted out directory
df = pd.DataFrame({"model": ["LogisticRegression"], "score": [score]})
df.to_json("sandbox/out/metrics.json")
