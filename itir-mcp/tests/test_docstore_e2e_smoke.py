from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from itir_mcp import build_default_registry
from itir_mcp.markdown_export import render_markdown_projection


JsonMap = dict[str, Any]


def _write_json(path: Path, payload: Any) -> Path:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def _render_projection(payload: Mapping[str, Any]) -> tuple[str, str]:
    return "markdown_export", render_markdown_projection(payload).page_text


def test_obsidian_bundle_to_docstore_open_questions_projection_smoke(tmp_path: Path) -> None:
    bundle_path = _write_json(
        tmp_path / "obsidian_bundle.json",
        {
            "records": [
                {
                    "schema_version": "obsidian.note_observer.v1",
                    "event": "note_observed",
                    "vault_id": "lane-6-smoke-vault",
                    "note_id": "lane-6-smoke-note",
                    "markdown": "\n".join(
                        [
                            "# Smoke Note",
                            "## Open questions",
                            "- Should the bundle candidate become a promoted ITIR proposal?",
                            "## Gaps",
                            "- Missing plugin runtime acknowledgement.",
                        ]
                    ),
                }
            ]
        },
    )

    registry = build_default_registry()
    tool_names = {tool.name for tool in registry.list_tools()}
    assert {"itir.obsidian.vault_scan", "itir.docstore.open_questions"} <= tool_names

    scan_result = registry.invoke(
        "itir.obsidian.vault_scan",
        {
            "bundle_path": str(bundle_path),
            "limit": 10,
        },
    )
    assert scan_result["ok"] is True
    scan_payload: JsonMap = scan_result["result"]
    assert scan_payload["version"] == "itir.obsidian.vault_scan.v1"
    assert scan_payload["authority_class"] == "observer"
    assert scan_payload["notes"][0]["authority_class"] == "observer"
    assert scan_payload["notes"][0]["note_id_hash"].startswith("sha256:")
    assert scan_payload["notes"][0]["vault_id_hash"].startswith("sha256:")

    scan_candidates = scan_payload["candidates"]
    assert scan_candidates
    assert {item["source_system"] for item in scan_candidates} == {"Obsidian"}
    assert {item["authority_class"] for item in scan_candidates} == {"observer"}
    assert {item["promotion_level"] for item in scan_candidates} == {"structured_hint"}
    assert "lane-6-smoke-note" not in json.dumps(scan_payload, sort_keys=True)

    open_result = registry.invoke(
        "itir.docstore.open_questions",
        {
            "roots": [str(tmp_path)],
            "bundle_path": str(bundle_path),
            "include_todo_graph": False,
            "include_markdown_hints": False,
            "limit": 10,
        },
    )
    assert open_result["ok"] is True
    open_payload: JsonMap = open_result["result"]
    assert open_payload["version"] == "itir.docstore.open_questions.v1"
    assert open_payload["counts"]["by_source_system"] == {"Obsidian": 2}
    assert open_payload["counts"]["by_promotion_level"] == {"structured_hint": 2}
    assert open_payload["sources"][-1] == {"kind": "obsidian_observer", "count": 2}

    questions = open_payload["questions"]
    assert {item["authority_class"] for item in questions} == {"observer"}
    assert "state" not in {item["authority_class"] for item in questions}
    assert "review" not in {item["authority_class"] for item in questions}
    question_texts = {item["question_text_or_reason"] for item in questions}
    assert "Should the bundle candidate become a promoted ITIR proposal?" in question_texts
    assert "Missing plugin runtime acknowledgement." in question_texts

    renderer_kind, projection = _render_projection(open_payload)
    assert renderer_kind == "markdown_export"
    assert "itir.docstore.open_questions" in projection
    assert "not an authority record" in projection
    assert "Should the bundle candidate become a promoted ITIR proposal?" in projection
    assert "Obsidian" in projection
    assert "observer" in projection
    assert "structured_hint" in projection
