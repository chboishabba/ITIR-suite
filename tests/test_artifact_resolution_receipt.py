from __future__ import annotations

import pytest

from itir_jmd_bridge.artifact_receipt import build_artifact_resolution_receipt


DIGEST = "a" * 64


def resolved(*, payload_digest: str = DIGEST, cid: str = "bafy-demo-erdfa-tar") -> dict:
    return {
        "artifactId": "mabo-formal-proof",
        "artifactRevision": "rev-1",
        "matchedBy": "direct-shard",
        "selectors": ["direct-shard=proof-1"],
        "shard": {
            "id": "proof-1",
            "contentDigest": f"sha256:{DIGEST}",
        },
        "selectedObjectRef": {
            "sink": "ipfs",
            "uri": f"ipfs://{cid}",
            "memberPath": "payload/proof-1.olean",
            "sizeBytes": 12,
            "contentDigest": f"sha256:{DIGEST}",
        },
        "payload": {
            "sizeBytes": 12,
            "sha256": payload_digest,
        },
        "fetch": {
            "sink": "ipfs",
            "uri": f"ipfs://{cid}",
            "memberPath": "payload/proof-1.olean",
            "metadata": {
                "cid": cid,
                "sha256": "b" * 64,
                "statusCode": 200,
            },
        },
    }


def test_build_artifact_resolution_receipt_binds_logical_and_transport_identity() -> None:
    receipt = build_artifact_resolution_receipt(resolved())

    assert receipt["schemaVersion"] == "artifact-resolution-receipt/v1"
    assert receipt["logicalContractVersion"] == "shared-shard-artifact/v1"
    assert receipt["logicalArtifactRef"] == "mabo-formal-proof@rev-1#proof-1"
    assert receipt["artifactId"] == "mabo-formal-proof"
    assert receipt["artifactRevision"] == "rev-1"
    assert receipt["shardId"] == "proof-1"
    assert receipt["contentDigest"] == f"sha256:{DIGEST}"
    assert receipt["payloadDigest"] == f"sha256:{DIGEST}"
    assert receipt["objectRef"]["sink"] == "ipfs"
    assert receipt["objectRef"]["uri"] == "ipfs://bafy-demo-erdfa-tar"
    assert receipt["transport"]["cid"] == "bafy-demo-erdfa-tar"
    assert receipt["verified"] is True
    assert receipt["authority"] == "transport-only"
    assert receipt["establishesProof"] is False


def test_artifact_resolution_receipt_rejects_payload_digest_mismatch() -> None:
    with pytest.raises(ValueError, match="payload digest"):
        build_artifact_resolution_receipt(resolved(payload_digest="c" * 64))


def test_artifact_resolution_receipt_rejects_ipfs_cid_mismatch() -> None:
    item = resolved()
    item["fetch"]["metadata"]["cid"] = "bafy-other"

    with pytest.raises(ValueError, match="IPFS CID"):
        build_artifact_resolution_receipt(item)
