import json
import subprocess
import sys
from pathlib import Path

import cbor2


def test_build_shared_shard_artifact_contract_dual_projection(tmp_path: Path) -> None:
    bin_path = tmp_path / "demo.bin"
    bin_path.write_bytes(b"abcdefgh" * 512)

    manifest_path = tmp_path / "zelph.manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "manifestVersion": "zelph-hf-layout/v3",
                "createdAtUtc": "2026-03-27T12:00:00Z",
                "source": {
                    "binPath": str(bin_path),
                    "indexPath": str(tmp_path / "demo.index.json"),
                },
                "selectorModel": {
                    "unit": "bucket",
                    "supportedOperations": ["header-probe", "selected-chunk-read", "node-route"],
                    "supportedSections": ["left", "right", "nameOfNode", "nodeOfName"],
                },
                "hfObjects": {
                    "manifest": {"path": "hf://datasets/example/zelph/demo-artifact/manifest.json"},
                    "nodeRouteIndex": {
                        "path": "hf://datasets/example/zelph/demo-artifact/artifact.route.json",
                        "sizeBytes": 123,
                    },
                },
                "sections": {
                    "left": {
                        "chunks": [
                            {
                                "chunkIndex": 0,
                                "length": 16,
                                "sourceOffset": 0,
                                "objectPath": "hf://datasets/example/zelph/demo-artifact/shards/left/chunk-000000.capnp-packed",
                            }
                        ]
                    },
                    "right": {
                        "chunks": [
                            {
                                "chunkIndex": 0,
                                "length": 16,
                                "sourceOffset": 16,
                                "objectPath": "hf://datasets/example/zelph/demo-artifact/shards/right/chunk-000000.capnp-packed",
                            }
                        ]
                    },
                    "nameOfNode": {
                        "chunks": [
                            {
                                "chunkIndex": 0,
                                "length": 16,
                                "sourceOffset": 32,
                                "lang": "en",
                                "objectPath": "hf://datasets/example/zelph/demo-artifact/shards/nameOfNode/chunk-000000-en.capnp-packed",
                            }
                        ]
                    },
                    "nodeOfName": {
                        "chunks": [
                            {
                                "chunkIndex": 0,
                                "length": 16,
                                "sourceOffset": 48,
                                "lang": "en",
                                "objectPath": "hf://datasets/example/zelph/demo-artifact/shards/nodeOfName/chunk-000000-en.capnp-packed",
                            }
                        ]
                    },
                },
            }
        ),
        encoding="utf-8",
    )

    ipfs_map = tmp_path / "ipfs-map.json"
    ipfs_map.write_text(
        json.dumps(
            {
                "left-bucket-000000": {"uri": "ipfs://bafy-left"},
                "right-bucket-000000": {"uri": "ipfs://bafy-right"},
                "routingIndex": {"uri": "ipfs://bafy-route"},
            }
        ),
        encoding="utf-8",
    )

    output_json = tmp_path / "shared.contract.json"
    output_cbor = tmp_path / "shared.contract.cbor"
    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "tools" / "build_shared_shard_artifact_contract.py"

    subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--manifest",
            str(manifest_path),
            "--output-json",
            str(output_json),
            "--output-cbor",
            str(output_cbor),
            "--artifact-id",
            "demo-shared-artifact",
            "--ipfs-map",
            str(ipfs_map),
        ],
        check=True,
    )

    contract = json.loads(output_json.read_text(encoding="utf-8"))
    assert contract["contractVersion"] == "shared-shard-artifact/v1"
    assert contract["artifactId"] == "demo-shared-artifact"
    assert contract["selectorModel"]["unit"] == "bucket"
    assert contract["transportHints"]["preferredReadSink"] == "hf"
    assert contract["transportHints"]["preferredPublishSink"] == "ipfs"
    assert len(contract["shards"]) == 4

    left = next(shard for shard in contract["shards"] if shard["shardId"] == "left-bucket-000000")
    assert left["logicalKind"] == "adjacency-bucket"
    assert left["objectRefs"][0]["sink"] == "hf"
    assert left["objectRefs"][1]["sink"] == "ipfs"
    assert left["objectRefs"][1]["uri"] == "ipfs://bafy-left"
    assert left["contentDigest"].startswith("sha256:")

    node_of_name = next(shard for shard in contract["shards"] if shard["section"] == "nodeOfName")
    assert "route-name" in node_of_name["routingKeys"]
    assert "lang:en" in node_of_name["routingKeys"]
    assert contract["routingIndex"]["objectRefs"][0]["sink"] == "hf"
    assert contract["routingIndex"]["objectRefs"][1]["sink"] == "ipfs"
    assert contract["routingIndex"]["objectRefs"][1]["uri"] == "ipfs://bafy-route"

    with output_cbor.open("rb") as handle:
        cbor_contract = cbor2.load(handle)
    assert cbor_contract["artifactId"] == contract["artifactId"]
    assert [shard["shardId"] for shard in cbor_contract["shards"]] == [
        shard["shardId"] for shard in contract["shards"]
    ]
