from __future__ import annotations

import json
import importlib.util
import sys
from pathlib import Path

_suite_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_suite_root))
sys.path.insert(0, str(_suite_root / "SensibLaw"))
sys.path.insert(0, str(_suite_root / "SensibLaw" / "scripts"))
sys.path.insert(0, str(_suite_root / "SensibLaw" / "src"))
sys.path.insert(0, str(_suite_root / "pyThunderbird"))
sys.path.insert(0, str(_suite_root / "reverse-engineered-chatgpt"))
sys.path.insert(0, str(_suite_root / "tircorder-JOBBIE"))

from normalized_artifact_join import join_suite_normalized_artifacts
from SensibLaw.scripts.build_gwb_broader_review import build_gwb_broader_review
from SensibLaw.scripts.build_gwb_public_review import build_gwb_public_review
from SensibLaw.tests.test_au_fact_review_bundle import _prepare_au_fact_review_bundle_fixture
from SensibLaw.src.ontology.wikidata_grounding_depth import (
    build_grounding_depth_priority_surface,
    build_grounding_depth_summary,
)
from thunderbird.follow import (
    build_retrieval_follow_artifact,
    build_retrieval_follow_normalized_artifact,
)
from re_gpt.retrieval_follow import (
    build_conversation_list_follow_normalized_artifact,
)
from integrations.chat_history_follow import (
    build_chat_history_follow_normalized_artifact,
)

_archive_pkg_root = _suite_root / "chat-export-structurer" / "src"
_archive_pkg_spec = importlib.util.spec_from_file_location(
    "chat_export_structurer_src",
    _archive_pkg_root / "__init__.py",
    submodule_search_locations=[str(_archive_pkg_root)],
)
assert _archive_pkg_spec and _archive_pkg_spec.loader
_archive_pkg = importlib.util.module_from_spec(_archive_pkg_spec)
sys.modules[_archive_pkg_spec.name] = _archive_pkg
_archive_pkg_spec.loader.exec_module(_archive_pkg)

_archive_module_spec = importlib.util.spec_from_file_location(
    "chat_export_structurer_src.suite_normalized_artifact",
    _archive_pkg_root / "suite_normalized_artifact.py",
)
assert _archive_module_spec and _archive_module_spec.loader
_archive_module = importlib.util.module_from_spec(_archive_module_spec)
sys.modules[_archive_module_spec.name] = _archive_module
_archive_module_spec.loader.exec_module(_archive_module)
build_archive_normalized_artifact = _archive_module.build_archive_normalized_artifact

_archive_follow_spec = importlib.util.spec_from_file_location(
    "chat_export_structurer_src.archive_search_follow",
    _archive_pkg_root / "archive_search_follow.py",
)
assert _archive_follow_spec and _archive_follow_spec.loader
_archive_follow_module = importlib.util.module_from_spec(_archive_follow_spec)
sys.modules[_archive_follow_spec.name] = _archive_follow_module
_archive_follow_spec.loader.exec_module(_archive_follow_module)
build_archive_search_derived_product = _archive_follow_module.build_archive_search_derived_product


def _assert_graph_invariants(graph: dict[str, object]) -> None:
    assert graph["derived_only"] is True
    assert graph["challengeable"] is True
    summary = graph.get("summary", {})
    assert isinstance(summary.get("node_count"), int)
    assert isinstance(summary.get("edge_count"), int)
    assert summary["node_count"] >= 1
    assert summary["edge_count"] >= 1


def _assert_promotion_gate(payload: dict[str, object]) -> None:
    gate = payload["promotion_gate"]
    assert gate["decision"] in {"promote", "audit", "abstain"}
    assert gate["product_ref"]
    derived_roles = [row["role"] for row in payload["compiler_contract"]["derived_products"]]
    assert len(derived_roles) == len(set(derived_roles))
    assert any(role in {"legal_follow_graph", "legal_linkage_graph"} for role in derived_roles)


def _load_payload(builder, tmp_path: Path) -> dict[str, object]:
    result = builder(tmp_path / "out")
    return json.loads(Path(result["artifact_path"]).read_text(encoding="utf-8"))


def _assert_join_payload(payload: dict[str, object]) -> None:
    assert payload["schema_version"] == "itir.normalized.artifact.join.v1"
    assert payload["artifact_role"] == "normalized_artifact_join"
    assert payload["artifact_ids"]
    assert payload["compatibility"]["distinct_roles"]
    assert payload["lineage"]["upstream_artifact_ids"]


def _assert_bounded_local_follow(payload: dict[str, object]) -> None:
    assert payload["unresolved_pressure_status"] == "follow_needed"
    authority = payload["authority"]
    assert authority["authority_class"] == "derived_inspection"
    assert authority.get("derived") is True
    follow_obligation = payload["follow_obligation"]
    assert isinstance(follow_obligation, dict)
    scope = str(follow_obligation.get("scope") or "").strip().lower()
    stop = str(follow_obligation.get("stop_condition") or "").lower()
    assert follow_obligation.get("trigger")
    assert "review up to" in scope
    assert "stop" in stop


def _assert_legal_follow_control_plane(view: dict[str, object], *, source_family: str) -> None:
    assert view["available"] is True
    control_plane = view["control_plane"]
    assert control_plane["version"] == "follow.control.v1"
    assert control_plane["source_family"] == source_family
    summary = view["summary"]
    queue = view["queue"]
    assert isinstance(summary["route_target_counts"], dict)
    assert isinstance(summary["resolution_status_counts"], dict)
    assert isinstance(queue, list)
    assert summary["queue_count"] == len(queue)
    if queue:
        assert queue[0]["conjecture_kind"] == "follow_needed_conjecture"
        assert queue[0]["resolution_status"] == "open"


def _assert_ranked_follow_summary(summary: dict[str, object]) -> None:
    assert isinstance(summary["priority_band_counts"], dict)
    assert isinstance(summary["highest_priority_score"], int)
    assert summary["highest_priority_score"] >= 0
    assert summary["highest_authority_yield"] in {"high", "medium", "low"}


def _load_wikidata_grounding_fixture() -> dict[str, object]:
    fixture_path = (
        _suite_root
        / "SensibLaw"
        / "tests"
        / "fixtures"
        / "wikidata"
        / "wikidata_nat_grounding_depth_packets_20260402.json"
    )
    return json.loads(fixture_path.read_text(encoding="utf-8"))


def test_cross_adopter_governance_invariants(tmp_path: Path) -> None:
    bundle, _, _, _ = _prepare_au_fact_review_bundle_fixture(tmp_path)
    au_graph = bundle["semantic_context"]["legal_follow_graph"]
    _assert_graph_invariants(au_graph)
    _assert_promotion_gate(bundle["semantic_context"])

    gwb_public = _load_payload(build_gwb_public_review, tmp_path / "gwb_public")
    gwb_broader = _load_payload(build_gwb_broader_review, tmp_path / "gwb_broader")

    for payload in (gwb_public, gwb_broader):
        _assert_graph_invariants(payload["legal_follow_graph"])
        _assert_promotion_gate(payload)


def test_cross_adopter_follow_and_receipt_metrics(tmp_path: Path) -> None:
    bundle, _, _, semantic_report = _prepare_au_fact_review_bundle_fixture(tmp_path)
    authority_follow = bundle["operator_views"]["authority_follow"]
    summary = authority_follow["summary"]
    queue_count = len(authority_follow["queue"])

    assert summary["queue_count"] == queue_count
    assert sum(summary["route_target_counts"].values()) == queue_count
    assert authority_follow["available"] is True
    assert summary["authority_receipt_count"] >= 1
    assert bundle["semantic_context"]["authority_receipts"]["summary"]["authority_receipt_count"] >= 1
    assert bundle["semantic_context"]["authority_receipts"]["summary"]["linked_receipt_count"] >= 1
    assert semantic_report["run_id"] == bundle["run"]["semantic_run_id"]
    _assert_ranked_follow_summary(summary)
    _assert_legal_follow_control_plane(
        bundle["operator_views"]["legal_follow_graph"],
        source_family="au_legal_follow",
    )

    gwb_public = _load_payload(build_gwb_public_review, tmp_path / "gwb_public_follow")
    _assert_ranked_follow_summary(gwb_public["operator_views"]["legal_follow_graph"]["summary"])
    _assert_legal_follow_control_plane(
        gwb_public["operator_views"]["legal_follow_graph"],
        source_family="gwb_legal_follow",
    )


def test_cross_adopter_join_and_retrieval_follow_contracts() -> None:
    archive_artifact = build_archive_normalized_artifact(
        source_id="src_test",
        platform="chatgpt",
        account_id="main",
        input_path="/tmp/conversations.json",
        db_path="/tmp/archive.sqlite",
        stats={
            "parsed_messages": 2,
            "thread_count": 1,
            "inserted": 2,
            "duplicates": 0,
            "total_messages": 2,
        },
    )

    retrieval_follow = build_retrieval_follow_artifact(
        "privacy-first memory",
        results=[
            {
                "message_id": "mail-1",
                "subject": "Privacy-first memory",
                "sender": "sam@example.test",
                "recipient": "alex@example.test",
                "date": "2026-04-02",
            }
        ],
        max_results=1,
        stop_after=True,
        trigger_command="pyThunderbird mail --mailid-like",
        trigger_params={"user": "test", "mailid_like": "privacy-first memory"},
    )
    normalized_follow = build_retrieval_follow_normalized_artifact(
        "test", retrieval_follow
    )

    assert normalized_follow["artifact_role"] == "derived_product"
    assert normalized_follow["authority"]["authority_class"] == "derived_inspection"
    assert normalized_follow["follow_obligation"]["trigger"] == "privacy-first memory"
    assert normalized_follow["unresolved_pressure_status"] == "follow_needed"

    joined = join_suite_normalized_artifacts([archive_artifact, normalized_follow])
    _assert_join_payload(joined)
    assert "mixed_authority_classes" in joined["compatibility"]["incompatibility_flags"]
    assert "unresolved_pressure_present" in joined["compatibility"]["incompatibility_flags"]

    re_gpt_follow = build_conversation_list_follow_normalized_artifact(
        query="conversation list",
        result_refs=["conv-1", "conv-2"],
        total_results=2,
        max_results=1,
        stop_after=True,
        trigger_params={"page_size": 10},
    )
    assert re_gpt_follow["artifact_role"] == "derived_product"
    assert re_gpt_follow["authority"]["authority_class"] == "derived_inspection"
    assert re_gpt_follow["unresolved_pressure_status"] == "follow_needed"

    archive_search_follow = build_archive_search_derived_product(
        search_id="search-01",
        query="privacy memory",
        result_ids=["msg-1", "msg-2"],
        total_matches=2,
        max_results=1,
    )
    assert archive_search_follow["artifact_role"] == "derived_product"
    assert archive_search_follow["authority"]["authority_class"] == "derived_inspection"
    assert archive_search_follow["unresolved_pressure_status"] == "follow_needed"

    tirc_follow = build_chat_history_follow_normalized_artifact(
        search_id="chatlist-01",
        query="assistant transcripts",
        retrieved_ids=["msg-1", "msg-2"],
        total_count=2,
        max_results=1,
    )
    assert tirc_follow["artifact_role"] == "derived_product"
    assert tirc_follow["authority"]["authority_class"] == "derived_inspection"
    assert tirc_follow["unresolved_pressure_status"] == "follow_needed"


def test_bounded_follow_obligations_force_local_first_authority_yield() -> None:
    retrieval_follow_artifact = build_retrieval_follow_artifact(
        "local-first context",
        results=[
            {
                "message_id": "mail-1",
                "subject": "bounded search",
                "sender": "sam@example.test",
                "recipient": "alex@example.test",
                "date": "2026-04-02",
            }
        ],
        max_results=1,
        stop_after=True,
        trigger_command="pyThunderbird mail --local",
        trigger_params={"user": "bounded"},
    )
    retrieval_normalized = build_retrieval_follow_normalized_artifact(
        "bounded-user",
        retrieval_follow_artifact,
    )
    _assert_bounded_local_follow(retrieval_normalized)

    re_gpt_follow = build_conversation_list_follow_normalized_artifact(
        query="bounded list",
        result_refs=["conv-1"],
        total_results=1,
        max_results=1,
        stop_after=True,
    )
    _assert_bounded_local_follow(re_gpt_follow)

    archive_search_follow = build_archive_search_derived_product(
        search_id="bounded-archive",
        query="local archive",
        result_ids=["doc-1"],
        total_matches=1,
        max_results=1,
        stop_after=True,
    )
    _assert_bounded_local_follow(archive_search_follow)
    archive_uncertainty = archive_search_follow["uncertainty_surface"]
    assert archive_uncertainty["search_bounds_status"] in {
        "no_matches",
        "bounded_reviewable",
        "truncated_reviewable",
        "narrow_local_bound_needed",
    }
    assert isinstance(archive_uncertainty["local_archive_sufficient"], bool)
    assert archive_uncertainty["recommended_next_bound"]

    tirc_follow_local = build_chat_history_follow_normalized_artifact(
        search_id="bounded-chat",
        query="local chat",
        retrieved_ids=["msg-1"],
        total_count=1,
        max_results=1,
        stop_after=True,
    )
    _assert_bounded_local_follow(tirc_follow_local)


def test_cross_adopter_uncertainty_surfaces_are_actionable(tmp_path: Path) -> None:
    bundle, _, _, _ = _prepare_au_fact_review_bundle_fixture(tmp_path)
    au_authority_summary = bundle["operator_views"]["authority_follow"]["summary"]
    _assert_ranked_follow_summary(au_authority_summary)

    gwb_public = _load_payload(build_gwb_public_review, tmp_path / "gwb_public_uncertainty")
    _assert_ranked_follow_summary(gwb_public["operator_views"]["legal_follow_graph"]["summary"])

    grounding_summary = build_grounding_depth_summary(fixture=_load_wikidata_grounding_fixture())
    priority_surface = build_grounding_depth_priority_surface(grounding_summary=grounding_summary)
    assert priority_surface["highest_priority_score"] >= 0
    assert isinstance(priority_surface["gap_class_counts"], dict)
    assert isinstance(priority_surface["missing_field_counts"], dict)
    assert isinstance(priority_surface["recommended_follow_scope_counts"], dict)
    assert priority_surface["dominant_gap_class"]

    archive_search_follow = build_archive_search_derived_product(
        search_id="uncertainty-archive",
        query="local archive uncertainty",
        result_ids=["doc-1", "doc-2"],
        total_matches=8,
        max_results=2,
        stop_after=True,
    )
    archive_uncertainty = archive_search_follow["uncertainty_surface"]
    assert archive_uncertainty["search_bounds_status"] in {
        "no_matches",
        "bounded_reviewable",
        "truncated_reviewable",
        "narrow_local_bound_needed",
    }
    assert archive_uncertainty["recommended_next_bound"]
