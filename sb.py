"""Monorepo import shim for the `sb` package.

This repo keeps StatiBaker's Python package at `StatiBaker/sb/`.
Creating a top-level `sb.py` lets `python -m sb.activity.sessionize ...` work
from the monorepo root without requiring packaging or environment variables.

We set `__path__` so Python treats this module as a package root.
"""

from __future__ import annotations

import sys
from pathlib import Path

_PKG_ROOT = Path(__file__).resolve().parent / "StatiBaker" / "sb"

# Allow `import sb.*` to resolve into the real package directory.
__path__ = [str(_PKG_ROOT)]  # type: ignore[name-defined]

# Also ensure direct imports that rely on sys.path work consistently.
_sb_parent = str(_PKG_ROOT.parent)
if _sb_parent not in sys.path:
    sys.path.insert(0, _sb_parent)
