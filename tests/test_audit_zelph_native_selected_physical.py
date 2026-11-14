"""No-Capnp synthetic controls for the physically anchored four-section native decoder runner."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
import audit_zelph_native_selected_physical as audit  # noqa: E402

REV = "a" * 40
ART = "wikidata-20260309-all"


def _write(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, sort_keys=True))


def _case(tmp_path: Path):
    root = tmp_path / "hf"
    manifest, route = {}, {}
    sections = {}
    byte_receipts = []
    all_bytes = b"header"
    for section in ("left", "right", "nameOfNode", "nodeOfName"):
        name = "chunk-000000.capnp-packed" if section in ("left", "right") else "chunk-000000-wikidata.capnp-packed"
        relative = f"{ART}/shards/{section}/{name}"
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        content = section.encode() + b":one-QID"
        path.write_bytes(content)
        part = {
            "chunkIndex": 0, "offset": len(all_bytes), "length": len(content),
            "objectPath": f"hf://datasets/acrion/zelph/{relative}"
        }
        if section in ("left", "right"):
            part["which"] = section
        else:
            part["lang"] = "wikidata"
        sections[section] = {"chunks": [part]}
        byte_receipts.append({
            "section": section, "chunk_index": 0,
            "sha256": sha256(content).hexdigest(),
            "bytes_compared": len(content),
            "object_uri": part["objectPath"],
        })
        all_bytes += content
    manifest = {
        "manifestVersion": 2, "storageMode": "split-by-direction-and-section",
        "source": {"artifactName": ART}, "sections": sections,
    }
    route = {
        "routeVersion": "zelph-filtered-route/v1",
        "requestedQids": ["Q1"],
        "qidToZelphNodeIds": {"Q1": 7},
        "qidToNodeOfNameChunks": {"Q1": 0},
        "nodeRoutes": {"7": {"left": [0], "right": [0], "nameOfNode": [0]}},
        "nodeAdjacency": {
            "7": {"left": [8, 9], "right": [10],
                  "leftValuesSeen": 2, "rightValuesSeen": 1,
                  "leftTruncated": False, "rightTruncated": False}
        },
        "source": {
            "binSizeBytes": len(all_bytes),
            "leftChunkCount": 1, "rightChunkCount": 1,
            "nameOfNodeChunkCount": 1, "nodeOfNameChunkCount": 1,
        },
        "sourceBinToPublishedHfDatasetIdentityVerified": False,
        "adjacencyOracleScope": "bounded-selected-roots-in-source-bin",
    }
    paths = {s: tmp_path / (s + ".json") for s in ("manifest", "route", "receipt")}
    _write(paths["manifest"], manifest)
    _write(paths["route"], route)
    mdig = sha256(paths["manifest"].read_bytes()).hexdigest()
    rdig = sha256(paths["route"].read_bytes()).hexdigest()
    proof = {
        "version": "itir.zelph.exact_original_bin_selected_hf_ranges.v1",
        "all_selected_shards_equal_local_original_bin_packed_ranges": True,
        "manifest_sha256_verified": mdig,
        "route_sha256_verified": rdig,
        "graph_revision_claim": REV,
        "physical_receipts": byte_receipts,
    }
    _write(paths["receipt"], proof)
    decoder = tmp_path / "native-decoder"
    decoder.touch()
    return {
        **paths, "root": root, "decoder": decoder,
        "manifest_sha": mdig,
    }


def _mock_run(*, mismatch=None):
    def run(argv, **kwargs):
        section = argv[argv.index("--section") + 1]
        if section == "left":
            rows = [{"node_id": 7, "neighbors": [8, 9], "values_seen": 2, "truncated": False}]
        elif section == "right":
            rows = [{"node_id": 7, "neighbors": [10], "values_seen": 1, "truncated": False}]
        else:
            rows = [{"name": "Q1", "node_id": 7}]
        if mismatch == section:
            if section in ("left", "right"):
                rows[0]["neighbors"] = [222]
            else:
                rows[0]["name"] = "Q2"
        data = {
            "version": "itir.zelph.selected_native_capnp_decode.v1",
            "section": section, "chunk_index": 0,
            "candidate_only": True, "authority": False, "rows": rows,
        }
        if section in ("nodeOfName", "nameOfNode"):
            data["language"] = "wikidata"
        return SimpleNamespace(returncode=0, stdout=json.dumps(data), stderr="")
    return run


def _verify(case):
    return audit.verify_native_selected_shard_answer(
        manifest_path=case["manifest"], route_path=case["route"],
        range_receipt_path=case["receipt"], shard_root=case["root"],
        decoder_executable=case["decoder"],
        dataset_revision=REV, manifest_sha256=case["manifest_sha"],
    )


def test_same_original_range_and_native_four_section_projection(monkeypatch, tmp_path):
    case = _case(tmp_path)
    monkeypatch.setattr(audit.subprocess, "run", _mock_run())
    result = _verify(case)
    assert result["native_schema_decoder_executed"]
    assert result["selected_name_routes_and_inverse_checked"]
    assert result["selected_root_one_hop_bidirectional_adjacency_equal_original_bin"]
    assert result["selected_object_count"] == 4
    assert result["general_query_family_closed"] is False
    assert result["native_P14143_P854_support_proved"] is False
    assert result["edit_authority"] is False


@pytest.mark.parametrize("bad_section", ["left", "right", "nodeOfName", "nameOfNode"])
def test_decoder_mismatch_fails_closed(monkeypatch, tmp_path, bad_section):
    case = _case(tmp_path)
    monkeypatch.setattr(audit.subprocess, "run", _mock_run(mismatch=bad_section))
    with pytest.raises(ValueError):
        _verify(case)


def test_same_length_post_proof_shard_tamper_fails_before_native_decode(monkeypatch, tmp_path):
    case = _case(tmp_path)
    monkeypatch.setattr(audit.subprocess, "run", _mock_run())
    shard = case["root"] / ART / "shards" / "left" / "chunk-000000.capnp-packed"
    original = shard.read_bytes()
    shard.write_bytes(b"Z" + original[1:])
    with pytest.raises(ValueError, match="physical bytes no longer match"):
        _verify(case)


def test_forged_range_receipt_sha_binding_fails(monkeypatch, tmp_path):
    case = _case(tmp_path)
    monkeypatch.setattr(audit.subprocess, "run", _mock_run())
    data = json.loads(case["receipt"].read_text())
    data["route_sha256_verified"] = "0" * 64
    _write(case["receipt"], data)
    with pytest.raises(ValueError, match="identity invalid"):
        _verify(case)


def test_missing_old_source_oracle_or_missing_root_rejected(monkeypatch, tmp_path):
    case = _case(tmp_path)
    monkeypatch.setattr(audit.subprocess, "run", _mock_run())
    route = json.loads(case["route"].read_text())
    route["nodeAdjacency"] = {}
    _write(case["route"], route)
    # Must fail before any attempted semantic promotion, independently
    # of the stale range receipt digest.
    with pytest.raises(ValueError):
        _verify(case)
