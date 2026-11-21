"""
benchmarks/latency_util.py - Unified inference latency measurement utility.

Provides a single standard measurement function with warm-up cycles and single-sample
batching for both MLA pipelines and naive baseline models.
"""

import time
from typing import Any
import numpy as np


def measure_p99_latency_ms(model_or_fn: Any, X_sample: Any, n_repeats: int = 100, warm_up: int = 10) -> float:
    """Measure 99th percentile single-sample inference latency in milliseconds with warm-up."""
    predict_fn = model_or_fn.predict if hasattr(model_or_fn, "predict") else model_or_fn
    for _ in range(warm_up):
        _ = predict_fn(X_sample)
    latencies = []
    for _ in range(n_repeats):
        t0 = time.perf_counter()
        _ = predict_fn(X_sample)
        latencies.append((time.perf_counter() - t0) * 1000)
    return float(np.percentile(latencies, 99))
