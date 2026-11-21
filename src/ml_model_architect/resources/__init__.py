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


def copy_resource_tree(resource_subpath: str, target_dir: Path) -> None:
    """Recursively copy a bundled resource directory tree to a target directory."""
    ref = resources.files("ml_model_architect.resources").joinpath(resource_subpath)
    target_dir.mkdir(parents=True, exist_ok=True)
    for item in ref.iterdir():
        if item.name.startswith("__pycache__") or item.name.endswith(".pyc"):
            continue
        dest = target_dir / item.name
        if item.is_dir():
            copy_resource_tree(f"{resource_subpath}/{item.name}", dest)
        else:
            dest.write_bytes(item.read_bytes())

