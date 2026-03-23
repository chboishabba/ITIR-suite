from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import json
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import threading
import time
from typing import Any, Callable

import requests

from .providers.erdfa import normalize_erdfa_descriptor
from .providers.dasl import decode_dasl_hex
from .providers.ipfs import fetch_ipfs_content
from .providers.pastebin import discover_host_capabilities, fetch_browse_listing, fetch_paste_record, parse_paste_reference


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _token_count(text: str) -> int:
    return len([token for token in text.split() if token])


def _content_ref_from_metadata(metadata: dict[str, Any], reference: dict[str, Any], erdfa: dict[str, Any]) -> dict[str, Any]:
    content_ref: dict[str, Any] = {
        "paste_ref": {
            "provider": reference["provider"],
            "paste_id": reference["paste_id"],
            "raw_url": reference["raw_url"],
            "paste_url": reference["paste_url"],
            "base_url": reference["base_url"],
        }
    }
    ipfs_cid = metadata.get("IPFS") or metadata.get("ipfs_cid") or erdfa.get("cid")
    if ipfs_cid:
        content_ref["cid_ref"] = {"provider": "ipfs", "cid": ipfs_cid}
    elif metadata.get("CID"):
        content_ref["cid_ref"] = {"provider": "kant-zk-pastebin-local-cid", "cid": metadata["CID"]}
    return content_ref


def _maybe_verify_ipfs(
    *,
    content_ref: dict[str, Any],
    base_url: str,
    text: str,
    get: Callable[..., Any] | None,
    timeout: float,
    ipfs_gateway_base_url: str | None = None,
    allow_ipfs_cli_fallback: bool = False,
) -> dict[str, Any] | None:
    cid_ref = content_ref.get("cid_ref")
    if not cid_ref or cid_ref.get("provider") != "ipfs":
        return None
    gateway_base = ipfs_gateway_base_url or base_url
    ipfs_record = fetch_ipfs_content(
        cid=cid_ref["cid"],
        base_url=gateway_base,
        get=get,
        timeout=timeout,
        allow_cli_fallback=allow_ipfs_cli_fallback,
    )
    normalized_proxy_text = ipfs_record["text"].strip()
    text_sha = sha256(text.strip().encode("utf-8")).hexdigest()
    return {
        "provider": ipfs_record["provider"],
        "url": ipfs_record["url"],
        "fetched_at": ipfs_record["fetched_at"],
        "status_code": ipfs_record["status_code"],
        "content_sha256": sha256(normalized_proxy_text.encode("utf-8")).hexdigest(),
        "matches_body_text": sha256(normalized_proxy_text.encode("utf-8")).hexdigest() == text_sha,
    }


def _build_default_getter() -> Callable[..., Any]:
    local = threading.local()

    def getter(url: str, timeout: float = 10.0, headers: dict[str, str] | None = None) -> Any:
        session = getattr(local, "session", None)
        if session is None:
            session = requests.Session()
            local.session = session
        return session.get(url, timeout=timeout, headers=headers)

    return getter


def _surface_status_map(capabilities: dict[str, Any]) -> dict[str, dict[str, Any]]:
    observed = {
        item["path"]: item
        for item in capabilities.get("observed_surfaces") or []
        if isinstance(item, dict) and item.get("path")
    }
    documented = set(capabilities.get("documented_paths") or [])
    statuses: dict[str, dict[str, Any]] = {}
    for path in sorted(documented | set(observed.keys())):
        observed_item = observed.get(path)
        statuses[path] = {
            "path": path,
            "documented": path in documented,
            "observed": observed_item is not None,
            "status_code": None if observed_item is None else observed_item.get("status_code"),
        }
    return statuses


def _dependency_metadata(
    capabilities: dict[str, Any],
    *,
    uses_raw: bool = False,
    uses_ipfs: bool = False,
) -> dict[str, Any]:
    surface_status = _surface_status_map(capabilities)
    dependencies: list[dict[str, Any]] = []
    if "/browse" in surface_status:
        dependencies.append({"role": "discovery", **surface_status["/browse"]})
    if uses_raw:
        raw_status = surface_status.get("/raw/example-probe", {"path": "/raw/example-probe", "documented": False, "observed": False, "status_code": None})
        dependencies.append({"role": "content_fetch", **raw_status})
    if uses_ipfs:
        ipfs_status = surface_status.get("/ipfs/example-probe", {"path": "/ipfs/example-probe", "documented": False, "observed": False, "status_code": None})
        dependencies.append({"role": "ipfs_verify", **ipfs_status})
    return {
        "dependencies": dependencies,
        "undeclared_dependency_count": sum(1 for item in dependencies if not item["documented"]),
    }


def _adaptive_ingest_settings(
    capabilities: dict[str, Any],
    *,
    requested_concurrency: int,
    requested_spacing_seconds: float,
) -> dict[str, Any]:
    concurrency = max(1, requested_concurrency)
    spacing_seconds = max(0.0, requested_spacing_seconds)
    reasons: list[str] = []
    warnings = capabilities.get("warnings") or []
    surface_status = _surface_status_map(capabilities)
    raw_status = surface_status.get("/raw/example-probe")

    if any(str(warning).startswith("openapi_unavailable:") for warning in warnings):
        concurrency = 1
        spacing_seconds = max(spacing_seconds, 0.75)
        reasons.append("openapi_probe_unstable")
    if raw_status is None or not raw_status.get("observed"):
        concurrency = 1
        spacing_seconds = max(spacing_seconds, 0.75)
        reasons.append("raw_surface_not_confirmed")
    elif not raw_status.get("documented"):
        concurrency = min(concurrency, 2)
        spacing_seconds = max(spacing_seconds, 0.5)
        reasons.append("raw_surface_undeclared")

    return {
        "requested_concurrency": requested_concurrency,
        "effective_concurrency": concurrency,
        "requested_spacing_seconds": requested_spacing_seconds,
        "effective_spacing_seconds": spacing_seconds,
        "reasons": reasons,
    }


def build_runtime_object(
    *,
    paste_url: str | None = None,
    base_url: str | None = None,
    paste_id: str | None = None,
    erdfa_descriptor: dict[str, Any] | str | Path | None = None,
    erdfa_tar_path: str | Path | None = None,
    get: Callable[..., Any] | None = None,
    timeout: float = 10.0,
    verify_ipfs: bool = False,
    ipfs_gateway_base_url: str | None = None,
    allow_ipfs_cli_fallback: bool = False,
) -> dict[str, Any]:
    reference = parse_paste_reference(paste_url=paste_url, base_url=base_url, paste_id=paste_id)
    paste_record = fetch_paste_record(reference, get=get, timeout=timeout)
    metadata = paste_record["metadata"]
    erdfa = normalize_erdfa_descriptor(erdfa_descriptor, tar_path=erdfa_tar_path)

    shard_id = str(erdfa.get("shard_id") or reference.paste_id)
    object_id = str(erdfa.get("object_id") or f"jmd:erdfa:shard:{shard_id}")
    text = paste_record["body"] or paste_record["raw_text"]
    content_ref = _content_ref_from_metadata(metadata, paste_record["reference"], erdfa)
    ipfs_verification = None
    if verify_ipfs:
        ipfs_verification = _maybe_verify_ipfs(
            content_ref=content_ref,
            base_url=reference.base_url,
            text=text,
            get=get,
            timeout=timeout,
            ipfs_gateway_base_url=ipfs_gateway_base_url,
            allow_ipfs_cli_fallback=allow_ipfs_cli_fallback,
        )
    object_payload = {
        "contract_version": "jmd.runtime.object.v1",
        "resolved_at": _utc_now(),
        "provider": {
            "kind": "pastebin",
            "name": "kant-zk-pastebin",
            "base_url": reference.base_url,
        },
        "object": {
            "object_id": object_id,
            "object_type": str(erdfa.get("object_type") or "shard"),
            "content_type": metadata.get("Mime", "text/plain; charset=utf-8"),
            "title": metadata.get("Title") or shard_id,
            "text": text,
            "raw_text": paste_record["raw_text"],
            "token_count": _token_count(text),
            "content_ref": content_ref,
            "erdfa": {
                "provider": str(erdfa.get("provider") or "erdfa-publish-rs"),
                "shard_id": shard_id,
                "cid": erdfa.get("cid") or metadata.get("IPFS") or metadata.get("CID"),
                "component_kind": erdfa.get("component_kind") or "text",
                "component_type": erdfa.get("component_type"),
                "local_cid": metadata.get("CID"),
                "witness": metadata.get("Witness"),
                "reply_to": metadata.get("Reply-To"),
                "dasl": decode_dasl_hex(metadata.get("DASL")),
                "tags": list(erdfa.get("tags") or []),
                "parent_refs": list(erdfa.get("parent_refs") or []),
                "link_refs": list(erdfa.get("link_refs") or []),
                "archive": erdfa.get("archive"),
            },
            "provenance": {
                "source": "pastebin",
                "captured_at": paste_record["retrieval"]["fetched_at"],
                "source_url": paste_record["reference"]["paste_url"],
                "retrieval_mode": "http_raw",
                "raw_text_sha256": paste_record["retrieval"]["raw_text_sha256"],
                "body_text_sha256": paste_record["retrieval"]["body_text_sha256"],
                "ipfs_verification": ipfs_verification,
            },
        },
    }
    return object_payload


def build_runtime_graph(runtime_object: dict[str, Any]) -> dict[str, Any]:
    obj = runtime_object["object"]
    erdfa = obj.get("erdfa", {})
    primary_node_id = obj["object_id"]
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    node_index: dict[str, dict[str, Any]] = {}
    seen_edges: set[str] = set()

    def ensure_node(node: dict[str, Any]) -> None:
        node_id = node["node_id"]
        existing = node_index.get(node_id)
        if existing is None:
            node_index[node_id] = node
            nodes.append(node)
            return
        for key, value in node.items():
            if key == "kind" and value and existing.get("kind") in {"shard", "parent", "linked"}:
                existing[key] = value
                continue
            if key not in existing or existing[key] in (None, "", [], {}):
                existing[key] = value

    def ensure_ref_node(ref: str, kind: str) -> None:
        ensure_node({"node_id": ref, "kind": kind, "cid": None, "label": ref, "ref": ref})

    def ensure_edge(edge: dict[str, Any]) -> None:
        edge_id = edge["edge_id"]
        if edge_id not in seen_edges:
            seen_edges.add(edge_id)
            edges.append(edge)

    ensure_node(
        {
            "node_id": primary_node_id,
            "kind": obj.get("object_type", "shard"),
            "cid": erdfa.get("cid"),
            "label": obj.get("title") or erdfa.get("shard_id") or primary_node_id,
            "ref": primary_node_id,
        }
    )

    archive_graph = ((erdfa.get("archive") or {}).get("graph") or {})
    for archive_node in archive_graph.get("nodes") or []:
        if isinstance(archive_node, dict) and archive_node.get("node_id"):
            ensure_node(dict(archive_node))
    for archive_edge in archive_graph.get("edges") or []:
        if isinstance(archive_edge, dict) and archive_edge.get("edge_id"):
            ensure_edge(dict(archive_edge))

    for parent_ref in erdfa.get("parent_refs") or []:
        ensure_ref_node(parent_ref, "parent")
        ensure_edge(
            {
                "edge_id": f"{parent_ref}->{primary_node_id}:parent",
                "from_node_id": parent_ref,
                "to_node_id": primary_node_id,
                "kind": "parent",
            }
        )
    for link_ref in erdfa.get("link_refs") or []:
        ensure_ref_node(link_ref, "linked")
        ensure_edge(
            {
                "edge_id": f"{primary_node_id}->{link_ref}:link",
                "from_node_id": primary_node_id,
                "to_node_id": link_ref,
                "kind": "link",
            }
        )

    graph_digest = sha256(json.dumps({"nodes": nodes, "edges": edges}, sort_keys=True).encode("utf-8")).hexdigest()
    return {
        "contract_version": "jmd.runtime.graph.v1",
        "generated_at": _utc_now(),
        "graph_id": f"jmd-graph:{graph_digest[:16]}",
        "source_object_id": primary_node_id,
        "nodes": nodes,
        "edges": edges,
    }


def build_runtime_receipt(
    runtime_object: dict[str, Any],
    runtime_graph: dict[str, Any] | None = None,
    *,
    downstream_handoffs: list[dict[str, Any]] | None = None,
    capabilities: dict[str, Any] | None = None,
) -> dict[str, Any]:
    obj = runtime_object["object"]
    provenance = obj["provenance"]
    content_ref = obj["content_ref"]
    raw_locator = content_ref["paste_ref"]["raw_url"]
    receipt_digest = sha256(
        json.dumps(
            {
                "object_id": obj["object_id"],
                "raw_locator": raw_locator,
                "graph_id": runtime_graph.get("graph_id") if runtime_graph else None,
                "resolved_at": runtime_object["resolved_at"],
            },
            sort_keys=True,
        ).encode("utf-8")
    ).hexdigest()
    receipt = {
        "contract_version": "jmd.runtime.receipt.v1",
        "receipt_id": f"jmd-receipt:{receipt_digest[:16]}",
        "recorded_at": _utc_now(),
        "status": "ok",
        "provider_kind": runtime_object["provider"]["kind"],
        "provider_name": runtime_object["provider"]["name"],
        "object_refs": [
            {
                "object_id": obj["object_id"],
                "locator": raw_locator,
                "content_sha256": provenance["body_text_sha256"],
            }
        ],
        "graph_refs": [],
        "actions": [
            {
                "kind": "fetch_raw",
                "locator": raw_locator,
                "fetched_at": provenance["captured_at"],
                "status": "ok",
            }
        ],
        "downstream_handoffs": list(downstream_handoffs or []),
    }
    if runtime_graph is not None:
        receipt["graph_refs"].append(
            {
                "graph_id": runtime_graph["graph_id"],
                "source_object_id": runtime_graph["source_object_id"],
            }
        )
    if obj.get("erdfa", {}).get("archive"):
        receipt["actions"].append(
            {
                "kind": "inspect_erdfa_archive",
                "locator": obj["erdfa"]["archive"]["archive_path"],
                "status": "ok",
            }
        )
    ipfs_verification = provenance.get("ipfs_verification")
    if ipfs_verification is not None:
        receipt["actions"].append(
            {
                "kind": "verify_ipfs_proxy",
                "locator": ipfs_verification["url"],
                "fetched_at": ipfs_verification["fetched_at"],
                "status": "ok" if ipfs_verification["matches_body_text"] else "mismatch",
            }
        )
    if capabilities is not None:
        receipt["dependency_metadata"] = _dependency_metadata(
            capabilities,
            uses_raw=True,
            uses_ipfs=ipfs_verification is not None,
        )
    return receipt


def build_runtime_bundle(
    *,
    paste_url: str | None = None,
    base_url: str | None = None,
    paste_id: str | None = None,
    erdfa_descriptor: dict[str, Any] | str | Path | None = None,
    erdfa_tar_path: str | Path | None = None,
    get: Callable[..., Any] | None = None,
    timeout: float = 10.0,
    downstream_handoffs: list[dict[str, Any]] | None = None,
    verify_ipfs: bool = False,
    ipfs_gateway_base_url: str | None = None,
    allow_ipfs_cli_fallback: bool = False,
    capabilities: dict[str, Any] | None = None,
) -> dict[str, dict[str, Any]]:
    runtime_object = build_runtime_object(
        paste_url=paste_url,
        base_url=base_url,
        paste_id=paste_id,
        erdfa_descriptor=erdfa_descriptor,
        erdfa_tar_path=erdfa_tar_path,
        get=get,
        timeout=timeout,
        verify_ipfs=verify_ipfs,
        ipfs_gateway_base_url=ipfs_gateway_base_url,
        allow_ipfs_cli_fallback=allow_ipfs_cli_fallback,
    )
    runtime_graph = build_runtime_graph(runtime_object)
    runtime_receipt = build_runtime_receipt(
        runtime_object,
        runtime_graph,
        downstream_handoffs=downstream_handoffs,
        capabilities=capabilities,
    )
    return {
        "runtime_object": runtime_object,
        "runtime_graph": runtime_graph,
        "runtime_receipt": runtime_receipt,
    }


def ingest_latest_pastes(
    *,
    base_url: str,
    limit: int = 5,
    get: Callable[..., Any] | None = None,
    timeout: float = 10.0,
    verify_ipfs: bool = False,
    concurrency: int = 2,
    request_spacing_seconds: float = 0.4,
    ipfs_gateway_base_url: str | None = None,
    allow_ipfs_cli_fallback: bool = False,
) -> dict[str, Any]:
    getter = get or _build_default_getter()
    capabilities = discover_host_capabilities(
        base_url=base_url,
        get=getter,
        timeout=timeout,
    )
    adaptive_settings = _adaptive_ingest_settings(
        capabilities,
        requested_concurrency=concurrency,
        requested_spacing_seconds=request_spacing_seconds,
    )
    browse_listing = fetch_browse_listing(
        base_url=base_url,
        limit=limit,
        get=getter,
        timeout=timeout,
    )
    results: list[dict[str, Any]] = []
    failure_count = 0

    limiter_lock = threading.Lock()
    next_start_at = time.monotonic()

    def wait_for_start_slot() -> None:
        nonlocal next_start_at
        effective_spacing_seconds = adaptive_settings["effective_spacing_seconds"]
        if effective_spacing_seconds <= 0:
            return
        with limiter_lock:
            now = time.monotonic()
            wait_seconds = max(0.0, next_start_at - now)
            next_start_at = max(now, next_start_at) + effective_spacing_seconds
        if wait_seconds > 0:
            time.sleep(wait_seconds)

    def resolve_entry(entry: dict[str, Any]) -> dict[str, Any]:
        wait_for_start_slot()
        try:
            bundle = build_runtime_bundle(
                base_url=entry["base_url"],
                paste_id=entry["paste_id"],
                get=getter,
                timeout=timeout,
                verify_ipfs=verify_ipfs,
                ipfs_gateway_base_url=ipfs_gateway_base_url,
                allow_ipfs_cli_fallback=allow_ipfs_cli_fallback,
                capabilities=capabilities,
            )
            runtime_object = bundle["runtime_object"]["object"]
            runtime_graph = bundle["runtime_graph"]
            runtime_receipt = bundle["runtime_receipt"]
            ipfs_verification = runtime_object["provenance"].get("ipfs_verification")
            return {
                "paste_id": entry["paste_id"],
                "title": entry["title"],
                "paste_url": entry["paste_url"],
                "status": "ok",
                "object_id": runtime_object["object_id"],
                "graph_node_count": len(runtime_graph["nodes"]),
                "graph_edge_count": len(runtime_graph["edges"]),
                "content_sha256": runtime_object["provenance"]["body_text_sha256"],
                "ipfs_verified": None if ipfs_verification is None else bool(ipfs_verification["matches_body_text"]),
                "dependency_metadata": runtime_receipt.get("dependency_metadata"),
            }
        except Exception as exc:
            return {
                "paste_id": entry["paste_id"],
                "title": entry["title"],
                "paste_url": entry["paste_url"],
                "status": "error",
                "error": str(exc),
            }

    entries = browse_listing["entries"]
    max_workers = max(1, min(int(adaptive_settings["effective_concurrency"]), len(entries) or 1))
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for item in executor.map(resolve_entry, entries):
            if item["status"] != "ok":
                failure_count += 1
            results.append(item)

    return {
        "base_url": browse_listing["base_url"],
        "browse_url": browse_listing["browse_url"],
        "fetched_at": browse_listing["fetched_at"],
        "capabilities": capabilities,
        "attempts": browse_listing["attempts"],
        "requested_limit": limit,
        "adaptive_settings": adaptive_settings,
        "concurrency": max_workers,
        "request_spacing_seconds": adaptive_settings["effective_spacing_seconds"],
        "resolved_count": len(results),
        "failure_count": failure_count,
        "results": results,
    }


def inspect_latest_pastes_with_prototype(
    *,
    base_url: str,
    limit: int = 5,
    get: Callable[..., Any] | None = None,
    timeout: float = 10.0,
    verify_ipfs: bool = False,
    concurrency: int = 2,
    request_spacing_seconds: float = 0.4,
    ipfs_gateway_base_url: str | None = None,
    allow_ipfs_cli_fallback: bool = False,
) -> dict[str, Any]:
    from .prototype_mdl import run_runtime_bundle_pipeline

    getter = get or _build_default_getter()
    capabilities = discover_host_capabilities(
        base_url=base_url,
        get=getter,
        timeout=timeout,
    )
    adaptive_settings = _adaptive_ingest_settings(
        capabilities,
        requested_concurrency=concurrency,
        requested_spacing_seconds=request_spacing_seconds,
    )
    browse_listing = fetch_browse_listing(
        base_url=base_url,
        limit=limit,
        get=getter,
        timeout=timeout,
    )
    results: list[dict[str, Any]] = []
    failure_count = 0

    limiter_lock = threading.Lock()
    next_start_at = time.monotonic()

    def wait_for_start_slot() -> None:
        nonlocal next_start_at
        effective_spacing_seconds = adaptive_settings["effective_spacing_seconds"]
        if effective_spacing_seconds <= 0:
            return
        with limiter_lock:
            now = time.monotonic()
            wait_seconds = max(0.0, next_start_at - now)
            next_start_at = max(now, next_start_at) + effective_spacing_seconds
        if wait_seconds > 0:
            time.sleep(wait_seconds)

    def inspect_entry(entry: dict[str, Any]) -> dict[str, Any]:
        wait_for_start_slot()
        try:
            bundle = build_runtime_bundle(
                base_url=entry["base_url"],
                paste_id=entry["paste_id"],
                get=getter,
                timeout=timeout,
                verify_ipfs=verify_ipfs,
                ipfs_gateway_base_url=ipfs_gateway_base_url,
                allow_ipfs_cli_fallback=allow_ipfs_cli_fallback,
                capabilities=capabilities,
            )
            runtime_object = bundle["runtime_object"]["object"]
            runtime_graph = bundle["runtime_graph"]
            prototype = run_runtime_bundle_pipeline(bundle)
            transform_plan = prototype["transform_plan"]
            proof = prototype["proof"]
            return {
                "paste_id": entry["paste_id"],
                "title": entry["title"],
                "paste_url": entry["paste_url"],
                "status": "ok",
                "object_id": runtime_object["object_id"],
                "graph_node_count": len(runtime_graph["nodes"]),
                "graph_edge_count": len(runtime_graph["edges"]),
                "candidate_count": len(prototype["candidate_transforms"]),
                "transform_count": len(transform_plan),
                "proof_net_gain": proof["net_gain"],
                "proof_base_cost": proof["base_cost"],
                "proof_normalized_cost": proof["normalized_cost"],
                "dictionary_keys": sorted(prototype["dictionary"].keys()),
                "transform_macros": [step["macro_id"] for step in transform_plan],
                "dependency_metadata": bundle["runtime_receipt"].get("dependency_metadata"),
            }
        except Exception as exc:
            return {
                "paste_id": entry["paste_id"],
                "title": entry["title"],
                "paste_url": entry["paste_url"],
                "status": "error",
                "error": str(exc),
            }

    entries = browse_listing["entries"]
    max_workers = max(1, min(int(adaptive_settings["effective_concurrency"]), len(entries) or 1))
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for item in executor.map(inspect_entry, entries):
            if item["status"] != "ok":
                failure_count += 1
            results.append(item)

    return {
        "base_url": browse_listing["base_url"],
        "browse_url": browse_listing["browse_url"],
        "fetched_at": browse_listing["fetched_at"],
        "capabilities": capabilities,
        "attempts": browse_listing["attempts"],
        "requested_limit": limit,
        "adaptive_settings": adaptive_settings,
        "concurrency": max_workers,
        "request_spacing_seconds": adaptive_settings["effective_spacing_seconds"],
        "resolved_count": len(results),
        "failure_count": failure_count,
        "results": results,
    }
