"""Deterministic, provenance-labelled graph overlay surfaces."""

from .baseline import (
    canonical_overlay_bytes,
    emit_baseline_overlay,
    replay_baseline_overlay,
)

__all__ = [
    "canonical_overlay_bytes",
    "emit_baseline_overlay",
    "replay_baseline_overlay",
]
