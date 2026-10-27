from __future__ import annotations

from itir_mcp import build_default_registry


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


def test_default_registry_registers_spectral_candidate_packet() -> None:
    registry = build_default_registry()
    spec = registry.get_tool_spec("itir.spectral.candidate_packet")

    assert spec is not None
    assert spec.response_version == "itir.pnf.spectral_candidate_packet.v0_1"
    assert getattr(spec, "authority_profile_key", None) == "itir.spectral.candidate_packet"

    profile = registry.get_tool_authority_profile("itir.spectral.candidate_packet")
    assert profile is not None
    assert profile["tool_id"] == "itir.spectral.candidate_packet"
    assert profile["authority_notes"]["candidate_only"] is True
    assert profile["authority_notes"]["non_authoritative"] is True


def test_spectral_candidate_packet_direct_invoke_returns_non_authoritative_packet() -> None:
    registry = build_default_registry()
    result = registry.invoke(
        "itir.spectral.candidate_packet",
        {
            "partial_view": _partial_view(),
            "spectral_payload_summary_or_payload": _summary_only_payload(),
        },
    )

    assert result["ok"] is True
    packet = result["result"]
    assert packet["version"] == "itir.pnf.spectral_candidate_packet.v0_1"
    assert packet["candidate_only"] is True
    assert packet["non_authoritative"] is True
    assert packet["validation"]["status"] == "not_performed"
    assert packet["authority_boundary"]["candidate_only"] is True
    assert packet["authority_boundary"]["non_authoritative"] is True


def test_spectral_candidate_packet_safe_invoke_abstains_on_candidate_only_profile() -> None:
    registry = build_default_registry()
    result = registry.safe_invoke(
        "itir.spectral.candidate_packet",
        {
            "partial_view": _partial_view(),
            "spectral_payload_summary_or_payload": _summary_only_payload(),
        },
    )

    assert result["ok"] is True
    payload = result["result"]
    assert payload["decision"] == "abstained"
    assert payload["authority_profile"]["tool_id"] == "itir.spectral.candidate_packet"
    assert payload["authority_profile"]["candidate_only"] is True
    assert payload["authority_profile"]["non_authoritative"] is True
    assert payload["receipt"]["event"] == "tool_output_abstained"
    assert "profile_candidate_only" in payload["receipt"]["reason_codes"]
    assert "profile_non_authoritative" in payload["receipt"]["reason_codes"]
    assert payload["status_explanation"]["primary_reason_code"] == "profile_candidate_only"


def test_default_registry_registers_pnf_eigen_motifs() -> None:
    registry = build_default_registry()
    spec = registry.get_tool_spec("itir.pnf.eigen_motifs")

    assert spec is not None
    assert spec.response_version == "itir.pnf.eigen_motifs.v1"
    assert spec.read_only is True


def test_pnf_eigen_motifs_direct_invoke_returns_non_promoting_analysis() -> None:
    registry = build_default_registry()
    result = registry.invoke(
        "itir.pnf.eigen_motifs",
        {
            "thread_multisets": [
                {"thread_id": "t1", "factors": {"alpha": 8, "beta": 7, "leaf": 0}},
                {"thread_id": "t2", "factors": {"alpha": 7, "beta": 6, "leaf": 1}},
                {"thread_id": "t3", "factors": {"alpha": 1, "beta": 0, "leaf": 5}},
                {"thread_id": "t4", "factors": {"alpha": 0, "beta": 1, "leaf": 4}},
            ],
            "k_eigens": 3,
            "pareto_factors": {
                "scale_density": [1.0, 2.0, 4.0, 8.0],
                "degree_counts": [80, 40, 27, 20],
            },
        },
    )

    assert result["ok"] is True
    packet = result["result"]
    assert packet["version"] == "itir.pnf.eigen_motifs.v1"
    assert packet["eigen_coordinates"]["thread_count"] == 4
    assert len(packet["eigen_coordinates"]["components"]) == 3
    assert packet["pareto_analysis"]["factors"]["scale_density"]["continuous_pareto"]["status"] == "fit"
    assert packet["pareto_analysis"]["factors"]["degree_counts"]["discrete_zipf"]["status"] == "fit"
    assert packet["authority_boundary"]["zipf_rank_creates_mathematical_theorem_truth"] is False
