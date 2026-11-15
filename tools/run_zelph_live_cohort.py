#!/usr/bin/env python3
"""P1/P2/P4 same-run physical Zelph + raw Wikibase candidate handoff.

Reuses the existing original-.bin producer, published-manifest comparator and
native four-section decoder; *never* manufactures physical/source authority.
An original Zelph edge is not asserted to be a revision-pinned Wikipedia FLN edge
or an independently sourced Wikidata statement. Only immutable coordinates,
observed original bytes and explicitly unresolved mappings leave this boundary.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import sys
from typing import Any

from run_zelph_local_physical_maxcut import run_local_physical_maxcut
from verify_wikidata_native_entity_snapshot import verify_native_entity_snapshot
from verify_zelph_bin_shard_exact import _read_json

_SHA = re.compile(r"[0-9a-f]{64}\Z")
_QID = re.compile(r"Q[1-9][0-9]*\Z")


def build_source_bound_candidate(*, physical: dict[str, Any],
                                 route: dict[str, Any],
                                 native: dict[str, Any],
                                 qid: str,
                                 source_bin_sha256: str,
                                 declared_family_required: bool = True) -> dict[str, Any]:
    if not _QID.fullmatch(qid) or not _SHA.fullmatch(source_bin_sha256):
        raise ValueError("canonical QID and exact original-bin SHA256 pin required")
    required_physical = (
        "source_bin_external_digest_matched_in_this_run",
        "original_packed_manifest_full_offset_cover_checked_in_this_run",
        "source_bin_ranges_reverified_in_same_native_audit",
        "selected_root_one_hop_equal_original_bin",
    )
    if any(physical.get(key) is not True for key in required_physical):
        raise ValueError("source-bin/manifest/selected native physical proof incomplete")
    if declared_family_required and physical.get("finite_words_complete") is not True:
        raise ValueError("declared finite left/right family has missing frontiers")
    if (physical.get("source_support_paid") is not False
            or physical.get("p854_document_verified") is not False
            or physical.get("edit_authority") is not False):
        raise ValueError("untrusted physical summary asserts authority")
    if route.get("routeVersion") != "zelph-filtered-route/v1":
        raise ValueError("route is not original-source producer output")
    roots = route.get("requestedQids")
    node_ids = route.get("qidToZelphNodeIds")
    if (type(roots) is not list or qid not in roots
            or type(node_ids) is not dict or set(roots) != set(node_ids)
            or type(node_ids[qid]) is not int or node_ids[qid] < 0):
        raise ValueError("native statement QID lacks exact original graph node")
    if (native.get("subject_qid") != qid or native.get("source_kind") != "full-wikibase-json-entity"
            or native.get("snapshot_bytes_match_pinned_digest") is not True
            or native.get("same_source_native_statement_found") is not True
            or not isinstance(native.get("raw_entity_sha256_checked"), str)
            or not _SHA.fullmatch(native["raw_entity_sha256_checked"])
            or type(native.get("native_entity_revision_id")) is not int):
        raise ValueError("original full Wikibase statement evidence incomplete")
    if (native.get("edit_authority") is not False
            or native.get("reviewed_source_support_paid") is not False):
        raise ValueError("untrusted native statement asserts source/authority promotion")
    return {
        "version": "itir.zelph_wikibase_source_bound_candidate.v1",
        "source_kind": "candidate-only-original-zelph-plus-native-wikibase",
        "graph_dataset_revision": physical["dataset_revision"],
        "graph_manifest_sha256": physical["manifest_sha256"],
        "original_bin_sha256_matched_supplied_pin": source_bin_sha256,
        "route_raw_sha256": physical["route_raw_sha256"],
        "physical_range_receipt_sha256": physical["range_proof_raw_sha256"],
        "physical_native_answer_sha256": physical["native_answer_raw_sha256"],
        "physical_partition_sha256": physical["original_packed_partition_raw_sha256"],
        "selected_root_bidirectional_source_adjacency_equal": True,
        "declared_lr_query_family_complete": physical.get("finite_words_complete") is True,
        "qid": qid, "zelph_internal_node_id": node_ids[qid],
        "statement_guid": native["statement_guid"],
        "property_id": native["property_id"],
        "wikibase_native_entity_revision_id": native["native_entity_revision_id"],
        "wikibase_native_raw_entity_sha256": native["raw_entity_sha256_checked"],
        "p854_candidate_urls": native["p854_url_candidates"],
        "native_quantity": native.get("native_quantity"),
        "qualified_references": native["references"],
        "qualifiers": native["qualifiers"],
        "wikibase_entity_revision_equals_graph_dataset_revision_proved": False,
        "wikipedia_oldid_first_qualified_link_same_as_zelph_edge_proved": False,
        "upstream_http_origin_independently_authenticated_here": False,
        "p854_primary_documents_independently_verified": False,
        "persisted_s29_review_verified": False,
        "source_support_paid": False, "creates_world_truth": False,
        "edit_authority": False,
    }


def run_cohort(*, source_bin: Path, manifest: Path, shard_root: Path,
               producer: Path, decoder: Path, output_dir: Path,
               dataset_revision: str, manifest_sha256: str,
               expected_source_bin_sha256: str,
               qids: list[str], target_qid: str, entity_raw: Path,
               expected_entity_sha256: str, statement_guid: str,
               property_id: str, entity_revision: int,
               family_path: Path,
               extra_nodes: list[int] | None = None,
               max_selected_gib: int = 16) -> dict[str, Any]:
    for name in ("raw-native-observation.json", "source-bound-cohort-candidate.json"):
        if (output_dir / name).exists():
            raise ValueError("candidate output already exists; refuse overwrite")
    if target_qid not in qids:
        raise ValueError("native statement QID must be in exact physically selected root set")
    # Refuse ambiguous/insufficient source digest even when the transport
    # operator has already downloaded a plausible-looking .bin.
    if not _SHA.fullmatch(expected_source_bin_sha256):
        raise ValueError("externally pinned source-bin SHA256 is mandatory")
    native = verify_native_entity_snapshot(
        path=entity_raw, expected_sha256=expected_entity_sha256,
        qid=target_qid, statement_guid=statement_guid,
        property_id=property_id, entity_revision=entity_revision)
    physical = run_local_physical_maxcut(
        source_bin=source_bin, manifest=manifest, shard_root=shard_root,
        producer=producer, decoder=decoder, output_dir=output_dir,
        dataset_revision=dataset_revision, manifest_sha256=manifest_sha256,
        expected_source_bin_sha256=expected_source_bin_sha256,
        qids=qids, extra_nodes=extra_nodes,
        family_path=family_path, max_selected_gib=max_selected_gib)
    route = _read_json(output_dir / "route-new.json", 64 * 1024 * 1024)
    # Read back actual physical receipt bytes; do not trust a free-floating
    # self-declared true flag if the driver failed to write its evidence.
    expected = {
        "route-new.json": physical["route_raw_sha256"],
        "original-packed-partition.json": physical["original_packed_partition_raw_sha256"],
        "selected-range-proof.json": physical["range_proof_raw_sha256"],
        "native-selected-physical-answer.json": physical["native_answer_raw_sha256"],
    }
    for name, expected_digest in expected.items():
        if sha256((output_dir / name).read_bytes()).hexdigest() != expected_digest:
            raise ValueError("physical receipt drift or missing original artifact: " + name)
    candidate = build_source_bound_candidate(
        physical=physical, route=route, native=native,
        qid=target_qid, source_bin_sha256=expected_source_bin_sha256)
    with (output_dir / "raw-native-observation.json").open("x", encoding="utf-8") as f:
        f.write(json.dumps(native, sort_keys=True, indent=2) + "\n")
    with (output_dir / "source-bound-cohort-candidate.json").open("x", encoding="utf-8") as f:
        f.write(json.dumps(candidate, sort_keys=True, indent=2) + "\n")
    return candidate


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for arg in ("source-bin", "manifest", "shard-root", "producer",
                "decoder", "output-dir", "entity-raw", "query-family"):
        parser.add_argument("--" + arg, required=True, type=Path)
    parser.add_argument("--dataset-revision", required=True)
    parser.add_argument("--manifest-sha256", required=True)
    parser.add_argument("--expected-source-bin-sha256", required=True)
    parser.add_argument("--qid", required=True, action="append", dest="qids")
    parser.add_argument("--target-qid", required=True)
    parser.add_argument("--expected-entity-sha256", required=True)
    parser.add_argument("--statement-guid", required=True)
    parser.add_argument("--property", dest="property_id", required=True)
    parser.add_argument("--entity-revision", required=True, type=int)
    parser.add_argument("--node", action="append", type=int, default=[])
    parser.add_argument("--max-selected-gib", type=int, default=16)
    args = parser.parse_args()
    try:
        candidate = run_cohort(
            source_bin=args.source_bin, manifest=args.manifest,
            shard_root=args.shard_root, producer=args.producer,
            decoder=args.decoder, output_dir=args.output_dir,
            dataset_revision=args.dataset_revision,
            manifest_sha256=args.manifest_sha256,
            expected_source_bin_sha256=args.expected_source_bin_sha256,
            qids=args.qids, target_qid=args.target_qid,
            entity_raw=args.entity_raw,
            expected_entity_sha256=args.expected_entity_sha256,
            statement_guid=args.statement_guid, property_id=args.property_id,
            entity_revision=args.entity_revision, family_path=args.query_family,
            extra_nodes=args.node, max_selected_gib=args.max_selected_gib)
        print(json.dumps(candidate, sort_keys=True, indent=2))
        return 0
    except (ValueError, OSError, TypeError, KeyError) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc),
                          "edit_authority": False}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
