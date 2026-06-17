from __future__ import annotations

import importlib
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any, Mapping


UNAVAILABLE = "UNAVAILABLE"


def materialize_sensiblaw_spectral_payload(
    source: Mapping[str, Any] | None = None,
    *,
    sensiblaw_path: str | Path | None = None,
) -> dict[str, Any]:
    """Optional SensibLaw boundary for explicit spectral materialization.

    This module deliberately does not import SensibLaw at import time. When the
    optional dependency or expected adapter hook is absent, the result is a
    diagnostic UNAVAILABLE packet with no fabricated receipt identifiers.
    """

    before_path = list(sys.path)
    before_modules = set(sys.modules)
    if sensiblaw_path is not None:
        sys.path.insert(0, str(Path(sensiblaw_path)))
    try:
        sensiblaw = _import_first(("SensibLaw", "sensiblaw"))
        if sensiblaw is None:
            return _unavailable("SensibLaw import unavailable")
        hook = getattr(sensiblaw, "materialize_pnf_spectral_numeric_abi", None)
        if not callable(hook):
            return _unavailable("SensibLaw spectral materializer unavailable")
        payload = hook(dict(source or {}))
        if not isinstance(payload, Mapping):
            return _unavailable("SensibLaw spectral materializer returned a non-object payload")
        return {"status": "AVAILABLE", "payload": dict(payload), "receipt_ids": _declared_receipt_ids(payload)}
    finally:
        sys.path[:] = before_path
        _remove_polluted_src_modules(before_modules)


def _import_first(names: Sequence[str]) -> Any:
    for name in names:
        try:
            return importlib.import_module(name)
        except ImportError:
            continue
    return None


def _unavailable(reason: str) -> dict[str, Any]:
    return {"status": UNAVAILABLE, "reason": reason, "receipt_ids": [], "diagnostic_only": True}


def _declared_receipt_ids(payload: Mapping[str, Any]) -> list[str]:
    receipt_ids: list[str] = []
    receipts = payload.get("receipts")
    if isinstance(receipts, list):
        for receipt in receipts:
            if isinstance(receipt, Mapping) and isinstance(receipt.get("receipt_id"), str):
                receipt_ids.append(receipt["receipt_id"])
    return receipt_ids


def _remove_polluted_src_modules(before_modules: set[str]) -> None:
    for name in list(sys.modules):
        if name not in before_modules and (name == "src" or name.startswith("src.")):
            sys.modules.pop(name, None)
