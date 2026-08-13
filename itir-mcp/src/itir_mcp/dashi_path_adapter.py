from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .pnf_numeric_abi import cpu_gemv, validate_numeric_abi


def resolve_dashicore_path(base: Path | None = None) -> Path | None:
    env_path = os.environ.get("ITIR_DASHICORE_PATH")
    candidates = []
    if env_path:
        candidates.append(Path(env_path).expanduser())
    root = base or Path(__file__).resolve().parents[3]
    candidates.append((root / "../dashiCORE").resolve())
    for path in candidates:
        if path.exists():
            return path.resolve()
    return None


def run_cpu_numeric_adapter(payload: dict[str, Any], *, base: Path | None = None) -> dict[str, Any]:
    validation = validate_numeric_abi(payload)
    dashi_path = resolve_dashicore_path(base)
    return {
        "suite": "dashi_vulkan_adapter",
        "status": "ok",
        "intent_gpu": False,
        "active_backend": "cpu",
        "fallback_reason": None if dashi_path else "dashicore_path_not_found",
        "dashicore_path": str(dashi_path) if dashi_path else None,
        "result": cpu_gemv(payload),
        "parity_hash": validation["parity_hash"],
        "schema": validation["schema"],
    }
