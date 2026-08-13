#!/usr/bin/env python3
"""Estimate remote fetch cost envelopes for a Zelph shard set.

This works from an emitted `--layout v2 --emit-shards` directory and reports:
  - per-section shard-size distribution
  - estimated route-node cost assuming one left + one right chunk fetch
  - estimated route-name cost assuming one nodeOfName chunk fetch

It does not claim exact workload weighting. The purpose is to distinguish
whether current shard granularity is plausibly interactive or obviously too
coarse for remote object-store querying.
"""

from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path


SECTION_NAMES = ("left", "right", "nameOfNode", "nodeOfName")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Estimate fetch budgets from a Zelph shard tree.")
    parser.add_argument("--shard-root", required=True, help="Root directory containing left/right/nameOfNode/nodeOfName shard folders.")
    parser.add_argument("--output", default=None, help="Optional JSON output path.")
    return parser.parse_args()


def percentile(sorted_values: list[int], q: float) -> int:
    if not sorted_values:
        raise ValueError("Cannot compute percentile of empty list")
    if len(sorted_values) == 1:
        return sorted_values[0]
    pos = q * (len(sorted_values) - 1)
    lo = int(pos)
    hi = min(lo + 1, len(sorted_values) - 1)
    frac = pos - lo
    return int(round(sorted_values[lo] * (1.0 - frac) + sorted_values[hi] * frac))


def mib(n: int) -> float:
    return n / (1024 * 1024)


def summarize_sizes(sizes: list[int]) -> dict[str, float | int]:
    sizes = sorted(sizes)
    return {
        "count": len(sizes),
        "minBytes": sizes[0],
        "p25Bytes": percentile(sizes, 0.25),
        "medianBytes": int(statistics.median(sizes)),
        "p75Bytes": percentile(sizes, 0.75),
        "p95Bytes": percentile(sizes, 0.95),
        "maxBytes": sizes[-1],
        "totalBytes": sum(sizes),
        "minMiB": round(mib(sizes[0]), 2),
        "p25MiB": round(mib(percentile(sizes, 0.25)), 2),
        "medianMiB": round(mib(int(statistics.median(sizes))), 2),
        "p75MiB": round(mib(percentile(sizes, 0.75)), 2),
        "p95MiB": round(mib(percentile(sizes, 0.95)), 2),
        "maxMiB": round(mib(sizes[-1]), 2),
        "totalMiB": round(mib(sum(sizes)), 2),
    }


def load_section_sizes(shard_root: Path, section_name: str) -> list[int]:
    section_dir = shard_root / section_name
    return sorted(p.stat().st_size for p in section_dir.glob("*") if p.is_file())


def main() -> int:
    args = parse_args()
    shard_root = Path(args.shard_root)
    if not shard_root.exists():
        raise SystemExit(f"Shard root not found: {shard_root}")

    by_section: dict[str, list[int]] = {}
    for section in SECTION_NAMES:
        sizes = load_section_sizes(shard_root, section)
        if sizes:
            by_section[section] = sizes

    if "left" not in by_section or "right" not in by_section:
        raise SystemExit("Shard root must contain at least left and right shard files")

    route_node_pair_sums = sorted(left + right for left in by_section["left"] for right in by_section["right"])
    route_name_sizes = sorted(by_section.get("nodeOfName", []))
    route_name_of_node_sizes = sorted(by_section.get("nameOfNode", []))

    report = {
        "shardRoot": str(shard_root),
        "sections": {section: summarize_sizes(sizes) for section, sizes in by_section.items()},
        "estimates": {
            "routeNode_left_plus_right": summarize_sizes(route_node_pair_sums),
            "routeName_nodeOfName_only": summarize_sizes(route_name_sizes) if route_name_sizes else None,
            "routeNameOfNode_only": summarize_sizes(route_name_of_node_sizes) if route_name_of_node_sizes else None,
        },
        "assumptions": {
            "routeNode": "One left shard plus one right shard per routed node lookup.",
            "routeName": "One nodeOfName shard per exact name lookup.",
            "routeNameOfNode": "One nameOfNode shard per node->name lookup.",
            "weighting": "Unweighted by node popularity or chunk occupancy.",
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
