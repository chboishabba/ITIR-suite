from __future__ import annotations

import json
from pathlib import Path

from itir_mcp import build_default_registry


def _write_json(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def test_docstore_open_questions_aggregates_structured_sources(tmp_path: Path) -> None:
    artifact_path = _write_json(
        tmp_path / "outputs" / "suite_normalized_artifact.json",
        {
            "schema_version": "itir.normalized.artifact.v1",
            "artifact_role": "compiled_state",
            "artifact_id": "statiBaker.compiled_state:2026-05-04",
            "provenance_anchor": {"source_system": "StatiBaker"},
            "authority": {"authority_class": "state", "derived": False},
            "lineage": {"upstream_artifact_ids": []},
            "unresolved_pressure_status": "follow_needed",
            "follow_obligation": {
                "trigger": "compiled_state_unresolved_pressure",
                "scope": "review unresolved open questions",
                "stop_condition": "all pressure resolved or held",
            },
        },
    )
    state_path = _write_json(
        tmp_path / "runs" / "2026-05-04" / "outputs" / "state.json",
        {
            "date": "2026-05-04",
            "day_state": "active",
            "human_energy": "medium",
            "priorities": ["ship docstore surface"],
            "open_questions": ["Which SL packet should be reviewed next?"],
            "blocked_tasks": ["Need provenance for vault bundle."],
            "alerts": [],
        },
    )
    review_packet_path = _write_json(
        tmp_path / "SensibLaw" / "tests" / "fixtures" / "wikidata_review_packet_fixture.json",
        {
            "packet_id": "packet-Q1",
            "page_signals": {"unresolved_questions": ["What source resolves Q1?"]},
            "reviewer_view": {
                "uncertainty_flags": ["page_open_questions"],
                "smallest_next_check": "resolve_page_open_questions",
            },
        },
    )
    markdown_path = tmp_path / "docs" / "planning.md"
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(
        "\n".join(
            [
                "# Plan",
                "## Open questions",
                "- Should Obsidian hints be promoted after review?",
                "## Gaps",
                "- Missing generated projection fixture.",
            ]
        ),
        encoding="utf-8",
    )

    registry = build_default_registry()
    result = registry.invoke(
        "itir.docstore.open_questions",
        {
            "artifact_paths": [str(artifact_path)],
            "state_paths": [str(state_path)],
            "review_packet_paths": [str(review_packet_path)],
            "markdown_paths": [str(markdown_path)],
            "include_todo_graph": False,
            "limit": 20,
        },
    )

    assert result["ok"] is True
    payload = result["result"]
    assert payload["version"] == "itir.docstore.open_questions.v1"
    texts = {item["question_text_or_reason"] for item in payload["questions"]}
    assert "review unresolved open questions" in texts
    assert "Which SL packet should be reviewed next?" in texts
    assert "What source resolves Q1?" in texts
    assert "Should Obsidian hints be promoted after review?" in texts
    assert payload["counts"]["by_promotion_level"]["typed_source"] >= 3
    assert payload["counts"]["by_promotion_level"]["structured_hint"] >= 2


def test_obsidian_scan_keeps_identity_hashed_and_candidates_observer_class(tmp_path: Path) -> None:
    vault = tmp_path / "Vault"
    vault.mkdir()
    note = vault / "Human Secret Project.md"
    note.write_text(
        "\n".join(
            [
                "# Human Secret Project",
                "tags: #private",
                "[[Backlink Target]]",
                "## Open questions",
                "- Should this note become an ITIR proposal?",
            ]
        ),
        encoding="utf-8",
    )

    registry = build_default_registry()
    result = registry.invoke(
        "itir.obsidian.vault_scan",
        {
            "vault_root": str(vault),
            "limit": 10,
        },
    )

    assert result["ok"] is True
    payload = result["result"]
    assert payload["version"] == "itir.obsidian.vault_scan.v1"
    assert payload["authority_class"] == "observer"
    assert payload["notes"][0]["note_id_hash"].startswith("sha256:")
    assert "display_path" not in payload["notes"][0]
    assert payload["candidates"][0]["source_system"] == "Obsidian"
    assert payload["candidates"][0]["authority_class"] == "observer"
    serialized = json.dumps(payload, sort_keys=True)
    assert "Human Secret Project.md" not in serialized
    assert "Backlink Target" not in serialized
    assert "#private" not in serialized
    assert "Should this note become an ITIR proposal?" in serialized


def test_docstore_status_joins_artifact_counts(tmp_path: Path) -> None:
    artifact_path = _write_json(
        tmp_path / "suite_normalized_artifact.json",
        {
            "schema_version": "itir.normalized.artifact.v1",
            "artifact_role": "compiled_state",
            "artifact_id": "statiBaker.compiled_state:2026-05-04",
            "provenance_anchor": {"source_system": "StatiBaker"},
            "authority": {"authority_class": "state", "derived": False},
            "lineage": {"upstream_artifact_ids": ["source:one"]},
            "unresolved_pressure_status": "follow_needed",
        },
    )

    registry = build_default_registry()
    result = registry.safe_invoke(
        "itir.docstore.status",
        {
            "artifact_paths": [str(artifact_path)],
            "include_todo_graph": False,
            "include_markdown_hints": False,
        },
    )

    assert result["ok"] is True
    payload = result["result"]
    assert payload["decision"] == "verified"
    assert payload["result"]["version"] == "itir.docstore.status.v1"
    assert payload["result"]["artifact_count"] == 1
    assert payload["result"]["producer_counts"] == {"StatiBaker": 1}


def test_docstore_open_questions_includes_explicit_producer_adapters(tmp_path: Path) -> None:
    dashboard_path = _write_json(
        tmp_path / "dashboard.json",
        {
            "date": "2026-05-04",
            "warnings": [{"text": "Dashboard warning needs review."}],
            "chat_context_usage": {"overflow_threads": 1, "overflow_tokens": 12},
        },
    )

    registry = build_default_registry()
    result = registry.invoke(
        "itir.docstore.open_questions",
        {
            "statibaker_dashboard_paths": [str(dashboard_path)],
            "include_todo_graph": False,
            "include_markdown_hints": False,
            "limit": 1000,
        },
    )

    assert result["ok"] is True
    payload = result["result"]
    texts = {item["question_text_or_reason"] for item in payload["questions"]}
    assert "Dashboard warning needs review." in texts
    assert "context overflow: 1 thread(s), 12 token(s)" in texts
    assert {"kind": "producer_pressure_adapters", "count": 2} in payload["sources"]
