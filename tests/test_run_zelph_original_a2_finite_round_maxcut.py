"""Integrated A2 original LR HTTP206 -> native finite words; no false source gaps."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
import run_zelph_original_a2_finite_round_maxcut as a2

REV="a"*40
MAN="b"*64
IDX="c"*64
MIB=1024**2


def fixtures(tmp_path):
    manifest=tmp_path/"manifest"
    index=tmp_path/"index"
    decoder=tmp_path/"decoder"
    roots=tmp_path/"positive.json"
    family=tmp_path/"finite.json"
    for path,body in [(manifest,"{}"),(index,"{}"),(decoder,"compiled native")]:
        path.write_text(body)
    roots.write_text(json.dumps({
        "version":"itir.zelph.original_direct_native_positive_qid_roots.v1",
        "dataset_revision":REV,"manifest_sha256":MAN,"original_index_sha256":IDX,
        "all_declared_qid_name_witnesses_positive":True,
        "native_exact_positive_name_to_node_rows":[{"qid":"Q42","node_id":1}],
        "edit_authority":False,
    }))
    family.write_text(json.dumps({
        "version":"itir.zelph.finite_lr_query_family.v1",
        "qid_root_nodes":{"Q42":1},
        "queries":[
            {"id":"left","qid":"Q42","word":["left"]},
            {"id":"right","qid":"Q42","word":["right"]},
            {"id":"left-right","qid":"Q42","word":["left","right"]},
            {"id":"right-left","qid":"Q42","word":["right","left"]},
        ]
    }))
    return dict(
        manifest=manifest,original_index=index,
        dataset_revision=REV,manifest_sha256=MAN,original_index_sha256=IDX,
        decoder=decoder,decoder_sha256=sha256(decoder.read_bytes()).hexdigest(),
        positive_roots_receipt=roots,
        query_family=family,
        query_family_sha256=sha256(family.read_bytes()).hexdigest(),
        left_receipts_dir=tmp_path/"physical-left",
        right_receipts_dir=tmp_path/"physical-right",
        shard_root=tmp_path/"equal-shards",
        native_audit_dir=tmp_path/"native-frontiers",
        max_network_mib=16,
    )


def stages(monkeypatch, *, complete=True):
    events=[]
    def geometry(**kwargs):
        events.append(("geometry",))
        return {"section_chunk_counts":{"leftChunkCount":2,"rightChunkCount":1}}
    monkeypatch.setattr(a2,"verify_index_manifest_files",geometry)
    def physical(**kwargs):
        s=kwargs["section"]
        want={"left":4*MIB,"right":6*MIB}[s]
        budget=kwargs["max_transfer_mib"]*MIB
        taken=min(want,budget) if kwargs["max_new_chunks"] else 0
        if kwargs["execute"]:
            kwargs["receipts_dir"].mkdir(parents=True,exist_ok=True)
        events.append(("physical",s,kwargs["execute"],taken))
        return {"version":"itir.zelph.original_lr_section_physical_http206.v1",
                "planned_two_source_bytes":taken,
                "all_original_adjacency_section_packed_bytes_verified":complete}
    monkeypatch.setattr(a2,"audit_adjacency_section",physical)
    def material_plan(**kwargs):
        assert kwargs["sections"]==("left","right")
        assert kwargs["shard_root"].is_dir()
        events.append(("material-plan",kwargs["max_transfer_mib"]))
        amount=MIB if kwargs["max_new_chunks"] else 0
        return {"version":"itir.zelph.original_equal_name_shard_rematerialization_plan.v1",
                "planned_one_sided_hf_bytes":amount}
    def material_run(*,plan):
        events.append(("material-execute",))
        return {**plan,"saved_new_chunks":[]}
    monkeypatch.setattr(a2,"materialization_plan",material_plan)
    monkeypatch.setattr(a2,"restore",material_run)
    def native_plan(**kwargs):
        numbers=sorted({1}|set(kwargs["extra_numeric_nodes"]))
        events.append(("native-plan",tuple(numbers)))
        return {"version":"itir.zelph.original_lr_native_plan.v1",
                "target_numeric_nodes":numbers}
    monkeypatch.setattr(a2,"native_original_lr_plan",native_plan)
    def native_run(**kwargs):
        numbers=kwargs["plan"]["target_numeric_nodes"]
        events.append(("native-run",tuple(numbers)))
        vals={(1,"left"):[2],(1,"right"):[3],
              (2,"right"):[4],(3,"left"):[5]}
        rows=[]
        for n in numbers:
            for direction in ("left","right"):
                adj=vals.get((n,direction),[])
                rows.append({
                    "node_id":n,"direction":direction,
                    "original_complete_direction_chunk_scan":complete,
                    "source_equal_scanned_chunks":({"left":2,"right":1}[direction]
                                                   if complete else 0),
                    "source_original_section_chunk_count":{"left":2,"right":1}[direction],
                    "native_packed_hit_chunk_indices":[0] if adj else [],
                    "native_original_neighbors_sorted_unique":adj,
                    "native_original_values_seen":len(adj),
                    "complete_one_hop_adjacency":complete,
                    "unknown_outside_scanned_source_chunks":not complete,
                })
        return {
            "version":"itir.zelph.original_lr_native_complete_chunk_scans.v1",
            "dataset_revision":REV,"manifest_sha256":MAN,
            "original_index_sha256":IDX,
            "positive_roots_receipt_sha256":kwargs.get("root_sha",root_sha_holder[0]),
            "decoder_binary_sha256":kwargs.get("decoder_sha",decoder_sha_holder[0]),
            "root_qid_node_ids":{"Q42":1},
            "target_numeric_nodes":numbers,
            "source_section_chunk_counts":{"left":2,"right":1},
            "native_decoded_source_equal_chunks_by_section":{
                "left":2 if complete else 0,"right":1 if complete else 0},
            "native_original_selected_node_direction_rows":rows,
            "all_source_equal_original_chunks_natively_scanned":complete,
            "all_selected_root_one_hop_adjacencies_complete":complete,
            "selected_root_adjacency_equal_exact_original_http206_bytes":complete,
            "edit_authority":False,
        }
    root_sha_holder=["d"*64]
    decoder_sha_holder=["e"*64]
    monkeypatch.setattr(a2,"run_native_original_lr",native_run)
    return events,root_sha_holder,decoder_sha_holder


def bind_hashes(args,holders):
    holders[0][0]=sha256(args["positive_roots_receipt"].read_bytes()).hexdigest()
    holders[1][0]=args["decoder_sha256"]


def test_zero_network_dry_plan_reserves_both_original_http206_sections(tmp_path,monkeypatch):
    args=fixtures(tmp_path)
    events,roots,dec=stages(monkeypatch)
    bind_hashes(args,(roots,dec))
    result=a2.run_a2_round(**args)
    assert not args["shard_root"].exists()
    assert result["execute"] is False
    assert result["planned_two_sided_http206_bytes"]==10*MIB
    assert result["planned_one_sided_restore_bytes"]==0
    assert result["finite_word_closure"] is None
    assert result["all_declared_original_lr_words_closed"] is False
    assert not any(e[0]=="native-run" for e in events)


def test_one_source_network_cap_applies_to_original_lr_and_one_sided_restore(tmp_path,monkeypatch):
    args=fixtures(tmp_path)
    events,roots,dec=stages(monkeypatch)
    bind_hashes(args,(roots,dec))
    result=a2.run_a2_round(**args,execute=True)
    assert result["planned_two_sided_http206_bytes"]==10*MIB
    assert result["planned_one_sided_restore_bytes"]==MIB
    assert result["planned_combined_network_bytes"]==11*MIB
    assert result["max_network_bytes"]==16*MIB
    assert result["all_declared_original_lr_words_closed"] is False
    assert result["next_numeric_nodes_to_scan"]==[2,3]
    assert (args["native_audit_dir"]/("original-lr-scan-"+
        sha256(b"[1]").hexdigest()+".json")).is_file()


def test_next_wave_closes_exact_four_declared_words_not_20(tmp_path,monkeypatch):
    args=fixtures(tmp_path)
    events,roots,dec=stages(monkeypatch)
    bind_hashes(args,(roots,dec))
    first=a2.run_a2_round(**args,execute=True)
    assert first["next_numeric_nodes_to_scan"]==[2,3]
    second=a2.run_a2_round(**args,execute=True)
    assert ("native-run",(1,2,3)) in events
    assert second["all_declared_original_lr_words_closed"] is True
    assert second["all_twenty_original_lr_words_closed"] is False
    assert second["finite_word_closure"]["next_numeric_nodes_to_native_scan"]==[]
    third=a2.run_a2_round(**args,execute=True)
    assert third["all_declared_original_lr_words_closed"] is True
    assert [e for e in events if e[0]=="native-run"]==[
        ("native-run",(1,)),("native-run",(1,2,3)),
    ]


def test_partial_native_scan_does_not_claim_missing_neighbor_absence(tmp_path,monkeypatch):
    args=fixtures(tmp_path)
    events,roots,dec=stages(monkeypatch,complete=False)
    bind_hashes(args,(roots,dec))
    result=a2.run_a2_round(**args,execute=True)
    assert result["native"]["all_source_equal_original_chunks_natively_scanned"] is False
    assert result["finite_word_closure"] is None
    assert result["all_declared_original_lr_words_closed"] is False
    assert not list(args["native_audit_dir"].glob("original-lr-scan-*.json"))


@pytest.mark.parametrize("bad", [
    {"decoder_sha256":"f"*64},
    {"query_family_sha256":"f"*64},
    {"max_network_mib":0},
    {"max_network_mib":True},
    {"max_numeric_frontier":257},
    {"max_steps":0},
])
def test_invalid_pins_or_resources_never_reach_network(tmp_path,monkeypatch,bad):
    args=fixtures(tmp_path)
    events,roots,dec=stages(monkeypatch)
    bind_hashes(args,(roots,dec))
    with pytest.raises(ValueError):
        a2.run_a2_round(**{**args,**bad},execute=True)
    assert not any(e[0]=="physical" for e in events)
    assert not args["native_audit_dir"].exists()


def test_original_http206_cross_section_budget_fail_closed(tmp_path,monkeypatch):
    args=fixtures(tmp_path)
    events,roots,dec=stages(monkeypatch)
    bind_hashes(args,(roots,dec))
    def overrun(**kwargs):
        return {"planned_two_source_bytes":kwargs["max_transfer_mib"]*MIB+1}
    monkeypatch.setattr(a2,"audit_adjacency_section",overrun)
    with pytest.raises(ValueError,match="budget overrun"):
        a2.run_a2_round(**args,execute=True)
    assert not args["shard_root"].exists()


def test_modified_prior_scan_cannot_be_reused_as_original_truth(tmp_path,monkeypatch):
    args=fixtures(tmp_path)
    events,roots,dec=stages(monkeypatch)
    bind_hashes(args,(roots,dec))
    a2.run_a2_round(**args,execute=True)
    p=next(args["native_audit_dir"].glob("original-lr-scan-*.json"))
    data=json.loads(p.read_text())
    data["dataset_revision"]="f"*40
    p.write_text(json.dumps(data))
    with pytest.raises(ValueError,match="identity/coverage drift"):
        a2.run_a2_round(**args,execute=True)


def test_tampered_family_roots_never_promoted(tmp_path,monkeypatch):
    args=fixtures(tmp_path)
    events,roots,dec=stages(monkeypatch)
    bind_hashes(args,(roots,dec))
    query=json.loads(args["query_family"].read_text())
    query["qid_root_nodes"]={"Q42":999}
    args["query_family"].write_text(json.dumps(query))
    args["query_family_sha256"]=sha256(args["query_family"].read_bytes()).hexdigest()
    with pytest.raises(ValueError,match="family/QID roots mismatch"):
        a2.run_a2_round(**args)
    assert not any(e[0]=="physical" for e in events)
