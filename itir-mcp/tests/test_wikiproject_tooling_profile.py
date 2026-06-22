from __future__ import annotations

import pytest

from itir_mcp.wikiproject_tooling_profile import (
    DEFAULT_WIKIPROJECT_TOOLING_PROFILE,
    WikiProjectToolingEntry,
    WikiProjectToolingProfile,
    build_default_wikiproject_tooling_profile,
    validate_wikiproject_tooling_profile,
)


def test_default_wikiproject_tooling_profile_is_candidate_only() -> None:
    profile = build_default_wikiproject_tooling_profile()

    assert profile["candidate_only"] is True
    assert profile["non_authoritative"] is True
    assert profile["promotion_enabled"] is False
    assert profile["W"]["B"]["non_authoritative"] is True
    assert profile["W"]["B"]["read_only"] is True
    assert profile["W"]["Pr"]["promotion_enabled"] is False
    assert profile["W"]["Pr"]["self_promotes"] is False
    assert profile["W"]["Rpt"]["authority_label"] == "candidate-only"
    assert profile["W"]["Rpt"]["diagnostic_only"] is True


def test_default_wikiproject_tooling_profile_has_expected_etherpad_tools() -> None:
    profile = DEFAULT_WIKIPROJECT_TOOLING_PROFILE
    tool_labels = [tool["label"] for tool in profile["W"]["T"]]
    tool_ids = [tool["tool_id"] for tool in profile["W"]["T"]]

    assert tool_labels == [
        "QuickStatements",
        "OpenRefine",
        "EntitySchemas",
        "KrBot",
        "Listeria",
        "Property constraints",
    ]
    assert tool_ids == [
        "quickstatements",
        "openrefine",
        "entityschemas",
        "krbot",
        "listeria",
        "property_constraints",
    ]
    assert profile["W"]["O"] == ["candidate", "diagnostic"]
    assert profile["W"]["K"] == [
        "batch_transport",
        "repair",
        "schema",
        "bot",
        "ingestion",
        "constraints",
    ]
    assert all(tool["candidate_only"] for tool in profile["W"]["T"])
    assert all(tool["non_authoritative"] for tool in profile["W"]["T"])
    assert all(tool["promotion_enabled"] is False for tool in profile["W"]["T"])
    assert all(tool["self_promotes"] is False for tool in profile["W"]["T"])
    assert all("promoted" not in tool["outputs"] for tool in profile["W"]["T"])


def test_no_tool_self_promotes() -> None:
    profile = WikiProjectToolingProfile(
        profile_id="wikiproject-tooling",
        candidate_only=True,
        non_authoritative=True,
        promotion_enabled=False,
        tools=(
            WikiProjectToolingEntry(
                tool_id="quickstatements",
                label="QuickStatements",
                kind="batch_transport",
                outputs=("candidate", "diagnostic"),
            ),
            WikiProjectToolingEntry(
                tool_id="bad_tool",
                label="Bad Tool",
                kind="bot",
                outputs=("candidate",),
                self_promotes=True,
            ),
        ),
        sigma={"taxonomy_source": "etherpad"},
        kappa={"tool_capabilities": {"quickstatements": ["batch transport"], "bad_tool": ["bot transport"]}},
        boundary={"read_only": True, "non_authoritative": True, "canonical_truth_mutated": False},
        promotion_rules={"promotion_enabled": False, "requires_gate": False, "self_promotes": False, "promotion_targets": []},
        report={"diagnostic_only": True, "authority_label": "candidate-only", "tool_count": 0},
        governance={"profile_class": "wiki-project-tooling", "governance_contract": "itir.wikiproject.tooling_profile.v1"},
    )

    with pytest.raises(ValueError, match="self-promote"):
        validate_wikiproject_tooling_profile(profile)


@pytest.mark.parametrize(
    ("field", "value", "match"),
    [
        ("candidate_only", False, "candidate_only"),
        ("non_authoritative", False, "non_authoritative"),
        ("promotion_enabled", True, "disable promotion"),
    ],
)
def test_profile_flags_fail_closed(field: str, value: bool, match: str) -> None:
    profile = {
        "version": "itir.wikiproject.tooling_profile.v1",
        "profile_id": "wikiproject-tooling",
        "candidate_only": True,
        "non_authoritative": True,
        "promotion_enabled": False,
        "tools": [
            {
                "tool_id": "quickstatements",
                "label": "QuickStatements",
                "kind": "batch_transport",
                "outputs": ["candidate", "diagnostic"],
                "candidate_only": True,
                "non_authoritative": True,
                "promotion_enabled": False,
                "self_promotes": False,
                "notes": {"taxonomy_group": "batch"},
            }
        ],
        "sigma": {"taxonomy_source": "etherpad", "candidate_only": True, "authority_label": "candidate-only", "non_authoritative": True},
        "kappa": {"tool_capabilities": {"quickstatements": ["batch transport", "candidate staging"]}},
        "boundary": {"read_only": True, "non_authoritative": True, "canonical_truth_mutated": False},
        "promotion_rules": {"promotion_enabled": False, "requires_gate": False, "self_promotes": False, "promotion_targets": []},
        "report": {"diagnostic_only": True, "authority_label": "candidate-only", "tool_count": 1},
        "governance": {"profile_class": "wiki-project-tooling", "governance_contract": "itir.wikiproject.tooling_profile.v1"},
    }
    profile[field] = value

    with pytest.raises(ValueError, match=match):
        validate_wikiproject_tooling_profile(profile)
