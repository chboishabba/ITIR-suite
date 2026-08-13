"""Make `import sb` work from monorepo root.

Python imports `sitecustomize` automatically at startup if it can be found on
`sys.path`. When running from the ITIR-suite repo root, `""` (CWD) is on
`sys.path`, so this file is importable and can adjust `sys.path` early.

This keeps the repo in a simple "src lives in subdir" shape without requiring
packaging for basic `python -m sb...` usage.
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
_SB_ROOT = _ROOT / "StatiBaker"

if _SB_ROOT.is_dir():
    sb_root_str = str(_SB_ROOT)
    if sb_root_str not in sys.path:
        sys.path.insert(0, sb_root_str)
