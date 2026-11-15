"""A2 native left/right selected-node observations from original source-equal bytes.

Accept scoped full-source section results only when all original chunks were
independently HTTP206 witnessed and actually decoded with same native binary.
The mock emits the actual original-schema C++ selected decoder JSON wire.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
import audit_zelph_native_original_lr_roots as scan
from test_verify_zelph_hf_original_header import _fixture, REV
from verify_zelph_bin_shard_exact import _ARTIFACT,_manifest_index


def inputs(tmp_path, *, omit_right=False):
    m,i=_fixture()
    mp=tmp_path/"manifest.json"
    ip=tmp_path/"index.json"
    mp.write_text(json.dumps(m,sort_keys=True))
    ip.write_text(json.dumps(i,sort_keys=True))
    m_sha=sha256(mp.read_bytes()).hexdigest()
    i_sha=sha256(ip.read_bytes()).hexdigest()
    root=tmp_path/"shards"
    receipt=tmp_path/"source-http206"
    root.mkdir()
    receipt.mkdir()
    full=_manifest_index(m,_ARTIFACT)
    for (section,n),item in full.items():
        if section not in ("left","right"):
            continue
        if omit_right and section=="right":
            continue
        raw=(section[0]+str(n)).encode()
        raw=(raw*(item["length"]//len(raw)+1))[:item["length"]]
        dest=root/item["relative"]
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(raw)
        digest=sha256(raw).hexdigest()
        proof={
            "version":"itir.zelph.direct_original_selected_chunk_equality.v1",
            "dataset_revision":REV,
            "original_manifest_raw_sha256":m_sha,
            "original_index_raw_sha256":i_sha,
            "source_bin_size_bytes":m["source"]["binSizeBytes"],
            "section":section,"chunk_index":n,
            "original_source_offset":item["offset"],
            "source_range_end_inclusive":item["offset"]+item["length"]-1,
            "bytes_compared":item["length"],
            "published_object_uri":item["object_uri"],
            "original_binary_uri":"hf://datasets/acrion/zelph/wikidata-20260309-all.bin",
            "original_source_http_status":206,
            "published_shard_http_status":200,
            "published_shard_raw_sha256":digest,
            "original_packed_range_raw_sha256":digest,
            "exact_original_packed_bytes_equal_published_shard":True,
            "full_index_manifest_offset_cover_checked":True,
            "original_qid_route_verified":False,
            "whole_name_domain_enumerated":False,
            "all_query_frontiers_closed":False,
            "native_p854_source_support_paid":False,
            "s29_persistence_paid":False,
            "edit_authority":False,
        }
        (receipt/f"{section}-{n:06d}.json").write_text(json.dumps(proof))
    positive=tmp_path/"five-original-positive-roots.json"
    positive.write_text(json.dumps({
        "version":"itir.zelph.original_direct_native_positive_qid_roots.v1",
        "dataset_revision":REV,
        "manifest_sha256":m_sha,
        "original_index_sha256":i_sha,
        "all_declared_qid_name_witnesses_positive":True,
        "native_exact_positive_name_to_node_rows":[
            {"qid":"Q42","node_id":11}],
        "edit_authority":False}))
    decoder=tmp_path/"native-adjacency"
    decoder.write_bytes(b"native-original-schema-fixture")
    args=dict(manifest=mp,original_index=ip,
              manifest_sha256=m_sha,original_index_sha256=i_sha,
              revision=REV,physical_receipts_dirs=[receipt],
              shard_root=root,positive_roots_receipt=positive)
    return args,decoder


def native_response(cmd, **kwargs):
    section=cmd[cmd.index("--section")+1]
    chunk=int(cmd[cmd.index("--chunk-index")+1])
    targets=[int(cmd[i+1]) for i,t in enumerate(cmd[:-1]) if t=="--node"]
    rows=[]
    if 11 in targets:
        if section=="left" and chunk==0:
            rows.append({"node_id":11,"neighbors":[7,8],
                         "values_seen":2,"truncated":False})
        elif section=="left" and chunk==1:
            rows.append({"node_id":11,"neighbors":[9],
                         "values_seen":1,"truncated":False})
        elif section=="right":
            rows.append({"node_id":11,"neighbors":[17],
                         "values_seen":1,"truncated":False})
    wire=json.dumps({
        "version":"itir.zelph.selected_native_capnp_decode.v1",
        "section":section,"chunk_index":chunk,
        "rows":rows,"candidate_only":True,"authority":False}).encode()
    return SimpleNamespace(returncode=0,stdout=wire,stderr=b"")


def test_full_original_sections_prove_scoped_exact_one_hop_not_twenty_words(tmp_path):
    args,decoder=inputs(tmp_path)
    plan=scan.native_original_lr_plan(**args)
    assert plan["available_native_chunk_count"]==3
    db=tmp_path/"selected-lr.sqlite"
    part=scan.run_native_original_lr(
        plan=plan,decoder=decoder,sqlite_index=db,max_new_chunks=1,
        runner=native_response)
    assert not part["all_selected_root_one_hop_adjacencies_complete"]
    assert all(not row["complete_one_hop_adjacency"]
               for row in part["native_original_selected_node_direction_rows"]
               if row["direction"]=="right")
    completed=scan.run_native_original_lr(
        plan=plan,decoder=decoder,sqlite_index=db,max_new_chunks=3,
        runner=native_response)
    assert completed["all_selected_root_one_hop_adjacencies_complete"]
    by_dir={row["direction"]:row for row in
            completed["native_original_selected_node_direction_rows"]}
    assert by_dir["left"]["native_original_neighbors_sorted_unique"]==[7,8,9]
    assert by_dir["right"]["native_original_neighbors_sorted_unique"]==[17]
    assert by_dir["left"]["source_equal_scanned_chunks"]==2
    assert by_dir["right"]["source_equal_scanned_chunks"]==1
    assert completed["all_twenty_finite_relation_words_closed"] is False
    assert completed["source_section_chunk_counts"]=={"left":2,"right":1}
    assert not completed["native_p854_source_support_paid"]
    assert not completed["edit_authority"]
    repeated=scan.run_native_original_lr(
        plan=plan,decoder=decoder,sqlite_index=db,max_new_chunks=3,
        runner=lambda *_a,**_kw: (_ for _ in ()).throw(
            AssertionError("native complete source must never be reexecuted")))
    assert repeated["newly_decoded_chunks"]==[]


def test_missing_physical_right_does_not_prove_no_neighbors(tmp_path):
    args,decoder=inputs(tmp_path,omit_right=True)
    plan=scan.native_original_lr_plan(**args)
    assert plan["available_native_chunk_count"]==2
    rows=scan.run_native_original_lr(
        plan=plan,decoder=decoder,sqlite_index=tmp_path/"partial.db",
        max_new_chunks=5,runner=native_response)
    assert not rows["all_selected_root_one_hop_adjacencies_complete"]
    right=next(r for r in rows["native_original_selected_node_direction_rows"]
               if r["direction"]=="right")
    assert right["native_original_neighbors_sorted_unique"]==[]
    assert right["unknown_outside_scanned_source_chunks"] is True
    assert not right["complete_one_hop_adjacency"]


def test_original_source_bytes_modified_after_receipt_refused(tmp_path):
    args,decoder=inputs(tmp_path)
    plan=scan.native_original_lr_plan(**args)
    chunk=Path(plan["available_native_source_equal_chunks"][0][
        "saved_original_equal_packed_file"])
    chunk.write_bytes(b"forged")
    with pytest.raises(ValueError,match="drift"):
        scan.run_native_original_lr(
            plan=plan,decoder=decoder,sqlite_index=tmp_path/"tamper.db",
            max_new_chunks=1,runner=native_response)


def test_new_node_targets_cannot_reuse_old_sqlite_native_scan(tmp_path):
    args,decoder=inputs(tmp_path)
    plan=scan.native_original_lr_plan(**args)
    db=tmp_path/"same-source-different-nodes.db"
    scan.run_native_original_lr(
        plan=plan,decoder=decoder,sqlite_index=db,max_new_chunks=1,
        runner=native_response)
    more=scan.native_original_lr_plan(**args,extra_numeric_nodes=[7])
    with pytest.raises(ValueError,match="mixed source revisions/target"):
        scan.run_native_original_lr(
            plan=more,decoder=decoder,sqlite_index=db,max_new_chunks=2,
            runner=native_response)


def test_noncanonical_or_conflicting_native_rows_cannot_support_source_closure(tmp_path):
    args,decoder=inputs(tmp_path)
    plan=scan.native_original_lr_plan(**args)
    def bad(cmd,**kwargs):
        r=native_response(cmd,**kwargs)
        raw=json.loads(r.stdout)
        raw["rows"]=[{"node_id":11,"neighbors":[8,7],
                      "values_seen":2,"truncated":False}]
        return SimpleNamespace(returncode=0,stdout=json.dumps(raw).encode())
    with pytest.raises(ValueError,match="ambiguous/truncated"):
        scan.run_native_original_lr(
            plan=plan,decoder=decoder,sqlite_index=tmp_path/"bad.db",
            runner=bad,max_new_chunks=1)


def test_original_qid_name_id_tampering_or_wrong_revision_blocked(tmp_path):
    args,decoder=inputs(tmp_path)
    p=args["positive_roots_receipt"]
    data=json.loads(p.read_text())
    data["dataset_revision"]="f"*40
    p.write_text(json.dumps(data))
    with pytest.raises(ValueError,match="root identity"):
        scan.native_original_lr_plan(**args)
