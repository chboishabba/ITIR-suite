import json
import subprocess
import sys
from pathlib import Path


def test_emit_zelph_hf_v2_writes_manifest_and_shards(tmp_path: Path) -> None:
    bin_path = tmp_path / "demo.bin"
    bin_path.write_bytes(b"x" * 4096)

    index_path = tmp_path / "demo.index.json"
    index_path.write_text(
        json.dumps(
            {
                "file": str(bin_path),
                "header": {"offset": 0, "length": 128},
                "left": [
                    {"chunkIndex": 0, "offset": 128, "length": 100, "which": "left"},
                ],
                "right": [
                    {"chunkIndex": 0, "offset": 228, "length": 50, "which": "right"},
                ],
                "nameOfNode": [
                    {"chunkIndex": 0, "offset": 278, "length": 25, "lang": "en"},
                    {"chunkIndex": 0, "offset": 303, "length": 26, "lang": "wikidata"},
                ],
                "nodeOfName": [
                    {"chunkIndex": 0, "offset": 329, "length": 40, "lang": "en"},
                ],
            }
        ),
        encoding="utf-8",
    )

    output_path = tmp_path / "demo.hf-v2.json"
    shard_root = tmp_path / "demo-shards"
    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "tools" / "emit_zelph_hf_v2.py"

    subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--bin",
            str(bin_path),
            "--index",
            str(index_path),
            "--output",
            str(output_path),
            "--artifact-name",
            "demo-artifact",
            "--hf-root",
            "hf://datasets/example/zelph",
            "--shard-root",
            str(shard_root),
        ],
        check=True,
    )

    manifest = json.loads(output_path.read_text(encoding="utf-8"))

    assert manifest["manifestVersion"] == "zelph-hf-layout/v2"
    assert manifest["storageMode"] == "multi-object-shards"
    assert manifest["selectorModel"]["unit"] == "section-chunk"
    assert manifest["capabilities"]["selectedChunkRead"] is True
    assert manifest["capabilities"]["nodeRouteIndex"] is False
    assert manifest["hfObjects"]["left"]["pathPrefix"] == "hf://datasets/example/zelph/demo-artifact/shards/left"
    assert manifest["sections"]["nameOfNode"]["languages"] == ["en", "wikidata"]

    emitted_chunks = list(shard_root.glob("**/*.capnp-packed"))
    assert len(emitted_chunks) == 5
    assert any(path.name == "chunk-000000-en.capnp-packed" for path in emitted_chunks)
    assert any(path.name == "chunk-000000-wikidata.capnp-packed" for path in emitted_chunks)
