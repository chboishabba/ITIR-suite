from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from typing import Any

from .artifact_receipt import build_artifact_resolution_receipt

_SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


def _required(name: str, value: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{name} must be non-empty")
    return text


def _statement_digest(value: str) -> str:
    text = _required("statement_digest", value).lower()
    if not _SHA256_RE.fullmatch(text):
        raise ValueError("statement_digest must be canonical sha256:<64 lowercase hex>")
    return text


def _sha256_bytes(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def package_formal_proof_artifact(
    *,
    source_path: Path,
    output_dir: Path,
    demand_ref: str,
    obligation_ref: str,
    statement_digest: str,
    da51_address: str | None,
    artifact_id: str | None = None,
) -> dict[str, Any]:
    source = source_path.resolve()
    if not source.is_file():
        raise ValueError(f"source_path is not a file: {source}")

    demand = _required("demand_ref", demand_ref)
    obligation = _required("obligation_ref", obligation_ref)
    statement = _statement_digest(statement_digest)
    da51 = None if da51_address is None else _required("da51_address", da51_address)

    payload = source.read_bytes()
    content_digest = _sha256_bytes(payload)
    content_hex = content_digest.split(":", 1)[1]
    size = len(payload)
    logical_artifact_id = (
        _required("artifact_id", artifact_id)
        if artifact_id is not None
        else f"formal-proof:{content_hex}"
    )
    artifact_revision = content_digest
    shard_id = "formal-proof-source"
    uri = source.as_uri()
    modified = datetime.fromtimestamp(source.stat().st_mtime, tz=timezone.utc).isoformat()

    object_ref = {
        "sink": "file",
        "uri": uri,
        "contentDigest": content_digest,
        "sizeBytes": size,
    }
    shard = {
        "shardId": shard_id,
        "contentDigest": content_digest,
        "sizeBytes": size,
        "objectRefs": [object_ref],
    }
    artifact: dict[str, Any] = {
        "contractVersion": "shared-shard-artifact/v1",
        "artifactId": logical_artifact_id,
        "artifactRevision": artifact_revision,
        "artifactClass": "formal-proof-source",
        "createdAtUtc": modified,
        "buildProvenance": {
            "sourceSystem": "slr-da51-formal-proof-runner",
            "sourcePath": str(source),
        },
        "formalProof": {
            "demandRef": demand,
            "obligationRef": obligation,
            "statementDigest": statement,
            "da51Address": da51,
        },
        "shards": [shard],
    }

    resolved = {
        "artifactId": logical_artifact_id,
        "artifactRevision": artifact_revision,
        "shard": {
            "id": shard_id,
            "contentDigest": content_digest,
        },
        "selectedObjectRef": object_ref,
        "payload": {
            "sha256": content_digest,
            "sizeBytes": size,
        },
        "fetch": {
            "sink": "file",
            "uri": uri,
            "metadata": {
                "source": "local-formal-proof-artifact",
            },
        },
        "matchedBy": "formal-proof-demand",
        "selectors": [
            f"formal-demand={demand}",
            f"external-obligation={obligation}",
            f"statement-digest={statement}",
        ],
    }
    receipt = build_artifact_resolution_receipt(resolved)

    out = output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    artifact_path = out / "shared-shard-artifact.json"
    resolved_path = out / "resolved-artifact.json"
    receipt_path = out / "artifact-resolution-receipt.json"
    artifact_path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    resolved_path.write_text(json.dumps(resolved, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    return {
        "artifact": artifact,
        "resolved": resolved,
        "receipt": receipt,
        "logical_artifact_ref": receipt["logicalArtifactRef"],
        "artifact_digest": receipt["contentDigest"],
        "artifact_path": str(source),
        "manifest_path": str(artifact_path),
        "resolved_path": str(resolved_path),
        "receipt_path": str(receipt_path),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Package one local formal proof source as a verified ITIR shared-shard artifact."
    )
    parser.add_argument("--source-path", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--demand-ref", required=True)
    parser.add_argument("--obligation-ref", required=True)
    parser.add_argument("--statement-digest", required=True)
    parser.add_argument("--da51")
    parser.add_argument("--artifact-id")
    args = parser.parse_args(argv)

    result = package_formal_proof_artifact(
        source_path=args.source_path,
        output_dir=args.output_dir,
        demand_ref=args.demand_ref,
        obligation_ref=args.obligation_ref,
        statement_digest=args.statement_digest,
        da51_address=args.da51,
        artifact_id=args.artifact_id,
    )
    print(f"logical_artifact_ref\t{result['logical_artifact_ref']}")
    print(f"artifact_digest\t{result['artifact_digest']}")
    print(f"artifact_path\t{result['artifact_path']}")
    print(f"artifact_resolution_receipt\t{result['receipt_path']}")
    print(f"shared_shard_manifest\t{result['manifest_path']}")
    print(f"resolved_artifact\t{result['resolved_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
