#!/usr/bin/env python3
"""Independently replay the local Nat Zelph manifest/route/packaged receipt bytes.

A *local cryptographic consistency check*, not authentication of the upstream HF
HTTP response, full nodeOfName enumeration, adjacency closure, P854 evidence,
Agda kernel acceptance or public Wikidata rights. This verifies raw bytes;
it never accepts a report of a hash without recomputing it.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Any

_SHA40 = re.compile(r"[0-9a-f]{40}\Z")
_SHA64 = re.compile(r"[0-9a-f]{64}\Z")
_QID = re.compile(r"Q[1-9][0-9]*\Z")
_LIMITS = {
    "request": 2 * 1024 * 1024,
    "manifest": 16 * 1024 * 1024,
    "route": 64 * 1024 * 1024,
    "receipt": 8 * 1024 * 1024,
}


def _no_duplicate_keys(items: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in items:
        if key in result:
            raise ValueError(f"duplicate JSON key in raw replay: {key}")
        result[key] = value
    return result


def _load_bytes(path: Path, name: str) -> tuple[dict[str, Any], bytes]:
    raw = path.read_bytes()
    if not raw or len(raw) > _LIMITS[name]:
        raise ValueError(f"{name} raw byte length missing or exceeds cap")
    try:
        parsed = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_no_duplicate_keys,
            parse_constant=lambda value: (_ for _ in ()).throw(
                ValueError(f"non-finite JSON number: {value}")
            ),
        )
    except UnicodeDecodeError as exc:
        raise ValueError(f"{name} not UTF-8") from exc
    if not isinstance(parsed, dict):
        raise ValueError(f"{name} root must be JSON object")
    return parsed, raw


def _digest(raw: bytes) -> str:
    return sha256(raw).hexdigest()


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError(reason)


def _qid_set(values: Any, label: str) -> list[str]:
    _require(isinstance(values, list) and bool(values), f"{label} requires nonempty list")
    _require(
        all(isinstance(item, str) and _QID.fullmatch(item) for item in values),
        f"{label} has invalid QID",
    )
    _require(len(set(values)) == len(values), f"{label} duplicate QID")
    return sorted(values)


def verify_local_replay(
    *,
    request_path: Path,
    manifest_path: Path,
    route_path: Path,
    receipt_path: Path,
    expected_dataset_sha: str,
    expected_manifest_sha256: str,
    artifact_name: str = "wikidata-20260309-all",
) -> dict[str, Any]:
    """Fail closed on any discrepancy among four independently read files.

    The expected digest and dataset SHA must come from an *independent* pinned
    source. In this offline verifier they are caller inputs and do not
    authenticate where the bytes originally came from.
    """
    _require(bool(_SHA40.fullmatch(expected_dataset_sha)), "invalid pinned dataset SHA")
    _require(bool(_SHA64.fullmatch(expected_manifest_sha256)), "invalid expected manifest SHA256")
    request, request_raw = _load_bytes(request_path, "request")
    manifest, manifest_raw = _load_bytes(manifest_path, "manifest")
    route, route_raw = _load_bytes(route_path, "route")
    receipt, receipt_raw = _load_bytes(receipt_path, "receipt")
    manifest_sha = _digest(manifest_raw)
    route_sha = _digest(route_raw)
    _require(manifest_sha == expected_manifest_sha256, "raw manifest SHA256 mismatch")
    _require(
        manifest.get("manifestVersion") == 2
        and manifest.get("storageMode") == "split-by-direction-and-section",
        "published full graph numeric v2 manifest ABI mismatch",
    )
    _require(
        (manifest.get("source") or {}).get("artifactName") == artifact_name,
        "manifest artifact-name mismatch",
    )
    declared_manifest = request.get("source_manifest")
    _require(isinstance(declared_manifest, dict), "request source manifest must be object")
    _require(
        receipt.get("source_manifest_identity") == declared_manifest,
        "receipt/request source manifest identity mismatch",
    )
    manifest_claim = declared_manifest.get("manifest_digest")
    _require(
        manifest_claim in (manifest_sha, f"sha256:{manifest_sha}"),
        "request manifest digest is not the raw manifest digest",
    )
    revision_claim = declared_manifest.get(
        "dataset_sha", declared_manifest.get("manifest_revision")
    )
    _require(
        revision_claim == expected_dataset_sha,
        "source manifest request not pinned to expected dataset SHA",
    )
    _require(
        route.get("routeVersion") == "zelph-filtered-route/v1",
        "unsupported route version",
    )
    _require(
        receipt.get("schema_version") == "itir.zelph_filtered_route_receipt.v0_1",
        "unsupported packaged receipt version",
    )
    _require(
        receipt.get("route_artifact_content_address") == f"sha256:{route_sha}",
        "raw route digest does not match receipt content address",
    )
    digest_on_receipt = receipt.get("receipt_digest_sha256")
    unsigned = dict(receipt)
    unsigned.pop("receipt_digest_sha256", None)
    canonical = json.dumps(
        unsigned, sort_keys=True, ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")
    _require(
        digest_on_receipt == _digest(canonical),
        "canonical receipt payload digest mismatch",
    )
    _require(
        receipt.get("source_request_ref") == request.get("request_ref")
        and isinstance(request.get("request_ref"), str)
        and bool(request.get("request_ref")),
        "source request identity mismatch",
    )

    expected_qids = _qid_set(request.get("qids"), "request QIDs")
    _require(
        _qid_set(route.get("requestedQids"), "route QIDs") == expected_qids,
        "requested route QID set mismatch",
    )
    _require(
        _qid_set(receipt.get("requested_qids"), "receipt QIDs") == expected_qids,
        "receipt QID set mismatch",
    )
    qid_to_node = route.get("qidToZelphNodeIds")
    name_chunks = route.get("qidToNodeOfNameChunks")
    node_routes = route.get("nodeRoutes")
    _require(
        isinstance(qid_to_node, dict)
        and isinstance(name_chunks, dict)
        and isinstance(node_routes, dict),
        "physical route maps missing",
    )
    _require(set(qid_to_node) == set(expected_qids), "route QID mapping domain mismatch")
    resolved = {
        qid: node for qid, node in qid_to_node.items() if node is not None
    }
    _require(
        all(type(node) is int and node >= 0 for node in resolved.values()),
        "invalid physical numeric node ID",
    )
    _require(
        set(name_chunks) == set(resolved)
        and all(type(index) is int and index >= 0 for index in name_chunks.values()),
        "missing or invalid physical nodeOfName chunks",
    )
    _require(
        set(node_routes) == {str(node) for node in resolved.values()},
        "nodeRoutes must exactly cover resolved numeric nodes",
    )
    for node, parts in node_routes.items():
        _require(isinstance(parts, dict), f"node {node} route missing")
        for key in ("left", "right", "nameOfNode"):
            indexes = parts.get(key)
            _require(
                isinstance(indexes, list)
                and all(type(value) is int and value >= 0 for value in indexes)
                and len(set(indexes)) == len(indexes),
                f"node {node} {key} has invalid/missing chunk indices",
            )
    _require(
        receipt.get("qid_to_zelph_node_ids") == qid_to_node
        and receipt.get("qid_to_node_of_name_chunks") == name_chunks,
        "packaged receipt changes decoded QID mapping",
    )
    for name, receiver in (
        ("left", "node_to_left_chunks"),
        ("right", "node_to_right_chunks"),
        ("nameOfNode", "node_to_name_of_node_chunks"),
    ):
        expected_parts = {node: list(parts[name]) for node, parts in node_routes.items()}
        _require(
            receipt.get(receiver) == expected_parts,
            f"packaged receipt {name} routes differ from raw route",
        )
    complete = len(resolved) == len(expected_qids)
    _require(
        route.get("resolvedQidCount") == len(resolved)
        and route.get("completeQidResolution") is complete
        and receipt.get("complete_qid_resolution") is complete,
        "complete-QID-resolution flags/count inconsistent with decoded keys",
    )
    _require(
        receipt.get("unresolved_qids")
        == sorted(set(expected_qids) - set(resolved)),
        "receipt unresolved QID set mismatch",
    )
    _require(
        receipt.get("missing_node_routes") == [],
        "packaged receipt missing node-route references",
    )
    _require(
        route.get("fullRouteMaterializationPerformed") is False
        and receipt.get("full_route_materialization_performed") is False,
        "unexpected full-route-materialization flag",
    )
    _require(
        all(
            receipt.get(flag) is False
            for flag in (
                "source_support_paid",
                "consumer_verification_performed",
                "semantic_promotion_performed",
                "edits_performed",
            )
        ),
        "packaged receipt claimed unverified authority or execution",
    )
    return {
        "version": "itir.zelph.local_raw_replay.v1",
        "status": "local-byte-and-semantic-replay-verified",
        "dataset_sha_claim": expected_dataset_sha,
        "manifest_sha256_recomputed": manifest_sha,
        "route_sha256_recomputed": route_sha,
        "request_sha256_recomputed": _digest(request_raw),
        "receipt_file_sha256_recomputed": _digest(receipt_raw),
        "receipt_payload_digest_verified": True,
        "manifest_request_receipt_binding_verified": True,
        "route_bytes_to_decoded_mapping_verified": True,
        "qid_count": len(expected_qids),
        "resolved_qid_count": len(resolved),
        "graph_query_closure_proved": False,
        "whole_name_domain_exhausted": False,
        "physical_chunk_bytes_verified": False,
        "source_bin_to_hf_dataset_identity_proved": False,
        "remote_response_origin_authenticated": False,
        "nora_source_support_paid": False,
        "production_accepted": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for field in ("request", "manifest", "route", "receipt"):
        parser.add_argument(f"--{field}", type=Path, required=True)
    parser.add_argument("--dataset-sha", required=True)
    parser.add_argument("--manifest-sha256", required=True)
    parser.add_argument("--artifact-name", default="wikidata-20260309-all")
    args = parser.parse_args()
    try:
        result = verify_local_replay(
            request_path=args.request,
            manifest_path=args.manifest,
            route_path=args.route,
            receipt_path=args.receipt,
            expected_dataset_sha=args.dataset_sha,
            expected_manifest_sha256=args.manifest_sha256,
            artifact_name=args.artifact_name,
        )
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except (ValueError, OSError, json.JSONDecodeError, TypeError) as exc:
        print(json.dumps({
            "status": "blocked",
            "reason": str(exc),
            "production_accepted": False,
        }, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
