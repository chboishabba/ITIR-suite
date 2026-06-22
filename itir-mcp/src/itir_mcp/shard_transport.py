from __future__ import annotations

from base64 import b64encode
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen


CONTRACT_VERSION = "shared-shard-artifact/v1"
ZELPH_HF_MANIFEST_CONTRACT_VERSION = "itir.zelph.hf_manifest_contract.v1"
SHARD_PAYLOAD_PROBE_VERSION = "itir.shard.payload_probe.v1"
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
_HF_SCHEMES = ("hf://datasets/", "hf://models/", "hf://spaces/")
_DEFAULT_MANIFEST_BYTE_CAP = 2 * 1024 * 1024
_DEFAULT_PAYLOAD_BYTE_CAP = 4096
_PROBE_PREVIEW_BYTES = 64


@dataclass(frozen=True)
class _HfRef:
    repo_type: str
    repo_id: str
    object_path: str

    def url(self, revision: str | None = None) -> str:
        ref = revision or "main"
        return f"https://huggingface.co/{self.repo_type}/{self.repo_id}/resolve/{ref}/{self.object_path}"


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


def route_selector(payload: Mapping[str, Any], selector: str, route_index: Mapping[str, Any] | None = None) -> list[str]:
    artifact = validate_shared_shard_artifact(payload)
    selector_text = _required_str({"value": selector}, "value")
    family, value = _split_selector(selector_text)
    if family is None:
        return []

    if family == "direct-shard":
        return [shard["shardId"] for shard in artifact["shards"] if shard["shardId"] == value]

    if family not in SELECTOR_FAMILIES:
        return []

    matched = _route_selector_from_sidecar(artifact, family, value, route_index)
    if matched:
        return matched

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


def build_shared_shard_contract_from_zelph_manifest(
    manifest: Mapping[str, Any],
    *,
    artifact_id: str | None = None,
    artifact_revision: str | None = None,
    artifact_class: str = "zelph-graph",
) -> dict[str, Any]:
    data = _mapping(manifest, "manifest")
    manifest_version = _required_str(data, "manifestVersion")
    if not manifest_version.startswith("zelph-hf-layout/v"):
        raise ValueError("manifestVersion must be zelph-hf-layout/v*")
    sections = _mapping(data.get("sections"), "sections")
    selector_model = dict(data.get("selectorModel") or {})
    source = dict(data.get("source") or {})
    hf_objects = dict(data.get("hfObjects") or {})
    source_bin_path = _optional_string(source.get("binPath"))
    created_at_utc = _optional_string(data.get("createdAtUtc")) or "unknown-created-at"
    resolved_artifact_id = artifact_id or _artifact_id_from_manifest(data, source_bin_path)
    resolved_revision = artifact_revision or created_at_utc

    shards: list[dict[str, Any]] = []
    selector_unit = str(selector_model.get("unit") or "section-chunk")
    for section_name, section_value in sections.items():
        section = _mapping(section_value, f"sections.{section_name}")
        chunks = section.get("chunks")
        if not isinstance(chunks, list):
            raise ValueError(f"sections.{section_name}.chunks must be an array")
        for chunk_index, chunk_value in enumerate(chunks):
            chunk = _mapping(chunk_value, f"sections.{section_name}.chunks[{chunk_index}]")
            enriched = dict(chunk)
            enriched["section"] = str(section_name)
            object_uri = _optional_string(enriched.get("objectPath")) or _optional_string(enriched.get("futureObjectPath"))
            if object_uri is None:
                object_uri = f"local-range://{section_name}/{_required_int(enriched, 'chunkIndex'):06d}"
            size_bytes = _required_int(enriched, "length")
            digest = _identity_digest(enriched)
            shard = {
                "shardId": _logical_shard_id(enriched, selector_unit),
                "section": str(section_name),
                "logicalKind": _infer_logical_kind(str(section_name), selector_unit),
                "encoding": _infer_encoding(object_uri),
                "sizeBytes": size_bytes,
                "contentDigest": digest,
                "routingKeys": _routing_keys_for_chunk(str(section_name), enriched),
                "objectRefs": [
                    {
                        "sink": _sink_for_uri(object_uri),
                        "uri": object_uri,
                        "sizeBytes": size_bytes,
                        "contentDigest": digest,
                    }
                ],
            }
            shards.append(shard)

    contract: dict[str, Any] = {
        "contractVersion": CONTRACT_VERSION,
        "artifactId": resolved_artifact_id,
        "artifactRevision": resolved_revision,
        "artifactClass": artifact_class,
        "createdAtUtc": created_at_utc,
        "buildProvenance": {
            "sourceManifestVersion": manifest_version,
            "sourceManifestPath": str((hf_objects.get("manifest") or {}).get("path") or ""),
            "sourceBinPath": source_bin_path,
            "sourceSystem": "Zelph-HF",
            "builder": "itir_mcp.shard_transport.build_shared_shard_contract_from_zelph_manifest",
        },
        "selectorModel": {
            "unit": selector_unit,
            "supportedOperations": list(selector_model.get("supportedOperations") or []),
            "supportedSections": list(selector_model.get("supportedSections") or []),
        },
        "transportHints": {
            "preferredReadSink": "hf",
            "payloadProbe": "bounded",
        },
        "nonAuthority": _non_authority_block(),
        "shards": shards,
    }
    node_route_obj = hf_objects.get("nodeRouteIndex")
    if isinstance(node_route_obj, Mapping) and isinstance(node_route_obj.get("path"), str):
        route_uri = str(node_route_obj["path"])
        route_digest = "identity-sha256:" + sha256(
            json.dumps(dict(node_route_obj), sort_keys=True).encode("utf-8")
        ).hexdigest()
        contract["routingIndex"] = {
            "logicalKind": "routing-index",
            "format": "zelph-node-route/v1",
            "objectRefs": [
                {
                    "sink": _sink_for_uri(route_uri),
                    "uri": route_uri,
                    "sizeBytes": int(node_route_obj.get("sizeBytes") or 0),
                    "contentDigest": route_digest,
                }
            ],
        }
    return contract


def fetch_zelph_hf_manifest_contract(
    *,
    hf_manifest_uri: str,
    revision: str | None = None,
    max_bytes: int = _DEFAULT_MANIFEST_BYTE_CAP,
    artifact_id: str | None = None,
    artifact_revision: str | None = None,
    artifact_class: str = "zelph-graph",
    opener: Any | None = None,
) -> dict[str, Any]:
    blob = _fetch_hf_bytes(hf_manifest_uri, revision=revision, max_bytes=max_bytes, opener=opener)
    try:
        manifest = json.loads(blob["bytes"].decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError("HF manifest payload must be JSON") from exc
    if not isinstance(manifest, Mapping):
        raise ValueError("HF manifest payload must be a JSON object")
    contract = build_shared_shard_contract_from_zelph_manifest(
        manifest,
        artifact_id=artifact_id,
        artifact_revision=artifact_revision or blob.get("revision") or revision,
        artifact_class=artifact_class,
    )
    return {
        "version": ZELPH_HF_MANIFEST_CONTRACT_VERSION,
        "source": {
            "hf_manifest_uri": hf_manifest_uri,
            "revision": revision,
            "resolved_revision": blob.get("revision"),
            "sizeBytes": blob["sizeBytes"],
            "sha256": blob["sha256"],
            "truncated": blob["truncated"],
        },
        "contract": contract,
        "authority_boundary": _authority_boundary(),
    }


def build_bounded_payload_probe(
    payload: Mapping[str, Any],
    *,
    selector: str | None = None,
    shard_id: str | None = None,
    route_index: Mapping[str, Any] | None = None,
    max_bytes: int = _DEFAULT_PAYLOAD_BYTE_CAP,
    allow_truncate: bool = False,
    revision: str | None = None,
    opener: Any | None = None,
) -> dict[str, Any]:
    if max_bytes <= 0:
        raise ValueError("max_bytes must be positive")
    artifact = validate_shared_shard_artifact(payload)
    selected_id = _select_probe_shard_id(artifact, selector=selector, shard_id=shard_id, route_index=route_index)
    shard = _shard_by_id(artifact, selected_id)
    object_ref = _preferred_object_ref(shard)
    declared_size = int(object_ref.get("sizeBytes") or shard["sizeBytes"])
    if declared_size > max_bytes and not allow_truncate:
        raise ValueError("selected shard exceeds max_bytes; set allow_truncate=true for a bounded prefix probe")

    probe_bytes = _read_probe_bytes(object_ref, max_bytes=max_bytes, revision=revision, opener=opener)
    data = probe_bytes["bytes"]
    read_truncated = bool(probe_bytes["truncated"] or declared_size > len(data))
    return {
        "version": SHARD_PAYLOAD_PROBE_VERSION,
        "artifact_identity": {
            "contractVersion": artifact["contractVersion"],
            "artifactId": artifact["artifactId"],
            "artifactRevision": artifact["artifactRevision"],
            "artifactClass": artifact["artifactClass"],
            "createdAtUtc": artifact["createdAtUtc"],
        },
        "selector": selector,
        "shard_id": selected_id,
        "section": shard["section"],
        "logicalKind": shard["logicalKind"],
        "encoding": shard["encoding"],
        "transport_ref": {
            "sink": object_ref["sink"],
            "uri": object_ref["uri"],
            "declaredSizeBytes": declared_size,
            "declaredContentDigest": object_ref["contentDigest"],
        },
        "byte_cap": max_bytes,
        "bytes_read": len(data),
        "truncated": read_truncated,
        "sample_sha256": sha256(data).hexdigest(),
        "sample_preview_hex": data[:_PROBE_PREVIEW_BYTES].hex(),
        "sample_preview_base64": b64encode(data[:_PROBE_PREVIEW_BYTES]).decode("ascii"),
        "payload_access": "bounded_prefix" if read_truncated else "bounded_complete_object",
        "candidate_only": True,
        "non_authoritative": True,
        "diagnostic_only": True,
        "complete_closure": False,
        "truth_authority": False,
        "support_authority": False,
        "admissibility_authority": False,
        "promotion_authority": False,
        "authority_boundary": _authority_boundary(),
    }


def build_payload_probe(
    selected_shard: Mapping[str, Any],
    payload: str | bytes,
    *,
    byte_cap: int = _DEFAULT_PAYLOAD_BYTE_CAP,
    truncate: bool = False,
    non_authority: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    if byte_cap <= 0:
        raise ValueError("byte_cap must be positive")
    shard = _mapping(selected_shard, "selected_shard")
    shard_id = _required_str(shard, "shardId")
    raw = payload.encode("utf-8") if isinstance(payload, str) else bytes(payload)
    if len(raw) > byte_cap and not truncate:
        raise ValueError("payload exceeds byte_cap; set truncate=true to retain a bounded sample")
    sample = raw[:byte_cap]
    try:
        sample_text = sample.decode("utf-8")
    except UnicodeDecodeError:
        sample_text = sample.hex()
    non_authority_block = dict(non_authority or _non_authority_block())
    return {
        "version": SHARD_PAYLOAD_PROBE_VERSION,
        "selected_shard_id": shard_id,
        "section": shard.get("section"),
        "logicalKind": shard.get("logicalKind"),
        "encoding": shard.get("encoding"),
        "byte_cap": byte_cap,
        "payload_metadata": {
            "byte_length": len(raw),
            "truncated": len(raw) > byte_cap,
        },
        "payload_digest": "sha256:" + sha256(raw).hexdigest(),
        "payload_sample": sample_text,
        "candidate_only": True,
        "non_authoritative": True,
        "diagnostic_only": True,
        "complete_closure": False,
        "truth_authority": False,
        "support_authority": False,
        "admissibility_authority": False,
        "promotion_authority": False,
        "nonAuthority": non_authority_block,
        "authority_boundary": _authority_boundary(),
    }


def _split_selector(selector: str) -> tuple[str | None, str]:
    if "=" not in selector:
        return None, ""
    family, value = selector.split("=", 1)
    if family not in SELECTOR_FAMILIES:
        return None, value
    return family, value


def _route_selector_from_sidecar(
    artifact: Mapping[str, Any],
    family: str,
    value: str,
    route_index: Mapping[str, Any] | None,
) -> list[str]:
    if route_index is None:
        embedded = artifact.get("routingIndex")
        if isinstance(embedded, Mapping):
            candidate = embedded.get("routeIndex") or embedded.get("routing")
            if isinstance(candidate, Mapping):
                route_index = candidate
    if route_index is None:
        return []
    route_payload = route_index.get("routing") if isinstance(route_index.get("routing"), Mapping) else route_index
    if not isinstance(route_payload, Mapping):
        return []
    chunk_keys = _matching_route_chunks(route_payload, family, value)
    if not chunk_keys:
        return []
    by_chunk = _shards_by_section_chunk(artifact)
    matched: list[str] = []
    for key in chunk_keys:
        shard_id = by_chunk.get(key)
        if shard_id and shard_id not in matched:
            matched.append(shard_id)
    return matched


def _matching_route_chunks(route_payload: Mapping[str, Any], family: str, value: str) -> list[tuple[str, int, str | None]]:
    sections: tuple[str, ...]
    entry_key: str
    if family == "route-left-node":
        sections = ("left",)
        entry_key = "nodes"
    elif family == "route-right-node":
        sections = ("right",)
        entry_key = "nodes"
    elif family == "route-node":
        sections = ("left", "right", "nameOfNode")
        entry_key = "nodes"
    elif family == "route-name":
        sections = ("nodeOfName",)
        entry_key = "names"
    else:
        return []

    matched: list[tuple[str, int, str | None]] = []
    for section in sections:
        entries = route_payload.get(section)
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, Mapping):
                continue
            values = entry.get(entry_key)
            if not isinstance(values, list):
                continue
            if value not in {str(item) for item in values}:
                continue
            matched.append((section, _required_int(entry, "chunkIndex"), _optional_string(entry.get("lang"))))
    return matched


def _shards_by_section_chunk(artifact: Mapping[str, Any]) -> dict[tuple[str, int, str | None], str]:
    index: dict[tuple[str, int, str | None], str] = {}
    for shard in artifact["shards"]:
        section = str(shard["section"])
        chunk_index = _chunk_index_from_shard_id(str(shard["shardId"]))
        if chunk_index is None:
            continue
        lang = None
        for key in shard["routingKeys"]:
            if isinstance(key, str) and key.startswith("lang:"):
                lang = key.split(":", 1)[1]
        index[(section, chunk_index, lang)] = str(shard["shardId"])
        index[(section, chunk_index, None)] = str(shard["shardId"])
    return index


def _chunk_index_from_shard_id(shard_id: str) -> int | None:
    for token in reversed(shard_id.replace("-", " ").split()):
        if token.isdigit():
            return int(token)
    return None


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


def _logical_shard_id(chunk: Mapping[str, Any], selector_unit: str) -> str:
    unit = "bucket" if selector_unit == "bucket" else "chunk"
    base = f"{chunk['section']}-{unit}-{_required_int(chunk, 'chunkIndex'):06d}"
    lang = _optional_string(chunk.get("lang"))
    if lang:
        return f"{base}-{_sanitize_token(lang)}"
    return base


def _sanitize_token(value: str) -> str:
    token = "".join(ch if (ch.isalnum() or ch in ("_", "-", ".")) else "_" for ch in value)
    return token or "token"


def _artifact_id_from_manifest(manifest: Mapping[str, Any], source_bin_path: str | None) -> str:
    source = manifest.get("source")
    if isinstance(source, Mapping):
        artifact_name = source.get("artifactName")
        if isinstance(artifact_name, str) and artifact_name.strip():
            return artifact_name.strip()
    if source_bin_path:
        return Path(source_bin_path).stem
    manifest_ref = manifest.get("hfObjects")
    if isinstance(manifest_ref, Mapping):
        manifest_object = manifest_ref.get("manifest")
        if isinstance(manifest_object, Mapping):
            path = manifest_object.get("path")
            if isinstance(path, str) and path.strip():
                return Path(path).parent.name or "shared-artifact"
    return "shared-artifact"


def _identity_digest(chunk: Mapping[str, Any]) -> str:
    stable_bits = {
        "section": chunk["section"],
        "chunkIndex": _required_int(chunk, "chunkIndex"),
        "length": _required_int(chunk, "length"),
        "sourceOffset": int(chunk.get("sourceOffset", chunk.get("offset", 0)) or 0),
        "lang": chunk.get("lang"),
        "objectPath": chunk.get("objectPath") or chunk.get("futureObjectPath"),
    }
    return "identity-sha256:" + sha256(json.dumps(stable_bits, sort_keys=True).encode("utf-8")).hexdigest()


def _infer_logical_kind(section: str, selector_unit: str) -> str:
    if section in ("left", "right"):
        return "adjacency-bucket" if selector_unit == "bucket" else "adjacency-chunk"
    if section in ("nameOfNode", "nodeOfName"):
        return "name-bucket" if selector_unit == "bucket" else "name-chunk"
    return "content-shard"


def _infer_encoding(object_uri: str) -> str:
    if object_uri.endswith(".capnp-packed"):
        return "capnp-packed"
    if object_uri.endswith(".cbor"):
        return "cbor"
    if object_uri.endswith(".json"):
        return "json"
    return "application/octet-stream"


def _routing_keys_for_chunk(section: str, chunk: Mapping[str, Any]) -> list[str]:
    keys = [f"section:{section}"]
    lang = _optional_string(chunk.get("lang"))
    if lang:
        keys.append(f"lang:{lang}")
    if section == "left":
        keys.append("route-left-node")
    elif section == "right":
        keys.append("route-right-node")
    elif section == "nameOfNode":
        keys.append("route-node")
    elif section == "nodeOfName":
        keys.append("route-name")
    return keys


def _sink_for_uri(uri: str) -> str:
    if uri.startswith(_HF_SCHEMES):
        return "hf"
    if uri.startswith("ipfs://"):
        return "ipfs"
    return "file"


def _non_authority_block() -> dict[str, bool]:
    return {
        "artifact_transport_only": True,
        "candidate_graph_logistics": True,
        "truth_authority": False,
        "support_authority": False,
        "admissibility_authority": False,
        "promotion_authority": False,
        "complete_closure_authority": False,
        "candidate_only": True,
        "diagnostic_only": True,
    }


def _authority_boundary() -> dict[str, bool]:
    return {
        "read_only": True,
        "non_authoritative": True,
        "candidate_only": True,
        "canonical_truth_mutated": False,
        "truth_authority": False,
        "support_authority": False,
        "admissibility_authority": False,
        "promotion_authority": False,
    }


def _select_probe_shard_id(
    artifact: Mapping[str, Any],
    *,
    selector: str | None,
    shard_id: str | None,
    route_index: Mapping[str, Any] | None,
) -> str:
    if shard_id and selector:
        raise ValueError("provide selector or shard_id, not both")
    if shard_id:
        _shard_by_id(artifact, shard_id)
        return shard_id
    if selector:
        ids = route_selector(artifact, selector, route_index=route_index)
        if not ids:
            raise ValueError("selector did not match any shard")
        return ids[0]
    raise ValueError("selector or shard_id is required")


def _shard_by_id(artifact: Mapping[str, Any], shard_id: str) -> Mapping[str, Any]:
    for shard in artifact["shards"]:
        if shard["shardId"] == shard_id:
            return shard
    raise ValueError(f"unknown shard_id: {shard_id}")


def _preferred_object_ref(shard: Mapping[str, Any]) -> Mapping[str, Any]:
    refs = shard.get("objectRefs")
    if not isinstance(refs, list) or not refs:
        raise ValueError("selected shard has no objectRefs")
    for sink in ("file", "hf", "ipfs"):
        for ref in refs:
            if isinstance(ref, Mapping) and ref.get("sink") == sink:
                if sink == "ipfs":
                    continue
                return ref
    raise ValueError("selected shard has no probe-supported objectRef")


def _read_probe_bytes(
    ref: Mapping[str, Any],
    *,
    max_bytes: int,
    revision: str | None,
    opener: Any | None,
) -> dict[str, Any]:
    sink = _required_str(ref, "sink")
    uri = _required_str(ref, "uri")
    if sink == "file":
        path = Path(uri)
        with path.open("rb") as handle:
            data = handle.read(max_bytes + 1)
        return {"bytes": data[:max_bytes], "truncated": len(data) > max_bytes}
    if sink == "hf":
        return _fetch_hf_bytes(uri, revision=revision, max_bytes=max_bytes, opener=opener)
    raise ValueError(f"payload probe does not support sink: {sink}")


def _fetch_hf_bytes(
    hf_uri: str,
    *,
    revision: str | None,
    max_bytes: int,
    opener: Any | None,
) -> dict[str, Any]:
    ref = _parse_hf_uri(hf_uri)
    request = Request(ref.url(revision), headers={"Range": f"bytes=0-{max_bytes}"})
    caller = opener or urlopen
    try:
        response = caller(request, timeout=20)
        with response:
            data = response.read(max_bytes + 1)
            headers = getattr(response, "headers", {}) or {}
            resolved_revision = headers.get("x-repo-commit") if hasattr(headers, "get") else None
    except URLError as exc:
        raise ValueError(f"failed to fetch HF object: {exc}") from exc
    return {
        "bytes": data[:max_bytes],
        "truncated": len(data) > max_bytes,
        "sizeBytes": len(data[:max_bytes]),
        "sha256": sha256(data[:max_bytes]).hexdigest(),
        "revision": resolved_revision,
    }


def _parse_hf_uri(uri: str) -> _HfRef:
    if not uri.startswith("hf://"):
        raise ValueError(f"unsupported HF URI: {uri}")
    parts = [part for part in uri[len("hf://") :].split("/") if part]
    if len(parts) < 4:
        raise ValueError(f"HF URI must include type, repo id, and object path: {uri}")
    repo_type = parts[0]
    if repo_type not in {"datasets", "models", "spaces"}:
        raise ValueError(f"unsupported HF repo type: {repo_type}")
    return _HfRef(repo_type=repo_type, repo_id=f"{parts[1]}/{parts[2]}", object_path="/".join(parts[3:]))


def _mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} must be an object")
    return dict(value)


def _optional_string(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


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
