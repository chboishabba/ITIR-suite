#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

PR1_FILES = [
    "itir_jmd_bridge/zkperf_stream_core.py",
    "itir_jmd_bridge/zkperf_stream_index.py",
    "itir_jmd_bridge/zkperf_stream_transport.py",
    "itir_jmd_bridge/zkperf_viz.py",
    "tests/test_zkperf_stream.py",
    "tests/test_zkperf_viz.py",
    "docs/planning/zkperf_pr1_payload_to_upstream_20260331.md",
]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Stage the generic zkperf PR1 payload into a standalone bundle directory."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("/tmp/zkperf-pr1-upstream-bundle"),
        help="Directory to populate with the staged payload.",
    )
    args = parser.parse_args()

    out = args.output_dir.resolve()
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)

    copied: list[str] = []
    for rel in PR1_FILES:
        src = ROOT / rel
        dst = out / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        copied.append(rel)

    manifest = {
        "bundleKind": "zkperf-pr1-upstream-bundle",
        "sourceRepo": str(ROOT),
        "copiedFiles": copied,
        "notes": [
            "This is a source snapshot, not a rewritten target-repo patch.",
            "Use docs/planning/zkperf_pr1_payload_to_upstream_20260331.md for destination mapping.",
            "SL and ITIR-local wrappers are intentionally excluded.",
        ],
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(str(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
