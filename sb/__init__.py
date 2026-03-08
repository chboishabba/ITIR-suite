"""Monorepo import shim for StatiBaker.

Allows `import sb` from the ITIR-suite repo root without installing a package.

Implementation detail: we expose StatiBaker's `sb` package by using its
`__path__`, so submodules like `sb.activity.sessionize` resolve normally.
"""

from __future__ import annotations

import importlib
import sys

_real = importlib.import_module("StatiBaker.sb")

# Make `import sb.activity...` work by adopting the real package's namespace.
__path__ = _real.__path__  # type: ignore[name-defined]
__package__ = "sb"

# Preserve usual module identity expectations.
sys.modules[__name__] = _real
