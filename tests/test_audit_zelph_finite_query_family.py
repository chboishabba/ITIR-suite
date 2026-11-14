"""Adversarial finite query-word boundary tests — synthetic roots, no live HF claim."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from hashlib import sha256
import importlib.util
import json

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "audit_zelph_finite_query_family.py"
spec = importlib.util.spec_from_file_location("finite_zelph", SCRIPT)
assert spec and spec.loader
finite = importlib.util.module_from_spec(spec)
spec.loader.exec_module(finite)

REV, HASH, DIGEST = "a" * 40, "b" * 64, "c" * 64


def _audit(*rows, qids=None, rev=REV):
    qids = qids or {"Q1": 1}
    if not rows:
        rows = [(1, "left", [2, 3]), (1, "right", [4])]
    selected = [
        {
            "node_id": n, "direction": d, "neighbors": ns,
            "source_values_seen": len(ns),
            "source_truncated": False, "physical_truncated": False,
        }
        for n, d, ns in rows
    ]
    return {
        "version": "itir.zelph.native_physical_selected_original_query_cut.v1",
        "dataset_revision": rev, "manifest_sha256": HASH,
        "artifact_id": "wikidata-20260309-all",
        "native_schema_decoder_executed": True,
        "selected_root_one_hop_bidirectional_adjacency_equal_original_bin": True,
        "selected_name_routes_and_inverse_checked": True,
        "source_bin_range_equality_reverified_in_this_run": True,
        "source_bin_route_oracle_recomputed_in_this_run": False,
        "original_bin_upstream_authenticity_proved": False,
        "edit_authority": False,
        "qid_root_nodes": qids, "root_adjacency": selected,
    }


def _family(*words):
    return {
        "version": "itir.zelph.finite_lr_query_family.v1",
        "qid_root_nodes": {"Q1": 1},
        "queries": [{"id": f"w{i}", "qid": "Q1", "word": list(word)}
                    for i, word in enumerate(words)],
    }


def _run(family=None, audits=None, **opts):
    return finite.finite_relation_word_closure(
        query_family=family or _family(["left"], ["left", "left"]),
        audits=audits or [(_audit(), DIGEST)], **opts,
    )


def test_constructive_one_hop_and_two_hop_endpoint_equality():
    first = _audit((1, "left", [2, 3]), (1, "right", [4]))
    second = _audit(
        (2, "left", [5]), (2, "right", []),
        (3, "left", [6]), (3, "right", [7]),
        qids={"Q2": 2, "Q3": 3},
    )
    report = _run(audits=[(first, "1" * 64), (second, "2" * 64)])
    assert report["all_declared_words_closed"] is True
    assert report["query_results"][0]["end_nodes"] == [2, 3]
    assert report["query_results"][1]["end_nodes"] == [5, 6]
    assert len(report["query_results"][1]["trace"]) == 2
    assert report["every_audit_reverified_source_bin_ranges_in_its_run"] is True
    assert report["real_original_bin_authenticity_independently_verified"] is False
    assert report["allows_scoped_negative_answer"] is False
    assert report["source_support_paid"] is False


def test_uncovered_second_hop_cannot_be_certified():
    first = _audit((1, "left", [2, 3]), (1, "right", [4]))
    report = _run(audits=[(first, DIGEST)])
    assert not report["all_declared_words_closed"]
    assert report["query_results"][0]["status"] == "complete-for-declared-finite-word"
    assert report["query_results"][1]["end_nodes"] is None
    assert {(x["node_id"], x["direction"]) for x in report["missing_boundaries"]} == {
        (2, "left"), (3, "left"),
    }


def test_empty_terminal_answer_never_creates_global_absence():
    last = _audit((4, "left", []), (4, "right", []), qids={"Q4": 4})
    result = _run(family=_family(["right", "right"]),
                  audits=[(_audit(), DIGEST), (last, "d" * 64)])
    assert result["all_declared_words_closed"]
    assert result["query_results"][0]["end_nodes"] == []
    assert not result["allows_scoped_negative_answer"]


def test_empty_word_is_reflexive_for_declared_root():
    out = _run(family=_family([]))
    assert out["all_declared_words_closed"]
    assert out["query_results"][0]["end_nodes"] == [1]


def test_consistent_duplicate_audits_can_coalesce_but_conflicts_refuse():
    first = _audit((1, "left", [2, 3]), (1, "right", [4]))
    duplicate = deepcopy(first)
    assert _run(family=_family(["left"]),
                audits=[(first, "1" * 64), (duplicate, "2" * 64)])["all_declared_words_closed"]
    changed = deepcopy(first)
    changed["root_adjacency"][0]["neighbors"] = [9]
    with pytest.raises(ValueError, match="conflicting source/selected"):
        _run(family=_family(["left"]),
             audits=[(first, "1" * 64), (changed, "2" * 64)])


def test_original_source_multiplicity_mismatch_across_audits_fails():
    first = _audit((1, "left", [2]), (1, "right", []))
    changed = deepcopy(first)
    changed["root_adjacency"][0]["source_values_seen"] = 2
    with pytest.raises(ValueError, match="conflicting source/selected"):
        _run(family=_family(["left"]),
             audits=[(first, "1" * 64), (changed, "2" * 64)])


def test_mixed_revisions_and_invalid_manifest_digest_fail():
    with pytest.raises(ValueError, match="mixed dataset"):
        _run(audits=[(_audit(), "1" * 64), (_audit(rev="f" * 40), "2" * 64)])
    wrong = _audit()
    wrong["manifest_sha256"] = "not-sha"
    with pytest.raises(ValueError, match="manifest digest missing"):
        _run(audits=[(wrong, DIGEST)])


def test_qid_to_node_drift_and_root_substitution_fail():
    one = _audit((1, "left", [2]), (1, "right", []))
    other = _audit((22, "left", []), (22, "right", []), qids={"Q1": 22})
    with pytest.raises(ValueError, match="conflicting physical node IDs"):
        _run(audits=[(one, "1" * 64), (other, "2" * 64)])
    with pytest.raises(ValueError, match="root QID/node conflicts"):
        _run(family=dict(_family(["left"]), qid_root_nodes={"Q1": 9}),
             audits=[(one, DIGEST)])


def test_missing_native_root_direction_rejected():
    with pytest.raises(ValueError, match="both directions"):
        _run(audits=[(_audit((1, "left", [2])), DIGEST)])


def test_unsorted_duplicate_and_truncated_neighbour_lists_refused():
    for neighbors in ([3, 2], [2, 2]):
        with pytest.raises(ValueError, match="sorted and distinct"):
            _run(audits=[(_audit((1, "left", neighbors), (1, "right", [])), DIGEST)])
    bad = _audit((1, "left", [2]), (1, "right", []))
    bad["root_adjacency"][0]["source_truncated"] = True
    with pytest.raises(ValueError, match="truncated"):
        _run(audits=[(bad, DIGEST)])


def test_invalid_property_query_grammar_and_step_cap_refused():
    with pytest.raises(ValueError, match="grammar/depth"):
        _run(family=_family(["P279"]))
    with pytest.raises(ValueError, match="grammar/depth"):
        _run(family=_family(["left", "left", "left"]), max_steps=2)


def test_frontier_budget_enforced_before_expansion():
    with pytest.raises(ValueError, match="frontier exceeds"):
        _run(family=_family(["left"]), max_frontier=1)


def test_prior_receipt_dependency_is_not_live_source_authentication():
    a = _audit()
    a["source_bin_range_equality_reverified_in_this_run"] = False
    report = _run(audits=[(a, DIGEST)])
    assert not report["every_audit_reverified_source_bin_ranges_in_its_run"]
    assert not report["real_original_bin_authenticity_independently_verified"]


def test_duplicate_query_id_and_unknown_qid_refused():
    family = _family(["left"], ["right"])
    family["queries"][1]["id"] = family["queries"][0]["id"]
    with pytest.raises(ValueError, match="unique nonempty"):
        _run(family=family)
    family = _family(["left"])
    family["queries"][0]["qid"] = "Q42"
    with pytest.raises(ValueError, match="outside declared"):
        _run(family=family)


def test_duplicate_raw_json_key_rejected(tmp_path):
    file = tmp_path / "forged.json"
    file.write_text('{"version":"v1","version":"v1"}')
    with pytest.raises(ValueError, match="duplicate input JSON key"):
        finite._strict_json(file)
