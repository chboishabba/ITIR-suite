#!/usr/bin/env python3
"""One bounded/resumable physical -> native Zelph A1 evidence round.

Reuses existing ITIR HF original 206/whole-object transport, original
manifest/index crosswalk, source-equal shard materializer, and transactional
upstream-schema SQLite native-name audit. NO second graph index, no new
transport, no statement/P854 source truth or S29 authority. A complete
physical/native row census does not imply an Agda decoder adequacy proof.

Default dry run. --execute opts in to bounded physical HF traffic and
bounded native decoded row insertion, with exact independent SHA pins.
Rerun safely: prior receipts/shards/SQLite work are checked and reused.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import sys
from typing import Any

from audit_zelph_hf_name_section_bytes import audit_name_section
from audit_zelph_native_name_fibres import original_name_plan, run_native_name_audit
from materialize_original_equal_name_shards import materialization_plan, restore

_REV = re.compile(r"[0-9a-f]{40}\Z")
_SHA = re.compile(r"[0-9a-f]{64}\Z")
_MIB = 1024 * 1024
_SECTIONS = ("nodeOfName", "nameOfNode")


def _hash(path: Path) -> str:
    if path.is_symlink() or not path.is_file() or not 0 < path.stat().st_size:
        raise ValueError("pinned original native executable must be a real file")
    h = sha256()
    with path.open("rb") as data:
        for piece in iter(lambda: data.read(_MIB), b""):
            h.update(piece)
    return h.hexdigest()


def run_a1_evidence_round(
    *, manifest: Path, original_index: Path,
    dataset_revision: str, manifest_sha256: str,
    original_index_sha256: str, decoder: Path,
    decoder_sha256: str, node_receipts_dir: Path,
    inverse_receipts_dir: Path, shard_root: Path,
    sqlite_index: Path, import_physical_receipts_dirs: list[Path] | None = None,
    positive_roots_receipt: Path | None = None,
    sections: tuple[str, ...] = _SECTIONS,
    max_total_network_mib: int = 1024,
    max_new_physical_chunks_per_section: int = 4,
    max_new_materialized_chunks: int = 4,
    max_new_native_chunks: int = 8,
    max_chunk_mib: int = 256,
    max_rows_per_chunk: int = 10_000_000,
    decoder_timeout_seconds: int = 900,
    execute: bool = False,
) -> dict[str, Any]:
    if (type(dataset_revision) is not str or not _REV.fullmatch(dataset_revision)
            or any(type(value) is not str or not _SHA.fullmatch(value)
                   for value in (manifest_sha256, original_index_sha256,
                                 decoder_sha256))):
        raise ValueError("independent immutable original revision/manifest/index/decoder SHA pins required")
    if _hash(decoder) != decoder_sha256:
        raise ValueError("native original-schema decoder SHA changed from independently supplied pin")
    if (type(sections) is not tuple or not sections
            or len(set(sections)) != len(sections)
            or any(sec not in _SECTIONS for sec in sections)):
        raise ValueError("explicit nonempty original name-section selection required")
    for number, upper in (
        (max_total_network_mib, 65536), (max_chunk_mib, 16384),
        (max_new_physical_chunks_per_section, 10000),
        (max_new_materialized_chunks, 4096),
        (max_new_native_chunks, 10000),
        (max_rows_per_chunk, 100000000),
        (decoder_timeout_seconds, 7200),
    ):
        if type(number) is not int or not 0 <= number <= upper:
            raise ValueError("invalid cumulative/original native evidence budget")
    if (max_total_network_mib == 0 or max_chunk_mib == 0
            or max_rows_per_chunk == 0 or decoder_timeout_seconds == 0):
        raise ValueError("positive byte/chunk/row/decode bounds required")
    if type(execute) is not bool:
        raise ValueError("explicit boolean physical execution gate required")
    imports = import_physical_receipts_dirs or []
    if (not isinstance(imports, list) or len(imports) > 14
            or any(not isinstance(p, Path) or p.is_symlink() or not p.is_dir()
                   for p in imports)):
        raise ValueError("existing non-symlink original physical receipt import directories required")
    receipts = {"nodeOfName": node_receipts_dir, "nameOfNode": inverse_receipts_dir}
    for section, root in receipts.items():
        if root.is_symlink() or (root.exists() and not root.is_dir()):
            raise ValueError(f"unsafe original {section} physical receipt directory")
        if execute and (not root.parent.is_dir() or root.parent.is_symlink()):
            raise ValueError("original physical receipt destination parent missing or symlinked")
    for root in (shard_root, sqlite_index.parent):
        if root.is_symlink() or (root.exists() and not root.is_dir()):
            raise ValueError("unsafe native source evidence storage directory")
    if sqlite_index.is_symlink() or (execute and (
            not shard_root.parent.is_dir() or shard_root.parent.is_symlink()
            or not sqlite_index.parent.is_dir() or sqlite_index.parent.is_symlink())):
        raise ValueError("unsafe SQLite/native packed shard destination")
    if (shard_root.resolve().is_relative_to(node_receipts_dir.resolve())
            or shard_root.resolve().is_relative_to(inverse_receipts_dir.resolve())
            or receipts["nodeOfName"].resolve().is_relative_to(shard_root.resolve())
            or receipts["nameOfNode"].resolve().is_relative_to(shard_root.resolve())):
        raise ValueError("physical receipt roots and native packed shard root must be separate")

    # Reserve the ACTUAL two-sided original .bin range + published object bytes
    # across both sections, before making either section's live requests.
    total_budget = max_total_network_mib * _MIB
    reserved = 0
    selected = {}
    for section in sections:
        remaining = total_budget - reserved
        per_section_limit = max(1, remaining // _MIB)
        new_count = max_new_physical_chunks_per_section if remaining >= _MIB else 0
        options = dict(
            manifest_path=manifest, original_index_path=original_index,
            dataset_revision=dataset_revision, manifest_sha256=manifest_sha256,
            original_index_sha256=original_index_sha256, section=section,
            receipts_dir=receipts[section],
            import_physical_receipts_dirs=imports,
            save_published_root=shard_root, max_new_chunks=new_count,
            max_chunk_mib=max_chunk_mib,
            max_transfer_mib=per_section_limit,
        )
        plan = audit_name_section(**options, execute=False)
        booked = plan["planned_transfer_bytes"]
        if type(booked) is not int or not 0 <= booked <= remaining:
            raise ValueError("original whole-binary+published-shard network reservation overrun")
        reserved += booked
        selected[section] = (options, plan)
    # No execute touches any evidence directory until ALL source metadata,
    # original section domains, pins and the combined network cap pass.
    if execute:
        shard_root.mkdir(parents=True, exist_ok=True)
    physical = {}
    for section, (options, plan) in selected.items():
        physical[section] = audit_name_section(
            **options, execute=True
        ) if execute else plan
        observed = physical[section]
        if (type(observed.get("planned_transfer_bytes")) is not int
                or observed["planned_transfer_bytes"] > plan["planned_transfer_bytes"]):
            raise ValueError("original source physical transfer exceeded preflight reservation")

    materialized = None
    native = None
    remaining = total_budget - reserved
    network_from_materialization = 0
    known_dirs = [receipts[sec] for sec in _SECTIONS if receipts[sec].is_dir()]
    known_dirs.extend(imports)
    if shard_root.is_dir() and known_dirs:
        rest = materialization_plan(
            manifest=manifest, original_index=original_index,
            revision=dataset_revision, manifest_sha256=manifest_sha256,
            original_index_sha256=original_index_sha256,
            physical_receipts_dirs=known_dirs, shard_root=shard_root,
            max_new_chunks=(
                max_new_materialized_chunks if remaining >= _MIB else 0
            ),
            max_transfer_mib=max(1, remaining // _MIB),
            max_chunk_mib=max_chunk_mib,
        )
        network_from_materialization = rest["planned_one_sided_hf_bytes"]
        if (type(network_from_materialization) is not int
                or not 0 <= network_from_materialization <= remaining):
            raise ValueError("published-shard restoration exceeds global network budget")
        materialized = restore(plan=rest) if execute else rest
        if execute and any(
            key not in materialized for key in ("saved_new_chunks",)
        ):
            raise ValueError("missing native source materialization receipt")
    if execute and shard_root.is_dir() and known_dirs:
        native_plan = original_name_plan(
            manifest=manifest, original_index=original_index,
            manifest_sha256=manifest_sha256,
            original_index_sha256=original_index_sha256,
            revision=dataset_revision,
            physical_receipts_dirs=known_dirs,
            shard_root=shard_root, max_chunk_mib=max_chunk_mib,
        )
        native = run_native_name_audit(
            plan=native_plan, sqlite_index=sqlite_index,
            decoder=decoder, max_new_chunks=max_new_native_chunks,
            max_rows_per_chunk=max_rows_per_chunk,
            timeout_seconds=decoder_timeout_seconds,
            positive_roots_receipt=positive_roots_receipt,
        )
    actual_net = reserved + network_from_materialization
    if actual_net > total_budget:
        raise ValueError("original source combined physical/rematerialization budget violated")
    all_name_native = bool(native and native.get(
        "all_original_name_section_native_chunks_decoded") is True)
    inverse_equal = (
        native.get("both_source_name_sections_pair_multiplicities_equal")
        if native is not None else None
    )
    complete = bool(native and native.get(
        "all_original_name_key_fibres_verified") is True)
    return {
        "version": "itir.zelph.original_a1_one_round_maxcut.v1",
        "dataset_revision": dataset_revision,
        "manifest_sha256": manifest_sha256,
        "original_index_sha256": original_index_sha256,
        "native_decoder_sha256": decoder_sha256,
        "sections": list(sections),
        "physical": physical,
        "materialization": materialized,
        "native": native,
        "execute": execute,
        "max_total_network_bytes": total_budget,
        "max_two_sided_original_source_network_bytes": reserved,
        "max_one_sided_published_shard_network_bytes": network_from_materialization,
        "planned_total_network_bytes": actual_net,
        "network_budget_respected": actual_net <= total_budget,
        "source_native_all_name_sections_observed": all_name_native,
        "both_native_name_section_pair_multiplicities_equal": inverse_equal,
        "original_name_fibres_complete_as_conditional_source_witness": complete,
        "formal_agda_A1_decoder_adequacy_weld_proved": False,
        "original_A2_adjacency_query_closure_proved": False,
        "wikidata_statement_p854_source_supported": False,
        "slr_s29_live_pg_persistence_paid": False,
        "external_nora_export_paid": False,
        "edit_authority": False,
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--original-index", type=Path, required=True)
    p.add_argument("--dataset-revision", required=True)
    p.add_argument("--manifest-sha256", required=True)
    p.add_argument("--original-index-sha256", required=True)
    p.add_argument("--decoder", type=Path, required=True)
    p.add_argument("--decoder-sha256", required=True)
    p.add_argument("--node-receipts-dir", type=Path, required=True)
    p.add_argument("--inverse-receipts-dir", type=Path, required=True)
    p.add_argument("--shard-root", type=Path, required=True)
    p.add_argument("--sqlite-index", type=Path, required=True)
    p.add_argument("--import-physical-receipts-dir", type=Path, action="append")
    p.add_argument("--positive-roots-receipt", type=Path)
    p.add_argument("--section", action="append", choices=_SECTIONS)
    p.add_argument("--max-total-network-mib", type=int, default=1024)
    p.add_argument("--max-new-physical-chunks-per-section", type=int, default=4)
    p.add_argument("--max-new-materialized-chunks", type=int, default=4)
    p.add_argument("--max-new-native-chunks", type=int, default=8)
    p.add_argument("--max-chunk-mib", type=int, default=256)
    p.add_argument("--max-rows-per-chunk", type=int, default=10000000)
    p.add_argument("--decoder-timeout-seconds", type=int, default=900)
    p.add_argument("--execute", action="store_true")
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    try:
        if args.output is not None and (args.output.exists() or args.output.is_symlink()):
            raise ValueError("refuse overwrite immutable combined original A1 round receipt")
        result = run_a1_evidence_round(
            manifest=args.manifest, original_index=args.original_index,
            dataset_revision=args.dataset_revision,
            manifest_sha256=args.manifest_sha256,
            original_index_sha256=args.original_index_sha256,
            decoder=args.decoder, decoder_sha256=args.decoder_sha256,
            node_receipts_dir=args.node_receipts_dir,
            inverse_receipts_dir=args.inverse_receipts_dir,
            shard_root=args.shard_root, sqlite_index=args.sqlite_index,
            import_physical_receipts_dirs=args.import_physical_receipts_dir,
            positive_roots_receipt=args.positive_roots_receipt,
            sections=tuple(args.section or _SECTIONS),
            max_total_network_mib=args.max_total_network_mib,
            max_new_physical_chunks_per_section=args.max_new_physical_chunks_per_section,
            max_new_materialized_chunks=args.max_new_materialized_chunks,
            max_new_native_chunks=args.max_new_native_chunks,
            max_chunk_mib=args.max_chunk_mib,
            max_rows_per_chunk=args.max_rows_per_chunk,
            decoder_timeout_seconds=args.decoder_timeout_seconds,
            execute=args.execute,
        )
        body = json.dumps(result, indent=2, sort_keys=True) + "\n"
        if args.output is not None:
            with args.output.open("x", encoding="utf-8") as output:
                output.write(body)
        else:
            print(body, end="")
        return 0
    except (ValueError, OSError, KeyError, TypeError,
            json.JSONDecodeError) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc),
                          "edit_authority": False}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
