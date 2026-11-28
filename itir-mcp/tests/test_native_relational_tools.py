import pytest
from itir_mcp import native_relational_tools as native
from itir_mcp.contracts import ToolInputError, ToolExecutionError


def test_family_readback_is_not_recomputed_or_promoted(monkeypatch):
    receipt = {"family_ref": "f", "projection": {
        "schema": "itir.relational-family.v2", "candidate_only": True,
        "formal_consumer_equivalence_paid": False, "all_live_reading_coverage_paid": False},
        "creates_access_authority": False, "applies_external_edit": False}
    def load(args):
        assert args == ["relational-family", "inspect", "f"]
        return receipt
    monkeypatch.setattr(native, "_native", load)
    result = native.inspect_relational_family({"family_ref": "f"})
    assert result["native_receipt"] is receipt
    assert result["mutates"] is False
    receipt["projection"]["formal_consumer_equivalence_paid"] = True
    with pytest.raises(ToolExecutionError):
        native.inspect_relational_family({"family_ref": "f"})


def test_no_mutating_action_or_actor_supplied_executable(monkeypatch):
    def fail(args):
        pytest.fail("invalid action must not invoke native executable")
    monkeypatch.setattr(native, "_native", fail)
    with pytest.raises(ToolInputError):
        native.inspect_relational_family({"action": "publish-revision", "transition_ref": "r"})
    with pytest.raises(ToolInputError):
        native.inspect_relational_family({"action": "original_relations", "numeric_run_ref": "r"})


def test_generic_demand_fibre_is_native_and_does_not_promote(monkeypatch):
    request = {"action": "demand_fibre", "numeric_run_ref": "n", "document_ref": "d",
               "source_sha256": "a" * 64, "demand_id": 7}
    receipt = {**{k: v for k, v in request.items() if k != "action"},
               "schema": "slr.native-demand-fibre.v1", "recorded_universe_exact": True,
               **{k: False for k in ("semantic_coverage_paid", "source_meaning_correspondence_paid",
                   "governed_identity_paid", "level_three_paid", "world_truth_paid")}}
    def load(args):
        assert args == ["numeric-pnf-native", "demand-fibre", "n", "d", "a" * 64, "7"]
        return receipt
    monkeypatch.setattr(native, "_native", load)
    result = native.inspect_relational_family(request)
    assert result["native_receipt"] is receipt
    assert result["mutates"] is False
    receipt["semantic_coverage_paid"] = True
    with pytest.raises(ToolExecutionError):
        native.inspect_relational_family(request)
    with pytest.raises(ToolInputError):
        native.inspect_relational_family({**request, "demand_id": True})


def test_factor_axis_allowlist_and_native_binding(monkeypatch):
    request = {"action": "factor_consumer", "numeric_run_ref": "n", "document_ref": "d",
               "snapshot_ref": "s", "packet_sha256": "p", "consumer_axis": "role"}
    receipt = {**{k: v for k, v in request.items() if k != "action"},
               "schema": "slr.recorded-factor-consumer.v1", "represented_product_projection_exact": True,
               **{k: False for k in ("semantic_coverage_paid", "source_meaning_correspondence_paid",
                   "governed_identity_paid", "level_three_paid", "world_truth_paid")}}
    def load(args):
        assert args == ["numeric-pnf-native", "factor-consumer", "n", "d", "s", "p", "role"]
        return receipt
    monkeypatch.setattr(native, "_native", load)
    assert native.inspect_relational_family(request)["native_receipt"] is receipt
    with pytest.raises(ToolInputError):
        native.inspect_relational_family({**request, "consumer_axis": "arbitrary"})
    receipt["snapshot_ref"] = "foreign"
    with pytest.raises(ToolExecutionError):
        native.inspect_relational_family(request)


def test_source_fibre_preserves_native_members_and_rejects_foreign_batches(monkeypatch):
    request = {"action": "source_fibre", "source_revision_ref": "rev",
               "numeric_run_ref": "n", "document_ref": "d", "snapshot_ref": "s",
               "packet_sha256": "a" * 64, "batch_refs": ["batch:1"]}
    receipt = {"schema": "slr.source-semantic-candidate-fragments.v1",
               "rows": [{"fragments": [], "outside_model_possible": True}],
               "semantic_coverage_paid": False, "world_truth_paid": False,
               "original_transport": {"outside_model_possible": True,
                   "source_coordinate_meet": {"source_revision_ref": "rev",
                       "common_current_authority_snapshot": False,
                       "checked_batches": [{"batch_ref": "batch:1"}],
                       "numeric_original": {k: request[k] for k in (
                           "numeric_run_ref", "document_ref", "snapshot_ref", "packet_sha256")}}}}
    def load(args):
        assert args == ["relational-family", "inspect-source-fibre", "rev", "n",
                        "d", "s", "a" * 64, '["batch:1"]']
        return receipt
    monkeypatch.setattr(native, "_native", load)
    result = native.inspect_relational_family(request)
    assert result["native_receipt"] is receipt
    assert result["mutates"] is False
    with pytest.raises(ToolInputError):
        native.inspect_relational_family({**request, "batch_refs": ["batch:1", "batch:1"]})
    receipt["original_transport"]["source_coordinate_meet"]["checked_batches"][0]["batch_ref"] = "foreign"
    with pytest.raises(ToolExecutionError):
        native.inspect_relational_family(request)


def test_research_frontier_preserves_inverse_and_defers_terminal_residuals(monkeypatch):
    receipt = {"schema": "slr.relational-research-frontier.v1", "family_ref": "f",
               "candidate_only": True, "satisfied_payment_refs": [],
               **{k: False for k in ("formal_consumer_equivalence_paid", "world_truth_paid",
                                     "creates_access_authority", "writes_database")},
               "residuals": [{"residual_ref": "r1", "status": "open"},
                             {"residual_ref": "r2", "status": "underidentified"}],
               "inverse": [{"residual_ref": "r1"}, {"residual_ref": "r2"}],
               "hypotheses": [{"residual_ref": "r1", "candidate_only": True}]}
    def load(args):
        assert args == ["relational-family", "inspect-research-frontier", "f"]
        return receipt
    monkeypatch.setattr(native, "_native", load)
    request = {"action": "research_frontier", "family_ref": "f"}
    assert native.inspect_relational_family(request)["native_receipt"] is receipt
    receipt["hypotheses"][0]["residual_ref"] = "r2"
    with pytest.raises(ToolExecutionError):
        native.inspect_relational_family(request)
    receipt["hypotheses"][0]["residual_ref"] = "r1"
    receipt["inverse"][1]["residual_ref"] = "r1"
    with pytest.raises(ToolExecutionError):
        native.inspect_relational_family(request)
    receipt["inverse"][1]["residual_ref"] = "r2"
    receipt["satisfied_payment_refs"] = ["fake"]
    with pytest.raises(ToolExecutionError):
        native.inspect_relational_family(request)


def test_recorded_parity_is_not_reviewed_or_semantic_parity(monkeypatch):
    receipt = {"schema": "slr.recorded-family-parity.v1", "family_ref": "f",
               "candidate_only": True, "formal_consumer_equivalence_paid": False,
               "world_truth_paid": False, "writes_database": False,
               "reviewed_representation_parity_paid": False, "source_independence_paid": False,
               "all_recorded_answers_equal": True, "pairs": [{"recorded_answer_equal": True}],
               "recorded_consumer_adequacy": [{"consumer_adequate": True}]}
    def load(args):
        assert args == ["relational-family", "inspect-recorded-parity", "f"]
        return receipt
    monkeypatch.setattr(native, "_native", load)
    req = {"action": "recorded_parity", "family_ref": "f"}
    assert native.inspect_relational_family(req)["native_receipt"] is receipt
    receipt["reviewed_representation_parity_paid"] = True
    with pytest.raises(ToolExecutionError):
        native.inspect_relational_family(req)
    receipt["reviewed_representation_parity_paid"] = False
    receipt["all_recorded_answers_equal"] = False
    with pytest.raises(ToolExecutionError):
        native.inspect_relational_family(req)


def test_local_research_readback_never_dispatches_or_ranks_uncalibrated_hits(monkeypatch):
    receipt = {"schema": "slr.relational-local-research.v1", "family_ref": "f",
               "candidate_only": True, "formal_consumer_equivalence_paid": False,
               "world_truth_paid": False, "writes_database": False,
               "creates_access_authority": False, "provider_acquisition_executed": False,
               "network_requests": 0, "planned_moves": [], "pareto_move_refs": [],
               "selected_move_ref": None, "source_manifest": [], "lexical_seeds": [],
               "no_hit_hypothesis_refs": [], "retrieval": [
                   {"candidate_only": True, "network_requests": 0, "passages": [
                       {"candidate_only": True, "source_revision_ref": "r"}]}]}
    def load(args):
        assert args == ["relational-family", "inspect-local-research", "f"]
        return receipt
    monkeypatch.setattr(native, "_native", load)
    req = {"action": "local_research", "family_ref": "f"}
    assert native.inspect_relational_family(req)["native_receipt"] is receipt
    receipt["planned_moves"] = [{"move_ref": "unpaid"}]
    with pytest.raises(ToolExecutionError):
        native.inspect_relational_family(req)
    receipt["planned_moves"] = []
    receipt["retrieval"][0]["passages"][0]["candidate_only"] = False
    with pytest.raises(ToolExecutionError):
        native.inspect_relational_family(req)


def test_investigation_preserves_gap_lanes_and_reopening_boundary(monkeypatch):
    receipt = {"schema": "slr.relational-investigation.v1", "family_ref": "f",
               **{k: True for k in ("derived_only", "challengeable", "candidate_only")},
               **{k: False for k in ("creates_graph_edges", "creates_actual_reopening",
                     "formal_consumer_equivalence_paid", "world_truth_paid", "creates_access_authority",
                     "provider_acquisition_executed", "writes_database")},
               "gap_rows": [{"residual_ref": "r", "comparison_ref": "c", "obligation_ref": "o",
                             "diagnostic_lane": "recorded_correspondence_unlicensed",
                             "route_state": "no_candidate_routes", "candidate_only": True,
                             "residual_paid": False, "formal_route_eligible": False}],
               "gap_counts": {"recorded_correspondence_unlicensed": 1},
               "dependency_edges": [], "potential_reopening_cones": [
                   {"creates_actual_reopening": False, "creates_semantic_authority": False}]}
    def load(args):
        assert args == ["relational-family", "inspect-investigation", "f"]
        return receipt
    monkeypatch.setattr(native, "_native", load)
    req = {"action": "investigation", "family_ref": "f"}
    assert native.inspect_relational_family(req)["native_receipt"] is receipt
    receipt["gap_rows"][0]["formal_route_eligible"] = True
    with pytest.raises(ToolExecutionError):
        native.inspect_relational_family(req)
    receipt["gap_rows"][0]["formal_route_eligible"] = False
    receipt["potential_reopening_cones"][0]["creates_actual_reopening"] = True
    with pytest.raises(ToolExecutionError):
        native.inspect_relational_family(req)


def test_mabo_formal_demands_keep_native_digest_and_obligation(monkeypatch):
    demand = {"demand_ref": "d", "obligation_ref": "o", "residual_ref": "r",
              "statement_digest": "sha256:" + "a"*64, "target_prover": "lean",
              "pnf_revision_ref": "pnf", "consumer_ref": "q",
              "candidate_only": True, "establishes_proof": False,
              "discharges_obligation": False, "all_source_refs_reviewed_in_graph": True,
              "formal_premise_evidence_refs": []}
    receipt = {"schema": "slr.mabo-formal-demand-readback.v1", "obligation_ref": "o",
               "residual_ref": "r", "candidate_only": True, "derived_only": True,
               **{k: False for k in ("shared_transaction_snapshot", "kernel_recertified",
                   "establishes_proof", "discharges_obligation", "creates_legal_authority",
                   "claim_truth_promoted", "search_executed", "writes_database")},
               "demands": [demand], "source_review_nodes": [], "ancestry_edges": []}
    def load(args):
        assert args == ["relational-family", "inspect-mabo-formal-demands", "o"]
        return receipt
    monkeypatch.setattr(native, "_native", load)
    req = {"action": "mabo_formal_demands", "obligation_ref": "o"}
    assert native.inspect_relational_family(req)["native_receipt"] is receipt
    demand["statement_digest"] = "a"*64
    with pytest.raises(ToolExecutionError):
        native.inspect_relational_family(req)
    demand["statement_digest"] = "sha256:" + "a"*64
    demand["obligation_ref"] = "foreign"
    with pytest.raises(ToolExecutionError):
        native.inspect_relational_family(req)


def test_licensed_view_cohort_reverse_binding_and_missing_pairs(monkeypatch):
    import json
    import copy
    req = {"left_selector_ref": "b", "right_selector_ref": "a",
           "evidence_ref": "ev", "repo": "r", "sha": "s", "path": "p",
           "canonical_thread_id": "t"}
    request = {"action": "licensed_view_cohort", "family_ref": "f",
               "query_ref": "q", "pair_evidence": [req]}
    pos, neg = {"positive": True, "negative": False}, {"positive": False, "negative": True}
    forward = {"status": "different", "left_support": pos, "right_support": neg,
               "lost": pos, "gained": neg, "opposed_signs": True,
               "bounded_signed_support_equal": False}
    backward = {**forward, "left_support": neg, "right_support": pos,
                "lost": neg, "gained": pos}
    proof = {"schema": "slr.authenticated-bounded-reciprocal-query.v1",
             "family_ref": "f", "query_ref": "q",
             **{k: False for k in ("creates_semantic_authority",
                 "all_live_semantic_readings_covered", "governed_identity_paid",
                 "world_truth_paid", "writes_database")},
             "binding": {"family_ref": "f", "consumer_ref": "c", "query_ref": "q",
                         "left_selector_ref": "b", "right_selector_ref": "a",
                         "forward_comparison_ref": "ba", "backward_comparison_ref": "ab",
                         "evidence_ref": "ev", "statement_digest": "stmt"},
             "authenticated_formal_premise": {"evidence_ref": "ev",
                 "statement_digest": "stmt", "formal_premise_paid": True,
                 "creates_legal_authority": False, "applicability_promoted": False,
                 "claim_truth_promoted": False},
             "answer": {"schema": "slr.signed-view-query-answer.v1", "query_ref": "q",
                        "left_support": neg, "right_support": pos}}
    held = {"status": "missing_authenticated_pair", "left_support": None,
            "right_support": None, "lost": None, "gained": None, "opposed_signs": None,
            "bounded_signed_support_equal": None}
    def pair(a, b, f, r, p):
        return {"pair_ref": a+b, "left_selector_ref": a, "right_selector_ref": b,
                "forward_comparison_ref": a+b, "backward_comparison_ref": b+a,
                "forward": f, "backward": r, "authenticated_pair": p,
                "source_independence_paid": False, "residual_paid": False}
    receipt = {"schema": "slr.authenticated-view-cohort.v1", "family_ref": "f",
               "consumer_ref": "c", "query_ref": "q", "selector_refs": ["a", "b", "c"],
               "shared_transaction_snapshot": True, "pair_count": 3,
               "authenticated_pair_count": 1, "available_pair_count": 1,
               "equal_support_pair_count": 0, "inconsistent_selector_refs": [],
               "all_pairs_bounded_signed_support_equal": False,
               **{k: False for k in ("derives_transitive_licences", "formal_consumer_equivalence_paid",
                   "all_live_semantic_readings_covered", "creates_semantic_authority",
                   "source_independence_paid", "world_truth_paid", "writes_database")},
               "pairs": [pair("a", "b", forward, backward, proof),
                         pair("a", "c", held.copy(), held.copy(), None),
                         pair("b", "c", held.copy(), held.copy(), None)]}
    baseline = copy.deepcopy(receipt)
    def load(args):
        assert args[:4] == ["relational-family", "inspect-licensed-view-cohort", "f", "q"]
        assert json.loads(args[4]) == [req]
        return receipt
    monkeypatch.setattr(native, "_native", load)
    result = native.inspect_relational_family(request)
    assert result["native_receipt"] is receipt and not result["mutates"]
    for mutate in (
        lambda r: r["pairs"].pop(),
        lambda r: r.update(all_pairs_bounded_signed_support_equal=True),
        lambda r: r["pairs"][0]["authenticated_pair"]["binding"].update(forward_comparison_ref="foreign"),
        lambda r: r["pairs"][0]["forward"].update(lost=neg),
        lambda r: r["pairs"][1].update(authenticated_pair=proof),
        lambda r: r.update(inconsistent_selector_refs=["a"]),
    ):
        receipt.clear()
        receipt.update(copy.deepcopy(baseline))
        mutate(receipt)
        with pytest.raises(ToolExecutionError):
            native.inspect_relational_family(request)
    with pytest.raises(ToolInputError):
        native.inspect_relational_family({**request, "pair_evidence": [req, req]})
    with pytest.raises(ToolInputError):
        native.inspect_relational_family({**request, "pair_evidence": [{**req, "left_support": pos}]})


def test_context_capsule_preserves_held_pairs_and_requires_current_digest(monkeypatch):
    import copy
    d = "sha256:" + "a"*64
    held = {"status": "missing_authenticated_pair", "left_support": None,
            "right_support": None, "lost": None, "gained": None,
            "opposed_signs": None, "bounded_signed_support_equal": None}
    cap = {"schema": "slr.query-context-capsule.v1", "family_ref": "f", "query_ref": "q",
           "family_digest": d, "full_readback_digest": d, "noncanonical": True,
           "query_scoped": True, "shared_transaction_snapshot": True,
           "creates_semantic_authority": False, "world_truth_paid": False, "writes_database": False,
           "sources": [{"selector_ref": s, "observation_ref": s, "source_revision_ref": s,
                        "source_span_ref": s, "predicate_candidate_ref": s,
                        "observation_digest": d, "context": {"time": None}} for s in ("a", "b")],
           "pairs": [{"pair_ref": "ab", "left_selector_ref": "a", "right_selector_ref": "b",
                      "forward": held.copy(), "backward": held.copy(), "proof_binding": None,
                      "formal_premise": None, "proof_readback_digest": None,
                      "residual_paid": False, "source_independence_paid": False}],
           "residuals": [{"residual_ref": "r", "acquisition_obligation_ref": "o"}],
           "reviews": [{"review_item_ref": "v", "obligation_ref": "o"}],
           "lifecycles": [{"obligation_ref": "o"}], "queues": [{"obligation_ref": "o"}],
           "pair_evidence": [],
           "loss_profile": {"omitted_inline": ["full_payloads"], "canonical_owners_retained": True,
                            "omission_implies_irrelevance": False,
                            "expansion_requires_exact_current_replay": True}}
    envelope = {"schema": "slr.query-context-capsule-envelope.v1", "capsule_digest": d,
                "capsule": cap, "full_readback_json_bytes": 5000, "capsule_body_json_bytes": 3000,
                "body_smaller_than_full_readback": True, "creates_semantic_authority": False,
                "writes_database": False}
    request = {"action": "query_context_capsule", "family_ref": "f", "query_ref": "q"}
    def read(args):
        assert args[:5] == ["relational-family", "inspect-query-context-capsule", "f", "q", "[]"]
        return envelope
    monkeypatch.setattr(native, "_native", read)
    assert native.inspect_relational_family(request)["native_receipt"] is envelope
    for mutate in (
        lambda e: e["capsule"]["pairs"].clear(),
        lambda e: e["capsule"]["queues"].clear(),
        lambda e: e["capsule"]["loss_profile"].update(omission_implies_irrelevance=True),
        lambda e: e.update(body_smaller_than_full_readback=False),
        lambda e: e["capsule"]["pairs"][0].update(proof_readback_digest=d),
    ):
        bad = copy.deepcopy(envelope)
        mutate(bad)
        monkeypatch.setattr(native, "_native", lambda _: bad)
        with pytest.raises(ToolExecutionError):
            native.inspect_relational_family(request)
    expanded = {"schema": "slr.query-context-expanded.v1", "capsule_digest": d,
                "capsule_envelope": envelope, "family": {"family_ref": "f"},
                "cohort": {"family_ref": "f", "query_ref": "q", "world_truth_paid": False},
                "exact_current_replay": True, "creates_semantic_authority": False,
                "writes_database": False}
    def expand(args):
        assert args[-1] == d
        return expanded
    monkeypatch.setattr(native, "_native", expand)
    request = {**request, "action": "expand_query_context_capsule", "capsule_digest": d}
    assert native.inspect_relational_family(request)["native_receipt"] is expanded
    expanded["exact_current_replay"] = False
    with pytest.raises(ToolExecutionError):
        native.inspect_relational_family(request)
