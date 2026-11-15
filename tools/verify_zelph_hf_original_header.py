#!/usr/bin/env python3
"""P0 original Zelph remote HEADER-only witness with native Cap'n Proto decode.

Fetch at most 1 MiB, using immutable HF revision, TLS and exact HTTP 206
Content-Range against the published original .bin (never a full 82 GiB
download). Independently cross-check complete original offset index against
HF-v2 manifest and the NATIVE decoded original header counts. This is a
source-header witness, not selected shard equality, whole .bin hash, complete
name-key domain or Wikidata semantic evidence.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import sys
from tempfile import TemporaryDirectory
from typing import Any, Callable
from urllib.request import Request, urlopen

from verify_zelph_index_manifest_original import verify_index_manifest_files

_REV = re.compile(r"[0-9a-f]{40}\Z")
_URL_PREFIX = "https://huggingface.co/datasets/acrion/zelph/resolve/"
_ARTIFACT = "wikidata-20260309-all"


def _http_206_header(*, revision: str, source_size: int, length: int,
                     opener: Callable[..., Any] = urlopen,
                     timeout_seconds: int = 60) -> tuple[bytes, str]:
    if not _REV.fullmatch(revision):
        raise ValueError("immutable Hugging Face 40-hex dataset revision required")
    if (type(length) is not int or not 0 < length <= 1024 * 1024 or
            type(source_size) is not int or source_size < length):
        raise ValueError("original packed header bounded length/source size required")
    if type(timeout_seconds) is not int or not 1 <= timeout_seconds <= 600:
        raise ValueError("bounded positive source header network timeout required")
    url = f"{_URL_PREFIX}{revision}/{_ARTIFACT}.bin"
    req = Request(
        url, headers={
            "Range": f"bytes=0-{length-1}",
            "Accept-Encoding": "identity",
            "User-Agent": "itir-zelph-original-header-proof/1",
        }, method="GET",
    )
    with opener(req, timeout=timeout_seconds) as response:
        if getattr(response, "status", None) != 206:
            raise ValueError("remote original source header did not return HTTP 206")
        if response.headers.get("Content-Range", "") != f"bytes 0-{length-1}/{source_size}":
            raise ValueError("remote original HTTP Content-Range differs from indexed full source")
        if response.headers.get("Content-Encoding", "identity").lower() not in ("", "identity"):
            raise ValueError("remote original header has non-identity content encoding")
        length_label = response.headers.get("Content-Length")
        if length_label is not None and length_label != str(length):
            raise ValueError("remote original header Content-Length mismatch")
        raw = response.read(length)
        if len(raw) != length or response.read(1):
            raise ValueError("remote original header range truncated or oversized")
    return raw, url


def _native_header_decoder(*, header: bytes, executable: Path, timeout_seconds: int) -> dict:
    if not executable.is_file():
        raise ValueError("native original header probe executable absent")
    with TemporaryDirectory(prefix="itir-zelph-original-header-") as location:
        path = Path(location) / "original-header.capnp-packed"
        path.write_bytes(header)
        proc = subprocess.run(
            [str(executable), "--header-file", str(path)],
            text=True, capture_output=True, timeout=timeout_seconds, check=False,
        )
        if proc.returncode != 0 or len(proc.stdout) > 1024 * 1024:
            raise ValueError(f"native original packed-header decode failed: {proc.stderr[:300]}")
        try:
            result = json.loads(proc.stdout)
        except json.JSONDecodeError as err:
            raise ValueError("native original packed-header decoder returned invalid JSON") from err
    if type(result) is not dict:
        raise ValueError("native original packed-header decoder must return object")
    return result


def verify_pinned_original_header(*, manifest_path: Path, index_path: Path,
                                  manifest_sha256: str, dataset_revision: str,
                                  header_decoder_executable: Path,
                                  original_index_sha256: str | None = None,
                                  opener: Callable[..., Any] = urlopen,
                                  decode_header: Callable[..., dict] | None = None,
                                  timeout_seconds: int = 60) -> dict[str, Any]:
    # Structural and cryptographic local preflight before ANY network access.
    index_crosswalk = verify_index_manifest_files(
        manifest_path=manifest_path, index_path=index_path,
        manifest_sha256=manifest_sha256, index_sha256=original_index_sha256,
    )
    length = index_crosswalk["original_header_length_bytes"]
    source_size = index_crosswalk["original_bin_size_bytes"]
    raw, source_url = _http_206_header(
        revision=dataset_revision, source_size=source_size, length=length,
        opener=opener, timeout_seconds=timeout_seconds,
    )
    if decode_header is None:
        native = _native_header_decoder(
            header=raw, executable=header_decoder_executable,
            timeout_seconds=timeout_seconds,
        )
    else:
        # Test seam ONLY: the exact committed native binary must be separately
        # compiled/tested in the existing original Cap'n Proto acceptance suite.
        native = decode_header(header=raw)
    if (type(native) is not dict or
            native.get("version") != "itir.zelph.native_original_packed_header_probe.v1" or
            type(native.get("header_size_bytes")) is not int or
            native["header_size_bytes"] != length or
            native.get("edit_authority") is not False or
            native.get("source_upstream_authenticity_proved") is not False):
        raise ValueError("native original packed header probe schema/authority mismatch")
    for name, expected_count in index_crosswalk["section_chunk_counts"].items():
        if type(native.get(name)) is not int or native[name] != expected_count:
            raise ValueError(f"native original header disagrees with manifest/index count: {name}")
    return {
        "version": "itir.zelph.remote_original_header_index_manifest_witness.v1",
        "dataset_revision": dataset_revision,
        "original_source_url": source_url,
        "original_source_http_status": 206,
        "original_source_content_range_exact": True,
        "header_bytes_received": len(raw),
        "header_raw_sha256": sha256(raw).hexdigest(),
        "manifest_raw_sha256": index_crosswalk["manifest_raw_sha256_rechecked"],
        "original_index_raw_sha256": index_crosswalk["original_index_raw_sha256_rechecked"],
        "full_original_index_manifest_geometry_checked": True,
        "native_original_capnp_header_executed": True,
        "native_original_header_matches_all_four_section_counts": True,
        "original_source_bin_size_claim_bytes": source_size,
        "remote_original_header_from_revisioned_hf_endpoint": True,
        "full_original_bin_sha256_verified": False,
        "all_name_shards_verified": False,
        "original_bin_selected_shard_bytes_equal": False,
        "name_domain_exhausted": False,
        "all_query_words_closed": False,
        "native_p854_source_verified": False,
        "source_support_paid": False,
        "edit_authority": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--original-index", type=Path, required=True)
    parser.add_argument("--manifest-sha256", required=True)
    parser.add_argument("--original-index-sha256")
    parser.add_argument("--dataset-revision", required=True)
    parser.add_argument("--header-decoder", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=60)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = verify_pinned_original_header(
            manifest_path=args.manifest, index_path=args.original_index,
            manifest_sha256=args.manifest_sha256,
            original_index_sha256=args.original_index_sha256,
            dataset_revision=args.dataset_revision,
            header_decoder_executable=args.header_decoder,
            timeout_seconds=args.timeout_seconds,
        )
        output = json.dumps(result, sort_keys=True, indent=2) + "\n"
        if args.output:
            if args.output.exists():
                raise ValueError("refuse overwrite of original remote header proof")
            args.output.write_text(output, encoding="utf-8")
        else:
            print(output, end="")
        return 0
    except (ValueError, OSError, TypeError, subprocess.TimeoutExpired, UnicodeDecodeError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc), "edit_authority": False}),
              file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
