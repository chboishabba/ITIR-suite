#!/usr/bin/env python3
"""Retired legacy title-keyword ChatGPT carousel.

Compatibility names fail closed. No transport, AO, session, or mutation imports.
Use scripts.evidence_fleet_controller for dry-run planning only.
"""
from __future__ import annotations


class LegacyCarouselRetired(RuntimeError):
    """Legacy carousel dispatch is permanently disabled."""


DIAGNOSTIC = (
    "Legacy title carousel retired. "
    "Use python -m scripts.evidence_fleet_controller --db PATH --plan"
)


def _retired(*args: object, **kwargs: object) -> None:
    raise LegacyCarouselRetired(DIAGNOSTIC)


class ThreadLifecycleManager:
    """Retired lifecycle: old ADVANCE/REVIVE labels were mutation triggers."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        _retired()

    get_thread_info = _retired
    evaluate_lifecycle = _retired


class CarouselFleetOrchestrator:
    """Compatibility surface: all former scheduling paths are disabled."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        _retired()

    load_fleet_roster = _retired
    synthesize_prompt = _retired
    advance_single_thread = _retired
    run_carousel_tick = _retired
    run_loop = _retired


def main() -> int:
    _retired()
    raise AssertionError("unreachable")


if __name__ == "__main__":
    raise SystemExit(DIAGNOSTIC)
