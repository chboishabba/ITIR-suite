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
