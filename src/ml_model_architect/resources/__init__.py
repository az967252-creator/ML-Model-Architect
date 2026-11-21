"""
Package resources for ml_model_architect.
Provides safe resource resolution using importlib.resources.
"""

from __future__ import annotations

import sys
from pathlib import Path
from importlib import resources


def get_resource_text(name: str) -> str:
    """Read a bundled resource as a UTF-8 string."""
    ref = resources.files("ml_model_architect.resources").joinpath(name)
    return ref.read_text(encoding="utf-8")


def get_resource_path(name: str) -> Path:
    """Get absolute Path to a bundled resource."""
    ref = resources.files("ml_model_architect.resources").joinpath(name)
    return Path(str(ref))
