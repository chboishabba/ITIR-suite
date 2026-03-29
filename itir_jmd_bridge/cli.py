from __future__ import annotations

import argparse
import json
from pathlib import Path

from .hf_rehearsal import (
    extract_tar_member_bytes,
    load_erdfa_manifest_fixture,
    load_hf_container_fixture,
    resolve_container_member,
    resolve_selector_to_local_member_payload,
    resolve_selector_to_container_member,
)
from .providers.pastebin import discover_host_capabilities
from .runtime import build_runtime_bundle, build_runtime_graph, ingest_latest_pastes, inspect_latest_pastes_with_prototype


def _write_json(payload: dict, path: Path | None) -> None:
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    if path is None:
        print(rendered)
    else:
        path.write_text(rendered + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="JMD runtime bridge CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    resolve = sub.add_parser("resolve-bundle", help="Resolve a paste/ERDFA source into runtime object/graph/receipt payloads")
    resolve.add_argument("--paste-url")
    resolve.add_argument("--base-url")
    resolve.add_argument("--paste-id")
    resolve.add_argument("--erdfa-descriptor", type=Path)
    resolve.add_argument("--erdfa-tar", type=Path)
    resolve.add_argument("--object-output", type=Path)
    resolve.add_argument("--graph-output", type=Path)
    resolve.add_argument("--receipt-output", type=Path)
    resolve.add_argument("--verify-ipfs", action="store_true")

    graph = sub.add_parser("build-graph", help="Build a runtime graph from a resolved runtime object")
    graph.add_argument("--runtime-object", type=Path, required=True)
    graph.add_argument("--output", type=Path)

    latest = sub.add_parser("ingest-latest", help="Resolve the latest N browse-page pastes into runtime bundles")
    latest.add_argument("--base-url", required=True)
    latest.add_argument("--limit", type=int, default=5)
    latest.add_argument("--concurrency", type=int, default=2)
    latest.add_argument("--request-spacing-ms", type=int, default=400)
    latest.add_argument("--verify-ipfs", action="store_true")
    latest.add_argument("--ipfs-gateway-base-url")
    latest.add_argument("--allow-ipfs-cli-fallback", action="store_true")
    latest.add_argument("--output", type=Path)
    latest.add_argument("--strict", action="store_true")

    prototype_latest = sub.add_parser("inspect-latest-prototype", help="Resolve the latest N browse-page pastes and summarize prototype normalization/proof output")
    prototype_latest.add_argument("--base-url", required=True)
    prototype_latest.add_argument("--limit", type=int, default=5)
    prototype_latest.add_argument("--concurrency", type=int, default=2)
    prototype_latest.add_argument("--request-spacing-ms", type=int, default=400)
    prototype_latest.add_argument("--verify-ipfs", action="store_true")
    prototype_latest.add_argument("--ipfs-gateway-base-url")
    prototype_latest.add_argument("--allow-ipfs-cli-fallback", action="store_true")
    prototype_latest.add_argument("--output", type=Path)
    prototype_latest.add_argument("--strict", action="store_true")

    discover = sub.add_parser("discover-capabilities", help="Probe documented and observed host surfaces")
    discover.add_argument("--base-url", required=True)
    discover.add_argument("--output", type=Path)

    rehearse_hf = sub.add_parser(
        "rehearse-hf-container",
        help="Resolve one shardId through the local HF container fixture",
    )
    rehearse_hf.add_argument("--fixture", type=Path, required=True)
    rehearse_hf.add_argument("--shard-id", required=True)
    rehearse_hf.add_argument("--output", type=Path)

    rehearse_selector = sub.add_parser(
        "rehearse-selector-fetch",
        help="Resolve selectors through the promoted-manifest fixture and optional HF container fixture",
    )
    rehearse_selector.add_argument("--manifest-fixture", type=Path, required=True)
    rehearse_selector.add_argument("--container-fixture", type=Path, help="If omitted, default memberPath inference is used")
    rehearse_selector.add_argument(
        "--selector",
        action="append",
        dest="selectors",
        required=True,
        help="Selector key such as route-name=tenant or route-lang=en",
    )
    rehearse_selector.add_argument("--output", type=Path)

    rehearse_tar = sub.add_parser(
        "rehearse-local-tar-extract",
        help="Extract one member from a local tar/tar.zst by member path",
    )
    rehearse_tar.add_argument("--tar-path", type=Path, required=True)
    rehearse_tar.add_argument("--member-path", required=True)
    rehearse_tar.add_argument("--output", type=Path)

    rehearse_selector_tar = sub.add_parser(
        "rehearse-selector-local-tar-fetch",
        help="Resolve selectors through fixtures and extract the matching member from a local tar",
    )
    rehearse_selector_tar.add_argument("--manifest-fixture", type=Path, required=True)
    rehearse_selector_tar.add_argument("--container-fixture", type=Path, help="If omitted, memberPath is inferred (shardId.cbor or payload/shardId.cbor)")
    rehearse_selector_tar.add_argument("--tar-path", type=Path, required=True)
    rehearse_selector_tar.add_argument(
        "--selector",
        action="append",
        dest="selectors",
        required=True,
        help="Selector key such as route-name=tenant or route-lang=en",
    )
    rehearse_selector_tar.add_argument("--output", type=Path)

    args = parser.parse_args(argv)

    if args.command == "resolve-bundle":
        bundle = build_runtime_bundle(
            paste_url=args.paste_url,
            base_url=args.base_url,
            paste_id=args.paste_id,
            erdfa_descriptor=args.erdfa_descriptor,
            erdfa_tar_path=args.erdfa_tar,
            verify_ipfs=bool(args.verify_ipfs),
        )
        _write_json(bundle["runtime_object"], args.object_output)
        _write_json(bundle["runtime_graph"], args.graph_output)
        _write_json(bundle["runtime_receipt"], args.receipt_output)
        return 0

    if args.command == "ingest-latest":
        payload = ingest_latest_pastes(
            base_url=args.base_url,
            limit=args.limit,
            concurrency=args.concurrency,
            request_spacing_seconds=max(args.request_spacing_ms, 0) / 1000.0,
            verify_ipfs=bool(args.verify_ipfs),
            ipfs_gateway_base_url=args.ipfs_gateway_base_url,
            allow_ipfs_cli_fallback=bool(args.allow_ipfs_cli_fallback),
        )
        _write_json(payload, args.output)
        return 1 if args.strict and payload["failure_count"] else 0

    if args.command == "inspect-latest-prototype":
        payload = inspect_latest_pastes_with_prototype(
            base_url=args.base_url,
            limit=args.limit,
            concurrency=args.concurrency,
            request_spacing_seconds=max(args.request_spacing_ms, 0) / 1000.0,
            verify_ipfs=bool(args.verify_ipfs),
            ipfs_gateway_base_url=args.ipfs_gateway_base_url,
            allow_ipfs_cli_fallback=bool(args.allow_ipfs_cli_fallback),
        )
        _write_json(payload, args.output)
        return 1 if args.strict and payload["failure_count"] else 0

    if args.command == "discover-capabilities":
        payload = discover_host_capabilities(base_url=args.base_url)
        _write_json(payload, args.output)
        return 0

    if args.command == "rehearse-hf-container":
        fixture = load_hf_container_fixture(args.fixture)
        payload = resolve_container_member(fixture, shard_id=args.shard_id)
        _write_json(payload, args.output)
        return 0

    if args.command == "rehearse-selector-fetch":
        manifest = load_erdfa_manifest_fixture(args.manifest_fixture)
        container_fixture = load_hf_container_fixture(args.container_fixture) if args.container_fixture else None
        payload = resolve_selector_to_container_member(
            manifest,
            container_fixture,
            selectors=list(args.selectors),
        )
        _write_json(payload, args.output)
        return 0

    if args.command == "rehearse-local-tar-extract":
        payload = {
            "memberPath": args.member_path,
            "payload": {
                "sizeBytes": len(extract_tar_member_bytes(args.tar_path, member_path=args.member_path)),
            },
        }
        _write_json(payload, args.output)
        return 0

    if args.command == "rehearse-selector-local-tar-fetch":
        manifest = load_erdfa_manifest_fixture(args.manifest_fixture)
        container_fixture = load_hf_container_fixture(args.container_fixture) if args.container_fixture else None
        payload = resolve_selector_to_local_member_payload(
            manifest,
            container_fixture,
            selectors=list(args.selectors),
            tar_path=args.tar_path,
        )
        _write_json(payload, args.output)
        return 0

    payload = json.loads(args.runtime_object.read_text(encoding="utf-8"))
    _write_json(build_runtime_graph(payload), args.output)
    return 0
