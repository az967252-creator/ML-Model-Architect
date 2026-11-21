"""
ML Model Architect - A strict, reference-driven framework for disciplined ML engineering.
"""

from .__version__ import __version__
from .model_selection import select_1se_model, compute_1se_from_folds
from .locker import lock_plan, verify_plan, unlock_plan
from .policy import PolicyEngine
from .scanner import scan_file, scan_directory
from .enforcer import enforce as enforce_constitution

__all__ = [
    "__version__",
    "select_1se_model",
    "compute_1se_from_folds",
    "lock_plan",
    "verify_plan",
    "unlock_plan",
    "PolicyEngine",
    "scan_file",
    "scan_directory",
    "enforce_constitution",
]
