#!/usr/bin/env python3
"""Lower-bound simulator for a bucketed Zelph HF v3 shard layout.

This does not inspect per-record keys. It uses section totals from an emitted
v2 shard tree and answers a narrower question:

  "If we re-bucketed payload bytes into N deterministic buckets with reasonably
   balanced distribution, what fetch envelope would we expect in the best case?"

Use this to decide whether a real v3 emitter is worth building. Do not treat
the output as promotable evidence by itself.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Simulate lower-bound fetch budgets for a bucketed Zelph v3 layout.")
    parser.add_argument("--v2-budget-json", required=True, help="Path to JSON output from estimate_zelph_shard_fetch_budget.py.")
    parser.add_argument(
        "--adj-buckets",
        default="256,512,1024",
        help="Comma-separated candidate bucket counts for left/right adjacency sections.",
    )
    parser.add_argument(
        "--name-buckets",
        default="128,256,512",
        help="Comma-separated candidate bucket counts for name sections.",
    )
    parser.add_argument("--output", default=None, help="Optional JSON output path.")
    return parser.parse_args()


def mib(n: int) -> float:
    return n / (1024 * 1024)


def parse_bucket_counts(raw: str) -> list[int]:
    values: list[int] = []
    for token in raw.split(","):
        token = token.strip()
        if not token:
            continue
        values.append(int(token))
    if not values:
        raise ValueError("At least one bucket count is required")
    return values


def lower_bound_section(total_bytes: int, bucket_count: int) -> dict[str, float | int]:
    avg = total_bytes / bucket_count
    ceil_avg = math.ceil(avg)
    return {
        "bucketCount": bucket_count,
        "averageBytes": avg,
        "averageMiB": round(mib(avg), 2),
        "ceilingBytes": ceil_avg,
        "ceilingMiB": round(mib(ceil_avg), 2),
    }


def main() -> int:
    args = parse_args()
    with Path(args.v2_budget_json).open("r", encoding="utf-8") as handle:
        v2 = json.load(handle)

    sections = v2["sections"]
    left_total = int(sections["left"]["totalBytes"])
    right_total = int(sections["right"]["totalBytes"])
    name_of_node_total = int(sections["nameOfNode"]["totalBytes"])
    node_of_name_total = int(sections["nodeOfName"]["totalBytes"])

    adj_counts = parse_bucket_counts(args.adj_buckets)
    name_counts = parse_bucket_counts(args.name_buckets)

    adjacency_candidates = []
    for bucket_count in adj_counts:
        left = lower_bound_section(left_total, bucket_count)
        right = lower_bound_section(right_total, bucket_count)
        route_left_avg = left["averageBytes"]
        route_right_avg = right["averageBytes"]
        route_node_avg = route_left_avg + route_right_avg
        route_node_one_sided_avg = max(route_left_avg, route_right_avg)
        adjacency_candidates.append(
            {
                "bucketCount": bucket_count,
                "left": left,
                "right": right,
                "routeLeft_averageMiB": round(mib(route_left_avg), 2),
                "routeRight_averageMiB": round(mib(route_right_avg), 2),
                "routeNode_twoSided_averageMiB": round(mib(route_node_avg), 2),
                "routeNode_oneSided_averageMiB": round(mib(route_node_one_sided_avg), 2),
            }
        )

    name_candidates = []
    for bucket_count in name_counts:
        name_of_node = lower_bound_section(name_of_node_total, bucket_count)
        node_of_name = lower_bound_section(node_of_name_total, bucket_count)
        name_candidates.append(
            {
                "bucketCount": bucket_count,
                "nameOfNode": name_of_node,
                "nodeOfName": node_of_name,
                "routeName_averageMiB": round(mib(node_of_name["averageBytes"]), 2),
                "routeNameOfNode_averageMiB": round(mib(name_of_node["averageBytes"]), 2),
            }
        )

    report = {
        "sourceBudgetJson": str(Path(args.v2_budget_json)),
        "model": "lower-bound-uniform-bucketing",
        "warning": "Assumes balanced redistribution into deterministic buckets; use only to decide whether a real v3 emitter is worth building.",
        "v2Observed": {
            "routeNode_medianMiB": v2["estimates"]["routeNode_left_plus_right"]["medianMiB"],
            "routeNode_p95MiB": v2["estimates"]["routeNode_left_plus_right"]["p95MiB"],
            "routeNode_maxMiB": v2["estimates"]["routeNode_left_plus_right"]["maxMiB"],
            "routeName_medianMiB": v2["estimates"]["routeName_nodeOfName_only"]["medianMiB"],
        },
        "v3Candidates": {
            "adjacency": adjacency_candidates,
            "names": name_candidates,
        },
    }

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
