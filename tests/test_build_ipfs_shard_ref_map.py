import json
import subprocess
import sys
from pathlib import Path


def test_build_ipfs_shard_ref_map(tmp_path: Path) -> None:
    shard_root = tmp_path / "shards"
    left_dir = shard_root / "left"
    left_dir.mkdir(parents=True)
    left_path = left_dir / "chunk-000000.capnp-packed"
    left_path.write_bytes(b"example-left-shard")
    route_path = tmp_path / "artifact.route.json"
    route_path.write_bytes(b"{\"route\":true}")

    contract_path = tmp_path / "shared.contract.json"
    contract_path.write_text(
        json.dumps(
            {
                "contractVersion": "shared-shard-artifact/v1",
                "shards": [
                    {
                        "shardId": "left-bucket-000000",
                        "section": "left",
                        "objectRefs": [
                            {
                                "sink": "hf",
                                "uri": "hf://datasets/example/zelph/demo/shards/left/chunk-000000.capnp-packed",
                            }
                        ],
                    }
                ],
                "routingIndex": {
                    "objectRefs": [
                        {
                            "sink": "hf",
                            "uri": "hf://datasets/example/zelph/demo/artifact.route.json",
                        }
                    ]
                },
            }
        ),
        encoding="utf-8",
    )

    output_path = tmp_path / "ipfs-map.json"
    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "tools" / "build_ipfs_shard_ref_map.py"

    subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--shared-contract",
            str(contract_path),
            "--shard-root",
            str(shard_root),
            "--routing-index-local-path",
            str(route_path),
            "--output",
            str(output_path),
        ],
        check=True,
    )

    mapping = json.loads(output_path.read_text(encoding="utf-8"))
    entry = mapping["left-bucket-000000"]
    assert entry["uri"].startswith("ipfs://b")
    assert entry["sizeBytes"] == len(b"example-left-shard")
    assert entry["contentDigest"].startswith("sha256:")
    assert entry["localPath"] == str(left_path)

    route_entry = mapping["routingIndex"]
    assert route_entry["uri"].startswith("ipfs://b")
    assert route_entry["sizeBytes"] == len(b"{\"route\":true}")
    assert route_entry["localPath"] == str(route_path)
    assert (
        mapping["hf://datasets/example/zelph/demo/artifact.route.json"]["uri"]
        == route_entry["uri"]
    )
