#!/usr/bin/env python3
"""Pinned Zelph P0 metadata-only operator handoff.

The optional --execute fetches ONLY two small published metadata objects at
the exact dataset revision (manifest + original offset index), then verifies
the original .bin first packed header with one exact HTTP 206 range and native
Cap'n Proto header decoder. No original 82 GiB .bin download is requested.
Default is dry-run/plan, with no network. No QID/name/adjacency or Wikidata
native statement authority is inferred from header/offset metadata.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Callable
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'itir-mcp' / 'src'))
from itir_mcp.shard_transport import fetch_pinned_zelph_object

from verify_zelph_hf_original_header import verify_pinned_original_header

_ART = "wikidata-20260309-all"
_REV = re.compile(r"[0-9a-f]{40}\Z")
_SHA = re.compile(r"[0-9a-f]{64}\Z")
_MANIFEST_REL = f"{_ART}/{_ART}.hf-v2.json"
_INDEX_REL = f"{_ART}/artifact.index.json"


def plan_metadata_header_probe(*, dataset_revision: str, manifest_sha256: str,
                               local_dir: Path, receipt_dir: Path,
                               original_index_sha256: str | None = None) -> dict[str, Any]:
    if not _REV.fullmatch(dataset_revision) or not _SHA.fullmatch(manifest_sha256):
        raise ValueError("immutable revision and independently pinned raw manifest SHA256 required")
    if original_index_sha256 is not None and not _SHA.fullmatch(original_index_sha256):
        raise ValueError("optional independently pinned raw index SHA256 must be valid")
    if not str(local_dir) or not str(receipt_dir):
        raise ValueError("separate explicit local and receipt paths required")
    if local_dir.resolve() == receipt_dir.resolve():
        raise ValueError("source metadata and immutable receipt directories must be distinct")
    command = [
        "hf", "download", "acrion/zelph",
        _MANIFEST_REL, _INDEX_REL,
        "--repo-type", "dataset", "--revision", dataset_revision,
        "--local-dir", str(local_dir),
    ]
    return {
        "version": "itir.zelph.pinned_hf_original_metadata_header_plan.v1",
        "dataset_revision": dataset_revision,
        "manifest_sha256_expected": manifest_sha256,
        "original_index_sha256_expected": original_index_sha256,
        "manifest_relative_path": _MANIFEST_REL,
        "original_offset_index_relative_path": _INDEX_REL,
        "hf_download_argv": command,
        "primary_transport_owner": "itir_mcp.shard_transport",
        "connector_will_fetch_exact_metadata": True,
        "header_raw_receipt_path": str(receipt_dir / "original-header.capnp-packed"),
        "header_proof_receipt_path": str(receipt_dir / "original-header-proof.json"),
        "selected_file_count": 2,
        "whole_original_bin_requested": False,
        "all_name_shards_requested": False,
        "full_graph_name_domain_verified": False,
        "network_executed": False,
        "edit_authority": False,
    }


def execute_metadata_header_probe(*, plan: dict[str, Any], local_dir: Path,
                                  receipt_dir: Path, native_header_decoder: Path,
                                  original_index_sha256: str | None = None,
                                  timeout_seconds: int = 900,
                                  run_download: Callable[..., Any] | None = None,
                                  fetch_object: Callable[..., dict] | None = None,
                                  run_header_check: Callable[..., dict] = verify_pinned_original_header,
                                  **header_kwargs: Any) -> dict[str, Any]:
    if type(timeout_seconds) is not int or not 1 <= timeout_seconds <= 3600:
        raise ValueError("bounded metadata download timeout required")
    if not native_header_decoder.is_file():
        raise ValueError("compiled upstream-schema native original header decoder required")
    for name in ("original-header.capnp-packed", "original-header-proof.json"):
        if (receipt_dir / name).exists():
            raise ValueError("refuse overwrite existing immutable P0 original header evidence")
    local_dir.mkdir(parents=True, exist_ok=True)
    receipt_dir.mkdir(parents=True, exist_ok=True)
    argv = plan["hf_download_argv"]
    expected_argv = [
        "hf", "download", "acrion/zelph",
        _MANIFEST_REL, _INDEX_REL,
        "--repo-type", "dataset", "--revision", plan["dataset_revision"],
        "--local-dir", str(local_dir),
    ]
    if argv != expected_argv:
        raise ValueError("metadata download plan attempts non-approved HF files or revision")
    manifest = local_dir / _MANIFEST_REL
    index = local_dir / _INDEX_REL
    if run_download is not None:
        # Backward-compatible deterministic injection seam for existing offline
        # acceptance; production never shells out to hf/download.
        run_download(argv, check=True, timeout=timeout_seconds)
    else:
        fetcher = fetch_object or fetch_pinned_zelph_object
        for relative, target in ((_MANIFEST_REL, manifest), (_INDEX_REL, index)):
            if target.exists() or target.is_symlink():
                raise ValueError("refuse overwrite existing immutable source metadata")
            proof = fetcher(
                hf_uri=f"hf://datasets/acrion/zelph/{relative}",
                revision=plan["dataset_revision"], max_bytes=16 * 1024 * 1024,
                timeout=min(timeout_seconds, 600),
            )
            data = proof.get("bytes")
            if (type(data) is not bytes or not 0 < len(data) <= 16 * 1024 * 1024
                    or sha256(data).hexdigest() != proof.get("sha256")
                    or proof.get("whole_object_observed") is not True):
                raise ValueError("HF connector did not return verified complete source metadata bytes")
            if (relative == _MANIFEST_REL
                    and proof["sha256"] != plan["manifest_sha256_expected"]):
                raise ValueError("pinned source manifest digest mismatch")
            if (relative == _INDEX_REL and original_index_sha256 is not None
                    and proof["sha256"] != original_index_sha256):
                raise ValueError("pinned original index digest mismatch")
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("xb") as out:
                out.write(data)
    for path in (manifest, index):
        if not path.is_file() or not 0 < path.stat().st_size <= 16 * 1024 * 1024:
            raise ValueError("immutable metadata transfer did not produce bounded raw files")
    result = run_header_check(
        manifest_path=manifest, index_path=index,
        manifest_sha256=plan["manifest_sha256_expected"],
        original_index_sha256=original_index_sha256,
        dataset_revision=plan["dataset_revision"],
        header_decoder_executable=native_header_decoder,
        raw_header_output=receipt_dir / "original-header.capnp-packed",
        **header_kwargs,
    )
    if (result.get("native_original_header_matches_all_four_section_counts") is not True
            or result.get("original_source_http_status") != 206
            or result.get("edit_authority") is not False):
        raise ValueError("immutable HF original header verification incomplete")
    # Rehash the retained raw header; do not trust a detached JSON result
    # without the actual exact original source bytes it is supposed to bind.
    raw_path = receipt_dir / "original-header.capnp-packed"
    if (not raw_path.is_file() or
            raw_path.stat().st_size != result.get("header_bytes_received") or
            sha256(raw_path.read_bytes()).hexdigest() != result.get("header_raw_sha256")):
        raise ValueError("original header receipt is not bound to retained raw source bytes")
    receipt = {
        **result,
        "metadata_hf_cli_invoked": run_download is not None,
        "metadata_itir_hf_connector_invoked": run_download is None,
        "metadata_network_transfer_measured": False,
        "whole_original_bin_downloaded": False,
        "selected_original_chunk_payloads_compared": False,
    }
    target = receipt_dir / "original-header-proof.json"
    with target.open("x", encoding="utf-8") as out:
        json.dump(receipt, out, indent=2, sort_keys=True)
        out.write("\n")
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-revision", required=True)
    parser.add_argument("--manifest-sha256", required=True)
    parser.add_argument("--original-index-sha256")
    parser.add_argument("--local-dir", type=Path, required=True)
    parser.add_argument("--receipt-dir", type=Path, required=True)
    parser.add_argument("--header-decoder", type=Path)
    parser.add_argument("--execute", action="store_true",
                        help="explicitly fetch ONLY 2 metadata objects and HTTP206 original packed header")
    parser.add_argument("--timeout-seconds", type=int, default=900)
    args = parser.parse_args()
    try:
        plan = plan_metadata_header_probe(
            dataset_revision=args.dataset_revision,
            manifest_sha256=args.manifest_sha256,
            original_index_sha256=args.original_index_sha256,
            local_dir=args.local_dir, receipt_dir=args.receipt_dir,
        )
        if not args.execute:
            print(json.dumps(plan, indent=2, sort_keys=True))
            return 0
        if args.header_decoder is None:
            raise ValueError("--execute requires compiled --header-decoder")
        result = execute_metadata_header_probe(
            plan=plan, local_dir=args.local_dir, receipt_dir=args.receipt_dir,
            native_header_decoder=args.header_decoder,
            original_index_sha256=args.original_index_sha256,
            timeout_seconds=args.timeout_seconds,
        )
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, TypeError, subprocess.SubprocessError) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc), "edit_authority": False}),
              file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
