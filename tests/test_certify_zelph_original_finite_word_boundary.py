"""Fail-closed finite source-reachable certificate regression tests."""
from __future__ import annotations

import copy
from pathlib import Path
import sys
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from test_close_original_http206_lr_finite_words import family, sweep, checks
from close_original_http206_lr_finite_words import original_http206_finite_words
from certify_zelph_original_finite_word_boundary import (
    make_certificate, verify_certificate,
)


def projected(sources, *, requested=None):
    query_family=requested or family()
    audits=checks(*sources)
    result=original_http206_finite_words(
        query_family=query_family,audits=audits)
    cert=make_certificate(
        query_family=query_family,audits=audits,finite_result=result,
        query_family_raw_sha256="a"*64,finite_result_raw_sha256="b"*64)
    return cert,result,audits,query_family


def test_partial_native_positive_is_not_complete_right_adjacency():
    partial=sweep([741397],{(741397,"right"):[11,12,13]},complete=False)
    partial["root_qid_node_ids"]={"Q56404383":741397}
    requested={"version":"itir.zelph.finite_lr_query_family.v1",
               "qid_root_nodes":{"Q56404383":741397},
               "queries":[{"id":"Q56404383:right","qid":"Q56404383",
                           "word":["right"]}]}
    cert,result,_,_=projected([partial],requested=requested)
    entry=cert["query_certificate_entries"][0]
    assert not cert["all_declared_words_conditional_boundary_complete"]
    assert entry["source_reachable_steps"]==[]
    assert entry["missing_source_boundaries"]==[
        {"step":0,"node_id":741397,"direction":"right"}]
    assert entry["end_nodes"] is None
    assert not cert["native_capnp_cpp_semantics_formally_refined_here"]
    assert not cert["agda_source_reachable_boundary_term_generated_here"]
    assert not cert["edit_authority"]


def test_two_step_reachable_frontier_and_exact_receipt_dependencies():
    first=sweep([1],{(1,"left"):[2],(1,"right"):[3]})
    onward=sweep([2,3],{(2,"right"):[4],(3,"left"):[5]})
    cert,result,audits,requested=projected([first,onward])
    assert cert["all_declared_words_conditional_boundary_complete"]
    entry=next(e for e in cert["query_certificate_entries"]
               if e["query_id"]=="Q42:left-right")
    assert [s["source_reachable_input_nodes"] for s in
            entry["source_reachable_steps"]]==[[1],[2]]
    assert [s["original_and_selected_next_nodes"] for s in
            entry["source_reachable_steps"]]==[[2],[4]]
    assert entry["end_nodes"]==[4]
    assert entry["source_reachable_steps"][1][
        "per_node_direction_witnesses"][0]["exact_native_audit_shas"]==[
            audits[1][1]]
    assert not cert["s29_persistence_paid"]
    verify_certificate(
        certificate=cert,query_family=requested,audits=audits,
        finite_result=result,query_family_raw_sha256="a"*64,
        finite_result_raw_sha256="b"*64)


def test_tampered_result_or_certificate_cannot_be_promoted():
    roots=sweep([1],{(1,"left"):[2],(1,"right"):[3]})
    cert,result,audits,requested=projected([roots])
    modified=copy.deepcopy(result)
    modified["query_results"][0]["trace"][0]["result_nodes"]=[999]
    with pytest.raises(ValueError,match="differs from replayed"):
        make_certificate(query_family=requested,audits=audits,
                         finite_result=modified,
                         query_family_raw_sha256="a"*64,
                         finite_result_raw_sha256="b"*64)
    forged=copy.deepcopy(cert)
    forged["all_declared_words_conditional_boundary_complete"]=True
    with pytest.raises(ValueError,match="differs from replayed"):
        verify_certificate(
            certificate=forged,query_family=requested,audits=audits,
            finite_result=result,query_family_raw_sha256="a"*64,
            finite_result_raw_sha256="b"*64)


def test_equal_neighbor_sets_do_not_erase_conflicting_multiplicity():
    first=sweep([1],{(1,"left"):[2],(1,"right"):[3]})
    drift=copy.deepcopy(first)
    next(r for r in drift["native_original_selected_node_direction_rows"]
         if r["direction"]=="left")["native_original_values_seen"]+=1
    audits=checks(first,drift)
    result=original_http206_finite_words(query_family=family(),audits=audits)
    with pytest.raises(ValueError,match="multiplicity"):
        make_certificate(
            query_family=family(),audits=audits,finite_result=result,
            query_family_raw_sha256="a"*64,
            finite_result_raw_sha256="b"*64)


def test_mixed_source_revision_rejected_before_certificate():
    a=sweep([1],{(1,"left"):[2]})
    b=sweep([2],{},revision="f"*40)
    with pytest.raises(ValueError,match="cross-source"):
        make_certificate(query_family=family(),audits=checks(a,b),
                         finite_result={},
                         query_family_raw_sha256="a"*64,
                         finite_result_raw_sha256="b"*64)
