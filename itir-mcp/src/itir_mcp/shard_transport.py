from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


CONTRACT_VERSION = "shared-shard-artifact/v1"
ALLOWED_SINKS = frozenset({"hf", "ipfs", "file"})
SELECTOR_FAMILIES = frozenset(
    {
        "direct-shard",
        "route-left-node",
        "route-right-node",
        "route-node",
        "route-name",
        "route-lang",
    }
)
AUTHORITY_FLAG_FIELDS = (
    "truth_authority",
    "support_authority",
    "admissibility_authority",
    "promotion_authority",
)


def validate_shared_shard_artifact(payload: Mapping[str, Any]) -> dict[str, Any]:
    data = _mapping(payload, "payload")
    contract_version = _required_str(data, "contractVersion")
    if contract_version != CONTRACT_VERSION:
        raise ValueError(f"contractVersion must be {CONTRACT_VERSION}")

    artifact_id = _required_str(data, "artifactId")
    artifact_revision = _required_str(data, "artifactRevision")
    artifact_class = _required_str(data, "artifactClass")
    created_at_utc = _required_str(data, "createdAtUtc")
    build_provenance = _mapping(data.get("buildProvenance"), "buildProvenance")

    shards_raw = data.get("shards")
    if not isinstance(shards_raw, list):
        raise ValueError("shards must be an array")

    normalized_shards: list[dict[str, Any]] = []
    for index, shard_raw in enumerate(shards_raw):
        shard = _mapping(shard_raw, f"shards[{index}]")
        shard_id = _required_str(shard, "shardId")
        section = _required_str(shard, "section")
        logical_kind = _required_str(shard, "logicalKind")
        encoding = _required_str(shard, "encoding")
        size_bytes = _required_int(shard, "sizeBytes")
        content_digest = _required_str(shard, "contentDigest")

        routing_keys_raw = shard.get("routingKeys")
        if not isinstance(routing_keys_raw, list):
            raise ValueError(f"shards[{index}].routingKeys must be an array")
        routing_keys = [_required_str({"value": item}, "value") for item in routing_keys_raw]

        object_refs_raw = shard.get("objectRefs")
        if not isinstance(object_refs_raw, list):
            raise ValueError(f"shards[{index}].objectRefs must be an array")

        normalized_refs: list[dict[str, Any]] = []
        for ref_index, ref_raw in enumerate(object_refs_raw):
            ref = _mapping(ref_raw, f"shards[{index}].objectRefs[{ref_index}]")
            sink = _required_str(ref, "sink")
            if sink not in ALLOWED_SINKS:
                raise ValueError(f"shards[{index}].objectRefs[{ref_index}].sink must be one of hf, ipfs, file")
            uri = _required_str(ref, "uri")
            ref_size_bytes = _required_int(ref, "sizeBytes")
            ref_content_digest = _required_str(ref, "contentDigest")
            normalized_ref = {
                "sink": sink,
                "uri": uri,
                "sizeBytes": ref_size_bytes,
                "contentDigest": ref_content_digest,
            }
            transport_hints = ref.get("transportHints")
            if transport_hints is not None:
                normalized_ref["transportHints"] = transport_hints
            normalized_refs.append(normalized_ref)

        normalized_shard = {
            "shardId": shard_id,
            "section": section,
            "logicalKind": logical_kind,
            "encoding": encoding,
            "sizeBytes": size_bytes,
            "contentDigest": content_digest,
            "routingKeys": routing_keys,
            "objectRefs": normalized_refs,
        }
        normalized_shards.append(normalized_shard)

    normalized: dict[str, Any] = {
        "contractVersion": contract_version,
        "artifactId": artifact_id,
        "artifactRevision": artifact_revision,
        "artifactClass": artifact_class,
        "createdAtUtc": created_at_utc,
        "buildProvenance": build_provenance,
        "shards": normalized_shards,
    }

    routing_index = data.get("routingIndex")
    if routing_index is not None:
        normalized["routingIndex"] = routing_index
    return normalized


def route_selector(payload: Mapping[str, Any], selector: str) -> list[str]:
    artifact = validate_shared_shard_artifact(payload)
    selector_text = _required_str({"value": selector}, "value")
    family, value = _split_selector(selector_text)
    if family is None:
        return []

    if family == "direct-shard":
        return [shard["shardId"] for shard in artifact["shards"] if shard["shardId"] == value]

    if family not in SELECTOR_FAMILIES:
        return []

    matched: list[str] = []
    for shard in artifact["shards"]:
        routing_keys = shard["routingKeys"]
        if (selector_text in routing_keys or family in routing_keys) and shard["shardId"] not in matched:
            matched.append(shard["shardId"])
    return matched


def build_partial_graph_view(payload: Mapping[str, Any], selectors: Sequence[str]) -> dict[str, Any]:
    artifact = validate_shared_shard_artifact(payload)
    selector_list: list[str] = []
    for selector in selectors:
        selector_list.append(_required_str({"value": selector}, "value"))
    selected_ids: list[str] = []
    for selector in selector_list:
        for shard_id in route_selector(artifact, selector):
            if shard_id not in selected_ids:
                selected_ids.append(shard_id)

    shard_index = {shard["shardId"]: shard for shard in artifact["shards"]}
    selected_shards = [_logical_shard_view(shard_index[shard_id]) for shard_id in selected_ids if shard_id in shard_index]
    selected_sections: list[str] = []
    for shard in selected_shards:
        section = shard["section"]
        if section not in selected_sections:
            selected_sections.append(section)

    return {
        "artifact_identity": {
            "contractVersion": artifact["contractVersion"],
            "artifactId": artifact["artifactId"],
            "artifactRevision": artifact["artifactRevision"],
            "artifactClass": artifact["artifactClass"],
            "createdAtUtc": artifact["createdAtUtc"],
        },
        "selected_shard_ids": selected_ids,
        "selected_sections": selected_sections,
        "selected_shards": selected_shards,
        "selectors": selector_list,
        "completeness": "partial",
        "subset_of_artifact": True,
        "candidate_only": True,
        "diagnostic_only": True,
        "truth_authority": False,
        "support_authority": False,
        "admissibility_authority": False,
        "promotion_authority": False,
    }


def _split_selector(selector: str) -> tuple[str | None, str]:
    if "=" not in selector:
        return None, ""
    family, value = selector.split("=", 1)
    if family not in SELECTOR_FAMILIES:
        return None, value
    return family, value


def _logical_shard_view(shard: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "shardId": shard["shardId"],
        "section": shard["section"],
        "logicalKind": shard["logicalKind"],
        "encoding": shard["encoding"],
        "sizeBytes": shard["sizeBytes"],
        "contentDigest": shard["contentDigest"],
        "routingKeys": list(shard["routingKeys"]),
    }


def _mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} must be an object")
    return dict(value)


def _required_str(mapping: Mapping[str, Any], key: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{key} is required")
    return value


def _required_int(mapping: Mapping[str, Any], key: str) -> int:
    value = mapping.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{key} must be an integer")
    return value
