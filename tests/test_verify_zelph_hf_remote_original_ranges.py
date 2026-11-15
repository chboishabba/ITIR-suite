"""No-network tests for pinned original-HF source HTTP range comparison."""
from __future__ import annotations

from hashlib import sha256
import io
import json
from pathlib import Path
import sys

import pytest


TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
import verify_zelph_hf_remote_original_ranges as remote  # noqa: E402

ARTIFACT = "wikidata-20260309-all"
REV = "a" * 40


def _fixture(tmp_path: Path) -> dict:
    root = tmp_path / "hf"
    manifest_path = tmp_path / "manifest.json"
    route_path = tmp_path / "route.json"
    binary = b"HDR"
    sections = {}
    for section in ("left", "right", "nameOfNode", "nodeOfName"):
        payload = section.encode("ascii") + b":node-test"
        offset = len(binary)
        binary += payload
        suffix = (
            "chunk-000000.capnp-packed" if section in ("left", "right")
            else "chunk-000000-wikidata.capnp-packed"
        )
        relative = f"{ARTIFACT}/shards/{section}/{suffix}"
        out = root / relative
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(payload)
        chunk = {
            "chunkIndex": 0, "offset": offset,
            "length": len(payload),
            "objectPath": f"hf://datasets/acrion/zelph/{relative}",
        }
        if section in ("left", "right"):
            chunk["which"] = section
        else:
            chunk["lang"] = "wikidata"
        sections[section] = {"chunks": [chunk]}
    manifest = {
        "manifestVersion": 2,
        "storageMode": "split-by-direction-and-section",
        "source": {"artifactName": ARTIFACT, "binSizeBytes": len(binary)},
        "sections": sections,
    }
    route = {
        "routeVersion": "zelph-filtered-route/v1",
        "requestedQids": ["Q1"],
        "qidToZelphNodeIds": {"Q1": 7},
        "qidToNodeOfNameChunks": {"Q1": 0},
        "nodeRoutes": {"7": {"left": [0], "right": [0], "nameOfNode": [0]}},
        "source": {"binSizeBytes": len(binary), "leftChunkCount": 1, "rightChunkCount": 1,
                   "nameOfNodeChunkCount": 1, "nodeOfNameChunkCount": 1},
    }
    manifest_path.write_text(json.dumps(manifest, sort_keys=True))
    route_path.write_text(json.dumps(route, sort_keys=True))
    return {
        "root": root, "manifest": manifest_path,
        "route": route_path, "binary": binary,
        "manifest_sha": sha256(manifest_path.read_bytes()).hexdigest(),
    }


class RangeResponse(io.BytesIO):
    def __init__(self, data, status, content_range, content_length=None):
        super().__init__(data)
        self.status = status
        self.headers = {
            "Content-Range": content_range,
            "Content-Length": str(len(data) if content_length is None else content_length),
            "Content-Encoding": "identity",
        }


def _range_opener(original: bytes, *, status=206, alter=False, wrong_range=False):
    def open_request(request, timeout):
        # Python urllib normalizes request header keys.
        header = request.get_header("Range")
        assert header and header.startswith("bytes=")
        start, end = (int(x) for x in header.removeprefix("bytes=").split("-"))
        chunk = original[start:end + 1]
        if alter:
            chunk = b"?" + chunk[1:]
        label = f"bytes {start}-{end}/{len(original)}"
        if wrong_range:
            label = f"bytes {start + 1}-{end}/{len(original)}"
        return RangeResponse(chunk, status, label)
    return open_request


def _verify(paths, opener, budget=8):
    return remote.verify_pinned_remote_ranges(
        manifest_path=paths["manifest"],
        route_path=paths["route"],
        shard_root=paths["root"],
        dataset_revision=REV,
        manifest_sha256=paths["manifest_sha"],
        max_selected_gib=budget,
        opener=opener,
    )


def test_four_selected_immutable_remote_ranges_equal_local_shard_bytes(tmp_path):
    p = _fixture(tmp_path)
    result = _verify(p, _range_opener(p["binary"]))
    assert result["selected_raw_remote_bin_ranges_equal_local_shard_bytes"] is True
    assert result["selected_object_count"] == 4
    assert len(result["receipts"]) == 4
    assert all(row["exact_content_range_verified"] for row in result["receipts"])
    assert result["all_source_bin_bytes_checked"] is False
    assert result["source_graph_query_closed"] is False
    assert result["native_statement_or_P854_proved"] is False


def test_http_200_whole_file_fallback_is_rejected(tmp_path):
    p = _fixture(tmp_path)
    with pytest.raises(ValueError, match="exact HTTP 206"):
        _verify(p, _range_opener(p["binary"], status=200))


def test_wrong_remote_byte_range_is_rejected(tmp_path):
    p = _fixture(tmp_path)
    with pytest.raises(ValueError, match="Content-Range mismatch"):
        _verify(p, _range_opener(p["binary"], wrong_range=True))


def test_same_length_remote_source_mutation_is_rejected(tmp_path):
    p = _fixture(tmp_path)
    with pytest.raises(ValueError, match="range differs"):
        _verify(p, _range_opener(p["binary"], alter=True))


def test_unpinned_dataset_reference_is_rejected(tmp_path):
    p = _fixture(tmp_path)
    with pytest.raises(ValueError, match="immutable dataset revision"):
        remote.verify_pinned_remote_ranges(
            manifest_path=p["manifest"], route_path=p["route"],
            shard_root=p["root"], dataset_revision="main",
            manifest_sha256=p["manifest_sha"],
            opener=_range_opener(p["binary"]),
        )


def test_missing_shard_does_not_trigger_any_network_request(tmp_path):
    p = _fixture(tmp_path)
    shard = p["root"] / ARTIFACT / "shards" / "left" / "chunk-000000.capnp-packed"
    shard.unlink()
    with pytest.raises((ValueError, FileNotFoundError)):
        _verify(p, _range_opener(p["binary"]))


def test_explicit_resource_cap_fail_closed_before_network(tmp_path):
    p = _fixture(tmp_path)
    def no_network(*args, **kwargs):
        raise AssertionError("network must not start")
    with pytest.raises(ValueError, match="budget"):
        _verify(p, no_network, budget=0)
