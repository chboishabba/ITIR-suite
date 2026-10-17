from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


XPOLLENATION_SCHEMA = "dashi.xpollenation-neighbourhood/v1"
SHARED_SHARD_CONTRACT = "shared-shard-artifact/v1"
XPOLLENATION_AUTHORITY = "navigation-enrichment-only"
XPOLLENATION_ROUTE_FORMAT = "xpollenation-route/v1"


def _text(name: str, value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{name} must be non-empty")
    return text


def _coordinate(name: str, value: Any) -> tuple[str, str]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{name} must be an object")
    return (
        _text(f"{name}.namespace", value.get("namespace")).lower(),
        _text(f"{name}.identifier", value.get("identifier")),
    )


def canonicalize_neighbourhood(item: Mapping[str, Any]) -> dict[str, Any]:
    if _text("schema", item.get("schema")) != XPOLLENATION_SCHEMA:
        raise ValueError("unsupported xPollenation neighbourhood schema")
    if (
        _text("authority", item.get("authority")) != XPOLLENATION_AUTHORITY
        or item.get("establishesProof") is not False
        or item.get("establishesPayment") is not False
    ):
        raise ValueError("xPollenation neighbourhood attempts authority escalation")
    _coordinate("subject", item.get("subject"))
    edges = item.get("edges")
    if not isinstance(edges, list):
        raise ValueError("xPollenation edges must be a list")
    normalized_edges: list[dict[str, Any]] = []
    seen: set[str] = set()
    for raw in edges:
        if not isinstance(raw, Mapping):
            raise ValueError("xPollenation edge must be an object")
        edge = copy.deepcopy(dict(raw))
        edge_id = _text("edgeId", edge.get("edgeId"))
        if edge_id in seen:
            raise ValueError("duplicate xPollenation edge id")
        seen.add(edge_id)
        _coordinate("edge.subject", edge.get("subject"))
        _coordinate("edge.object", edge.get("object"))
        _text("edge.relation", edge.get("relation"))
        _text("edge.sourceRef", edge.get("sourceRef"))
        _text("edge.sourceRevision", edge.get("sourceRevision"))
        _text("edge.acquisitionReceipt", edge.get("acquisitionReceipt"))
        _text("edge.status", edge.get("status"))
        if edge.get("promotionAllowed") is not False:
            raise ValueError("xPollenation edge attempts promotion authority")
        if edge.get("sameObjectVerified") is True and edge.get("sameObjectClaimed") is not True:
            raise ValueError("same-object verification requires an explicit claim")
        normalized_edges.append(edge)
    normalized = copy.deepcopy(dict(item))
    normalized["edges"] = sorted(normalized_edges, key=lambda edge: edge["edgeId"])
    return normalized


def resolve_xpollenation_selector(
    artifact: Mapping[str, Any], selector: str
) -> list[str]:
    """Resolve one xPollenation external selector to logical shard IDs.

    This deliberately stops at logical shard identity. Existing ITIR transport
    code may then resolve/fetch an objectRef for the selected shard. CID/path
    choice therefore remains downstream of semantic routing.
    """
    selector = _text("selector", selector)
    if not selector.startswith("route-external="):
        return []
    routing_index = artifact.get("routingIndex")
    if not isinstance(routing_index, Mapping):
        return []
    if routing_index.get("format") != XPOLLENATION_ROUTE_FORMAT:
        return []
    routes = routing_index.get("routes")
    if not isinstance(routes, Mapping):
        return []
    raw = routes.get(selector)
    if not isinstance(raw, list):
        return []
    known = {
        _text("shardId", shard.get("shardId"))
        for shard in artifact.get("shards", [])
        if isinstance(shard, Mapping) and shard.get("shardId")
    }
    result: list[str] = []
    for value in raw:
        shard_id = _text("routing shard id", value)
        if shard_id in known and shard_id not in result:
            result.append(shard_id)
    return result


def build_xpollenation_artifact(
    neighbourhood: Mapping[str, Any],
    *,
    artifact_id: str,
) -> dict[str, Any]:
    payload = canonicalize_neighbourhood(neighbourhood)
    namespace, identifier = _coordinate("subject", payload["subject"])
    canonical_json = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    payload_bytes = canonical_json.encode("utf-8")
    digest_body = hashlib.sha256(payload_bytes).hexdigest()
    content_digest = f"sha256:{digest_body}"
    artifact_id = _text("artifact_id", artifact_id)
    routing_key = f"route-external={namespace}:{identifier}"
    return {
        "contractVersion": SHARED_SHARD_CONTRACT,
        "artifactId": artifact_id,
        "artifactRevision": digest_body,
        "artifactClass": "xpollenation-neighbourhood",
        "createdAtUtc": _text("createdAtUtc", payload.get("createdAtUtc") or "unknown-created-at"),
        "buildProvenance": {
            "builder": "itir_jmd_bridge.xpollenation_artifact",
            "builderVersion": "1",
            "sourceSchema": XPOLLENATION_SCHEMA,
            "subject": {"namespace": namespace, "identifier": identifier},
        },
        "shards": [
            {
                "shardId": "neighbourhood",
                "section": "neighbourhood",
                "logicalKind": "xpollenation-neighbourhood",
                "encoding": "json",
                "sizeBytes": len(payload_bytes),
                "contentDigest": content_digest,
                "routingKeys": [routing_key],
                "objectRefs": [],
            }
        ],
        "routingIndex": {
            "format": XPOLLENATION_ROUTE_FORMAT,
            "routes": {routing_key: ["neighbourhood"]},
        },
        "embeddedPayloads": {"neighbourhood": canonical_json},
        "nonAuthority": {
            "semanticIdentityFromCid": False,
            "promotionAuthority": False,
            "proofAuthority": False,
            "consumerPaymentAuthority": False,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m itir_jmd_bridge emit-xpollenation-artifact"
    )
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--artifact-id", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    neighbourhood = json.loads(args.input.read_text(encoding="utf-8"))
    if not isinstance(neighbourhood, dict):
        raise ValueError("xPollenation input must be one JSON object")
    artifact = build_xpollenation_artifact(
        neighbourhood,
        artifact_id=args.artifact_id,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(artifact, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
