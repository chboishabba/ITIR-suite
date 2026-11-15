#!/usr/bin/env python3
"""A1: resumable, collision-preserving ORIGINAL native name-row enumeration.

Each eligible shard MUST be independently source-equal at the pinned original
.bin HTTP206 range (existing physical receipts) and have a matching retained
published packed file. Runs the ORIGINAL-schema C++ decoder in
--stream-name-rows mode. Rows enter a SQLite scratch INDEX only after the
native terminal frame AND process exit 0. A failed chunk rolls back completely.

The exact original name-key universe and inverse name↔node fibres are ONLY
claimed when both complete indexed name sections have been decoded, physically
covered, all receipts are present and every pair's multiplicity agrees. This
does not promote Wikipedia oldid, Wikidata statement/P854, source truth or edit
authority. SQLite is local audit scratch, NOT SLR S29 persistence.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import sqlite3
import subprocess
import sys
import tempfile
from typing import Any, Callable

from audit_zelph_hf_name_section_bytes import _check_receipt, _read_receipt
from verify_zelph_bin_shard_exact import _ARTIFACT, _manifest_index, _read_json
from verify_zelph_index_manifest_original import verify_index_manifest_files

_SHA = re.compile(r"[0-9a-f]{64}\Z")
_REV = re.compile(r"[0-9a-f]{40}\Z")
_SECTIONS = ("nodeOfName", "nameOfNode")
_ROW_VERSION = "itir.zelph.native_original_name_row.v1"
_END_VERSION = "itir.zelph.native_original_name_rows_end.v1"
_MIB = 1024 * 1024
_DDL = (
    "CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL)",
    """CREATE TABLE IF NOT EXISTS native_rows (
       section TEXT NOT NULL, chunk_index INTEGER NOT NULL, row_index INTEGER NOT NULL,
       name TEXT NOT NULL, node_id TEXT NOT NULL,
       PRIMARY KEY(section, chunk_index, row_index))""",
    "CREATE INDEX IF NOT EXISTS name_node_idx ON native_rows(name,node_id,section)",
    "CREATE INDEX IF NOT EXISTS node_name_idx ON native_rows(node_id,name,section)",
    """CREATE TABLE IF NOT EXISTS completed_chunks (
       section TEXT NOT NULL, chunk_index INTEGER NOT NULL,
       physical_receipt_sha256 TEXT NOT NULL, packed_sha256 TEXT NOT NULL,
       decoder_sha256 TEXT NOT NULL, stream_sha256 TEXT NOT NULL,
       rows_emitted INTEGER NOT NULL,
       PRIMARY KEY(section,chunk_index))""",
)


def _file_sha(path: Path, limit: int | None = None) -> str:
    if not path.is_file() or path.is_symlink():
        raise ValueError("missing or symlinked original source artifact")
    if limit is not None and not 0 < path.stat().st_size <= limit:
        raise ValueError("source evidence size exceeds explicit limit")
    h = sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(_MIB), b""):
            h.update(block)
    return h.hexdigest()


def _strict(raw: bytes) -> dict:
    def no_duplicates(items):
        obj = {}
        for k, v in items:
            if k in obj:
                raise ValueError("duplicate original-native JSON key")
            obj[k] = v
        return obj
    row = json.loads(raw.decode("utf-8"), object_pairs_hook=no_duplicates,
                     parse_constant=lambda v: (_ for _ in ()).throw(
                         ValueError("invalid native number: " + v)))
    if type(row) is not dict:
        raise ValueError("original native row must be a JSON object")
    return row


def original_name_plan(*, manifest: Path, original_index: Path,
                       manifest_sha256: str, original_index_sha256: str,
                       revision: str, physical_receipts_dirs: list[Path],
                       shard_root: Path, max_chunk_mib: int = 256) -> dict:
    if (type(revision) is not str or not _REV.fullmatch(revision)
            or type(manifest_sha256) is not str or not _SHA.fullmatch(manifest_sha256)
            or type(original_index_sha256) is not str or not _SHA.fullmatch(original_index_sha256)
            or type(max_chunk_mib) is not int or not 0 < max_chunk_mib <= 16384):
        raise ValueError("pinned immutable revision, manifest, index and chunk budget required")
    if not physical_receipts_dirs or len(physical_receipts_dirs) > 16:
        raise ValueError("1..16 physical original-equality receipt directories required")
    if any(not d.is_dir() or d.is_symlink() for d in physical_receipts_dirs):
        raise ValueError("missing or symlinked physical receipt directory")
    if not shard_root.is_dir() or shard_root.is_symlink():
        raise ValueError("existing real source-equal packed shard root required")
    root = shard_root.resolve(strict=True)
    meta = verify_index_manifest_files(
        manifest_path=manifest, index_path=original_index,
        manifest_sha256=manifest_sha256, index_sha256=original_index_sha256)
    index = _manifest_index(_read_json(manifest, 16 * _MIB), _ARTIFACT)
    names = {(section, num): row for (section, num), row in index.items()
             if section in _SECTIONS}
    if not names or any(num not in range(meta["section_chunk_counts"][section + "ChunkCount"])
                        for section, num in names):
        raise ValueError("original named-section manifest domain incomplete")
    entries = []
    for (section, chunk), row in sorted(names.items()):
        proof_path = None
        proof_hash = None
        for receipts_dir in physical_receipts_dirs:
            p = receipts_dir / f"{section}-{chunk:06d}.json"
            if p.is_symlink():
                raise ValueError("symlinked original-range receipt rejected")
            if not p.exists():
                continue
            digest = _file_sha(p, _MIB)
            if proof_path is None:
                proof_path, proof_hash = p, digest
            else:
                other = _read_receipt(p)
                first = _read_receipt(proof_path)
                # Different auditors may add saved-path/status details,
                # while preserving the same immutable byte identity.
                comparable = (
                    "dataset_revision", "original_manifest_raw_sha256",
                    "original_index_raw_sha256", "section", "chunk_index",
                    "original_source_offset", "source_range_end_inclusive",
                    "bytes_compared", "published_object_uri",
                    "original_binary_uri", "source_bin_size_bytes",
                    "published_shard_raw_sha256",
                    "original_packed_range_raw_sha256",
                )
                if any(other.get(k) != first.get(k) for k in comparable):
                    raise ValueError("conflicting original-range receipts for same native chunk")
        if proof_path is None:
            continue
        proof = _read_receipt(proof_path)
        _check_receipt(
            proof, row=row, number=chunk, section=section, rev=revision,
            manifest_sha=manifest_sha256, index_sha=original_index_sha256,
            bin_size=meta["original_bin_size_bytes"])
        if row["length"] > max_chunk_mib * _MIB:
            raise ValueError("original name shard outside per-chunk budget")
        shard = (root / row["relative"]).resolve(strict=False)
        if not shard.is_relative_to(root) or shard.is_symlink():
            raise ValueError("unsafe source-equal local shard path")
        if not shard.is_file() or shard.stat().st_size != row["length"]:
            # Missing saved bytes are unmaterialized, not negative QID evidence.
            continue
        sha = _file_sha(shard)
        if sha != proof["published_shard_raw_sha256"]:
            raise ValueError("saved packed name shard differs from genuine original-range receipt")
        entries.append({
            "section": section, "chunk_index": chunk,
            "physical_receipt": str(proof_path), "physical_receipt_sha256": proof_hash,
            "packed_shard": str(shard), "packed_sha256": sha,
            "physical_bytes": row["length"],
        })
    return {
        "version": "itir.zelph.native_original_name_fibre_plan.v1",
        "dataset_revision": revision, "manifest_sha256": manifest_sha256,
        "original_index_sha256": original_index_sha256,
        "original_bin_size_bytes": meta["original_bin_size_bytes"],
        "source_section_chunk_counts": {
            section: meta["section_chunk_counts"][section + "ChunkCount"]
            for section in _SECTIONS},
        "available_verified_native_chunks": entries,
        "available_native_chunk_count": len(entries),
        "unmaterialized_chunks_do_not_imply_name_absence": True,
        "original_http206_reverified_in_this_native_run": False,
        "local_audit_not_slr_s29": True,
        "edit_authority": False,
    }


def _validated_native_frame(frame: dict, *, section: str, chunk: int,
                            expected_row_index: int, done: bool) -> tuple[str, Any]:
    if (frame.get("section") != section or frame.get("chunk_index") != chunk
            or frame.get("language") != "wikidata"):
        raise ValueError("native name row/terminal section and language mismatch")
    if done:
        if (frame.get("version") != _END_VERSION or
                type(frame.get("rows_emitted")) is not int or
                frame["rows_emitted"] != expected_row_index or
                frame.get("candidate_only") is not True or
                frame.get("authority") is not False):
            raise ValueError("missing/mismatched native packed EOF terminal frame")
        return ("end", None)
    if (frame.get("version") != _ROW_VERSION or
            type(frame.get("row_index")) is not int or
            frame["row_index"] != expected_row_index or
            type(frame.get("name")) is not str or
            type(frame.get("node_id")) is not int or
            not 0 <= frame["node_id"] <= 2**64 - 1):
        raise ValueError("native original name row order/type/coordinate invalid")
    return ("row", (frame["name"], str(frame["node_id"])))


def _stream_native_chunk(conn: sqlite3.Connection, *, entry: dict,
                         decoder: Path, decoder_sha: str,
                         max_rows: int = 10_000_000,
                         timeout_seconds: int = 900,
                         popen: Callable[..., Any] = subprocess.Popen) -> tuple[int, str]:
    section, chunk = entry["section"], entry["chunk_index"]
    if (type(max_rows) is not int or not 0 < max_rows <= 100000000
            or type(timeout_seconds) is not int or not 0 < timeout_seconds <= 7200):
        raise ValueError("positive bounded original native row/decoder budgets required")
    cmd = [str(decoder), "--file", entry["packed_shard"],
           "--section", section, "--chunk-index", str(chunk),
           "--lang", "wikidata", "--stream-name-rows",
           "--max-name-rows", str(max_rows)]
    count, ended, stream_hash = 0, False, sha256()
    # SQLite transaction rollback guards against a native failure that emitted
    # many plausible rows before a trailing-byte corruption/timeout.
    with tempfile.TemporaryFile(mode="w+b") as stderr:
        process = popen(cmd, stdout=subprocess.PIPE, stderr=stderr)
        try:
            if process.stdout is None:
                raise ValueError("native decoder emitted no stdout stream")
            # A bounded C++ output line; no unbounded stdout.read().
            while True:
                wire = process.stdout.readline(4 * _MIB + 1)
                if not wire:
                    break
                if len(wire) > 4 * _MIB or not wire.endswith(b"\n"):
                    raise ValueError("native JSONL record exceeds bound or is unterminated")
                stream_hash.update(wire)
                frame = _strict(wire)
                kind, value = _validated_native_frame(
                    frame, section=section, chunk=chunk,
                    expected_row_index=count, done=frame.get("version") == _END_VERSION)
                if kind == "end":
                    if ended:
                        raise ValueError("duplicate native packed terminal frame")
                    ended = True
                    # No further bytes, including forged rows after terminal.
                    if process.stdout.read(1):
                        raise ValueError("trailing native rows after EOF frame")
                    break
                if ended:
                    raise ValueError("rows emitted after final original packed frame")
                if count >= max_rows:
                    raise ValueError("native name row budget exceeded")
                conn.execute(
                    "INSERT INTO native_rows VALUES (?,?,?,?,?)",
                    (section, chunk, count, value[0], value[1]))
                count += 1
            rc = process.wait(timeout=timeout_seconds)
            if rc != 0 or not ended:
                stderr.seek(0)
                message = stderr.read(1024).decode("utf-8", "replace")
                raise ValueError("native decoder failed/omitted exact EOF: " + message)
            conn.execute(
                "INSERT INTO completed_chunks VALUES (?,?,?,?,?,?,?)",
                (section, chunk, entry["physical_receipt_sha256"], entry["packed_sha256"],
                 decoder_sha, stream_hash.hexdigest(), count))
            return count, stream_hash.hexdigest()
        except BaseException:
            try:
                process.kill()
            except ProcessLookupError:
                pass
            process.wait()
            raise
        finally:
            if process.stdout is not None:
                process.stdout.close()


def _equal_name_node_multisets(conn: sqlite3.Connection) -> bool:
    # SQLite may use temp files for GROUP BY, never Python per-row storage.
    q = """SELECT name,node_id,COUNT(*) AS n FROM native_rows
            WHERE section=? GROUP BY name,node_id"""
    left = q.replace("?", "'nodeOfName'")
    right = q.replace("?", "'nameOfNode'")
    # In SQLite EXCEPT is set difference over grouped rows (name,node,count),
    # preserving duplicate multiplicities as a COUNT field.
    return (conn.execute(f"SELECT 1 FROM ({left} EXCEPT {right}) LIMIT 1").fetchone()
            is None and
            conn.execute(f"SELECT 1 FROM ({right} EXCEPT {left}) LIMIT 1").fetchone()
            is None)


def run_native_name_audit(*, plan: dict, sqlite_index: Path,
                          decoder: Path, max_new_chunks: int = 4,
                          max_rows_per_chunk: int = 10_000_000,
                          timeout_seconds: int = 900,
                          popen: Callable[..., Any] = subprocess.Popen) -> dict:
    if (type(max_new_chunks) is not int or not 0 <= max_new_chunks <= 10000
            or not decoder.is_file() or decoder.is_symlink()
            or sqlite_index.is_symlink()):
        raise ValueError("valid native decoder, audit index and chunk budget required")
    decoder_sha = _file_sha(decoder)
    pins = {
        "version": plan["version"], "revision": plan["dataset_revision"],
        "manifest_sha256": plan["manifest_sha256"],
        "index_sha256": plan["original_index_sha256"],
        "original_bin_size": str(plan["original_bin_size_bytes"]),
        "decoder_sha256": decoder_sha,
    }
    if not sqlite_index.parent.is_dir() or sqlite_index.parent.is_symlink():
        raise ValueError("local native name-audit index parent missing/symlinked")
    with sqlite3.connect(sqlite_index) as db:
        for statement in _DDL:
            db.execute(statement)
        previously = dict(db.execute("SELECT key,value FROM metadata"))
        if previously and previously != pins:
            raise ValueError("SQLite name fibre audit pins differ: refuse cross-revision reuse")
        if not previously:
            if (db.execute("SELECT COUNT(*) FROM completed_chunks").fetchone()[0] or
                    db.execute("SELECT COUNT(*) FROM native_rows").fetchone()[0]):
                raise ValueError("unidentified existing native rows cannot be adopted as source proof")
            db.executemany("INSERT INTO metadata VALUES (?,?)", pins.items())
        present = {(row[0],row[1]): row for row in
                   db.execute("SELECT section,chunk_index,physical_receipt_sha256,packed_sha256,decoder_sha256 FROM completed_chunks")}
        eligible = {(r["section"], r["chunk_index"]): r for r in plan["available_verified_native_chunks"]}
        if set(present) - set(eligible):
            raise ValueError("previous native chunks lack current physical receipt/shard evidence")
        for key, row in present.items():
            entry = eligible[key]
            if row[2:5] != (entry["physical_receipt_sha256"], entry["packed_sha256"], decoder_sha):
                raise ValueError("persisted native chunk differs from current original source/decoder")
        added = []
        for entry in plan["available_verified_native_chunks"]:
            key = (entry["section"], entry["chunk_index"])
            if key in present or len(added) >= max_new_chunks:
                continue
            with db:
                rows, stream_digest = _stream_native_chunk(
                    db, entry=entry, decoder=decoder, decoder_sha=decoder_sha,
                    max_rows=max_rows_per_chunk, timeout_seconds=timeout_seconds,
                    popen=popen)
            added.append({"section": key[0], "chunk_index": key[1],
                          "rows": rows, "stream_sha256": stream_digest})
        counts = dict(db.execute(
            "SELECT section,COUNT(*) FROM completed_chunks GROUP BY section"))
        all_name_chunks = all(
            counts.get(section, 0) == plan["source_section_chunk_counts"][section]
            for section in _SECTIONS)
        parity = _equal_name_node_multisets(db) if all_name_chunks else None
        total = db.execute("SELECT COUNT(*) FROM native_rows").fetchone()[0]
        duplicate_groups = db.execute(
            "SELECT COUNT(*) FROM (SELECT name,node_id FROM native_rows "
            "WHERE section='nodeOfName' GROUP BY name,node_id HAVING COUNT(*)>1)"
        ).fetchone()[0]
        # Name-key multiplicity can be >1 even if each pair occurs once.
        multi_fibre_names = db.execute(
            "SELECT COUNT(*) FROM (SELECT name FROM native_rows "
            "WHERE section='nodeOfName' GROUP BY name HAVING COUNT(DISTINCT node_id)>1)"
        ).fetchone()[0]
        return {
            "version": "itir.zelph.native_original_name_fibres.v1",
            "dataset_revision": plan["dataset_revision"],
            "manifest_sha256": plan["manifest_sha256"],
            "original_index_sha256": plan["original_index_sha256"],
            "native_decoder_sha256": decoder_sha,
            "source_section_chunk_counts": plan["source_section_chunk_counts"],
            "native_decoded_chunk_counts": {sec: counts.get(sec, 0) for sec in _SECTIONS},
            "native_rows_persisted": total,
            "newly_completed_chunks": added,
            "duplicate_original_name_node_pair_groups": duplicate_groups,
            "original_name_keys_with_multiple_nodes_in_checked_rows": multi_fibre_names,
            "all_original_name_section_native_chunks_decoded": all_name_chunks,
            "both_source_name_sections_pair_multiplicities_equal": parity,
            "all_original_name_key_fibres_verified": all_name_chunks and parity is True,
            "all_packed_bytes_reverified_by_live_http206_in_same_native_run": False,
            "native_original_packed_footer_and_process_exit_checked_per_chunk": True,
            "wikidata_qid_global_absence_proved_before_full_source_cover": False,
            "a1_formal_kernel_instantiation_paid": False,
            "source_support_paid": False,
            "original_full_bin_digest_verified": False,
            "left_right_root_adjacency_verified": False,
            "p854_source_support_paid": False,
            "s29_review_persistence_paid": False,
            "edit_authority": False,
        }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--original-index", type=Path, required=True)
    p.add_argument("--manifest-sha256", required=True)
    p.add_argument("--original-index-sha256", required=True)
    p.add_argument("--dataset-revision", required=True)
    p.add_argument("--physical-receipts-dir", type=Path, action="append", required=True)
    p.add_argument("--shard-root", type=Path, required=True)
    p.add_argument("--decoder", type=Path, required=True)
    p.add_argument("--sqlite-index", type=Path, required=True)
    p.add_argument("--max-new-chunks", type=int, default=4)
    p.add_argument("--max-chunk-mib", type=int, default=256)
    p.add_argument("--max-rows-per-chunk", type=int, default=10_000_000)
    p.add_argument("--decoder-timeout-seconds", type=int, default=900)
    p.add_argument("--execute", action="store_true")
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    try:
        plan = original_name_plan(
            manifest=args.manifest, original_index=args.original_index,
            manifest_sha256=args.manifest_sha256,
            original_index_sha256=args.original_index_sha256,
            revision=args.dataset_revision,
            physical_receipts_dirs=args.physical_receipts_dir,
            shard_root=args.shard_root, max_chunk_mib=args.max_chunk_mib)
        if not args.execute:
            print(json.dumps(plan, sort_keys=True, indent=2))
            return 0
        result = run_native_name_audit(
            plan=plan, sqlite_index=args.sqlite_index, decoder=args.decoder,
            max_new_chunks=args.max_new_chunks,
            max_rows_per_chunk=args.max_rows_per_chunk,
            timeout_seconds=args.decoder_timeout_seconds)
        wire = json.dumps(result, sort_keys=True, indent=2) + "\n"
        if args.output:
            with args.output.open("x", encoding="utf-8") as f:
                f.write(wire)
        else:
            print(wire, end="")
        return 0
    except (ValueError, OSError, TypeError, KeyError, json.JSONDecodeError,
            sqlite3.DatabaseError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc),
                          "edit_authority": False}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
