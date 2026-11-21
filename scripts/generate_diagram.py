#!/usr/bin/env python3
"""Thin compatibility shim delegating to ml_model_architect.tools.diagram."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import ml_model_architect.tools.diagram as _impl

# Transparent proxying for direct imports and unittest.mock patching
sys.modules[__name__] = _impl

if __name__ == "__main__":
    if hasattr(_impl, "main"):
        sys.exit(_impl.main())
