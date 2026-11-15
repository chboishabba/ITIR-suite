"""A2 original source-equal full-section scan -> exact finite left/right words."""
from __future__ import annotations

from hashlib import sha256
import sys
from pathlib import Path

import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from close_original_http206_lr_finite_words import original_http206_finite_words

REV="a"*40
MAN="b"*64
INDEX="c"*64
ROOTS="d"*64
DECODER="e"*64


def sweep(nodes,adjacency,*,complete=True,revision=REV):
    rows=[]
    for node in nodes:
        for direction in ("left","right"):
            values=adjacency.get((node,direction),[])
            rows.append({
                "node_id":node,"direction":direction,
                "original_complete_direction_chunk_scan":complete,
                "source_equal_scanned_chunks":2 if complete else 1,
                "source_original_section_chunk_count":2,
                "native_packed_hit_chunk_indices":[0] if values else [],
                "native_original_neighbors_sorted_unique":values,
                "native_original_values_seen":len(values),
                "complete_one_hop_adjacency":complete,
                "unknown_outside_scanned_source_chunks":not complete,
            })
    return {
        "version":"itir.zelph.original_lr_native_complete_chunk_scans.v1",
        "dataset_revision":revision,
        "manifest_sha256":MAN,
        "original_index_sha256":INDEX,
        "positive_roots_receipt_sha256":ROOTS,
        "decoder_binary_sha256":DECODER,
        "root_qid_node_ids":{"Q42":1},
        "target_numeric_nodes":sorted(nodes),
        "source_section_chunk_counts":{"left":2,"right":2},
        "native_decoded_source_equal_chunks_by_section":{
            "left":2 if complete else 1,"right":2 if complete else 1},
        "native_original_selected_node_direction_rows":rows,
        "all_source_equal_original_chunks_natively_scanned":complete,
        "all_selected_root_one_hop_adjacencies_complete":complete,
        "selected_root_adjacency_equal_exact_original_http206_bytes":complete,
        "edit_authority":False,
    }


def family():
    return {"version":"itir.zelph.finite_lr_query_family.v1",
            "qid_root_nodes":{"Q42":1},
            "queries":[
                {"id":"Q42:left","qid":"Q42","word":["left"]},
                {"id":"Q42:right","qid":"Q42","word":["right"]},
                {"id":"Q42:left-right","qid":"Q42","word":["left","right"]},
                {"id":"Q42:right-left","qid":"Q42","word":["right","left"]},
            ]}


def checks(*sources):
    return [(src,sha256(str(i).encode()).hexdigest())
            for i,src in enumerate(sources)]


def test_first_exact_root_scan_closes_one_step_and_emits_true_missing_second_hops():
    roots=sweep([1],{(1,"left"):[2],(1,"right"):[3]})
    result=original_http206_finite_words(query_family=family(),audits=checks(roots))
    assert result["query_count"]==4
    assert not result["all_declared_original_lr_words_closed"]
    assert result["next_numeric_nodes_to_native_scan"]==[2,3]
    assert len(result["missing_source_numeric_frontiers"])==2
    assert [r["status"] for r in result["query_results"]]==[
        "complete-for-declared-original-word",
        "complete-for-declared-original-word",
        "incomplete-unobserved-source-boundary",
        "incomplete-unobserved-source-boundary",
    ]
    assert not result["all_twenty_original_lr_words_closed"]


def test_second_exact_frontier_scan_closes_all_declared_words_only():
    roots=sweep([1],{(1,"left"):[2],(1,"right"):[3]})
    onward=sweep([2,3],{(2,"right"):[4],(3,"left"):[5]})
    done=original_http206_finite_words(
        query_family=family(),audits=checks(roots,onward))
    assert done["all_declared_original_lr_words_closed"] is True
    assert done["all_twenty_original_lr_words_closed"] is False
    assert done["next_numeric_nodes_to_native_scan"]==[]
    assert done["query_results"][2]["end_nodes"]==[4]
    assert done["query_results"][3]["end_nodes"]==[5]
    assert not done["p854_source_support_paid"]
    assert not done["edit_authority"]


def test_any_missing_source_section_keeps_boundary_unknown_not_negative():
    roots=sweep([1],{(1,"left"):[2]},complete=False)
    res=original_http206_finite_words(query_family=family(),audits=checks(roots))
    assert not res["all_declared_original_lr_words_closed"]
    assert res["next_numeric_nodes_to_native_scan"]==[1]
    assert res["observed_exact_node_direction_rows"]==0


def test_conflicting_exact_full_source_node_row_rejected():
    one=sweep([1],{(1,"left"):[2]})
    other=sweep([1],{(1,"left"):[99]})
    with pytest.raises(ValueError,match="conflicting"):
        original_http206_finite_words(
            query_family=family(),audits=checks(one,other))


def test_cross_revision_mixing_rejected():
    one=sweep([1],{(1,"left"):[2]})
    other=sweep([2],{},revision="f"*40)
    with pytest.raises(ValueError,match="cross-source"):
        original_http206_finite_words(
            query_family=family(),audits=checks(one,other))


def test_overclaimed_completion_without_original_chunks_is_blocked():
    one=sweep([1],{(1,"left"):[2]})
    one["native_decoded_source_equal_chunks_by_section"]["left"]=1
    with pytest.raises(ValueError,match="physical complete section count"):
        original_http206_finite_words(
            query_family=family(),audits=checks(one))


def test_invalid_query_qid_or_word_cannot_be_interpreted_as_original_graph():
    one=sweep([1],{})
    bad=family()
    bad["qid_root_nodes"]={"Q42":999}
    with pytest.raises(ValueError,match="QIDs/roots"):
        original_http206_finite_words(query_family=bad,audits=checks(one))
    bad=family()
    bad["queries"][0]["word"]=["P31"]
    with pytest.raises(ValueError,match="label/word"):
        original_http206_finite_words(query_family=bad,audits=checks(one))


def test_exact_20_word_flag_only_for_twenty_truly_closed_requested_words():
    one=sweep([1],{(1,"left"):[2],(1,"right"):[3]})
    two=sweep([2,3],{(2,"right"):[4],(3,"left"):[5]})
    queries=family()["queries"]
    requested={
        "version":"itir.zelph.finite_lr_query_family.v1",
        "qid_root_nodes":{"Q42":1},
        "queries":[{**queries[i%4],"id":f"explicit-{i:02d}"}
                   for i in range(20)]}
    result=original_http206_finite_words(
        query_family=requested,audits=checks(one,two))
    assert result["query_count"]==20
    assert result["all_twenty_original_lr_words_closed"] is True
    assert result["all_original_source_bin_bytes_hashed_in_one_full_binary_sha"] is False
