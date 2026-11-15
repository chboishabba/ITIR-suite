"""Old original HTTP206 receipt -> pinned full HF object -> native packed file.

Offline transport fixture only; the real HTTP206 comparator is separately
covered by existing native and physical matrix suites.
"""
from __future__ import annotations

from hashlib import sha256
import io
import json
from pathlib import Path
import sys

import pytest

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
import materialize_original_equal_name_shards as tool
from test_verify_zelph_hf_original_header import _fixture, REV
from verify_zelph_bin_shard_exact import _manifest_index, _ARTIFACT


def fixture(tmp_path):
    manifest, index = _fixture()
    m = tmp_path / "manifest.json"
    i = tmp_path / "original-index.json"
    m.write_text(json.dumps(manifest, sort_keys=True))
    i.write_text(json.dumps(index, sort_keys=True))
    msha, isha = sha256(m.read_bytes()).hexdigest(), sha256(i.read_bytes()).hexdigest()
    physical = tmp_path / "receipt"
    physical.mkdir()
    original = _manifest_index(manifest, _ARTIFACT)
    for (sec, n), item in original.items():
        if sec not in ("nodeOfName", "nameOfNode"):
            continue
        data = (b"n" if sec == "nodeOfName" else b"m") * item["length"]
        proof = {
            "version": "itir.zelph.direct_original_selected_chunk_equality.v1",
            "dataset_revision": REV,
            "original_manifest_raw_sha256": msha,
            "original_index_raw_sha256": isha,
            "source_bin_size_bytes": manifest["source"]["binSizeBytes"],
            "section": sec, "chunk_index": n,
            "original_source_offset": item["offset"],
            "source_range_end_inclusive": item["offset"] + item["length"] - 1,
            "bytes_compared": item["length"],
            "published_object_uri": item["object_uri"],
            "original_binary_uri": f"hf://datasets/acrion/zelph/{_ARTIFACT}.bin",
            "original_source_http_status": 206,
            "published_shard_http_status": 200,
            "exact_original_packed_bytes_equal_published_shard": True,
            "full_index_manifest_offset_cover_checked": True,
            "original_qid_route_verified": False,
            "whole_name_domain_enumerated": False,
            "all_query_frontiers_closed": False,
            "native_p854_source_support_paid": False,
            "s29_persistence_paid": False, "edit_authority": False,
            "published_shard_raw_sha256": sha256(data).hexdigest(),
            "original_packed_range_raw_sha256": sha256(data).hexdigest(),
        }
        (physical / f"{sec}-{n:06d}.json").write_text(json.dumps(proof))
    return dict(
        manifest=m, original_index=i,
        manifest_sha256=msha, original_index_sha256=isha,
        revision=REV, physical_receipts_dirs=[physical],
        shard_root=tmp_path / "verified-packed",
    )


def source_copy(**kwargs):
    assert kwargs["revision"] == REV
    assert kwargs["expected_size"] == 5
    prefix = b"n" if "/nodeOfName/" in kwargs["hf_uri"] else b"m"
    return io.BytesIO(prefix * 5)


def test_missing_original_equal_packed_files_restore_without_source_bin_download(
    tmp_path, monkeypatch
):
    cfg = fixture(tmp_path)
    monkeypatch.setattr(tool, "open_pinned_zelph_complete_object", source_copy)
    plan = tool.materialization_plan(**cfg, max_new_chunks=1)
    assert plan["eligible_prior_original_byte_witnesses"] == 2
    assert plan["selected_object_count"] == 1
    first = tool.restore(plan=plan)
    assert first["all_selected_saved_shards_match_prior_original_http206_receipts"]
    assert first["revalidated_original_bin_remote_byte_ranges_in_this_step"] is False
    follow = tool.materialization_plan(**cfg, max_new_chunks=1)
    assert follow["already_locally_verified_shards"] == 1
    assert follow["missing_locally_saved_shards"] == 1
    second = tool.restore(plan=follow)
    assert len(second["saved_new_chunks"]) == 1
    done = tool.materialization_plan(**cfg, max_new_chunks=8)
    assert done["already_locally_verified_shards"] == 2
    assert done["selected_object_count"] == 0
    assert done["source_support_paid"] is False
    assert done["edit_authority"] is False


def test_original_range_retained_receipt_forgery_refused_before_network(tmp_path):
    cfg = fixture(tmp_path)
    proof_file = cfg["physical_receipts_dirs"][0] / "nodeOfName-000000.json"
    proof = json.loads(proof_file.read_text())
    proof["original_source_offset"] += 4
    proof_file.write_text(json.dumps(proof))
    with pytest.raises(ValueError, match="original_source_offset"):
        tool.materialization_plan(**cfg)


def test_wrong_retrieved_complete_object_refused_with_no_local_copy(tmp_path, monkeypatch):
    cfg = fixture(tmp_path)
    monkeypatch.setattr(
        tool, "open_pinned_zelph_complete_object",
        lambda **kwargs: io.BytesIO(b"Z" * kwargs["expected_size"]))
    plan = tool.materialization_plan(**cfg, max_new_chunks=1)
    with pytest.raises(ValueError, match="differs from original"):
        tool.restore(plan=plan)
    assert not Path(plan["selected_restore_chunks"][0]["destination"]).exists()
    assert not list(cfg["shard_root"].rglob(".original-native-hf-*"))


def test_existing_same_name_shard_different_digest_refused(tmp_path):
    cfg = fixture(tmp_path)
    manifest = json.loads(cfg["manifest"].read_text())
    index = _manifest_index(manifest, _ARTIFACT)
    location = cfg["shard_root"] / index[("nameOfNode", 0)]["relative"]
    location.parent.mkdir(parents=True)
    location.write_bytes(b"X" * 5)
    with pytest.raises(ValueError, match="differs from exact original"):
        tool.materialization_plan(**cfg)


def test_zero_budget_and_missing_receipt_dir_are_blocked(tmp_path):
    cfg = fixture(tmp_path)
    with pytest.raises(ValueError):
        tool.materialization_plan(**cfg, max_transfer_mib=0)
    cfg["physical_receipts_dirs"] = [tmp_path/"missing-receipts"]
    with pytest.raises(ValueError):
        tool.materialization_plan(**cfg)


def test_explicit_original_left_right_receipt_restoration_reuses_same_transport(
    tmp_path, monkeypatch
):
    cfg = fixture(tmp_path)
    manifest = json.loads(cfg["manifest"].read_text())
    idx = _manifest_index(manifest, _ARTIFACT)
    physical = cfg["physical_receipts_dirs"][0]
    for section, char in (("left",b"l"),("right",b"r")):
        item = idx[(section,0)]
        base = json.loads((physical/"nodeOfName-000000.json").read_text())
        base.update({
            "section":section,
            "chunk_index":0,
            "original_source_offset":item["offset"],
            "source_range_end_inclusive":item["offset"]+item["length"]-1,
            "bytes_compared":item["length"],
            "published_object_uri":item["object_uri"],
            "published_shard_raw_sha256":sha256(char*item["length"]).hexdigest(),
            "original_packed_range_raw_sha256":sha256(char*item["length"]).hexdigest(),
        })
        (physical/f"{section}-000000.json").write_text(json.dumps(base))
    seen=[]
    def original_hf_complete(**kwargs):
        assert "wikidata-20260309-all.bin" not in kwargs["hf_uri"]
        sec="left" if "/left/" in kwargs["hf_uri"] else "right"
        seen.append(sec)
        return io.BytesIO((b"l" if sec=="left" else b"r")*kwargs["expected_size"])
    monkeypatch.setattr(tool,"open_pinned_zelph_complete_object",original_hf_complete)
    plan=tool.materialization_plan(
        **cfg,sections=("left","right"),max_new_chunks=3)
    assert plan["selected_original_sections"]==["left","right"]
    assert plan["eligible_prior_original_byte_witnesses"]==2
    tool.restore(plan=plan)
    assert sorted(seen)==["left","right"]
    for section,char in (("left",b"l"),("right",b"r")):
        item=idx[(section,0)]
        assert (cfg["shard_root"]/item["relative"]).read_bytes()==char*item["length"]
    again=tool.materialization_plan(**cfg,sections=("left","right"))
    assert again["already_locally_verified_shards"]==2
    assert again["planned_one_sided_hf_bytes"]==0


@pytest.mark.parametrize("sections",[
    ("left","left"),(),("left","wrong"),["left","right"],
])
def test_bad_original_adjacency_rematerialization_selection_blocks(tmp_path,sections):
    cfg=fixture(tmp_path)
    with pytest.raises(ValueError,match="selection"):
        tool.materialization_plan(**cfg,sections=sections)
