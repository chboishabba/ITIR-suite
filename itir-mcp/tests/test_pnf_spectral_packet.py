from __future__ import annotations

import json
from pathlib import Path

import pytest

from itir_mcp.pnf_spectral_numeric_abi import spectral_parity_hash
from itir_mcp.pnf_spectral_packet import VERSION, build_candidate_spectral_packet


FIXTURE_PATH = (
    Path(__file__).resolve().parent / "fixtures" / "pnf_spectral_numeric_abi" / "sensiblaw_predicate_pnf_graph_v0_2.json"
)


def _full_payload() -> dict:
    payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    assert payload["parity_hash"] == spectral_parity_hash(payload)
    return payload


def _partial_view() -> dict:
    return {
        "artifact_identity": {
            "contractVersion": "shared-shard-artifact/v1",
            "artifactId": "artifact:spectral-demo",
            "artifactRevision": "rev-7",
            "artifactClass": "spectral-partial",
            "createdAtUtc": "2026-06-22T00:00:00Z",
        },
        "selectors": ["direct-shard=logical:left", "route-name=right-name"],
        "selected_shard_ids": ["logical:left", "logical:right"],
        "selected_sections": ["left", "right"],
        "completeness": "partial",
        "subset_of_artifact": True,
    }


def _summary_only_payload() -> dict:
    return {
        "summary": {
            "schema": "itir.pnf.spectral_numeric_abi.summary.v0_1",
            "graph_version": "graph:test:spectral:summary:v1",
            "operator_profile": "spectral-symbolic-summary",
            "objects": 2,
            "rows": 2,
            "spectral_dimensions": 2,
            "probe_rows": 1,
            "edge_kinds": ["noTypedMeetEdge"],
            "gemv_rows": 2,
            "candidate_only": True,
            "diagnostic_only": True,
        },
        "candidate_refs": [
            {
                "probe_id": "p0",
                "candidate_ref": "candidate:summary:0",
                "row": 1,
                "object_id": "fact:summary",
                "rank": 0,
            }
        ],
        "parity_hash": "sha256:summary-only",
    }


def _assert_no_bulky_fields(value: object) -> None:
    if isinstance(value, dict):
        forbidden = {"raw_text", "receipts", "full_receipts", "span_refs", "span_arrays", "text"}
        assert forbidden.isdisjoint(value.keys())
        for item in value.values():
            _assert_no_bulky_fields(item)
    elif isinstance(value, list):
        for item in value:
            _assert_no_bulky_fields(item)


def test_build_candidate_spectral_packet_projects_full_abi_fixture() -> None:
    payload = _full_payload()
    packet = build_candidate_spectral_packet(_partial_view(), payload)

    assert packet["version"] == VERSION
    assert packet["candidate_only"] is True
    assert packet["non_authoritative"] is True
    assert packet["parity_hash"] == payload["parity_hash"]
    assert packet["graph_refs"]["selected_shard_ids"] == ["logical:left", "logical:right"]
    assert packet["graph_refs"]["artifact_identity"]["artifactId"] == "artifact:spectral-demo"
    assert packet["candidate_refs"][0] == {
        "probe_id": "probe:repair-duty",
        "candidate_ref": "candidate:repair-duty:0",
        "row": 2,
        "object_id": "fact:repair-duty",
        "rank": 0,
    }
    assert packet["validation"]["status"] == "validated"
    assert packet["validation"]["summary"]["schema"] == "itir.pnf.spectral_numeric_abi.v0_2"
    assert packet["validation"]["summary"]["candidate_only"] is True
    assert packet["phi_psi_ref_summary"]["phi"]["rows"] == 4
    assert packet["phi_psi_ref_summary"]["psi"]["probe_rows"] == 1
    assert packet["authority_boundary"]["truth"] is False
    _assert_no_bulky_fields(packet)


def test_build_candidate_spectral_packet_accepts_summary_only_projection() -> None:
    packet = build_candidate_spectral_packet(_partial_view(), _summary_only_payload())

    assert packet["validation"]["status"] == "not_performed"
    assert packet["validation"]["summary"]["graph_version"] == "graph:test:spectral:summary:v1"
    assert packet["candidate_refs"] == [
        {
            "probe_id": "p0",
            "candidate_ref": "candidate:summary:0",
            "row": 1,
            "object_id": "fact:summary",
            "rank": 0,
        }
    ]
    assert packet["parity_hash"] == "sha256:summary-only"
    assert packet["phi_psi_ref_summary"]["refs"]["candidate_ref_count"] == 1
    assert packet["authority_boundary"]["non_authoritative"] is True
    _assert_no_bulky_fields(packet)


@pytest.mark.parametrize("field", ["truth", "promoted"])
def test_build_candidate_spectral_packet_rejects_authority_creep(field: str) -> None:
    payload = _summary_only_payload()
    payload[field] = True

    with pytest.raises(ValueError, match=field):
        build_candidate_spectral_packet(_partial_view(), payload)


def test_build_candidate_spectral_packet_omits_full_receipts_and_span_fields_from_output() -> None:
    payload = _summary_only_payload()
    payload["raw_text"] = "full text should not surface"
    payload["receipts"] = [{"receipt_id": "receipt:1", "full_receipts": ["do-not-emit"]}]
    payload["span_arrays"] = [[0, 3]]
    packet = build_candidate_spectral_packet(_partial_view(), payload)

    _assert_no_bulky_fields(packet)
