"""One-command A1 original physical+native maximum-cut integration controls."""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import run_zelph_original_a1_one_round_maxcut as round_a1

REV = "a" * 40
MAN = "b" * 64
IDX = "c" * 64
_MIB = 1024**2


def _args(tmp_path):
    m = tmp_path / "manifest.json"
    i = tmp_path / "original-index.json"
    decoder = tmp_path / "selected-decoder"
    m.write_text("{}")
    i.write_text("{}")
    decoder.write_bytes(b"real externally pinned compiled upstream decoder placeholder")
    return {
        "manifest": m, "original_index": i, "dataset_revision": REV,
        "manifest_sha256": MAN, "original_index_sha256": IDX,
        "decoder": decoder, "decoder_sha256": sha256(decoder.read_bytes()).hexdigest(),
        "node_receipts_dir": tmp_path / "nodeOfName-receipts",
        "inverse_receipts_dir": tmp_path / "nameOfNode-receipts",
        "shard_root": tmp_path / "source-equal-packed",
        "sqlite_index": tmp_path / "name-fibres.sqlite",
    }


def _fake_stages(monkeypatch):
    events = []
    def physical(**kwargs):
        section = kwargs["section"]
        execute = kwargs["execute"]
        limit = kwargs["max_transfer_mib"] * _MIB
        desired = {"nodeOfName": 2 * _MIB, "nameOfNode": 4 * _MIB}[section]
        needed = min(desired, limit) if kwargs["max_new_chunks"] else 0
        if execute:
            kwargs["receipts_dir"].mkdir(parents=True, exist_ok=True)
        events.append(("physical", section, execute, needed))
        return {
            "version": "itir.zelph.name_section_original_byte_audit.v1",
            "section": section, "planned_transfer_bytes": needed,
            "verified_chunk_count": 1 if execute else 0,
            "all_name_section_packed_payload_bytes_verified": False,
        }
    def materialize_plan(**kwargs):
        events.append(("materialize-plan", kwargs["max_transfer_mib"],
                       kwargs["max_new_chunks"]))
        assert kwargs["shard_root"].is_dir()
        for p in kwargs["physical_receipts_dirs"]:
            assert p.is_dir()
        return {
            "version": "itir.zelph.original_equal_name_shard_rematerialization_plan.v1",
            "planned_one_sided_hf_bytes": (
                min(_MIB, kwargs["max_transfer_mib"] * _MIB)
                if kwargs["max_new_chunks"] else 0
            ),
            "selected_restore_chunks": [],
        }
    def materialize_execute(*, plan):
        events.append(("materialize-execute",))
        return {**plan, "saved_new_chunks": [{"chunk_index": 0}]}
    def native_plan(**kwargs):
        events.append(("native-plan",))
        return {
            "version": "itir.zelph.native_original_name_fibre_plan.v1",
            "available_verified_native_chunks": [],
        }
    def native_execute(**kwargs):
        events.append(("native-execute", kwargs["max_new_chunks"]))
        return {
            "version": "itir.zelph.native_original_name_fibres.v1",
            "all_original_name_section_native_chunks_decoded": False,
            "both_source_name_sections_pair_multiplicities_equal": None,
            "all_original_name_key_fibres_verified": False,
            "a1_formal_kernel_instantiation_paid": False,
        }
    monkeypatch.setattr(round_a1, "audit_name_section", physical)
    monkeypatch.setattr(round_a1, "materialization_plan", materialize_plan)
    monkeypatch.setattr(round_a1, "restore", materialize_execute)
    monkeypatch.setattr(round_a1, "original_name_plan", native_plan)
    monkeypatch.setattr(round_a1, "run_native_name_audit", native_execute)
    return events


def test_default_offline_plan_never_creates_files_or_fetches_sources(tmp_path, monkeypatch):
    args = _args(tmp_path)
    events = _fake_stages(monkeypatch)
    proof = round_a1.run_a1_evidence_round(**args, max_total_network_mib=8)
    assert proof["execute"] is False
    assert proof["planned_total_network_bytes"] == 6 * _MIB
    assert proof["source_native_all_name_sections_observed"] is False
    assert proof["original_name_fibres_complete_as_conditional_source_witness"] is False
    assert proof["formal_agda_A1_decoder_adequacy_weld_proved"] is False
    assert proof["materialization"] is None
    assert proof["native"] is None
    assert events == [
        ("physical", "nodeOfName", False, 2 * _MIB),
        ("physical", "nameOfNode", False, 4 * _MIB),
    ]
    assert not args["node_receipts_dir"].exists()
    assert not args["shard_root"].exists()
    assert not args["sqlite_index"].exists()


def test_single_budget_covers_two_source_physical_then_restore_and_native(
    tmp_path, monkeypatch
):
    args = _args(tmp_path)
    events = _fake_stages(monkeypatch)
    result = round_a1.run_a1_evidence_round(
        **args, max_total_network_mib=8, execute=True,
    )
    assert result["max_two_sided_original_source_network_bytes"] == 6 * _MIB
    assert result["max_one_sided_published_shard_network_bytes"] == _MIB
    assert result["planned_total_network_bytes"] == 7 * _MIB
    assert result["network_budget_respected"] is True
    assert result["native"]["all_original_name_section_native_chunks_decoded"] is False
    assert result["original_name_fibres_complete_as_conditional_source_witness"] is False
    assert events == [
        ("physical", "nodeOfName", False, 2 * _MIB),
        ("physical", "nameOfNode", False, 4 * _MIB),
        ("physical", "nodeOfName", True, 2 * _MIB),
        ("physical", "nameOfNode", True, 4 * _MIB),
        ("materialize-plan", 2, 4), ("materialize-execute",),
        ("native-plan",), ("native-execute", 8),
    ]


def test_global_transfer_cap_reserves_physical_before_one_sided_rematerialisation(
    tmp_path, monkeypatch
):
    args = _args(tmp_path)
    events = _fake_stages(monkeypatch)
    result = round_a1.run_a1_evidence_round(
        **args, max_total_network_mib=3, execute=True,
    )
    assert result["planned_total_network_bytes"] == 3 * _MIB
    assert result["max_one_sided_published_shard_network_bytes"] == 0
    assert ("physical", "nameOfNode", False, _MIB) in events
    assert ("materialize-plan", 1, 0) in events


def test_decoder_pin_drift_refuses_before_any_network_or_source_plan(tmp_path, monkeypatch):
    args = _args(tmp_path)
    events = _fake_stages(monkeypatch)
    args["decoder_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="decoder SHA changed"):
        round_a1.run_a1_evidence_round(**args, execute=True)
    assert events == []


def test_exact_network_preflight_says_no_for_greater_than_global_budget(
    tmp_path, monkeypatch
):
    args = _args(tmp_path)
    events = _fake_stages(monkeypatch)
    def malicious_plan(**kwargs):
        return {"planned_transfer_bytes": 1 + kwargs["max_transfer_mib"] * _MIB}
    monkeypatch.setattr(round_a1, "audit_name_section", malicious_plan)
    with pytest.raises(ValueError, match="network reservation overrun"):
        round_a1.run_a1_evidence_round(
            **args, max_total_network_mib=1, execute=True,
        )
    assert not args["shard_root"].exists()


def test_physical_range_failure_never_promotes_native_or_sqlite(tmp_path, monkeypatch):
    args = _args(tmp_path)
    events = _fake_stages(monkeypatch)
    original = round_a1.audit_name_section
    def failing_source(**kwargs):
        if kwargs["execute"]:
            raise ValueError("HTTP206 source changed during original comparison")
        return original(**kwargs)
    monkeypatch.setattr(round_a1, "audit_name_section", failing_source)
    with pytest.raises(ValueError, match="HTTP206 source changed"):
        round_a1.run_a1_evidence_round(**args, execute=True)
    assert not any(row[0] == "native-execute" for row in events)
    assert not args["sqlite_index"].exists()


@pytest.mark.parametrize("value", [
    0, -1, True, 65537,
])
def test_invalid_aggregate_network_budget_blocks(tmp_path, value):
    args = _args(tmp_path)
    with pytest.raises(ValueError, match="budget|bounds"):
        round_a1.run_a1_evidence_round(
            **args, max_total_network_mib=value,
        )


def test_duplicate_sections_and_physical_native_root_alias_are_refused(tmp_path):
    args = _args(tmp_path)
    with pytest.raises(ValueError, match="selection"):
        round_a1.run_a1_evidence_round(
            **args, sections=("nodeOfName", "nodeOfName"),
        )
    args["shard_root"] = args["node_receipts_dir"]
    with pytest.raises(ValueError, match="separate"):
        round_a1.run_a1_evidence_round(**args)


def test_complete_source_native_evidence_still_cannot_claim_agda_or_p854(
    tmp_path, monkeypatch
):
    args = _args(tmp_path)
    _fake_stages(monkeypatch)
    def native_true(**kwargs):
        return {
            "all_original_name_section_native_chunks_decoded": True,
            "both_source_name_sections_pair_multiplicities_equal": True,
            "all_original_name_key_fibres_verified": True,
            "a1_formal_kernel_instantiation_paid": False,
        }
    monkeypatch.setattr(round_a1, "run_native_name_audit", native_true)
    result = round_a1.run_a1_evidence_round(**args, execute=True)
    assert result["original_name_fibres_complete_as_conditional_source_witness"] is True
    assert result["formal_agda_A1_decoder_adequacy_weld_proved"] is False
    assert result["original_A2_adjacency_query_closure_proved"] is False
    assert result["slr_s29_live_pg_persistence_paid"] is False
    assert result["edit_authority"] is False
