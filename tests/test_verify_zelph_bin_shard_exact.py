"""Byte-range witness tests for the published Zelph HF-v2 section-global ABI."""
from __future__ import annotations

import importlib.util
from hashlib import sha256
import json
from pathlib import Path

import pytest


SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "verify_zelph_bin_shard_exact.py"
spec = importlib.util.spec_from_file_location("verify_zelph_bin_shard_exact", SCRIPT)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


DATASET_SHA = "a" * 40
ARTIFACT = "wikidata-20260309-all"


def _save(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, sort_keys=True), encoding="utf-8")


def _fixture(tmp_path: Path) -> dict:
    root = tmp_path / "hf"
    manifest_path = tmp_path / "manifest.json"
    route_path = tmp_path / "route.json"
    bin_path = tmp_path / "original.bin"
    chunks = {
        "left": b"left-raw-payload",
        "right": b"right-raw-payload",
        "nameOfNode": b"name-to-node-payload",
        "nodeOfName": b"node-to-name-payload",
    }
    original = b"header-payload"
    manifest_sections = {}
    for section, payload in chunks.items():
        off = len(original)
        original += payload
        suffix = "chunk-000000.capnp-packed" if section in ("left", "right") else "chunk-000000-wikidata.capnp-packed"
        rel = f"{ARTIFACT}/shards/{section}/{suffix}"
        uri = f"hf://datasets/acrion/zelph/{rel}"
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(payload)
        part = {
            "chunkIndex": 0,
            "offset": off,
            "length": len(payload),
            "objectPath": uri,
        }
        if section in ("left", "right"):
            part["which"] = section
        else:
            part["lang"] = "wikidata"
        manifest_sections[section] = {"chunks": [part]}
    bin_path.write_bytes(original)
    manifest = {
        "manifestVersion": 2,
        "storageMode": "split-by-direction-and-section",
        "source": {"artifactName": ARTIFACT, "binSizeBytes": len(original)},
        "sections": manifest_sections,
    }
    _save(manifest_path, manifest)
    route = {
        "routeVersion": "zelph-filtered-route/v1",
        "requestedQids": ["Q10403939"],
        "qidToZelphNodeIds": {"Q10403939": 12345},
        "qidToNodeOfNameChunks": {"Q10403939": 0},
        "nodeRoutes": {"12345": {"left": [0], "right": [0], "nameOfNode": [0]}},
        "source": {
            "binSizeBytes": len(original),
            "leftChunkCount": 1,
            "rightChunkCount": 1,
            "nameOfNodeChunkCount": 1,
            "nodeOfNameChunkCount": 1,
        },
    }
    _save(route_path, route)
    return {
        "root": root, "manifest": manifest_path, "route": route_path,
        "bin": bin_path, "manifest_sha": sha256(manifest_path.read_bytes()).hexdigest(),
    }


def _verify(paths: dict, *, manifest_sha: str | None = None, max_selected_gib: int = 16):
    return module.verify_selected_source_ranges(
        manifest_path=paths["manifest"],
        route_path=paths["route"],
        source_bin=paths["bin"],
        shard_root=paths["root"],
        dataset_revision=DATASET_SHA,
        manifest_sha256=manifest_sha or paths["manifest_sha"],
        max_selected_gib=max_selected_gib,
    )


def test_selected_4_sections_exactly_equal_original_bin_ranges(tmp_path):
    paths = _fixture(tmp_path)
    result = _verify(paths)
    assert result["all_selected_shards_equal_local_original_bin_packed_ranges"]
    assert result["selected_object_count"] == 4
    assert result["selected_bytes_compared"] == paths["bin"].stat().st_size - len(b"header-payload")
    assert len({(r["section"], r["chunk_index"]) for r in result["physical_receipts"]}) == 4
    assert result["entire_bin_sha256_verified"] is False
    assert result["original_bin_upstream_authenticity_proved"] is False
    assert result["full_query_family_closure_proved"] is False
    assert result["promotion_authority"] is False


def test_same_length_shard_tamper_is_rejected(tmp_path):
    paths = _fixture(tmp_path)
    shard = paths["root"] / ARTIFACT / "shards" / "left" / "chunk-000000.capnp-packed"
    shard.write_bytes(b"x" + shard.read_bytes()[1:])
    with pytest.raises(ValueError, match="bytes differ"):
        _verify(paths)


def test_same_length_original_bin_tamper_is_rejected(tmp_path):
    paths = _fixture(tmp_path)
    raw = paths["bin"].read_bytes()
    paths["bin"].write_bytes(raw[:-1] + b"!")
    with pytest.raises(ValueError, match="bytes differ"):
        _verify(paths)


def test_missing_shard_or_wrong_size_is_rejected(tmp_path):
    paths = _fixture(tmp_path)
    shard = paths["root"] / ARTIFACT / "shards" / "right" / "chunk-000000.capnp-packed"
    shard.unlink()
    with pytest.raises((ValueError, FileNotFoundError), match="physical shard missing|No such file"):
        _verify(paths)


def test_route_cannot_select_out_of_manifest_chunk_domain(tmp_path):
    paths = _fixture(tmp_path)
    route = json.loads(paths["route"].read_text())
    route["nodeRoutes"]["12345"]["right"] = [1]
    _save(paths["route"], route)
    with pytest.raises(ValueError, match="absent physical chunks"):
        _verify(paths)


def test_rehashed_manifest_with_forged_physical_offset_is_detected(tmp_path):
    paths = _fixture(tmp_path)
    manifest = json.loads(paths["manifest"].read_text())
    manifest["sections"]["left"]["chunks"][0]["offset"] += 1
    _save(paths["manifest"], manifest)
    with pytest.raises(ValueError, match="bytes differ"):
        _verify(paths, manifest_sha=sha256(paths["manifest"].read_bytes()).hexdigest())


def test_manifest_digest_fails_before_interpretation(tmp_path):
    paths = _fixture(tmp_path)
    manifest = json.loads(paths["manifest"].read_text())
    manifest["source"]["artifactName"] = "forged-graph"
    _save(paths["manifest"], manifest)
    with pytest.raises(ValueError, match="manifest SHA256 mismatch"):
        _verify(paths)


def test_manifest_same_digest_claim_but_different_object_path_fails(tmp_path):
    paths = _fixture(tmp_path)
    manifest = json.loads(paths["manifest"].read_text())
    manifest["sections"]["nodeOfName"]["chunks"][0]["objectPath"] += ".other"
    _save(paths["manifest"], manifest)
    with pytest.raises(ValueError, match="not exact immutable artifact path"):
        _verify(paths, manifest_sha=sha256(paths["manifest"].read_bytes()).hexdigest())


def test_original_bin_route_size_mismatch_fails(tmp_path):
    paths = _fixture(tmp_path)
    route = json.loads(paths["route"].read_text())
    route["source"]["binSizeBytes"] -= 1
    _save(paths["route"], route)
    with pytest.raises(ValueError, match="original .bin size differs from route"):
        _verify(paths)


def test_declared_chunk_indices_must_be_dense_and_section_global(tmp_path):
    paths = _fixture(tmp_path)
    manifest = json.loads(paths["manifest"].read_text())
    manifest["sections"]["nodeOfName"]["chunks"][0]["chunkIndex"] = 7
    manifest["sections"]["nodeOfName"]["chunks"][0]["objectPath"] = (
        f"hf://datasets/acrion/zelph/{ARTIFACT}/shards/nodeOfName/"
        "chunk-000007-wikidata.capnp-packed"
    )
    _save(paths["manifest"], manifest)
    with pytest.raises(ValueError, match="0..N-1"):
        _verify(paths, manifest_sha=sha256(paths["manifest"].read_bytes()).hexdigest())


def test_zero_budget_cannot_bypass_explicit_resource_guard(tmp_path):
    paths = _fixture(tmp_path)
    with pytest.raises(ValueError, match="budget"):
        _verify(paths, max_selected_gib=0)


def test_manifest_duplicate_json_keys_are_rejected(tmp_path):
    paths = _fixture(tmp_path)
    paths["manifest"].write_text('{"manifestVersion": 2, "manifestVersion": 2}')
    with pytest.raises(ValueError, match="duplicate JSON key"):
        _verify(paths, manifest_sha=sha256(paths["manifest"].read_bytes()).hexdigest())


def test_ambiguous_or_missing_original_node_route_is_rejected(tmp_path):
    paths = _fixture(tmp_path)
    route = json.loads(paths["route"].read_text())
    route["qidToZelphNodeIds"]["Q10403939"] = None
    _save(paths["route"], route)
    with pytest.raises(ValueError, match="unresolved QID"):
        _verify(paths)


def test_extra_unnamed_numeric_frontier_is_valid_route_domain(tmp_path):
    paths = _fixture(tmp_path)
    route = json.loads(paths["route"].read_text())
    route["additionalNumericNodes"] = [999]
    route["nodeRoutes"]["999"] = {
        "left": [0], "right": [0], "nameOfNode": [],
    }
    _save(paths["route"], route)
    output = _verify(paths)
    assert output["all_selected_shards_equal_local_original_bin_packed_ranges"] is True
    # This verifies physical chunk selection only, not a fabricated QID/name
    # or existence of row 999; the native decoder checks that separately.


@pytest.mark.parametrize("bad", [[8, 8], [9, 8], [-1], ["8"], [True], [2**64]])
def test_extra_numeric_frontier_must_be_sorted_distinct_uint64(tmp_path, bad):
    paths = _fixture(tmp_path)
    route = json.loads(paths["route"].read_text())
    route["additionalNumericNodes"] = bad
    _save(paths["route"], route)
    with pytest.raises(ValueError, match="extra numeric frontier"):
        _verify(paths)


def test_extra_numeric_route_cannot_omit_its_original_source_node(tmp_path):
    paths = _fixture(tmp_path)
    route = json.loads(paths["route"].read_text())
    route["additionalNumericNodes"] = [999]
    _save(paths["route"], route)
    with pytest.raises(ValueError, match="node route domain"):
        _verify(paths)
