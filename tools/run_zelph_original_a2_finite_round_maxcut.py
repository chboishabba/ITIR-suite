#!/usr/bin/env python3
"""Bounded original HTTP206 -> original Capnp LR -> finite-word A2 round.

Reuses exact original adjacency section auditor, original-equal packed shard
restorer, original native selected-node LR scanner and finite-word evaluator.
A selected-node row is exact ONLY after every physical LR chunk has been
original-byte checked and natively scanned. Partial coverage is UNKNOWN.
Default plan has no network or SQLite mutations; --execute is explicit.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import sys

from audit_zelph_hf_original_adjacency_sections import audit_adjacency_section
from audit_zelph_native_original_lr_roots import (
    _roots_from_receipt, native_original_lr_plan, run_native_original_lr,
)
from audit_zelph_finite_query_family import _strict_json
from close_original_http206_lr_finite_words import original_http206_finite_words
from materialize_original_equal_name_shards import materialization_plan, restore
from verify_zelph_index_manifest_original import verify_index_manifest_files

SHA = re.compile(r"[0-9a-f]{64}\Z")
REV = re.compile(r"[0-9a-f]{40}\Z")
MIB = 1024**2
DIRECTIONS = ("left", "right")


def digest(path: Path) -> str:
    if path.is_symlink() or not path.is_file():
        raise ValueError("missing/symlinked immutable A2 evidence")
    h = sha256()
    with path.open("rb") as src:
        for piece in iter(lambda: src.read(MIB), b""):
            h.update(piece)
    return h.hexdigest()


def read_existing_scans(directory: Path, *, revision: str, manifest_sha: str,
                        index_sha: str, decoder_sha: str, root_sha: str,
                        root_nodes: dict, source_counts: dict) -> list:
    if not directory.exists():
        return []
    if directory.is_symlink() or not directory.is_dir():
        raise ValueError("invalid original A2 scan receipt directory")
    paths = sorted(directory.glob("original-lr-scan-*.json"))
    if len(paths) > 64:
        raise ValueError("more than 64 numeric frontier scan receipts")
    audits, seen = [], set()
    expected = {
        "version": "itir.zelph.original_lr_native_complete_chunk_scans.v1",
        "dataset_revision": revision, "manifest_sha256": manifest_sha,
        "original_index_sha256": index_sha, "decoder_binary_sha256": decoder_sha,
        "positive_roots_receipt_sha256": root_sha,
        "root_qid_node_ids": root_nodes,
        "source_section_chunk_counts": source_counts,
        "all_source_equal_original_chunks_natively_scanned": True,
        "all_selected_root_one_hop_adjacencies_complete": True,
        "selected_root_adjacency_equal_exact_original_http206_bytes": True,
        "edit_authority": False,
    }
    for p in paths:
        if p.is_symlink():
            raise ValueError("symlink original native LR scan")
        entry, sha = _strict_json(p, 16*MIB)
        cohort_sqlite = p.with_suffix(".sqlite")
        old_sqlite_sha = entry.get("completed_original_native_cohort_sqlite_sha256")
        if (type(old_sqlite_sha) is not str or not SHA.fullmatch(old_sqlite_sha)
                or not cohort_sqlite.is_file() or cohort_sqlite.is_symlink()
                or digest(cohort_sqlite) != old_sqlite_sha):
            raise ValueError("old complete original native LR scan SQLite snapshot SHA drift")
        for key, correct in expected.items():
            if type(entry.get(key)) is not type(correct) or entry[key] != correct:
                raise ValueError("old original native LR scan identity/coverage drift: " + key)
        nodes = entry.get("target_numeric_nodes")
        if (not isinstance(nodes, list) or not nodes or len(nodes) > 256
                or nodes != sorted(set(nodes))
                or any(type(n) is not int or not 0 <= n <= 2**64-1 for n in nodes)
                or not set(root_nodes.values()) <= set(nodes)
                or tuple(nodes) in seen):
            raise ValueError("malformed/duplicate original LR numeric target set")
        seen.add(tuple(nodes))
        if entry.get("native_decoded_source_equal_chunks_by_section") != source_counts:
            raise ValueError("historical native LR scan lacks complete original source sections")
        audits.append((entry, sha))
    return audits


def run_a2_round(
    *, manifest: Path, original_index: Path, dataset_revision: str,
    manifest_sha256: str, original_index_sha256: str,
    decoder: Path, decoder_sha256: str,
    positive_roots_receipt: Path, query_family: Path,
    query_family_sha256: str,
    left_receipts_dir: Path, right_receipts_dir: Path,
    shard_root: Path, native_audit_dir: Path,
    import_receipt_dirs: list[Path] | None = None,
    max_network_mib: int = 1024, max_physical_per_section: int = 8,
    max_restore: int = 8, max_native_chunks: int = 16,
    max_numeric_frontier: int = 64, max_chunk_mib: int = 256,
    max_neighbors: int = 200000, max_frontier: int = 200000,
    max_steps: int = 16, timeout_seconds: int = 900,
    execute: bool = False,
) -> dict:
    if (type(dataset_revision) is not str or not REV.fullmatch(dataset_revision)
            or any(type(x) is not str or not SHA.fullmatch(x)
                   for x in (manifest_sha256, original_index_sha256,
                             decoder_sha256, query_family_sha256))):
        raise ValueError("immutable original source/decoder/family pins required")
    if digest(decoder) != decoder_sha256 or digest(query_family) != query_family_sha256:
        raise ValueError("independently pinned decoder or original finite family SHA mismatch")
    caps = ((max_network_mib, 65536, 1), (max_physical_per_section,4096,0),
            (max_restore,4096,0), (max_native_chunks,4096,0),
            (max_numeric_frontier,256,0), (max_chunk_mib,16384,1),
            (max_neighbors,1000000,1), (max_frontier,1000000,1),
            (max_steps,64,1), (timeout_seconds,7200,1))
    if type(execute) is not bool or any(
        type(n) is not int or not minimum <= n <= maximum
        for n, maximum, minimum in caps
    ):
        raise ValueError("bounded original LR source/network/native resource limits required")
    imports = import_receipt_dirs or []
    if (not isinstance(imports, list) or len(imports) > 14
            or any(not isinstance(d,Path) or not d.is_dir() or d.is_symlink()
                   for d in imports)):
        raise ValueError("original HTTP206 receipt import directories invalid")
    roots, proof = _roots_from_receipt(positive_roots_receipt)
    if (proof.get("dataset_revision") != dataset_revision
            or proof.get("manifest_sha256") != manifest_sha256
            or proof.get("original_index_sha256") != original_index_sha256):
        raise ValueError("positive original QID name roots differ from source pins")
    family, _ = _strict_json(query_family)
    if (family.get("version") != "itir.zelph.finite_lr_query_family.v1"
            or family.get("qid_root_nodes") != roots
            or not isinstance(family.get("queries"), list) or not family["queries"]):
        raise ValueError("declared original LR family/QID roots mismatch")
    if len(family["queries"]) > 10000:
        raise ValueError("original finite query family exceeds fixed row count")
    labels = set()
    for item in family["queries"]:
        if not isinstance(item, dict):
            raise ValueError("finite original LR query entry must be object")
        label, qid, word = item.get("id"), item.get("qid"), item.get("word")
        if (type(label) is not str or not label or label in labels
                or type(qid) is not str or qid not in roots
                or type(word) is not list or len(word) > max_steps
                or any(type(direction) is not str or direction not in DIRECTIONS
                       for direction in word)):
            raise ValueError("unrecognised finite original LR query word, QID or duplicate label")
        labels.add(label)
    if len(set(roots.values())) > 256:
        raise ValueError("overlarge source-native positive root set")
    geometry = verify_index_manifest_files(
        manifest_path=manifest, index_path=original_index,
        manifest_sha256=manifest_sha256, index_sha256=original_index_sha256)
    counts = {s:geometry["section_chunk_counts"][s+"ChunkCount"] for s in DIRECTIONS}
    if any(n <= 0 for n in counts.values()):
        raise ValueError("original source adjacency geometry incomplete")
    physical_dirs = {"left":left_receipts_dir, "right":right_receipts_dir}
    for r in (left_receipts_dir, right_receipts_dir, shard_root, native_audit_dir):
        if r.is_symlink() or (r.exists() and not r.is_dir()) or (
            execute and (not r.parent.is_dir() or r.parent.is_symlink())
        ):
            raise ValueError("unsafe original LR physical/native workspace root")
    for r in physical_dirs.values():
        if (shard_root.resolve() == r.resolve()
                or shard_root.resolve().is_relative_to(r.resolve())
                or r.resolve().is_relative_to(shard_root.resolve())):
            raise ValueError("packed and physical original LR evidence roots overlap")
    root_sha = digest(positive_roots_receipt)
    prior = read_existing_scans(
        native_audit_dir, revision=dataset_revision,
        manifest_sha=manifest_sha256, index_sha=original_index_sha256,
        decoder_sha=decoder_sha256, root_sha=root_sha,
        root_nodes=roots, source_counts=counts)
    earlier = original_http206_finite_words(
        query_family=family, audits=prior, max_frontier=max_frontier,
        max_steps=max_steps) if prior else None
    existing_roots = set(roots.values())
    needed = earlier["next_numeric_nodes_to_native_scan"] if earlier else []
    limited = max(0, min(max_numeric_frontier, 256-len(existing_roots)))
    extras = [n for n in needed if n not in existing_roots][:limited]
    do_wave = not (earlier and earlier["all_declared_original_lr_words_closed"])
    if earlier and needed and not extras:
        do_wave = False
    cohort = sorted(existing_roots | set(extras))
    token = sha256(json.dumps(cohort, separators=(",",":")).encode()).hexdigest()
    scan_sqlite = native_audit_dir / ("original-lr-scan-"+token+".sqlite")
    scan_receipt = native_audit_dir / ("original-lr-scan-"+token+".json")
    if scan_sqlite.is_symlink() or scan_receipt.is_symlink():
        raise ValueError("original LR cohort SQLite/receipt symlink refused")
    # Two-sided HTTP206 source+standalone shard bytes for BOTH directions
    # are planned before a single network request.
    remaining = max_network_mib*MIB
    plans = {}
    for s in DIRECTIONS:
        options = dict(
            manifest_path=manifest, original_index_path=original_index,
            dataset_revision=dataset_revision, manifest_sha256=manifest_sha256,
            original_index_sha256=original_index_sha256,
            section=s, receipts_dir=physical_dirs[s],
            save_published_root=shard_root,
            import_physical_receipts_dirs=imports,
            max_chunk_mib=max_chunk_mib,
            max_new_chunks=max_physical_per_section if remaining >= MIB else 0,
            max_transfer_mib=max(1, remaining//MIB))
        plan = audit_adjacency_section(**options, execute=False)
        physical_bytes = plan["planned_two_source_bytes"]
        if type(physical_bytes) is not int or not 0 <= physical_bytes <= remaining:
            raise ValueError("combined original HTTP206 L/R network budget overrun")
        remaining -= physical_bytes
        plans[s] = (options,plan)
    if execute:
        shard_root.mkdir(parents=True,exist_ok=True)
        native_audit_dir.mkdir(parents=True,exist_ok=True)
    physical = {}
    for s, (args,planned) in plans.items():
        result = audit_adjacency_section(**args,execute=True) if execute else planned
        if (type(result.get("planned_two_source_bytes")) is not int
                or result["planned_two_source_bytes"] > planned["planned_two_source_bytes"]):
            raise ValueError("original LR executed HTTP206 budget differs from preflight")
        physical[s] = result
    two_sided = max_network_mib*MIB-remaining
    available_dirs = [p for p in physical_dirs.values() if p.is_dir()]+imports
    restoration = None
    one_sided = 0
    if shard_root.is_dir() and available_dirs:
        plan = materialization_plan(
            manifest=manifest, original_index=original_index,
            revision=dataset_revision, manifest_sha256=manifest_sha256,
            original_index_sha256=original_index_sha256,
            physical_receipts_dirs=available_dirs,
            shard_root=shard_root, sections=DIRECTIONS,
            max_chunk_mib=max_chunk_mib,
            max_new_chunks=max_restore if remaining >= MIB else 0,
            max_transfer_mib=max(1, remaining//MIB))
        one_sided = plan["planned_one_sided_hf_bytes"]
        if type(one_sided) is not int or not 0 <= one_sided <= remaining:
            raise ValueError("restoration exceeds remaining original LR network budget")
        restoration = restore(plan=plan) if execute else plan
    native = None
    new_receipt = False
    if execute and shard_root.is_dir() and available_dirs and do_wave:
        candidate = native_original_lr_plan(
            manifest=manifest, original_index=original_index,
            revision=dataset_revision,
            manifest_sha256=manifest_sha256,
            original_index_sha256=original_index_sha256,
            physical_receipts_dirs=available_dirs,
            shard_root=shard_root,
            positive_roots_receipt=positive_roots_receipt,
            extra_numeric_nodes=extras,
            max_chunk_mib=max_chunk_mib)
        if scan_receipt.exists():
            native = next(
                value for value,_ in prior
                if value["target_numeric_nodes"] == candidate["target_numeric_nodes"])
        else:
            native = run_native_original_lr(
                plan=candidate, decoder=decoder, sqlite_index=scan_sqlite,
                max_new_chunks=max_native_chunks, max_neighbors=max_neighbors,
                timeout_seconds=timeout_seconds)
            if native["all_source_equal_original_chunks_natively_scanned"] is True:
                if not scan_sqlite.is_file() or scan_sqlite.is_symlink():
                    raise ValueError("cannot issue full original LR native scan receipt without SQLite")
                native = {**native,
                          "completed_original_native_cohort_sqlite_sha256": digest(scan_sqlite)}
                wire = json.dumps(native,sort_keys=True,indent=2)+"\n"
                with scan_receipt.open("x",encoding="utf-8") as out:out.write(wire)
                prior.append((native,sha256(wire.encode()).hexdigest()))
                new_receipt = True
    closure = original_http206_finite_words(
        query_family=family, audits=prior, max_frontier=max_frontier,
        max_steps=max_steps) if prior else None
    return {
        "version":"itir.zelph.original_a2_physical_native_finite_round.v1",
        "dataset_revision":dataset_revision,
        "manifest_sha256":manifest_sha256,"original_index_sha256":original_index_sha256,
        "decoder_sha256":decoder_sha256,
        "positive_roots_receipt_sha256":root_sha,
        "query_family_sha256":query_family_sha256,
        "execute":execute,
        "original_source_section_chunk_counts":counts,
        "physical":physical,"restoration":restoration,
        "current_native_cohort_targets":cohort,
        "next_numeric_frontier_input":extras,
        "native":native,
        "native_cohort_sqlite":str(scan_sqlite) if do_wave else None,
        "new_complete_native_scan_receipt":str(scan_receipt) if new_receipt else None,
        "finite_word_closure":closure,
        "next_numeric_nodes_to_scan":(
            closure["next_numeric_nodes_to_native_scan"] if closure else []),
        "all_declared_original_lr_words_closed":bool(
            closure and closure["all_declared_original_lr_words_closed"]),
        "all_twenty_original_lr_words_closed":bool(
            closure and closure["all_twenty_original_lr_words_closed"]),
        "original_full_binary_digest_verified":False,
        "agda_original_A2_frontier_weld_paid":False,
        "p854_source_support_paid":False,
        "s29_live_postgresql_paid":False,
        "nora_external_export_paid":False,
        "edit_authority":False,
        "max_network_bytes":max_network_mib*MIB,
        "planned_two_sided_http206_bytes":two_sided,
        "planned_one_sided_restore_bytes":one_sided,
        "planned_combined_network_bytes":two_sided+one_sided,
    }


def main()->int:
    p=argparse.ArgumentParser(description=__doc__)
    for name in ("manifest","original-index","decoder",
                 "positive-roots-receipt","query-family",
                 "left-receipts-dir","right-receipts-dir",
                 "shard-root","native-audit-dir"):
        p.add_argument("--"+name,type=Path,required=True)
    for name in ("dataset-revision","manifest-sha256","original-index-sha256",
                 "decoder-sha256","query-family-sha256"):
        p.add_argument("--"+name,required=True)
    p.add_argument("--import-physical-receipts-dir",type=Path,action="append")
    for name,default in (
        ("max-network-mib",1024),("max-physical-per-section",8),
        ("max-restore",8),("max-native-chunks",16),("max-numeric-frontier",64),
        ("max-chunk-mib",256),("max-neighbors",200000),
        ("max-frontier",200000),("max-steps",16),("timeout-seconds",900)):
        p.add_argument("--"+name,type=int,default=default)
    p.add_argument("--execute",action="store_true")
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    try:
        if args.output is not None and (args.output.exists() or args.output.is_symlink()):
            raise ValueError("refuse overwrite original A2 finite frontier receipt")
        result=run_a2_round(
            manifest=args.manifest,original_index=args.original_index,
            dataset_revision=args.dataset_revision,
            manifest_sha256=args.manifest_sha256,
            original_index_sha256=args.original_index_sha256,
            decoder=args.decoder,decoder_sha256=args.decoder_sha256,
            positive_roots_receipt=args.positive_roots_receipt,
            query_family=args.query_family,query_family_sha256=args.query_family_sha256,
            left_receipts_dir=args.left_receipts_dir,
            right_receipts_dir=args.right_receipts_dir,
            shard_root=args.shard_root,native_audit_dir=args.native_audit_dir,
            import_receipt_dirs=args.import_physical_receipts_dir,
            max_network_mib=args.max_network_mib,
            max_physical_per_section=args.max_physical_per_section,
            max_restore=args.max_restore,max_native_chunks=args.max_native_chunks,
            max_numeric_frontier=args.max_numeric_frontier,
            max_chunk_mib=args.max_chunk_mib,max_neighbors=args.max_neighbors,
            max_frontier=args.max_frontier,max_steps=args.max_steps,
            timeout_seconds=args.timeout_seconds,execute=args.execute)
        wire=json.dumps(result,sort_keys=True,indent=2)+"\n"
        if args.output:
            with args.output.open("x",encoding="utf-8") as out:out.write(wire)
        else:print(wire,end="")
        return 0
    except (ValueError,OSError,KeyError,TypeError,json.JSONDecodeError) as exc:
        print(json.dumps({"status":"blocked","reason":str(exc),
                          "edit_authority":False}),file=sys.stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
