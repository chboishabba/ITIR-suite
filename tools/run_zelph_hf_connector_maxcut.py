#!/usr/bin/env python3
"""One physical P0 Zelph HF connector cut, zero extra HTTP ownership.

Default: immutable pinned dry-run. With --execute, acquire manifest+index via
existing itir_mcp.shard_transport, prove tiny original native header HTTP206,
and optionally (ONLY if a separate exact physical source-backed route exists)
stream selected HF shard objects and compare each against original remote .bin
HTTP206 bytes. Original QID→chunk routing is NEVER inferred from an index.
No 82 GiB original download, new index, database, authority or truth promotion.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import sys
from typing import Any

from probe_zelph_hf_original_metadata import (
    plan_metadata_header_probe, execute_metadata_header_probe,
)
from plan_zelph_hf_selected_fetch import (
    selected_fetch_plan, execute_selected_fetch,
)
from verify_zelph_hf_remote_original_ranges import verify_pinned_remote_ranges

_REV = re.compile(r"[0-9a-f]{40}\Z")
_SHA = re.compile(r"[0-9a-f]{64}\Z")
_MANIFEST = ("wikidata-20260309-all/"
             "wikidata-20260309-all.hf-v2.json")


def _save_exclusive(path: Path, data: dict[str, Any]) -> None:
    with path.open("x", encoding="utf-8") as out:
        json.dump(data, out, indent=2, sort_keys=True)
        out.write("\n")


def run_hf_connector_maxcut(*, revision: str, manifest_sha256: str,
                            workspace: Path, execute: bool = False,
                            header_decoder: Path | None = None,
                            original_index_sha256: str | None = None,
                            source_backed_route: Path | None = None,
                            max_selected_gib: int = 8) -> dict[str, Any]:
    if (type(revision) is not str or not _REV.fullmatch(revision)
            or type(manifest_sha256) is not str
            or not _SHA.fullmatch(manifest_sha256)):
        raise ValueError("immutable original revision and independently pinned manifest SHA required")
    if (original_index_sha256 is not None
            and (type(original_index_sha256) is not str
                 or not _SHA.fullmatch(original_index_sha256))):
        raise ValueError("optional independently pinned raw index SHA required")
    if (type(max_selected_gib) is not int or max_selected_gib <= 0
            or max_selected_gib > 64):
        raise ValueError("selected HF physical budget must be 1..64 GiB")
    if workspace.is_symlink():
        raise ValueError("evidence workspace must not be a symlink")
    metadata_dir = workspace / "metadata"
    header_dir = workspace / "original-header"
    shard_dir = workspace / "selected-shards"
    plan = plan_metadata_header_probe(
        dataset_revision=revision, manifest_sha256=manifest_sha256,
        original_index_sha256=original_index_sha256,
        local_dir=metadata_dir, receipt_dir=header_dir,
    )
    if not execute:
        return {
            "version": "itir.zelph.connector_original_physical_maxcut_plan.v1",
            "metadata_header_plan": plan,
            "source_backed_route_supplied": source_backed_route is not None,
            "selected_route_provenance_independently_verified_here": False,
            "original_bin_requested_whole": False,
            "metadata_fetched": False,
            "original_header_verified": False,
            "selected_source_bytes_verified": False,
            "edit_authority": False,
        }
    if header_decoder is None or not header_decoder.is_file():
        raise ValueError("--execute requires compiled native original header probe")
    if source_backed_route is not None and not source_backed_route.is_file():
        raise ValueError("supplied source-backed route does not exist")
    if workspace.exists():
        raise ValueError("refuse overwrite an existing physical evidence workspace")
    workspace.mkdir(parents=True)
    header = execute_metadata_header_probe(
        plan=plan, local_dir=metadata_dir, receipt_dir=header_dir,
        native_header_decoder=header_decoder,
        original_index_sha256=original_index_sha256,
    )
    if (header.get("original_source_http_status") != 206
            or header.get("native_original_header_matches_all_four_section_counts") is not True
            or header.get("full_original_index_manifest_geometry_checked") is not True
            or header.get("edit_authority") is not False):
        raise ValueError("real original header/index/manifest physical witness incomplete")
    result: dict[str, Any] = {
        "version": "itir.zelph.connector_original_physical_maxcut.v1",
        "revision": revision,
        "manifest_sha256": manifest_sha256,
        "original_header_proof_raw_sha256":
            sha256((header_dir / "original-header-proof.json").read_bytes()).hexdigest(),
        "original_header_bytes_sha256": header["header_raw_sha256"],
        "header_from_original_http206": True,
        "full_original_offset_index_manifest_geometry_checked": True,
        "selected_route_supplied": source_backed_route is not None,
        "selected_route_origin_independently_authenticated_here": False,
        "selected_original_source_byte_ranges_verified": False,
        "entire_original_binary_downloaded": False,
        "name_domain_complete": False,
        "full_query_family_closed": False,
        "p854_support_paid": False,
        "s29_persistence_paid": False,
        "edit_authority": False,
    }
    if source_backed_route is not None:
        manifest_path = metadata_dir / _MANIFEST
        selection = selected_fetch_plan(
            manifest_path=manifest_path,
            route_path=source_backed_route,
            dataset_revision=revision, manifest_sha256=manifest_sha256,
            shard_root=shard_dir, max_selected_gib=max_selected_gib,
        )
        fetched = execute_selected_fetch(
            plan=selection, manifest_path=manifest_path,
            route_path=source_backed_route, shard_root=shard_dir,
        )
        if fetched.get("selected_original_hf_objects_bytes_observed") is not True:
            raise ValueError("selected HF objects not fully fetched")
        _save_exclusive(workspace / "selected-shard-objects.json", fetched)
        original_ranges = verify_pinned_remote_ranges(
            manifest_path=manifest_path, route_path=source_backed_route,
            shard_root=shard_dir, dataset_revision=revision,
            manifest_sha256=manifest_sha256,
            max_selected_gib=max_selected_gib,
        )
        if original_ranges.get("selected_raw_remote_bin_ranges_equal_local_shard_bytes") is not True:
            raise ValueError("original HTTP206 ranges not identical to selected HF shards")
        # Bind the two independently acquired pinned-HF source paths by
        # complete, unique per-object digest keys, not a self-asserted boolean.
        fetched_receipts = fetched.get("selected_object_receipts")
        source_receipts = original_ranges.get("receipts")
        if (type(fetched_receipts) is not list or type(source_receipts) is not list
                or not fetched_receipts or len(fetched_receipts) != len(source_receipts)):
            raise ValueError("original and published selected-object receipt domains differ")
        observed = {}
        for row in fetched_receipts:
            if type(row) is not dict:
                raise ValueError("invalid selected HF object receipt")
            key = "hf://datasets/acrion/zelph/" + row.get("object_relative_path", "")
            digest = row.get("raw_hf_object_sha256")
            if (key in observed or type(digest) is not str
                    or not _SHA.fullmatch(digest)
                    or row.get("exact_complete_hf_object_observed") is not True):
                raise ValueError("selected HF complete-object evidence invalid/duplicate")
            observed[key] = digest
        original = {}
        for row in source_receipts:
            if type(row) is not dict:
                raise ValueError("invalid original HTTP206 selected-source receipt")
            key, digest = row.get("shard_object_uri"), row.get("equal_raw_sha256")
            if (type(key) is not str or key in original or type(digest) is not str
                    or not _SHA.fullmatch(digest)
                    or row.get("exact_content_range_verified") is not True
                    or row.get("range_http_status") != 206):
                raise ValueError("original HTTP206 source receipt invalid/duplicate")
            original[key] = digest
        if observed != original:
            raise ValueError("same-revision published HF objects disagree with original source range digest")
        _save_exclusive(workspace / "original-selected-byte-equality.json", original_ranges)
        result.update({
            "same_pinned_revision_hf_object_and_original_range_digest_join_verified": True,
            "selected_original_source_byte_ranges_verified": True,
            "selected_object_count": original_ranges["selected_object_count"],
            "selected_byte_count": original_ranges["selected_byte_count"],
            "route_raw_sha256": sha256(source_backed_route.read_bytes()).hexdigest(),
            "selected_objects_receipt_sha256":
                sha256((workspace / "selected-shard-objects.json").read_bytes()).hexdigest(),
            "original_selected_range_receipt_sha256":
                sha256((workspace / "original-selected-byte-equality.json").read_bytes()).hexdigest(),
        })
    _save_exclusive(workspace / "physical-p0-disposition.json", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-revision", required=True)
    parser.add_argument("--manifest-sha256", required=True)
    parser.add_argument("--original-index-sha256")
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--header-decoder", type=Path)
    parser.add_argument("--source-backed-route", type=Path)
    parser.add_argument("--max-selected-gib", type=int, default=8)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    try:
        result = run_hf_connector_maxcut(
            revision=args.dataset_revision, manifest_sha256=args.manifest_sha256,
            workspace=args.workspace, execute=args.execute,
            header_decoder=args.header_decoder,
            original_index_sha256=args.original_index_sha256,
            source_backed_route=args.source_backed_route,
            max_selected_gib=args.max_selected_gib,
        )
        print(json.dumps(result, sort_keys=True, indent=2))
        return 0
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc),
                          "edit_authority": False}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
