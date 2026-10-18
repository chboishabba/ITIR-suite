from __future__ import annotations

import json
from pathlib import Path

from itir_jmd_bridge.artifact_receipt import main


DIGEST = "a" * 64


def test_artifact_resolution_receipt_cli_emits_verified_transport_receipt(tmp_path: Path) -> None:
    resolved_path = tmp_path / "resolved.json"
    output_path = tmp_path / "receipt.json"
    resolved_path.write_text(
        json.dumps(
            {
                "artifactId": "mabo-formal-proof",
                "artifactRevision": "rev-1",
                "matchedBy": "direct-shard",
                "selectors": ["direct-shard=proof-1"],
                "shard": {"id": "proof-1", "contentDigest": f"sha256:{DIGEST}"},
                "selectedObjectRef": {
                    "sink": "ipfs",
                    "uri": "ipfs://bafy-demo-erdfa-tar",
                    "memberPath": "payload/proof-1.olean",
                    "sizeBytes": 12,
                    "contentDigest": f"sha256:{DIGEST}",
                },
                "payload": {"sizeBytes": 12, "sha256": DIGEST},
                "fetch": {
                    "sink": "ipfs",
                    "uri": "ipfs://bafy-demo-erdfa-tar",
                    "memberPath": "payload/proof-1.olean",
                    "metadata": {"cid": "bafy-demo-erdfa-tar", "statusCode": 200},
                },
            }
        ),
        encoding="utf-8",
    )

    code = main(["--resolved-json", str(resolved_path), "--output", str(output_path)])

    assert code == 0
    receipt = json.loads(output_path.read_text(encoding="utf-8"))
    assert receipt["logicalArtifactRef"] == "mabo-formal-proof@rev-1#proof-1"
    assert receipt["transport"]["cid"] == "bafy-demo-erdfa-tar"
    assert receipt["verified"] is True
    assert receipt["establishesProof"] is False
