from __future__ import annotations

import json
from pathlib import Path

from itir_jmd_bridge.__main__ import main


DIGEST = "a" * 64


def test_package_cli_dispatches_artifact_resolution_receipt(tmp_path: Path) -> None:
    resolved = tmp_path / "resolved.json"
    output = tmp_path / "receipt.json"
    resolved.write_text(
        json.dumps(
            {
                "artifactId": "mabo",
                "artifactRevision": "rev",
                "shard": {"id": "proof", "contentDigest": f"sha256:{DIGEST}"},
                "selectedObjectRef": {
                    "sink": "ipfs",
                    "uri": "ipfs://bafy-demo",
                    "sizeBytes": 1,
                    "contentDigest": f"sha256:{DIGEST}",
                },
                "payload": {"sizeBytes": 1, "sha256": DIGEST},
                "fetch": {
                    "sink": "ipfs",
                    "uri": "ipfs://bafy-demo",
                    "metadata": {"cid": "bafy-demo"},
                },
            }
        ),
        encoding="utf-8",
    )

    code = main(
        [
            "emit-artifact-resolution-receipt",
            "--resolved-json", str(resolved),
            "--output", str(output),
        ]
    )

    assert code == 0
    receipt = json.loads(output.read_text(encoding="utf-8"))
    assert receipt["logicalArtifactRef"] == "mabo@rev#proof"
    assert receipt["authority"] == "transport-only"
