import json
import subprocess
import sys
from pathlib import Path


def test_build_zelph_hf_manifest(tmp_path: Path) -> None:
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
                    {"chunkIndex": 1, "offset": 228, "length": 100, "which": "left"},
                ],
                "right": [
                    {"chunkIndex": 0, "offset": 328, "length": 50, "which": "right"}
                ],
                "nameOfNode": [
                    {"chunkIndex": 0, "offset": 378, "length": 25, "lang": "en"},
                    {"chunkIndex": 1, "offset": 403, "length": 30, "lang": "wikidata"},
                ],
                "nodeOfName": [
                    {"chunkIndex": 0, "offset": 433, "length": 40, "lang": "en"}
                ],
            }
        ),
        encoding="utf-8",
    )

    output_path = tmp_path / "manifest.json"
    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "tools" / "build_zelph_hf_manifest.py"

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
            "--hf-root",
            "hf://datasets/example/zelph",
            "--artifact-name",
            "demo-artifact",
        ],
        check=True,
    )

    manifest = json.loads(output_path.read_text(encoding="utf-8"))

    assert manifest["manifestVersion"] == "zelph-hf-layout/v1"
    assert manifest["storageMode"] == "single-file-offset-sidecar"
    assert manifest["selectorModel"]["unit"] == "section-chunk"
    assert manifest["capabilities"]["selectedChunkRead"] is True
    assert manifest["capabilities"]["nodeRouteIndex"] is False
    assert manifest["hfObjects"]["bin"]["path"] == "hf://datasets/example/zelph/demo-artifact/artifact.bin"
    assert manifest["sections"]["left"]["chunkCount"] == 2
    assert manifest["sections"]["left"]["totalBytes"] == 200
    assert manifest["sections"]["left"]["chunks"][0]["range"] == "bytes=128-227"
    assert manifest["sections"]["nameOfNode"]["languages"] == ["en", "wikidata"]
    assert manifest["futureLayoutPlan"]["layoutVersion"] == "planned-multi-object/v0"
    assert manifest["futureLayoutPlan"]["objectPrefix"] == "hf://datasets/example/zelph/demo-artifact/chunks"


def test_build_zelph_hf_manifest_v2_with_shard_emit(tmp_path: Path) -> None:
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
                ],
                "nodeOfName": [
                    {"chunkIndex": 0, "offset": 303, "length": 40, "lang": "en"},
                ],
            }
        ),
        encoding="utf-8",
    )

    output_path = tmp_path / "manifest_v2.json"
    shard_root = tmp_path / "artifacts-shards"
    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "tools" / "build_zelph_hf_manifest.py"

    subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--layout",
            "v2",
            "--bin",
            str(bin_path),
            "--index",
            str(index_path),
            "--output",
            str(output_path),
            "--hf-root",
            "hf://datasets/example/zelph",
            "--artifact-name",
            "demo-artifact",
            "--emit-shards",
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
    assert manifest["sections"]["left"]["chunkCount"] == 1
    assert manifest["sections"]["left"]["chunks"][0]["sourceOffset"] == 128
    assert manifest["sections"]["left"]["chunks"][0]["sourceRange"] == "bytes=128-227"
    assert manifest["sections"]["nameOfNode"]["chunks"][0]["lang"] == "en"

    emitted_chunks = list(shard_root.glob("**/*.capnp-packed"))
    assert len(emitted_chunks) == 4
    assert any(path.name == "chunk-000000-en.capnp-packed" for path in emitted_chunks)


def test_build_zelph_hf_manifest_v2_with_lang_suffix_avoids_object_collisions(tmp_path: Path) -> None:
    bin_path = tmp_path / "demo.bin"
    bin_path.write_bytes(b"x" * 4096)

    index_path = tmp_path / "demo.index.json"
    index_path.write_text(
        json.dumps(
            {
                "file": str(bin_path),
                "header": {"offset": 0, "length": 128},
                "left": [],
                "right": [],
                "nameOfNode": [
                    {"chunkIndex": 0, "offset": 128, "length": 25, "lang": "en"},
                    {"chunkIndex": 0, "offset": 153, "length": 26, "lang": "wikidata"},
                    {"chunkIndex": 1, "offset": 179, "length": 30, "lang": "en"},
                ],
                "nodeOfName": [
                    {"chunkIndex": 0, "offset": 209, "length": 25, "lang": "en"},
                    {"chunkIndex": 0, "offset": 234, "length": 25, "lang": "wikidata"},
                ],
            }
        ),
        encoding="utf-8",
    )

    output_path = tmp_path / "manifest_v2.json"
    shard_root = tmp_path / "artifacts-shards"
    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "tools" / "build_zelph_hf_manifest.py"

    subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--layout",
            "v2",
            "--bin",
            str(bin_path),
            "--index",
            str(index_path),
            "--output",
            str(output_path),
            "--artifact-name",
            "demo-artifact",
            "--emit-shards",
            "--shard-root",
            str(shard_root),
        ],
        check=True,
    )

    manifest = json.loads(output_path.read_text(encoding="utf-8"))
    left = {chunk["objectPath"] for chunk in manifest["sections"]["nameOfNode"]["chunks"]}
    assert len(left) == 3
    assert len(left) == len(manifest["sections"]["nameOfNode"]["chunks"])
    assert "chunk-000000-en.capnp-packed" in manifest["sections"]["nameOfNode"]["chunks"][0]["objectPath"]
    assert "chunk-000000-wikidata.capnp-packed" in manifest["sections"]["nameOfNode"]["chunks"][1]["objectPath"]

    emitted_chunks = list(shard_root.glob("**/*.capnp-packed"))
    assert len(emitted_chunks) == 5
    assert any(path.name == "chunk-000000-en.capnp-packed" for path in emitted_chunks)
    assert any(path.name == "chunk-000000-wikidata.capnp-packed" for path in emitted_chunks)
