#!/usr/bin/env python3
"""Package a bounded Zelph filtered-route result into a provenance-bearing receipt.

The C++ producer emits only exact route data.  This wrapper binds that output to
an upstream request, preserves the pinned base-producer lineage, and gives the
raw filtered route artifact a byte-level SHA-256 content address.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


RECEIPT_SCHEMA = "itir.zelph_filtered_route_receipt.v0_1"
FILTERED_ROUTE_VERSION = "zelph-filtered-route/v1"
ACTUAL_PRODUCER_PATH = "tools/zelph_bin_filtered_route_builder.cpp"
BASE_PRODUCER_PATH = "tools/zelph_bin_route_builder.cpp"
BASE_PRODUCER_COMMIT = "24f62fecbec11909bcdb32916801b2315a796513"


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected object in {path}")
    return payload


def _sha256_bytes(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _text(value: Any) -> str:
    return "" if value is None else str(value).strip()


def build_receipt(
    *,
    request: Mapping[str, Any],
    route: Mapping[str, Any],
    route_path: Path,
    actual_producer_commit: str,
) -> dict[str, Any]:
    requested_qids = sorted(str(item) for item in request.get("qids", []))
    route_qids = sorted(str(item) for item in route.get("requestedQids", []))
    if requested_qids != route_qids:
        raise ValueError("filtered route QIDs do not exactly match request")
    if _text(route.get("routeVersion")) != FILTERED_ROUTE_VERSION:
        raise ValueError("unexpected filtered route version")
    if _text(request.get("request_ref")) == "":
        raise ValueError("request_ref is required")
    if not bool(request.get("filtered_request")):
        raise ValueError("request is not marked filtered")
    if bool(request.get("full_route_materialization_required")):
        raise ValueError("bounded receipt refuses full-route request")
    if bool(route.get("fullRouteMaterializationPerformed")):
        raise ValueError("producer unexpectedly materialized a full route")

    qid_to_node = route.get("qidToZelphNodeIds")
    node_routes = route.get("nodeRoutes")
    if not isinstance(qid_to_node, dict) or not isinstance(node_routes, dict):
        raise ValueError("route missing QID or node-route mappings")

    unresolved_qids = sorted(qid for qid in requested_qids if qid_to_node.get(qid) is None)
    resolved_nodes = sorted({str(qid_to_node[qid]) for qid in requested_qids if qid_to_node.get(qid) is not None})
    missing_node_routes = sorted(node for node in resolved_nodes if node not in node_routes)
    complete = not unresolved_qids and not missing_node_routes and bool(route.get("completeQidResolution"))

    route_digest = _sha256_bytes(route_path)
    receipt_without_digest = {
        "schema_version": RECEIPT_SCHEMA,
        "source_request_ref": _text(request.get("request_ref")),
        "source_manifest_identity": dict(request.get("source_manifest") or {}),
        "producer_lineage": {
            "repository": "chboishabba/ITIR-suite",
            "derived_from": {
                "commit": BASE_PRODUCER_COMMIT,
                "path": BASE_PRODUCER_PATH,
                "route_format": "zelph-node-route/v1",
            },
            "actual_producer": {
                "commit": actual_producer_commit,
                "path": ACTUAL_PRODUCER_PATH,
                "route_format": FILTERED_ROUTE_VERSION,
            },
        },
        "requested_qids": requested_qids,
        "qid_to_zelph_node_ids": qid_to_node,
        "qid_to_node_of_name_chunks": dict(route.get("qidToNodeOfNameChunks") or {}),
        "node_to_left_chunks": {
            node: list((node_routes.get(node) or {}).get("left") or []) for node in resolved_nodes
        },
        "node_to_right_chunks": {
            node: list((node_routes.get(node) or {}).get("right") or []) for node in resolved_nodes
        },
        "node_to_name_of_node_chunks": {
            node: list((node_routes.get(node) or {}).get("nameOfNode") or []) for node in resolved_nodes
        },
        "route_source_identity": dict(route.get("source") or {}),
        "route_artifact_content_address": "sha256:" + route_digest,
        "complete_qid_resolution": complete,
        "unresolved_qids": unresolved_qids,
        "missing_node_routes": missing_node_routes,
        "full_route_materialization_performed": False,
        "network_performed": False,
        "source_support_paid": False,
        "consumer_verification_performed": False,
        "semantic_promotion_performed": False,
        "edits_performed": False,
    }
    canonical = json.dumps(receipt_without_digest, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    receipt = dict(receipt_without_digest)
    receipt["receipt_digest_sha256"] = hashlib.sha256(canonical).hexdigest()
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", required=True)
    parser.add_argument("--route", required=True)
    parser.add_argument("--actual-producer-commit", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    request_path = Path(args.request)
    route_path = Path(args.route)
    receipt = build_receipt(
        request=_load(request_path),
        route=_load(route_path),
        route_path=route_path,
        actual_producer_commit=args.actual_producer_commit,
    )
    Path(args.output).write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0 if receipt["complete_qid_resolution"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
