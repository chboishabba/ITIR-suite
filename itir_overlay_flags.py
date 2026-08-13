"""
Small helper for marking overlay payloads as `derived_only`.

Use in adapters that emit non-canonical overlays (e.g., TextGraphs-style
projections) to guarantee downstream consumers see the provenance boundary.

The helper returns a shallow-copied payload with two fields:
- `canonical_status`: set to the string `"derived_only"`
- `overlay_flags`: a set-like list including `"derived_only"`

It does not mutate the input.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Iterable, List

DERIVED_ONLY_FLAG = "derived_only"


def as_derived_only(payload: Dict[str, Any], *, reason: str | None = None) -> Dict[str, Any]:
    """
    Return a copy of `payload` tagged as derived-only.

    - Adds/overwrites `canonical_status` to DERIVED_ONLY_FLAG.
    - Merges DERIVED_ONLY_FLAG into `overlay_flags` (list of strings).
    - If `reason` is provided, stores it under `derived_only_reason`.
    """

    out: Dict[str, Any] = deepcopy(payload)
    flags: List[str] = list(out.get("overlay_flags", []))
    if DERIVED_ONLY_FLAG not in flags:
        flags.append(DERIVED_ONLY_FLAG)
    out["overlay_flags"] = flags
    out["canonical_status"] = DERIVED_ONLY_FLAG
    if reason:
        out["derived_only_reason"] = reason
    return out


def is_derived_only(payload: Dict[str, Any]) -> bool:
    """Cheap predicate so adapters/tests can guard consumption."""
    if payload.get("canonical_status") == DERIVED_ONLY_FLAG:
        return True
    flags: Iterable[str] = payload.get("overlay_flags", []) or []
    return DERIVED_ONLY_FLAG in flags


def assert_not_derived_only(payload: Dict[str, Any], *, allow_derived: bool = False) -> None:
    """
    Raise ValueError if payload is marked derived_only and allow_derived is False.
    Use at ingestion sites to prevent silent promotion of non-canonical overlays.
    """
    if is_derived_only(payload) and not allow_derived:
        raise ValueError("derived_only overlay cannot be consumed without explicit opt-in")
