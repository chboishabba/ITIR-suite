#!/usr/bin/env python3
"""Plan or explicitly execute an immutable, budgeted HF selected-shard fetch.

The artifact and every relative shard path are verified against a pinned v2
manifest and a filtered route. The default is *no network*. With --execute,
reuse the installed official 'hf download' CLI, avoiding a duplicate transfer
implementation and never asking it to download the full 82 GiB .bin.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import shlex
import subprocess
import sys
from typing import Any

from verify_zelph_bin_shard_exact import (
    _ARTIFACT, _SHA40, _SHA64,
    _manifest_index, _read_json, _selected_route_keys,
)


def selected_fetch_plan(
    *, manifest_path: Path, route_path: Path,
    dataset_revision: str, manifest_sha256: str,
    shard_root: Path, max_selected_gib: int = 8,
) -> dict[str, Any]:
    if not _SHA40.fullmatch(dataset_revision) or not _SHA64.fullmatch(manifest_sha256):
        raise ValueError("pinned HF SHA and exact raw manifest digest required")
    raw_manifest = manifest_path.read_bytes()
    if not raw_manifest or len(raw_manifest) > 16 * 1024 * 1024:
        raise ValueError("manifest missing or exceeds 16 MiB bound")
    if sha256(raw_manifest).hexdigest() != manifest_sha256:
        raise ValueError("raw manifest content hash differs from declared digest")
    manifest = _read_json(manifest_path, 16 * 1024 * 1024)
    route = _read_json(route_path, 64 * 1024 * 1024)
    source = route.get("source")
    if not isinstance(source, dict):
        raise ValueError("route source identity missing")
    index = _manifest_index(manifest, _ARTIFACT)
    selected = _selected_route_keys(route)
    if selected - set(index):
        raise ValueError("selected chunks omitted from actual manifest")
    for section, field in (
        ("left", "leftChunkCount"), ("right", "rightChunkCount"),
        ("nameOfNode", "nameOfNodeChunkCount"), ("nodeOfName", "nodeOfNameChunkCount"),
    ):
        if source.get(field) != sum(name == section for name, _ in index):
            raise ValueError("route source vs manifest section count mismatch")
    total = sum(index[key]["length"] for key in selected)
    if (type(max_selected_gib) is not int or max_selected_gib <= 0
            or total > max_selected_gib * 1024 ** 3):
        raise ValueError("selected bytes exceed explicit max-selected-GiB limit")
    paths = [index[key]["relative"] for key in sorted(selected)]
    if len(set(paths)) != len(paths):
        raise ValueError("manifest maps selected chunk keys to duplicate paths")
    # hf download syntax: repo_id [filenames ...] --repo-type dataset
    # --revision SHA --local-dir root; no user-constructed shell evaluation.
    command = [
        "hf", "download", "acrion/zelph", *paths,
        "--repo-type", "dataset",
        "--revision", dataset_revision,
        "--local-dir", str(shard_root),
    ]
    return {
        "version": "itir.zelph.budgeted_immutable_hf_selected_shards.v1",
        "dataset_revision": dataset_revision,
        "manifest_sha256_verified": manifest_sha256,
        "route_sha256_verified": sha256(route_path.read_bytes()).hexdigest(),
        "selected_shard_files": paths,
        "selected_object_count": len(paths),
        "advertised_selected_bytes": total,
        "max_selected_gib": max_selected_gib,
        "invocation": command,
        "printable_command": shlex.join(command),
        "network_executed": False,
        "original_bin_requested": False,
        "source_bin_to_shard_ranges_verified": False,
        "candidate_only": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--route", type=Path, required=True)
    parser.add_argument("--dataset-revision", required=True)
    parser.add_argument("--manifest-sha256", required=True)
    parser.add_argument("--shard-root", type=Path, required=True)
    parser.add_argument("--max-selected-gib", type=int, default=8)
    parser.add_argument("--execute", action="store_true",
                        help="explicitly execute immutable hf download; default plans only")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = selected_fetch_plan(
            manifest_path=args.manifest, route_path=args.route,
            dataset_revision=args.dataset_revision,
            manifest_sha256=args.manifest_sha256,
            shard_root=args.shard_root,
            max_selected_gib=args.max_selected_gib,
        )
        if args.execute:
            # Download command intentionally does not run via a shell.
            # It reuses HF's existing client authentication, retries and cache.
            subprocess.run(result["invocation"], check=True)
            result["network_executed"] = True
            result["source_bin_to_shard_ranges_verified"] = False
        output = json.dumps(result, indent=2, sort_keys=True) + "\n"
        if args.output:
            args.output.write_text(output, encoding="utf-8")
        else:
            sys.stdout.write(output)
        return 0
    except (OSError, ValueError, json.JSONDecodeError, subprocess.CalledProcessError) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc),
                          "source_bin_to_shard_ranges_verified": False}, sort_keys=True),
              file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
