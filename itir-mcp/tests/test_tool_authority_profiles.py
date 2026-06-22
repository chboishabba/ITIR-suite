from __future__ import annotations

import pytest

from itir_mcp.tool_authority_profiles import (
    AUTHORITY_STATUS_ORDER,
    AuthorityStatus,
    ToolAuthorityProfile,
    ToolKind,
    DEFAULT_TOOL_AUTHORITY_PROFILES,
    DEFAULT_REGISTRY_TOOL_AUTHORITY_PROFILES,
    validate_tool_authority_profile,
)


def test_default_profiles_validate_and_keep_outputs_non_authoritative() -> None:
    profiles = DEFAULT_TOOL_AUTHORITY_PROFILES

    assert validate_tool_authority_profile(profiles["zelph_hf_shared_shards"])
    assert AUTHORITY_STATUS_ORDER[profiles["zelph_hf_shared_shards"]["max_authority"]] <= AUTHORITY_STATUS_ORDER[
        AuthorityStatus.RECEIPT.value
    ]

    pnf = validate_tool_authority_profile(profiles["pnf_spectral_abi"])
    assert AUTHORITY_STATUS_ORDER[pnf["max_authority"]] <= AUTHORITY_STATUS_ORDER[AuthorityStatus.RECEIPT.value]
    assert AuthorityStatus.PROMOTED.value not in pnf["outputs"]
    assert AuthorityStatus.DIAGNOSTIC.value in pnf["outputs"]


def test_quickstatements_mutates_without_truth_promotion() -> None:
    profile = validate_tool_authority_profile(DEFAULT_TOOL_AUTHORITY_PROFILES["quickstatements"])

    assert profile["mutates"] is True
    assert profile["max_authority"] != AuthorityStatus.PROMOTED.value
    assert AuthorityStatus.PROMOTED.value not in profile["outputs"]


def test_spectral_candidate_packet_profile_stays_candidate_only() -> None:
    profile = validate_tool_authority_profile(DEFAULT_REGISTRY_TOOL_AUTHORITY_PROFILES["itir.spectral.candidate_packet"])

    assert profile["tool_id"] == "itir.spectral.candidate_packet"
    assert profile["kind"] == ToolKind.CANDIDATE_CLOSURE.value
    assert profile["mutates"] is False
    assert profile["max_authority"] == AuthorityStatus.RECEIPT.value
    assert profile["promotion_requires_gate"] is False
    assert profile["authority_notes"]["candidate_only"] is True
    assert profile["authority_notes"]["non_authoritative"] is True
    assert AuthorityStatus.PROMOTED.value not in profile["outputs"]


def test_wikidata_object_review_bundle_profile_stays_candidate_only_and_non_authoritative() -> None:
    profile = validate_tool_authority_profile(
        DEFAULT_REGISTRY_TOOL_AUTHORITY_PROFILES["itir.wikidata.object_review_bundle"]
    )

    assert profile["tool_id"] == "itir.wikidata.object_review_bundle"
    assert profile["mutates"] is False
    assert profile["max_authority"] == AuthorityStatus.RECEIPT.value
    assert profile["promotion_requires_gate"] is False
    assert profile["authority_notes"]["candidate_only"] is True
    assert profile["authority_notes"]["non_authoritative"] is True
    assert AuthorityStatus.PROMOTED.value not in profile["outputs"]


@pytest.mark.parametrize(
    "tool_id",
    [
        "itir.wikidata.migration_candidate",
        "itir.climate.claim_review",
        "itir.gwb.follow_graph",
        "itir.zelph.pack_sources",
    ],
)
def test_new_candidate_domain_profiles_stay_receipt_only(tool_id: str) -> None:
    profile = validate_tool_authority_profile(DEFAULT_REGISTRY_TOOL_AUTHORITY_PROFILES[tool_id])

    assert profile["tool_id"] == tool_id
    assert profile["mutates"] is False
    assert profile["max_authority"] == AuthorityStatus.RECEIPT.value
    assert profile["promotion_requires_gate"] is False
    assert profile["authority_notes"]["candidate_only"] is True
    assert profile["authority_notes"]["non_authoritative"] is True
    assert AuthorityStatus.PROMOTED.value not in profile["outputs"]


def test_invalid_self_promoting_candidate_fails_closed() -> None:
    profile = ToolAuthorityProfile(
        tool_id="bad_candidate",
        kind=ToolKind.CANDIDATE_CLOSURE.value,
        inputs=(AuthorityStatus.OBSERVED.value,),
        outputs=(AuthorityStatus.CANDIDATE.value,),
        mutates=False,
        validation_mode="strict",
        repair_mode="none",
        max_authority=AuthorityStatus.CANDIDATE.value,
        promotion_requires_gate=False,
        authority_notes={"note": "missing gate metadata"},
    )

    with pytest.raises(ValueError, match="promotion_requires_gate"):
        validate_tool_authority_profile(profile)


@pytest.mark.parametrize(
    ("field", "value", "match"),
    [
        ("kind", "unknown_kind", "unknown kind"),
        ("max_authority", "unknown_status", "unknown status"),
    ],
)
def test_unknown_kind_or_status_fails_closed(field: str, value: str, match: str) -> None:
    payload = {
        "tool_id": "bad_profile",
        "kind": ToolKind.INGESTION.value,
        "inputs": [AuthorityStatus.OBSERVED.value],
        "outputs": [AuthorityStatus.RECEIPT.value],
        "mutates": False,
        "validation_mode": "strict",
        "repair_mode": "none",
        "max_authority": AuthorityStatus.RECEIPT.value,
        "promotion_requires_gate": False,
        "authority_notes": {},
    }
    payload[field] = value

    with pytest.raises(ValueError, match=match):
        validate_tool_authority_profile(payload)
