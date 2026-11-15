#!/usr/bin/env python3
"""Plan or explicitly execute an immutable, budgeted HF selected-shard fetch.

The artifact and every relative shard path are verified against a pinned v2
manifest and a filtered route. The default is *no network*. With --execute, stream exact selected objects through the existing ITIR HF
connector, never requesting the full original 82 GiB binary.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import shlex
import sys
from typing import Any
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'itir-mcp' / 'src'))
from itir_mcp.shard_transport import open_pinned_zelph_complete_object

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
        "primary_transport_owner": "itir_mcp.shard_transport",
        "printable_command": shlex.join(command),
        "download_client_invoked": False,
        "network_transfer_confirmed": False,
        "original_bin_requested": False,
        "source_bin_to_shard_ranges_verified": False,
        "candidate_only": True,
    }



def execute_selected_fetch(*, plan: dict[str, Any], manifest_path: Path,
                           route_path: Path, shard_root: Path,
                           opener: Any | None = None, timeout: int = 60) -> dict[str, Any]:
    """Stream exact selected immutable HF objects via the existing connector."""
    revision = plan.get("dataset_revision")
    if (not isinstance(revision, str) or not _SHA40.fullmatch(revision)
            or plan.get("version") != "itir.zelph.budgeted_immutable_hf_selected_shards.v1"):
        raise ValueError("exact pinned selected-shard fetch plan required")
    rebuilt = selected_fetch_plan(
        manifest_path=manifest_path, route_path=route_path,
        dataset_revision=revision,
        manifest_sha256=plan.get("manifest_sha256_verified"),
        shard_root=shard_root, max_selected_gib=plan.get("max_selected_gib"),
    )
    for field in ("dataset_revision", "manifest_sha256_verified",
                  "route_sha256_verified", "selected_shard_files",
                  "selected_object_count", "advertised_selected_bytes",
                  "max_selected_gib", "invocation"):
        if plan.get(field) != rebuilt[field]:
            raise ValueError("selected HF plan changed after pinned inputs")
    if type(timeout) is not int or not 0 < timeout <= 600:
        raise ValueError("positive bounded selected HF network timeout required")
    if shard_root.is_symlink():
        raise ValueError("selected shard root must not be symlink")
    if not shard_root.exists():
        shard_root.mkdir(parents=True)
    root = shard_root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("selected shard root must be a directory")
    manifest = _read_json(manifest_path, 16 * 1024 * 1024)
    index = _manifest_index(manifest, _ARTIFACT)
    selected = _selected_route_keys(_read_json(route_path, 64 * 1024 * 1024))
    ordered = [index[key] for key in sorted(selected)]
    for row in ordered:
        target = root / row["relative"]
        if target.exists() or target.is_symlink():
            raise ValueError("selected HF evidence already exists; refuse overwrite")
        for parent in target.parents:
            if parent == root:
                break
            if parent.is_symlink():
                raise ValueError("selected HF shard parent symlink refused")
    receipts = []
    for row in ordered:
        rel, length = row["relative"], row["length"]
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        digest = sha256()
        bytes_seen = 0
        with open_pinned_zelph_complete_object(
            hf_uri=f"hf://datasets/acrion/zelph/{rel}",
            revision=revision, expected_size=length,
            max_bytes=plan["max_selected_gib"] * 1024**3,
            opener=opener, timeout=timeout,
        ) as remote:
            with target.open("xb") as out:
                while bytes_seen < length:
                    block = remote.read(min(1024 * 1024, length - bytes_seen))
                    if not block:
                        raise ValueError("HF selected shard truncated")
                    bytes_seen += len(block)
                    out.write(block)
                    digest.update(block)
                if remote.read(1):
                    raise ValueError("HF selected shard has unaccounted extra bytes")
        receipts.append({
            "object_relative_path": rel, "size_bytes": bytes_seen,
            "raw_hf_object_sha256": digest.hexdigest(),
            "exact_complete_hf_object_observed": True,
            "http_status": getattr(remote, "status", None),
            "original_bin_source_range_equality_checked": False,
        })
    return {
        **plan, "connector_transport_owner": "itir_mcp.shard_transport",
        "download_client_invoked": False, "network_transfer_confirmed": True,
        "original_bin_requested": False,
        "selected_original_hf_objects_bytes_observed": True,
        "selected_object_receipts": receipts,
        "source_bin_to_shard_ranges_verified": False,
        "upstream_source_authority_paid": False, "edit_authority": False,
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
                        help="stream exact immutable selected HF objects via existing connector; default plans only")
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
            result = execute_selected_fetch(
                plan=result, manifest_path=args.manifest, route_path=args.route,
                shard_root=args.shard_root,
            )
        output = json.dumps(result, indent=2, sort_keys=True) + "\n"
        if args.output:
            args.output.write_text(output, encoding="utf-8")
        else:
            sys.stdout.write(output)
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc),
                          "source_bin_to_shard_ranges_verified": False}, sort_keys=True),
              file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
