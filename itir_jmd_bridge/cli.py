from __future__ import annotations

import argparse
import json
from pathlib import Path

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

    payload = json.loads(args.runtime_object.read_text(encoding="utf-8"))
    _write_json(build_runtime_graph(payload), args.output)
    return 0
