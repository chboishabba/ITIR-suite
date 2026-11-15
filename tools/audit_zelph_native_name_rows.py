#!/usr/bin/env python3
"""Physical P0-S -> native A1 precursor: exhaustive ORIGINAL packed name rows.

Input must be one retained immutable direct-original HTTP206 equality receipt,
the pinned manifest AND original offset index, and local identical packed shard
bytes. Execute existing original-schema C++ --stream-name-rows decoder,
spooling stdout to disk (no in-memory whole-section output). Require every
row's section/chunk/language/index, an exact terminal count, successful native
exit and no trailing output. Preserve duplicate QID name fibres rather than
turning rows into an assumed single-valued map.

This proves native enumeration *for an authenticated named chunk only*,
not completeness of absent chunks or global A1 until separately joined.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import re
from contextlib import ExitStack
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory, NamedTemporaryFile
from typing import Any, Callable

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "itir-mcp" / "src"))
from itir_mcp.shard_transport import open_pinned_zelph_complete_object
from audit_zelph_hf_name_section_bytes import _check_receipt, _read_receipt
from verify_zelph_bin_shard_exact import _ARTIFACT, _manifest_index, _read_json
from verify_zelph_index_manifest_original import verify_index_manifest_files

_REV = re.compile(r"[0-9a-f]{40}\Z")
_SHA = re.compile(r"[0-9a-f]{64}\Z")
_QID = re.compile(r"Q[1-9][0-9]*\Z")
_ROW = "itir.zelph.native_original_name_row.v1"
_END = "itir.zelph.native_original_name_rows_end.v1"
_VERSION = "itir.zelph.native_original_name_chunk_enumeration.v1"


def _hash_file(path: Path, *, max_bytes: int | None = None) -> str:
    if path.is_symlink() or not path.is_file():
        raise ValueError("source evidence must be a regular non-symlink file")
    if max_bytes is not None and not 0 < path.stat().st_size <= max_bytes:
        raise ValueError("source evidence exceeds declared bounded size")
    digest = sha256()
    with path.open("rb") as raw:
        for block in iter(lambda: raw.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _json_object(raw: bytes) -> dict:
    def unique(items):
        found = {}
        for key, value in items:
            if key in found:
                raise ValueError("duplicate native name row JSON field")
            found[key] = value
        return found
    data = json.loads(
        raw, object_pairs_hook=unique,
        parse_constant=lambda v: (_ for _ in ()).throw(
            ValueError("invalid nonfinite native JSON number")
        ),
    )
    if type(data) is not dict:
        raise ValueError("native name-row NDJSON frame must be object")
    return data


def enumerate_authenticated_name_chunk(
    *, manifest_path: Path, original_index_path: Path,
    dataset_revision: str, manifest_sha256: str, original_index_sha256: str,
    section: str, chunk_index: int, receipt_path: Path,
    shard_root: Path, decoder_path: Path,
    expected_decoder_sha256: str,
    target_qids: tuple[str, ...] = (),
    max_name_rows: int = 10000000, max_stdout_mib: int = 2048,
    max_line_bytes: int = 65536, timeout_seconds: int = 600,
    rows_output: Path | None = None,
    hydrate_missing_shard: bool = False,
    max_hydrate_mib: int = 128,
    opener: Callable[..., Any] | None = None,
) -> dict[str, Any]:
    if (type(dataset_revision) is not str or not _REV.fullmatch(dataset_revision)
            or type(manifest_sha256) is not str or not _SHA.fullmatch(manifest_sha256)
            or type(original_index_sha256) is not str
            or not _SHA.fullmatch(original_index_sha256)):
        raise ValueError("immutable original revision, manifest and index pins required")
    if (type(expected_decoder_sha256) is not str
            or not _SHA.fullmatch(expected_decoder_sha256)):
        raise ValueError("independent pinned native decoder executable SHA256 required")
    if section not in ("nameOfNode", "nodeOfName"):
        raise ValueError("exhaustive native enumeration only for name sections")
    if type(chunk_index) is not int or chunk_index < 0:
        raise ValueError("exact nonnegative native name chunk index required")
    if (type(max_name_rows) is not int or not 0 < max_name_rows <= 100000000
            or type(max_stdout_mib) is not int or not 0 < max_stdout_mib <= 16384
            or type(max_line_bytes) is not int or not 0 < max_line_bytes <= 1048576
            or type(timeout_seconds) is not int or not 0 < timeout_seconds <= 3600):
        raise ValueError("bounded native stream rows/bytes/timeout required")
    if (type(hydrate_missing_shard) is not bool
            or type(max_hydrate_mib) is not int
            or not 1 <= max_hydrate_mib <= 16384):
        raise ValueError("bounded explicit native packed shard hydration required")
    if (not isinstance(target_qids, tuple)
            or len(target_qids) > 10000
            or any(type(q) is not str or not _QID.fullmatch(q)
                   for q in target_qids)
            or len(set(target_qids)) != len(target_qids)):
        raise ValueError("target QIDs must be unique exact native names")
    if rows_output is not None and (rows_output.exists() or rows_output.is_symlink()):
        raise ValueError("refuse overwrite of native name-row output")
    cross = verify_index_manifest_files(
        manifest_path=manifest_path, index_path=original_index_path,
        manifest_sha256=manifest_sha256, index_sha256=original_index_sha256,
    )
    index = _manifest_index(_read_json(manifest_path, 16 * 1024 * 1024), _ARTIFACT)
    key = (section, chunk_index)
    if key not in index:
        raise ValueError("native source chunk absent from pinned complete index")
    row = index[key]
    if row["language"] != "wikidata":
        raise ValueError("original native name shard must have exact wikidata language")
    receipt = _read_receipt(receipt_path)
    _check_receipt(
        receipt, row=row, number=chunk_index, section=section,
        rev=dataset_revision, manifest_sha=manifest_sha256,
        index_sha=original_index_sha256,
        bin_size=cross["original_bin_size_bytes"],
    )
    if shard_root.is_symlink():
        raise ValueError("native packed shard root symlink refused")
    if hydrate_missing_shard and not shard_root.exists():
        shard_root.mkdir(parents=True, exist_ok=True)
    root = shard_root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("native physical shard root must be real directory")
    file = root / row["relative"]
    if (file.is_symlink()
            or not file.resolve().is_relative_to(root)):
        raise ValueError("native shard path escapes immutable source root")
    hydrated = False
    if not file.exists() and hydrate_missing_shard:
        if row["length"] > max_hydrate_mib * 1024**2:
            raise ValueError("retained original-equal shard exceeds hydration transfer cap")
        file.parent.mkdir(parents=True, exist_ok=True)
        if file.parent.is_symlink():
            raise ValueError("symlinked native packed shard parent refused")
        with ExitStack() as stack:
            scratch_out = stack.enter_context(NamedTemporaryFile(
                mode="wb", dir=file.parent, prefix=".original-equal-name-",
                delete=False,
            ))
            scratch = Path(scratch_out.name)
            stack.callback(lambda: scratch.unlink(missing_ok=True))
            remote = stack.enter_context(open_pinned_zelph_complete_object(
                hf_uri=row["object_uri"], revision=dataset_revision,
                expected_size=row["length"],
                max_bytes=max_hydrate_mib * 1024**2, opener=opener,
            ))
            digest = sha256()
            count = 0
            while count < row["length"]:
                block = remote.read(min(1024 * 1024, row["length"] - count))
                if not block:
                    raise ValueError("source-backed published shard hydration truncated")
                scratch_out.write(block)
                digest.update(block)
                count += len(block)
            if remote.read(1) or digest.hexdigest() != receipt["published_shard_raw_sha256"]:
                raise ValueError("hydrated published shard differs from original HTTP206 receipt")
            scratch_out.flush()
            os.fsync(scratch_out.fileno())
            # Atomic, overwrite-refusing publication of the already-pinned
            # whole-object bytes. No second original .bin request is required.
            os.link(scratch, file, follow_symlinks=False)
            hydrated = True
    if (not file.is_file() or file.is_symlink()
            or not file.resolve(strict=True).is_relative_to(root)
            or file.stat().st_size != row["length"]
            or _hash_file(file) != receipt["published_shard_raw_sha256"]):
        raise ValueError("local packed Capnp shard does not equal original HTTP206 witness")
    decoder_hash = _hash_file(decoder_path)
    if decoder_hash != expected_decoder_sha256:
        raise ValueError("original-schema native decoder executable digest mismatches pin")
    requested = [str(decoder_path), "--file", str(file), "--section", section,
                 "--chunk-index", str(chunk_index), "--lang", "wikidata",
                 "--stream-name-rows", "--max-name-rows", str(max_name_rows)]
    targets = {q: [] for q in target_qids}
    count = 0
    total_bytes = 0
    with TemporaryDirectory(prefix="itir-original-name-rows-") as tmp:
        output = Path(tmp) / "native-rows.ndjson"
        err = Path(tmp) / "native.err"
        with output.open("wb") as out, err.open("wb") as stderr:
            result = subprocess.run(
                requested, stdout=out, stderr=stderr,
                timeout=timeout_seconds, check=False,
            )
        if result.returncode != 0:
            raise ValueError("native original name-row decoder failed or was truncated")
        if output.stat().st_size > max_stdout_mib * 1024**2:
            raise ValueError("native name-row output exceeds explicit byte budget")
        footer_seen = False
        with output.open("rb") as stream:
            while True:
                line = stream.readline(max_line_bytes + 1)
                if not line:
                    break
                if len(line) > max_line_bytes or not line.endswith(b"\n"):
                    raise ValueError("native name row too long/truncated")
                total_bytes += len(line)
                frame = _json_object(line)
                if frame.get("version") == _END:
                    if footer_seen or any(stream.read(1)):
                        raise ValueError("native row completion marker not terminal")
                    required = {
                        "version": _END, "section": section,
                        "chunk_index": chunk_index, "language": "wikidata",
                        "rows_emitted": count,
                        "candidate_only": True, "authority": False,
                    }
                    if frame != required:
                        raise ValueError("native complete-row count/authority mismatch")
                    footer_seen = True
                    break
                required_keys = {
                    "version", "section", "chunk_index", "language",
                    "row_index", "name", "node_id",
                }
                if (set(frame) != required_keys or frame.get("version") != _ROW
                        or frame.get("section") != section
                        or frame.get("chunk_index") != chunk_index
                        or frame.get("language") != "wikidata"
                        or type(frame.get("row_index")) is not int
                        or frame["row_index"] != count
                        or type(frame.get("name")) is not str
                        or type(frame.get("node_id")) is not int
                        or not 0 <= frame["node_id"] <= 2**64 - 1):
                    raise ValueError("native original name-row frame identity/order mismatch")
                if frame["name"] in targets:
                    targets[frame["name"]].append(frame["node_id"])
                    if len(targets[frame["name"]]) > max_name_rows:
                        raise ValueError("native duplicate name fibre exceeds row budget")
                count += 1
                if count > max_name_rows:
                    raise ValueError("native name rows exceed explicit bound")
        if not footer_seen:
            raise ValueError("native original name-row stream lacks final EOF certification")
        digest = _hash_file(output)
        if rows_output is not None:
            with rows_output.open("xb") as dest, output.open("rb") as src:
                shutil.copyfileobj(src, dest, 1024 * 1024)
            if _hash_file(rows_output) != digest:
                raise ValueError("persisted native row stream changed after decode")
    return {
        "version": _VERSION,
        "dataset_revision": dataset_revision, "section": section,
        "chunk_index": chunk_index, "language": "wikidata",
        "manifest_raw_sha256": manifest_sha256,
        "original_index_raw_sha256": original_index_sha256,
        "physical_original_name_chunk_receipt_sha256": _hash_file(receipt_path),
        "original_packed_chunk_raw_sha256": receipt["original_packed_range_raw_sha256"],
        "native_decoder_executable_sha256": decoder_hash,
        "packed_shard_hydrated_from_pinned_hf_whole_object": hydrated,
        "original_bin_requeried_for_hydration": False,
        "native_packed_chunk_rows_enumerated": count,
        "native_name_rows_stdout_sha256": digest,
        "native_stdout_bytes": total_bytes,
        "native_name_rows_file": str(rows_output) if rows_output is not None else None,
        "target_name_fibres": targets,
        "complete_native_row_stream_for_this_chunk": True,
        "name_duplicates_discarded": False,
        "all_original_name_chunks_verified": False,
        "full_name_domain_A1_instantiated": False,
        "global_name_absence_proved": False,
        "edit_authority": False,
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--original-index", type=Path, required=True)
    p.add_argument("--dataset-revision", required=True)
    p.add_argument("--manifest-sha256", required=True)
    p.add_argument("--original-index-sha256", required=True)
    p.add_argument("--section", choices=("nameOfNode", "nodeOfName"), required=True)
    p.add_argument("--chunk-index", type=int, required=True)
    p.add_argument("--physical-receipt", type=Path, required=True)
    p.add_argument("--shard-root", type=Path, required=True)
    p.add_argument("--decoder", type=Path, required=True)
    p.add_argument("--decoder-sha256", required=True,
                   help="independently computed sha256sum of locally compiled original Capnp decoder")
    p.add_argument("--qid", action="append", default=[])
    p.add_argument("--max-name-rows", type=int, default=10000000)
    p.add_argument("--max-stdout-mib", type=int, default=2048)
    p.add_argument("--timeout-seconds", type=int, default=600)
    p.add_argument("--rows-output", type=Path)
    p.add_argument("--hydrate-missing-shard", action="store_true",
                   help="fetch only full published object when original-equal physical receipt already exists")
    p.add_argument("--max-hydrate-mib", type=int, default=128)
    p.add_argument("--receipt-output", type=Path)
    args = p.parse_args()
    try:
        if args.receipt_output is not None and (
            args.receipt_output.exists() or args.receipt_output.is_symlink()
        ):
            raise ValueError("refuse overwrite native enumeration receipt")
        proof = enumerate_authenticated_name_chunk(
            manifest_path=args.manifest, original_index_path=args.original_index,
            dataset_revision=args.dataset_revision,
            manifest_sha256=args.manifest_sha256,
            original_index_sha256=args.original_index_sha256,
            section=args.section, chunk_index=args.chunk_index,
            receipt_path=args.physical_receipt, shard_root=args.shard_root,
            decoder_path=args.decoder,
            expected_decoder_sha256=args.decoder_sha256,
            target_qids=tuple(args.qid),
            max_name_rows=args.max_name_rows,
            max_stdout_mib=args.max_stdout_mib,
            timeout_seconds=args.timeout_seconds, rows_output=args.rows_output,
            hydrate_missing_shard=args.hydrate_missing_shard,
            max_hydrate_mib=args.max_hydrate_mib,
        )
        rendered = json.dumps(proof, sort_keys=True, indent=2) + "\n"
        if args.receipt_output:
            with args.receipt_output.open("x", encoding="utf-8") as out:
                out.write(rendered)
        else:
            print(rendered, end="")
        return 0
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError,
            subprocess.TimeoutExpired) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc),
                          "edit_authority": False}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
