#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from itir_jmd_bridge.zkperf_stream import (
    build_zkperf_stream_fixture_from_observations,
    load_zkperf_observations,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a zkperf stream fixture from ZKPerfObservation JSON or NDJSON input"
    )
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--stream-id")
    parser.add_argument("--stream-revision")
    parser.add_argument("--created-at-utc")
    parser.add_argument("--max-observations-per-window", type=int)
    args = parser.parse_args()

    fixture = build_zkperf_stream_fixture_from_observations(
        load_zkperf_observations(args.input),
        stream_id=args.stream_id,
        stream_revision=args.stream_revision,
        created_at_utc=args.created_at_utc,
        max_observations_per_window=args.max_observations_per_window,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(fixture, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
