"""The selected HF transfer plan must be pinned, bounded and exact."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import sys

import pytest

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
import plan_zelph_hf_selected_fetch as planner  # noqa: E402

REV = "a" * 40
ART = "wikidata-20260309-all"


def _inputs(tmp: Path):
    manifest = {"manifestVersion": 2, "storageMode": "split-by-direction-and-section",
                "source": {"artifactName": ART}, "sections": {}}
    names = ("left", "right", "nameOfNode", "nodeOfName")
    for i, sec in enumerate(names):
        filename = (
            "chunk-000000.capnp-packed" if sec in ("left", "right")
            else "chunk-000000-wikidata.capnp-packed"
        )
        part = {
            "chunkIndex": 0, "offset": i * 8, "length": 8,
            "objectPath": f"hf://datasets/acrion/zelph/{ART}/shards/{sec}/{filename}",
        }
        if sec in ("left", "right"):
            part["which"] = sec
        else:
            part["lang"] = "wikidata"
        manifest["sections"][sec] = {"chunks": [part]}
    route = {
        "routeVersion": "zelph-filtered-route/v1",
        "requestedQids": ["Q1"],
        "qidToZelphNodeIds": {"Q1": 7},
        "qidToNodeOfNameChunks": {"Q1": 0},
        "nodeRoutes": {"7": {"left": [0], "right": [0], "nameOfNode": [0]}},
        "source": {
            "leftChunkCount": 1, "rightChunkCount": 1,
            "nameOfNodeChunkCount": 1, "nodeOfNameChunkCount": 1,
        },
    }
    m, r = tmp / "manifest.json", tmp / "route.json"
    m.write_text(json.dumps(manifest, sort_keys=True))
    r.write_text(json.dumps(route, sort_keys=True))
    return m, r, sha256(m.read_bytes()).hexdigest()


def _plan(tmp):
    m, r, digest = _inputs(tmp)
    return planner.selected_fetch_plan(
        manifest_path=m, route_path=r, dataset_revision=REV,
        manifest_sha256=digest, shard_root=tmp / "hf",
    )


def test_download_is_only_a_plan_by_default_and_selects_four_chunks(tmp_path):
    result = _plan(tmp_path)
    assert result["download_client_invoked"] is False
    assert result["network_transfer_confirmed"] is False
    assert result["selected_object_count"] == 4
    assert result["advertised_selected_bytes"] == 32
    assert result["original_bin_requested"] is False
    assert result["source_bin_to_shard_ranges_verified"] is False
    args = result["invocation"]
    assert args[:3] == ["hf", "download", "acrion/zelph"]
    assert args[3:7] == result["selected_shard_files"]
    assert args[args.index("--revision") + 1] == REV
    assert f"{ART}.bin" not in args


def test_wrong_manifest_digest_rejected(tmp_path):
    m, r, _ = _inputs(tmp_path)
    with pytest.raises(ValueError, match="raw manifest content hash"):
        planner.selected_fetch_plan(
            manifest_path=m, route_path=r,
            dataset_revision=REV, manifest_sha256="0" * 64,
            shard_root=tmp_path / "hf",
        )


def test_unpinned_revision_and_zero_budget_rejected(tmp_path):
    m, r, digest = _inputs(tmp_path)
    with pytest.raises(ValueError, match="pinned HF SHA"):
        planner.selected_fetch_plan(
            manifest_path=m, route_path=r, dataset_revision="main",
            manifest_sha256=digest, shard_root=tmp_path / "hf",
        )
    with pytest.raises(ValueError, match="max-selected-GiB limit"):
        planner.selected_fetch_plan(
            manifest_path=m, route_path=r,
            dataset_revision=REV, manifest_sha256=digest,
            shard_root=tmp_path / "hf", max_selected_gib=0,
        )


def test_extra_selected_adjacency_chunk_rejected(tmp_path):
    m, r, digest = _inputs(tmp_path)
    route = json.loads(r.read_text())
    route["nodeRoutes"]["7"]["left"] = [0, 99]
    r.write_text(json.dumps(route))
    with pytest.raises(ValueError, match="omitted from actual manifest"):
        planner.selected_fetch_plan(
            manifest_path=m, route_path=r, dataset_revision=REV,
            manifest_sha256=digest, shard_root=tmp_path / "hf",
        )


def test_connector_fetches_all_exact_selected_objects_and_retains_raw_sha(tmp_path):
    import io
    from plan_zelph_hf_selected_fetch import execute_selected_fetch
    m, r, digest = _inputs(tmp_path)
    root = tmp_path / "selected-hf"
    plan = planner.selected_fetch_plan(
        manifest_path=m, route_path=r, dataset_revision=REV,
        manifest_sha256=digest, shard_root=root,
    )
    called = []
    class Response(io.BytesIO):
        def __init__(self, raw):
            super().__init__(raw)
            self.status = 206
            self.headers = {
                "Content-Range": "bytes 0-7/8",
                "Content-Length": "8",
                "Content-Encoding": "identity",
            }
        def geturl(self):
            return "https://huggingface.co/original-pinned-data"
    def opener(req, timeout):
        assert req.get_header("Range") == "bytes=0-7"
        assert "/resolve/" + REV + "/" in req.full_url
        assert "wikidata-20260309-all.bin" not in req.full_url
        called.append(req.full_url)
        return Response(b"shard123")
    result = execute_selected_fetch(
        plan=plan, manifest_path=m, route_path=r, shard_root=root,
        opener=opener,
    )
    assert len(called) == 4
    assert result["network_transfer_confirmed"] is True
    assert result["download_client_invoked"] is False
    assert result["connector_transport_owner"] == "itir_mcp.shard_transport"
    assert result["source_bin_to_shard_ranges_verified"] is False
    for receipt in result["selected_object_receipts"]:
        assert receipt["size_bytes"] == 8
        assert receipt["raw_hf_object_sha256"] == sha256(b"shard123").hexdigest()
        assert (root / receipt["object_relative_path"]).read_bytes() == b"shard123"


def test_connector_refuses_http200_and_never_promotes_source_equality(tmp_path):
    import io
    from plan_zelph_hf_selected_fetch import execute_selected_fetch
    m, r, digest = _inputs(tmp_path)
    root = tmp_path / "selected"
    plan = planner.selected_fetch_plan(
        manifest_path=m, route_path=r, dataset_revision=REV,
        manifest_sha256=digest, shard_root=root,
    )
    class NotRange(io.BytesIO):
        def __init__(self):
            super().__init__(b"shard123")
            self.status = 200
            self.headers = {"Content-Length": "8"}
    with pytest.raises(ValueError, match="exact HTTP 206"):
        execute_selected_fetch(
            plan=plan, manifest_path=m, route_path=r, shard_root=root,
            opener=lambda *_a, **_kw: NotRange(),
        )
    assert not list(root.rglob("*.capnp-packed"))


def test_connector_rejects_pretend_selected_plan_without_network(tmp_path):
    from plan_zelph_hf_selected_fetch import execute_selected_fetch
    m, r, digest = _inputs(tmp_path)
    root = tmp_path / "selected"
    plan = planner.selected_fetch_plan(
        manifest_path=m, route_path=r, dataset_revision=REV,
        manifest_sha256=digest, shard_root=root,
    )
    plan["selected_shard_files"] = plan["selected_shard_files"][:1]
    def refuse(*_a, **_kw):
        raise AssertionError("never contact source for tampered route selection")
    with pytest.raises(ValueError, match="plan changed"):
        execute_selected_fetch(
            plan=plan, manifest_path=m, route_path=r, shard_root=root,
            opener=refuse,
        )


def test_connector_never_overwrites_existing_selected_shard(tmp_path):
    from plan_zelph_hf_selected_fetch import execute_selected_fetch
    m, r, digest = _inputs(tmp_path)
    root = tmp_path / "selected"
    plan = planner.selected_fetch_plan(
        manifest_path=m, route_path=r, dataset_revision=REV,
        manifest_sha256=digest, shard_root=root,
    )
    old = root / plan["selected_shard_files"][0]
    old.parent.mkdir(parents=True)
    old.write_bytes(b"old evidence")
    def refuse(*_a, **_kw):
        raise AssertionError("existing immutable file must block before fetching")
    with pytest.raises(ValueError, match="refuse overwrite"):
        execute_selected_fetch(
            plan=plan, manifest_path=m, route_path=r, shard_root=root,
            opener=refuse,
        )
    assert old.read_bytes() == b"old evidence"
