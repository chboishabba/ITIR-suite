from __future__ import annotations

import json
from pathlib import Path

import pytest

from itir_mcp.pnf_spectral_numeric_abi import (
    SCHEMA,
    spectral_parity_hash,
    validate_authority_gate,
    validate_rebuild_witness,
    validate_spectral_numeric_abi,
)

FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "pnf_spectral_numeric_abi_minimal.json"
REAL_FIXTURE_PATH = (
    Path(__file__).resolve().parent / "fixtures" / "pnf_spectral_numeric_abi" / "sensiblaw_predicate_pnf_graph_v0_2.json"
)


def _payload() -> dict:
    payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    assert payload["parity_hash"] == spectral_parity_hash(payload)
    return payload


def _real_payload() -> dict:
    payload = json.loads(REAL_FIXTURE_PATH.read_text(encoding="utf-8"))
    assert payload["parity_hash"] == spectral_parity_hash(payload)
    return payload


def test_validate_spectral_numeric_abi_minimal_fixture_accepts_no_typed_meet_edge() -> None:
    summary = validate_spectral_numeric_abi(_payload())
    assert summary["schema"] == SCHEMA
    assert summary["rows"] == 2
    assert summary["objects"] == 2
    assert summary["spectral_dimensions"] == 2
    assert summary["probe_rows"] == 1
    assert summary["gemv_rows"] == 2
    assert summary["candidate_only"] is True
    assert summary["diagnostic_only"] is True


def test_validate_spectral_numeric_abi_real_fixture_covers_residual_edges() -> None:
    summary = validate_spectral_numeric_abi(_real_payload())
    assert summary["rows"] == 4
    assert summary["edge_kinds"] == ["contradictionEdge", "exactResidualEdge", "noTypedMeetEdge", "partialResidualEdge"]
    assert summary["candidate_only"] is True


def test_validate_spectral_numeric_abi_requires_graph_version() -> None:
    payload = _payload()
    payload["graph_version"] = ""
    payload["parity_hash"] = spectral_parity_hash(payload)
    with pytest.raises(ValueError, match="graph_version"):
        validate_spectral_numeric_abi(payload)


def test_validate_spectral_numeric_abi_requires_receipt_coverage() -> None:
    payload = _payload()
    payload["receipts"] = [{"receipt_id": "r0"}]
    payload["parity_hash"] = spectral_parity_hash(payload)
    with pytest.raises(ValueError, match="missing receipt coverage"):
        validate_spectral_numeric_abi(payload)


def test_validate_spectral_numeric_abi_rejects_bad_edge_index() -> None:
    payload = _payload()
    payload["residual_edge_table"][0]["target_row"] = 3
    payload["parity_hash"] = spectral_parity_hash(payload)
    with pytest.raises(ValueError, match="bad edge index"):
        validate_spectral_numeric_abi(payload)


def test_validate_spectral_numeric_abi_rejects_unknown_edge_kind() -> None:
    payload = _payload()
    payload["residual_edge_table"][0]["kind"] = "unknownEdgeKind"
    payload["parity_hash"] = spectral_parity_hash(payload)
    with pytest.raises(ValueError, match="unknown edge kind"):
        validate_spectral_numeric_abi(payload)


def test_validate_spectral_numeric_abi_rejects_wrong_edge_kind_class_mapping() -> None:
    payload = _real_payload()
    payload["residual_edge_table"][1]["weight_class"] = "exactResidualWeight"
    payload["parity_hash"] = spectral_parity_hash(payload)
    with pytest.raises(ValueError, match="weight_class"):
        validate_spectral_numeric_abi(payload)


def test_validate_spectral_numeric_abi_rejects_positive_contradiction_weight() -> None:
    payload = _real_payload()
    edge = payload["residual_edge_table"][3]
    edge.pop("signed_weight")
    edge["weight"] = 9.0
    payload["parity_hash"] = spectral_parity_hash(payload)
    with pytest.raises(ValueError, match="contradictionEdge weight must be negative"):
        validate_spectral_numeric_abi(payload)


def test_validate_spectral_numeric_abi_requires_registry_binding() -> None:
    payload = _real_payload()
    payload["object_registry"].pop("fact:repair-duty")
    payload["parity_hash"] = spectral_parity_hash(payload)
    with pytest.raises(ValueError, match="missing object_registry binding"):
        validate_spectral_numeric_abi(payload)


def test_validate_spectral_numeric_abi_rejects_dimension_mismatch() -> None:
    payload = _payload()
    payload["adjacency"] = [[0.0], [1.0]]
    payload["parity_hash"] = spectral_parity_hash(payload)
    with pytest.raises(ValueError, match="adjacency"):
        validate_spectral_numeric_abi(payload)


def test_validate_spectral_numeric_abi_rejects_stale_parity_hash() -> None:
    payload = _payload()
    payload["degree"] = [3.0, 2.0]
    with pytest.raises(ValueError, match="degree rebuild mismatch|stale parity_hash"):
        validate_spectral_numeric_abi(payload)


@pytest.mark.parametrize("flag", ["truth", "support", "admissibility", "runtime", "promoted"])
def test_authority_gate_fails_closed(flag: str) -> None:
    payload = _payload()
    payload["authority"][flag] = True
    payload["parity_hash"] = spectral_parity_hash(payload)
    with pytest.raises(ValueError, match=fr"authority\.{flag}"):
        validate_authority_gate(payload["authority"])
    with pytest.raises(ValueError, match=fr"authority\.{flag}"):
        validate_spectral_numeric_abi(payload)


def test_validate_spectral_numeric_abi_rejects_phi_row_mismatch() -> None:
    payload = _payload()
    payload["spectral_coordinates"]["phi"][1]["row"] = 0
    payload["parity_hash"] = spectral_parity_hash(payload)
    with pytest.raises(ValueError, match="phi row mismatch"):
        validate_spectral_numeric_abi(payload)


def test_validate_spectral_numeric_abi_rejects_psi_row_mismatch() -> None:
    payload = _payload()
    payload["spectral_coordinates"]["psi"]["probes"][0]["row"] = 1
    payload["parity_hash"] = spectral_parity_hash(payload)
    with pytest.raises(ValueError, match="psi row alignment"):
        validate_spectral_numeric_abi(payload)


def test_validate_spectral_numeric_abi_rejects_phi_mismatch() -> None:
    payload = _payload()
    payload["spectral_coordinates"]["phi"][0]["object_id"] = "different"
    payload["parity_hash"] = spectral_parity_hash(payload)
    with pytest.raises(ValueError, match="phi row alignment"):
        validate_spectral_numeric_abi(payload)


def test_validate_spectral_numeric_abi_rejects_psi_mismatch() -> None:
    payload = _payload()
    payload["spectral_coordinates"]["psi"]["probes"][0]["object_id"] = "different"
    payload["parity_hash"] = spectral_parity_hash(payload)
    with pytest.raises(ValueError, match="psi row alignment"):
        validate_spectral_numeric_abi(payload)


def test_validate_spectral_numeric_abi_rejects_psi_authority_claims() -> None:
    payload = _real_payload()
    payload["spectral_coordinates"]["psi"]["probes"][0]["truth"] = True
    payload["parity_hash"] = spectral_parity_hash(payload)
    with pytest.raises(ValueError, match="truth"):
        validate_spectral_numeric_abi(payload)


def test_validate_rebuild_witness_rejects_inconsistent_laplacian() -> None:
    payload = _payload()
    payload["laplacian"][0][0] = 9.0
    with pytest.raises(ValueError, match="laplacian rebuild mismatch"):
        validate_rebuild_witness(payload)


def test_spectral_parity_hash_changes_when_graph_mutates() -> None:
    payload = _real_payload()
    mutated = _real_payload()
    mutated["residual_edge_table"][1]["signed_weight"]["magnitude"] = 2
    assert spectral_parity_hash(mutated) != payload["parity_hash"]
