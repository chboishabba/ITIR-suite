from __future__ import annotations

from pathlib import Path

import pytest

from itir_mcp.markdown_export import (
    render_markdown_projection,
    stable_projection_path,
    write_markdown_projection,
)
from itir_mcp import build_default_registry


def test_render_open_questions_projection_has_warning_and_provenance() -> None:
    response = {
        "ok": True,
        "result": {
            "version": "itir.docstore.open_questions.v1",
            "questions": [
                {
                    "source_system": "StatiBaker",
                    "pressure_kind": "open_question",
                    "status": "open",
                    "promotion_level": "typed_source",
                    "question_text_or_reason": "Which packet should be reviewed next?",
                    "next_action": "review compiled state pressure",
                    "provenance_refs": [
                        {
                            "kind": "statiBaker_state",
                            "path": "runs/2026-05-04/outputs/state.json",
                            "line_no": 8,
                        }
                    ],
                }
            ],
            "counts": {
                "total": 1,
                "by_source_system": {"StatiBaker": 1},
                "by_status": {"open": 1},
                "by_pressure_kind": {"open_question": 1},
                "by_promotion_level": {"typed_source": 1},
            },
            "truncated": False,
            "sources": [{"kind": "statiBaker_state", "count": 1}],
        },
    }

    projection = render_markdown_projection(response, refreshed_at="2026-05-04T00:00:00+10:00")

    assert projection.relative_path == Path("_ITIR/generated/docstore/open-questions.md")
    assert "ITIR-GENERATED:BEGIN itir:itir-docstore-open-questions-v1" in projection.block_text
    assert "not an authority record" in projection.block_text
    assert "Which packet should be reviewed next?" in projection.block_text
    assert "runs/2026-05-04/outputs/state.json" in projection.block_text
    assert projection.block_text == render_markdown_projection(
        response,
        refreshed_at="2026-05-04T00:00:00+10:00",
    ).block_text


def test_write_projection_replaces_generated_block_idempotently(tmp_path: Path) -> None:
    response = {
        "version": "itir.docstore.status.v1",
        "artifact_count": 1,
        "state_count": 2,
        "producer_counts": {"StatiBaker": 1},
        "role_counts": {"compiled_state": 1},
        "authority_counts": {"state": 1},
        "unresolved_pressure_counts": {"follow_needed": 1},
        "open_question_counts": {"total": 0},
        "latest_artifacts": [
            {
                "artifact_id": "statiBaker.compiled_state:2026-05-04",
                "artifact_role": "compiled_state",
                "source_system": "StatiBaker",
                "unresolved_pressure_status": "follow_needed",
            }
        ],
        "sources": [{"kind": "normalized_artifacts", "count": 1}],
    }
    target = tmp_path / stable_projection_path(response)
    target.parent.mkdir(parents=True)
    target.write_text(
        "\n".join(
            [
                "# ITIR Docstore Status",
                "",
                "Human note before.",
                "<!-- ITIR-GENERATED:BEGIN itir:itir-docstore-status-v1 -->",
                "stale generated content",
                "<!-- ITIR-GENERATED:END itir:itir-docstore-status-v1 -->",
                "Human note after.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    first_path = write_markdown_projection(response, output_root=tmp_path, refreshed_at="fixed")
    first_text = first_path.read_text(encoding="utf-8")
    second_path = write_markdown_projection(response, output_root=tmp_path, refreshed_at="fixed")
    second_text = second_path.read_text(encoding="utf-8")

    assert first_path == target
    assert first_text == second_text
    assert "stale generated content" not in second_text
    assert "Human note before." in second_text
    assert "Human note after." in second_text
    assert "statiBaker.compiled_state:2026-05-04" in second_text


def test_obsidian_projection_omits_full_note_bodies_and_display_paths(tmp_path: Path) -> None:
    response = {
        "version": "itir.obsidian.vault_scan.v1",
        "authority_class": "observer",
        "notes": [
            {
                "schema_version": "obsidian.note_observer.v1",
                "note_id_hash": "sha256:note",
                "vault_id_hash": "sha256:vault",
                "event": "note_scanned",
                "authority_class": "observer",
                "display_path": "Private Project/Secret.md",
                "body": "This is the full private note body and must not be exported.",
            }
        ],
        "candidates": [
            {
                "source_system": "Obsidian",
                "pressure_kind": "open_question",
                "status": "open",
                "promotion_level": "structured_hint",
                "question_text_or_reason": "Should this hint be promoted after review?",
                "next_action": "review structured Markdown hint",
                "provenance_refs": [
                    {
                        "kind": "obsidian_note",
                        "note_id_hash": "sha256:note",
                        "vault_id_hash": "sha256:vault",
                    }
                ],
            }
        ],
        "counts": {"total": 1, "by_source_system": {"Obsidian": 1}},
        "sources": [{"kind": "obsidian_vault_root", "vault_id_hash": "sha256:vault", "note_limit": 10}],
    }

    path = write_markdown_projection(response, output_root=tmp_path, refreshed_at="fixed")
    text = path.read_text(encoding="utf-8")

    assert path == tmp_path / "_ITIR/generated/obsidian/vault-scan.md"
    assert "Should this hint be promoted after review?" in text
    assert "sha256:note" in text
    assert "Private Project/Secret.md" not in text
    assert "full private note body" not in text


def test_writer_refuses_existing_file_without_generated_markers(tmp_path: Path) -> None:
    response = {"version": "itir.docstore.status.v1", "artifact_count": 0, "state_count": 0}
    target = tmp_path / stable_projection_path(response)
    target.parent.mkdir(parents=True)
    target.write_text("# Human maintained page\n", encoding="utf-8")

    with pytest.raises(ValueError, match="generated markers"):
        write_markdown_projection(response, output_root=tmp_path)


def test_markdown_projection_tools_render_and_write(tmp_path: Path) -> None:
    response = {
        "version": "itir.docstore.open_questions.v1",
        "questions": [
            {
                "source_system": "Obsidian",
                "pressure_kind": "open_question",
                "status": "open",
                "promotion_level": "structured_hint",
                "question_text_or_reason": "Should the projection tool write this?",
                "next_action": "review generated projection",
                "provenance_refs": [{"kind": "obsidian_note", "note_id_hash": "sha256:note"}],
            }
        ],
    }
    registry = build_default_registry()

    rendered = registry.invoke("itir.markdown.render_projection", {"response": response, "refreshed_at": "fixed"})
    assert rendered["ok"] is True
    assert rendered["result"]["version"] == "itir.markdown.render_projection.v1"
    assert rendered["result"]["relative_path"] == "_ITIR/generated/docstore/open-questions.md"
    assert "Should the projection tool write this?" in rendered["result"]["page_text"]

    written = registry.invoke(
        "itir.markdown.write_projection",
        {"response": response, "output_root": str(tmp_path), "refreshed_at": "fixed"},
    )
    assert written["ok"] is True
    assert written["result"]["version"] == "itir.markdown.write_projection.v1"
    assert Path(written["result"]["written_path"]).read_text(encoding="utf-8") == rendered["result"]["page_text"]
