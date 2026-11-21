#!/usr/bin/env python3
"""Thin compatibility shim delegating to ml_model_architect.cli."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ml_model_architect.cli import main

if __name__ == "__main__":
    sys.exit(main())
