#!/usr/bin/env python3
"""Check a measured GWB event inventory against the versioned baseline receipt."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def _args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--baseline",
        type=Path,
        default=Path("baselines/gwb_timeline_scorecard_v0_2.json"),
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--observed-count", type=int)
    group.add_argument(
        "--scorecard",
        type=Path,
        help="JSON scorecard containing observed_event_count or event_count",
    )
    return parser.parse_args()


def _observed(args: argparse.Namespace) -> int:
    if args.observed_count is not None:
        return int(args.observed_count)
    scorecard = json.loads(args.scorecard.read_text(encoding="utf-8"))
    for key in ("observed_event_count", "event_count", "timeline_event_count"):
        if key in scorecard:
            return int(scorecard[key])
    raise ValueError("scorecard has no supported event-count field")


def main() -> int:
    args = _args()
    baseline = json.loads(args.baseline.read_text(encoding="utf-8"))
    observed = _observed(args)
    expected = int(baseline["accepted_regression_event_count"])
    result = {
        "schema_version": "itir.gwb_timeline_baseline_check.v0_1",
        "baseline_ref": baseline["baseline_ref"],
        "observed_event_count": observed,
        "accepted_regression_event_count": expected,
        "matches": observed == expected,
        "timeline_complete": False,
        "historical_truth_closed": False,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["matches"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
