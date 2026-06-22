import json
import importlib.util
import subprocess
import sys
from pathlib import Path


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
    assert contract["nonAuthority"] == {
        "artifact_transport_only": True,
        "candidate_graph_logistics": True,
        "truth_authority": False,
        "support_authority": False,
        "admissibility_authority": False,
        "promotion_authority": False,
        "complete_closure_authority": False,
    }
    assert len(contract["shards"]) == 4

    left = next(shard for shard in contract["shards"] if shard["shardId"] == "left-bucket-000000")
    assert left["logicalKind"] == "adjacency-bucket"
    assert left["routingKeys"] == ["section:left", "route-left-node"]
    assert left["objectRefs"][0]["sink"] == "hf"
    assert left["objectRefs"][0]["contentDigest"] == left["contentDigest"]
    assert left["objectRefs"][1]["sink"] == "ipfs"
    assert left["objectRefs"][1]["uri"] == "ipfs://bafy-left"
    assert left["objectRefs"][1]["contentDigest"] == left["contentDigest"]
    assert left["contentDigest"].startswith("sha256:")

    node_of_name = next(shard for shard in contract["shards"] if shard["section"] == "nodeOfName")
    assert node_of_name["logicalKind"] == "name-bucket"
    assert "route-name" in node_of_name["routingKeys"]
    assert "lang:en" in node_of_name["routingKeys"]
    assert node_of_name["objectRefs"][0]["contentDigest"] == node_of_name["contentDigest"]
    assert contract["routingIndex"]["objectRefs"][0]["sink"] == "hf"
    assert contract["routingIndex"]["objectRefs"][1]["sink"] == "ipfs"
    assert contract["routingIndex"]["objectRefs"][1]["uri"] == "ipfs://bafy-route"
    assert contract["routingIndex"]["objectRefs"][0]["contentDigest"].startswith("identity-sha256:")

    if importlib.util.find_spec("cbor2") is None:
        return
    import cbor2

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
    with output_cbor.open("rb") as handle:
        cbor_contract = cbor2.load(handle)
    assert json.loads(output_json.read_text(encoding="utf-8")) == cbor_contract


def test_build_shared_shard_artifact_contract_hf_v2_manifest_contract(tmp_path: Path) -> None:
    source_bin = tmp_path / "zelph-sharded.bin"
    source_bin.write_bytes((b"hf-v2-contract-fixture-" * 256)[:4096])

    index_path = tmp_path / "zelph-sharded.index.json"
    index_path.write_text(
        json.dumps(
            {
                "file": str(source_bin),
                "header": {"offset": 0, "length": 128},
                "left": [
                    {"chunkIndex": 0, "offset": 128, "length": 64, "which": "left"},
                ],
                "right": [
                    {"chunkIndex": 0, "offset": 192, "length": 64, "which": "right"},
                ],
                "nameOfNode": [
                    {"chunkIndex": 0, "offset": 256, "length": 64, "lang": "en"},
                ],
                "nodeOfName": [
                    {"chunkIndex": 0, "offset": 320, "length": 64, "lang": "en"},
                ],
            }
        ),
        encoding="utf-8",
    )

    manifest_path = tmp_path / "zelph-sharded.hf-v2.json"
    manifest_path.write_text(
        json.dumps(
            {
                "manifestVersion": "zelph-hf-layout/v2",
                "createdAtUtc": "2026-06-22T10:15:00Z",
                "storageMode": "multi-object-shards",
                "transport": {
                    "primary": "hf-object-fetch",
                    "fallback": "local-file",
                },
                "source": {
                    "binPath": str(source_bin),
                    "indexPath": str(index_path),
                    "binSizeBytes": source_bin.stat().st_size,
                    "headerLengthBytes": 128,
                    "totalChunkCount": 4,
                    "totalChunkBytes": 256,
                },
                "hfObjects": {
                    "manifest": {
                        "path": "hf://datasets/chbwa/zelph-sharded/manifest.json",
                    },
                    "left": {
                        "pathPrefix": "hf://datasets/chbwa/zelph-sharded/shards/left",
                        "count": 1,
                        "role": "section-shards",
                        "mediaType": "application/octet-stream",
                    },
                    "right": {
                        "pathPrefix": "hf://datasets/chbwa/zelph-sharded/shards/right",
                        "count": 1,
                        "role": "section-shards",
                        "mediaType": "application/octet-stream",
                    },
                    "nameOfNode": {
                        "pathPrefix": "hf://datasets/chbwa/zelph-sharded/shards/nameOfNode",
                        "count": 1,
                        "role": "section-shards",
                        "mediaType": "application/octet-stream",
                    },
                    "nodeOfName": {
                        "pathPrefix": "hf://datasets/chbwa/zelph-sharded/shards/nodeOfName",
                        "count": 1,
                        "role": "section-shards",
                        "mediaType": "application/octet-stream",
                    },
                    "nodeRouteIndex": {
                        "path": "hf://datasets/chbwa/zelph-sharded/artifact.route.json",
                        "role": "node-route-sidecar",
                        "mediaType": "application/json",
                        "sizeBytes": 321,
                    },
                },
                "selectorModel": {
                    "unit": "bucket",
                    "supportedSections": ["left", "right", "nameOfNode", "nodeOfName"],
                    "supportedOperations": [
                        "headerProbe",
                        "selectedChunkRead",
                        "nodeRouteIndex",
                    ],
                    "unsupportedOperations": [],
                },
                "layoutPlan": {
                    "isCanonical": True,
                    "supportsNodeRouteIndex": True,
                    "nodeRoutingIndex": {
                        "path": "hf://datasets/chbwa/zelph-sharded/artifact.route.json",
                        "format": "zelph-node-route/v1",
                    },
                },
                "capabilities": {
                    "headerProbe": True,
                    "selectedChunkRead": True,
                    "nodeRouteIndex": True,
                    "smallNeighborhoodExpansion": False,
                    "fullReasoningSafe": False,
                },
                "sections": {
                    "left": {
                        "chunks": [
                            {
                                "chunkIndex": 0,
                                "length": 64,
                                "sourceOffset": 128,
                                "objectPath": "hf://datasets/chbwa/zelph-sharded/shards/left/chunk-000000.capnp-packed",
                            }
                        ]
                    },
                    "right": {
                        "chunks": [
                            {
                                "chunkIndex": 0,
                                "length": 64,
                                "sourceOffset": 192,
                                "objectPath": "hf://datasets/chbwa/zelph-sharded/shards/right/chunk-000000.capnp-packed",
                            }
                        ]
                    },
                    "nameOfNode": {
                        "chunks": [
                            {
                                "chunkIndex": 0,
                                "length": 64,
                                "sourceOffset": 256,
                                "lang": "en",
                                "objectPath": "hf://datasets/chbwa/zelph-sharded/shards/nameOfNode/chunk-000000-en.capnp-packed",
                            }
                        ]
                    },
                    "nodeOfName": {
                        "chunks": [
                            {
                                "chunkIndex": 0,
                                "length": 64,
                                "sourceOffset": 320,
                                "lang": "en",
                                "objectPath": "hf://datasets/chbwa/zelph-sharded/shards/nodeOfName/chunk-000000-en.capnp-packed",
                            }
                        ]
                    },
                },
            }
        ),
        encoding="utf-8",
    )

    output_json = tmp_path / "shared.contract.json"
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
            "--artifact-id",
            "zelph-sharded-demo",
        ],
        check=True,
    )

    contract = json.loads(output_json.read_text(encoding="utf-8"))
    assert contract["contractVersion"] == "shared-shard-artifact/v1"
    assert contract["artifactId"] == "zelph-sharded-demo"
    assert contract["selectorModel"]["supportedOperations"] == [
        "headerProbe",
        "selectedChunkRead",
        "nodeRouteIndex",
    ]
    assert contract["nonAuthority"] == {
        "artifact_transport_only": True,
        "candidate_graph_logistics": True,
        "truth_authority": False,
        "support_authority": False,
        "admissibility_authority": False,
        "promotion_authority": False,
        "complete_closure_authority": False,
    }
    assert contract["nonAuthority"]["promotion_authority"] is False

    assert contract["routingIndex"]["logicalKind"] == "routing-index"
    assert contract["routingIndex"]["format"] == "zelph-node-route/v1"
    assert contract["routingIndex"]["objectRefs"] == [
        {
            "sink": "hf",
            "uri": "hf://datasets/chbwa/zelph-sharded/artifact.route.json",
            "sizeBytes": 321,
            "contentDigest": contract["routingIndex"]["objectRefs"][0]["contentDigest"],
        }
    ]
    assert contract["routingIndex"]["objectRefs"][0]["contentDigest"].startswith("identity-sha256:")

    shard_uris = {
        "left": "hf://datasets/chbwa/zelph-sharded/shards/left/chunk-000000.capnp-packed",
        "right": "hf://datasets/chbwa/zelph-sharded/shards/right/chunk-000000.capnp-packed",
        "nameOfNode": "hf://datasets/chbwa/zelph-sharded/shards/nameOfNode/chunk-000000-en.capnp-packed",
        "nodeOfName": "hf://datasets/chbwa/zelph-sharded/shards/nodeOfName/chunk-000000-en.capnp-packed",
    }
    assert {shard["section"] for shard in contract["shards"]} == set(shard_uris)
    for shard in contract["shards"]:
        assert shard["objectRefs"] == [
            {
                "sink": "hf",
                "uri": shard_uris[shard["section"]],
                "sizeBytes": shard["sizeBytes"],
                "contentDigest": shard["contentDigest"],
            }
        ]
        assert shard["objectRefs"][0]["contentDigest"].startswith("sha256:")
        assert shard["objectRefs"][0]["uri"].startswith("hf://datasets/chbwa/zelph-sharded/")
