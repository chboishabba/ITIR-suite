"""A2 immutable original HTTP206-vs-shard adjacency: selected + complete scope.

No mocked code path may turn incomplete physical left/right sections into
validating an exact original node route/negative or 20-word query closure.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
import audit_zelph_hf_original_adjacency_sections as audit
from test_verify_zelph_hf_original_header import _fixture, REV
from verify_zelph_bin_shard_exact import _ARTIFACT,_manifest_index


def inputs(tmp_path):
    manifest,index=_fixture()
    m=tmp_path/"manifest.json"
    i=tmp_path/"index.json"
    m.write_text(json.dumps(manifest,sort_keys=True))
    i.write_text(json.dumps(index,sort_keys=True))
    return dict(
        manifest_path=m,original_index_path=i,dataset_revision=REV,
        manifest_sha256=sha256(m.read_bytes()).hexdigest(),
        original_index_sha256=sha256(i.read_bytes()).hexdigest(),
        receipts_dir=tmp_path/"physical-left",section="left",
    )


def fake_source_equal(**kwargs):
    manifest=json.loads(kwargs["manifest_path"].read_text())
    item=_manifest_index(manifest,_ARTIFACT)[
        (kwargs["section"],kwargs["chunk_index"])]
    raw=b"x"*item["length"]
    saved=kwargs.get("save_published_copy")
    if saved is not None:
        saved.write_bytes(raw)
    digest=sha256(raw).hexdigest()
    return {
        "version":"itir.zelph.direct_original_selected_chunk_equality.v1",
        "dataset_revision":kwargs["dataset_revision"],
        "original_manifest_raw_sha256":kwargs["manifest_sha256"],
        "original_index_raw_sha256":kwargs["original_index_sha256"],
        "source_bin_size_bytes":manifest["source"]["binSizeBytes"],
        "section":kwargs["section"],"chunk_index":kwargs["chunk_index"],
        "original_source_offset":item["offset"],
        "source_range_end_inclusive":item["offset"]+item["length"]-1,
        "bytes_compared":item["length"],
        "published_object_uri":item["object_uri"],
        "original_binary_uri":"hf://datasets/acrion/zelph/wikidata-20260309-all.bin",
        "published_shard_http_status":200,
        "original_source_http_status":206,
        "exact_original_packed_bytes_equal_published_shard":True,
        "full_index_manifest_offset_cover_checked":True,
        "published_shard_raw_sha256":digest,
        "original_packed_range_raw_sha256":digest,
        "original_qid_route_verified":False,
        "whole_name_domain_enumerated":False,
        "all_query_frontiers_closed":False,
        "native_p854_source_support_paid":False,
        "s29_persistence_paid":False,
        "edit_authority":False,
        "saved_original_equal_published_copy":str(saved) if saved is not None else None,
    }


def test_adjacency_section_source_geometry_preflight_only(tmp_path):
    result=audit.audit_adjacency_section(**inputs(tmp_path))
    assert result["original_section_chunk_count"]==2
    assert result["physically_verified_chunk_count"]==0
    assert result["planned_new_http206_chunk_indices"]==[0,1]
    assert result["all_original_adjacency_section_packed_bytes_verified"] is False
    assert result["all_selected_root_routes_complete"] is False
    assert result["all_declared_query_words_closed"] is False


def test_two_source_equal_chunks_close_only_physical_left_not_lr_routes(tmp_path):
    cfg=inputs(tmp_path)
    packed=tmp_path/"saved-original-equal"
    first=audit.audit_adjacency_section(
        **cfg,execute=True,max_new_chunks=1,compare=fake_source_equal,
        save_published_root=packed)
    assert first["physically_verified_chunk_indices"]==[0]
    assert not first["all_original_adjacency_section_packed_bytes_verified"]
    second=audit.audit_adjacency_section(
        **cfg,execute=True,max_new_chunks=1,compare=fake_source_equal,
        save_published_root=packed)
    assert second["all_original_adjacency_section_packed_bytes_verified"] is True
    assert second["all_selected_root_routes_complete"] is False
    assert second["all_declared_query_words_closed"] is False
    assert len(list(cfg["receipts_dir"].glob("*.json")))==2
    m=json.loads(cfg["manifest_path"].read_text())
    for key in (("left",0),("left",1)):
        item=_manifest_index(m,_ARTIFACT)[key]
        assert (packed/item["relative"]).read_bytes()==b"x"*item["length"]


def test_original_same_shard_receipts_resume_without_new_original_http206(tmp_path):
    cfg=inputs(tmp_path)
    audit.audit_adjacency_section(
        **cfg,execute=True,max_new_chunks=2,compare=fake_source_equal)
    def forbidden(**_):
        raise AssertionError("all selected source ranges already evidenced")
    result=audit.audit_adjacency_section(**cfg,execute=True,compare=forbidden)
    assert result["new_http206_chunk_indices"]==[]
    assert result["all_original_adjacency_section_packed_bytes_verified"] is True


def test_import_other_physical_matrix_without_fetch(tmp_path):
    cfg=inputs(tmp_path)
    old=cfg["receipts_dir"]
    audit.audit_adjacency_section(
        **cfg,execute=True,max_new_chunks=2,compare=fake_source_equal)
    new=tmp_path/"new-original-equal-receipts"
    changed={**cfg,"receipts_dir":new}
    result=audit.audit_adjacency_section(
        **changed,execute=True,max_new_chunks=0,
        import_physical_receipts_dirs=[old],
        compare=lambda **_: (_ for _ in ()).throw(
            AssertionError("import never calls remote")))
    assert result["new_imported_chunk_indices"]==[0,1]
    assert result["planned_two_source_bytes"]==0
    assert result["all_original_adjacency_section_packed_bytes_verified"] is True
    for i in (0,1):
        name=f"left-{i:06d}.json"
        assert (new/name).read_bytes()==(old/name).read_bytes()


@pytest.mark.parametrize("bad", [
    {"max_new_chunks":-1},
    {"max_transfer_mib":0},
    {"max_chunk_mib":False},
    {"section":"nodeOfName"},
    {"dataset_revision":"main"},
    {"manifest_sha256":"0"*64},
])
def test_invalid_adjacency_contract_fails_without_source_transfer(tmp_path,bad):
    c={**inputs(tmp_path),**bad}
    with pytest.raises(ValueError):
        audit.audit_adjacency_section(**c)


def test_tampered_immutable_source_offset_blocks_resume(tmp_path):
    cfg=inputs(tmp_path)
    audit.audit_adjacency_section(
        **cfg,execute=True,max_new_chunks=1,compare=fake_source_equal)
    p=cfg["receipts_dir"]/"left-000000.json"
    forged=json.loads(p.read_text())
    forged["original_source_offset"]+=1
    p.write_text(json.dumps(forged))
    with pytest.raises(ValueError,match="original_source_offset"):
        audit.audit_adjacency_section(**cfg,execute=True,max_new_chunks=1,
                                      compare=fake_source_equal)


def test_absent_original_chunk_is_unknown_not_negative_adjacency(tmp_path):
    c={**inputs(tmp_path),"section":"right",
       "receipts_dir":tmp_path/"right"}
    r=audit.audit_adjacency_section(**c)
    assert r["original_section_chunk_count"]==1
    assert r["physically_verified_chunk_count"]==0
    assert r["all_original_adjacency_nodes_decoded"] is False
    assert r["all_selected_root_routes_complete"] is False
    assert r["edit_authority"] is False
