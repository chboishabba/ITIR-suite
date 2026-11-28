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
