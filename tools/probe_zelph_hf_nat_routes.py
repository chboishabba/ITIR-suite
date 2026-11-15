#!/usr/bin/env python3
"""Pin upstream Zelph HF metadata and produce read-only exact Nat QID route receipts.

No Wikidata edits, graph truth promotion, full shard downloads or Cap'n Proto decode.
A missing advertised route sidecar is a BLOCKED routing result, never QID absence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import quote
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "itir-mcp" / "src"))
from itir_mcp.shard_transport import (  # noqa: E402
    build_shared_shard_contract_from_zelph_manifest,
    exact_wikidata_name_route,
)

API_URL = "https://huggingface.co/api/datasets/acrion/zelph"
ARTIFACTS = {
    "full": "wikidata-20260309-all",
    "pruned-small": "wikidata-20260309-all-pruned-small",
}
NAT_QIDS = ("Q10403939", "Q10416948", "Q10422059", "Q10651551", "Q56404383")
MANIFEST_CAP = 16 * 1024 * 1024
SIDECAR_CAP = 32 * 1024 * 1024


def _fetch_json(url: str, limit: int) -> tuple[dict, str]:
    req = Request(url, headers={"User-Agent": "itir-zelph-hf-audit/1.0"})
    with urlopen(req, timeout=40) as response:
        data = response.read(limit + 1)
    if len(data) > limit:
        raise ValueError(f"artifact exceeds bounded metadata cap of {limit} bytes")
    value = json.loads(data)
    if not isinstance(value, dict):
        raise ValueError("HF metadata must be a JSON object")
    return value, hashlib.sha256(data).hexdigest()


def _hf_object_https(uri: str, sha: str) -> str:
    prefix = "hf://datasets/acrion/zelph/"
    if not uri.startswith(prefix):
        raise ValueError("advertised route must be inside the pinned acrion/zelph dataset")
    object_path = uri[len(prefix):]
    if not object_path or ".." in object_path.split("/"):
        raise ValueError("invalid HF object path")
    return f"https://huggingface.co/datasets/acrion/zelph/resolve/{sha}/{quote(object_path, safe='/')}"


def _record(args: argparse.Namespace) -> dict:
    offline = bool(args.manifest_file or args.sidecar_file)
    if offline and not (args.manifest_file and args.sidecar_file and args.revision):
        raise ValueError("offline mode requires --manifest-file, --sidecar-file and --revision")
    if offline:
        sha = args.revision
        manifest_bytes = Path(args.manifest_file).read_bytes()
        route_bytes = Path(args.sidecar_file).read_bytes()
        if len(manifest_bytes) > MANIFEST_CAP or len(route_bytes) > SIDECAR_CAP:
            raise ValueError("offline metadata exceeds bounded cap")
        manifest = json.loads(manifest_bytes)
        route = json.loads(route_bytes)
        manifest_digest = hashlib.sha256(manifest_bytes).hexdigest()
        route_digest = hashlib.sha256(route_bytes).hexdigest()
        source = "offline-local-fixture"
    else:
        meta, _ = _fetch_json(API_URL, 1024 * 1024)
        sha = str(meta.get("sha") or "")
        if not re.fullmatch(r"[0-9a-fA-F]{40}", sha):
            raise ValueError("HF dataset API did not return a 40-digit immutable SHA")
        name = ARTIFACTS[args.artifact]
        path = f"{name}/{name}.hf-v2.json"
        manifest, manifest_digest = _fetch_json(
            _hf_object_https("hf://datasets/acrion/zelph/" + path, sha),
            MANIFEST_CAP,
        )
        route_info = (manifest.get("hfObjects") or {}).get("nodeRouteIndex")
        if not isinstance(route_info, dict) or not isinstance(route_info.get("path"), str):
            return {
                "status": "blocked",
                "phase": "manifest-route-index-not-advertised",
                "artifact": args.artifact,
                "dataset_sha": sha,
                "manifest_sha256": manifest_digest,
                "route_unresolved_is_not_absence": True,
                "production_accepted": False,
            }
        route, route_digest = _fetch_json(_hf_object_https(route_info["path"], sha), SIDECAR_CAP)
        source = "HF-revision-pinned-remote-metadata"
    if not isinstance(manifest, dict) or not isinstance(route, dict):
        raise ValueError("manifest and sidecar must both be JSON objects")
    contract = build_shared_shard_contract_from_zelph_manifest(
        manifest, artifact_revision=sha
    )
    receipts = []
    for qid in (tuple(args.qid) if args.qid else NAT_QIDS):
        try:
            result = exact_wikidata_name_route(contract, qid, route_index=route)
            receipts.append({"qid": qid, "status": "exact-route-planned", **result})
        except ValueError as exc:
            receipts.append({"qid": qid, "status": "route-unresolved", "reason": str(exc)})
    matched = sum(item["status"] == "exact-route-planned" for item in receipts)
    return {
        "status": "metadata-only" if matched == len(receipts) else "partial-or-blocked",
        "source": source,
        "artifact": args.artifact,
        "dataset_sha": sha,
        "manifest_sha256": manifest_digest,
        "sidecar_sha256": route_digest,
        "qid_count": len(receipts),
        "exact_route_count": matched,
        "route_receipts": receipts,
        "payload_fetch": False,
        "payload_decode": False,
        "semantic_coverage_proved": False,
        "native_wikidata_statement_proved": False,
        "source_support_paid": False,
        "wikidata_edits": False,
        "production_accepted": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", choices=ARTIFACTS, default="full")
    parser.add_argument("--qid", action="append", help="override one of the five Nat QIDs; repeat")
    parser.add_argument("--manifest-file", help="offline fixture only, never claim HF acceptance")
    parser.add_argument("--sidecar-file", help="offline fixture only")
    parser.add_argument("--revision", help="pinned offline fixture identity")
    args = parser.parse_args()
    try:
        receipt = _record(args)
        print(json.dumps(receipt, indent=2, sort_keys=True))
        return 0 if receipt["status"] == "metadata-only" else 2
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(json.dumps({
            "status": "blocked", "phase": "metadata-or-transport",
            "reason": str(exc), "production_accepted": False,
            "wikidata_edits": False,
        }, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
