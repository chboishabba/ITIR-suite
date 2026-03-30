#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from itir_jmd_bridge.sl_zkperf import (
    build_zkperf_observation_from_contested_review_db,
    build_zkperf_observation_from_sl_file,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build one bounded ZKPerfObservation from an SL JSON payload or a persisted contested-review SQLite run"
    )
    parser.add_argument("--input", type=Path)
    parser.add_argument("--db-path", type=Path)
    parser.add_argument("--review-run-id")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--theory-evidence-json", type=Path)
    parser.add_argument("--theory-family")
    parser.add_argument("--run-id")
    parser.add_argument("--trace-id")
    parser.add_argument("--asserted-at")
    args = parser.parse_args()

    if bool(args.input) == bool(args.db_path):
        raise SystemExit("use exactly one of --input or --db-path")

    if args.input:
        observation = build_zkperf_observation_from_sl_file(
            args.input,
            run_id=args.run_id,
            trace_id=args.trace_id,
            asserted_at=args.asserted_at,
            theory_evidence_path=args.theory_evidence_json,
            theory_family=args.theory_family,
        )
    else:
        observation = build_zkperf_observation_from_contested_review_db(
            args.db_path,
            review_run_id=args.review_run_id,
            run_id=args.run_id,
            trace_id=args.trace_id,
            asserted_at=args.asserted_at,
            theory_evidence_path=args.theory_evidence_json,
            theory_family=args.theory_family,
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(observation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
