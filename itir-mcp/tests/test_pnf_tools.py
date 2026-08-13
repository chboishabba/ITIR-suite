from __future__ import annotations

from itir_mcp import build_default_registry


def _grounding_catalog() -> dict:
    return {
        "groundings": {
            "kent tender queue": [
                {
                    "grounded_node": "corkysoft:kent_tender_queue",
                    "grounded_label": "Kent tender queue",
                    "grounding_residual": "exact_grounding",
                }
            ]
        }
    }


def _project_context() -> dict:
    return {
        "context_id": "gamma:kent_moveware",
        "context_pnfs": [
            {
                "atom_id": "ctx:schema:todo",
                "predicate_family": "task_schema",
                "structural_signature": "TaskSchemaPNF",
                "lifecycle_effect": "promote_todo",
                "roles": {"lifecycle_effect": "promote_todo"},
            },
            {
                "atom_id": "ctx:entity:kent",
                "predicate_family": "project_ontology",
                "structural_signature": "ProjectOntologyPNF",
                "label": "Kent tender queue",
                "roles": {"object": "Kent tender queue", "feature": "Kent tender queue"},
            },
            {
                "atom_id": "ctx:board:kent",
                "predicate_family": "board_state",
                "structural_signature": "TaskCardPNF",
                "task_id": "task_existing_kent",
                "roles": {
                    "task_id": "task_existing_kent",
                    "object": "Kent tender queue",
                    "status": "todo",
                },
            },
        ],
    }


def test_pnf_context_index_wraps_sensiblaw_gamma_surface() -> None:
    registry = build_default_registry()

    result = registry.invoke(
        "itir.pnf.context_index",
        {"project_context": _project_context()},
    )

    assert result["ok"] is True
    payload = result["result"]
    assert payload["version"] == "itir.pnf.context_index.v1"
    assert payload["context_index"]["schema_version"] == "sl.project_context_pnf_index.v0_1"
    assert payload["context_index"]["authority_boundary"]["context_is_pnf_indexed"] is True
    assert payload["authority_boundary"]["canonical_truth_mutated"] is False


def test_pnf_task_memory_preview_projects_supplied_pnf_and_kanban_preview() -> None:
    registry = build_default_registry()
    documents = [
        {
            "doc_id": "openrecall:kent_moveware",
            "segments": [
                {
                    "segment_id": "openrecall:kent_moveware:s1",
                    "text": "MoveWare transition screen shows Kent tender enum mismatch.",
                    "atoms": [
                        {
                            "atom_id": "a1",
                            "predicate": "transition_followup",
                            "task_pnf": {
                                "predicate_family": "action",
                                "action_type": "validate",
                                "lifecycle_effect": "promote_todo",
                                "project_relevant": True,
                            },
                            "roles": {"object": "Kent tender queue"},
                            "wrapper_state": "explicit_request",
                            "acceptance_criteria": "Kent and MoveWare transition fields reconcile in fixture import.",
                        }
                    ],
                }
            ],
            "provenance": {"source": "openrecall_activity"},
        }
    ]

    result = registry.invoke(
        "itir.pnf.task_memory_preview",
        {
            "documents": documents,
            "grounding_catalog": _grounding_catalog(),
            "ontology_snapshot_id": "kent_moveware_fixture",
            "project_context": _project_context(),
            "include_kanban_projection": True,
        },
    )

    assert result["ok"] is True
    payload = result["result"]
    task_memory = payload["task_memory"]
    assert payload["version"] == "itir.pnf.task_memory_preview.v1"
    assert task_memory["schema_version"] == "sl.statibaker_task_memory.v0_1"
    assert task_memory["task_count"] == 1
    assert task_memory["tasks"][0]["object"] == "Kent tender queue"
    assert task_memory["authority_boundary"]["raw_keyword_tasking"] is False
    assert payload["kanban_projection"]["schema_version"] == "sl.statibaker_kanban_projection.v0_1"
    assert payload["kanban_projection"]["authority_boundary"]["kanban_projection_only"] is True
    assert payload["authority_boundary"]["canonical_truth_mutated"] is False


def test_pnf_task_memory_preview_ignores_raw_text_without_atoms() -> None:
    registry = build_default_registry()

    result = registry.invoke(
        "itir.pnf.task_memory_preview",
        {
            "documents": [
                {
                    "doc_id": "raw_openrecall",
                    "text": "Need to check Kent MoveWare transition screen.",
                }
            ],
            "grounding_catalog": _grounding_catalog(),
            "ontology_snapshot_id": "kent_moveware_fixture",
            "project_context": _project_context(),
        },
    )

    assert result["ok"] is True
    task_memory = result["result"]["task_memory"]
    assert task_memory["task_count"] == 0
    assert task_memory["ignored_segments"][0]["reason"] == "no_supplied_atoms"


def test_pnf_observer_evidence_preserves_openrecall_browser_residuals_without_tasks() -> None:
    registry = build_default_registry()
    pnf = {
        "predicate": "user_requested_validate_transition",
        "structural_signature": "browser_assist_task_candidate",
        "roles": {"object": {"value": "Kent tender queue"}},
        "wrapper": {"evidence_only": True},
    }

    result = registry.invoke(
        "itir.pnf.observer_evidence",
        {
            "browser_assist_records": [
                {
                    "session_id": "browser-assist-1",
                    "ts": "2026-06-04T00:00:00Z",
                    "task_label": "check Kent MoveWare transition",
                    "text_preview": "Kent tender queue visible",
                    "text_hash": "sha256:preview",
                    "openrecall_entry_refs": ["openrecall.entry:7"],
                    "pnf_candidates": [pnf],
                    "task_identity_residual": "partial",
                    "lifecycle_residual": "no_typed_meet",
                }
            ],
            "openrecall_activity_rows": [
                {
                    "source_ref": "openrecall.entry:7",
                    "ts": 1780531200,
                    "signal": "openrecall_activity",
                    "activity_kind": "browser_activity",
                    "ocr_preview": "MoveWare job mapping page",
                    "deep_link": "http://127.0.0.1:8082/entry/7",
                    "screenshot_present": True,
                }
            ],
        },
    )

    assert result["ok"] is True
    payload = result["result"]
    assert payload["version"] == "itir.pnf.observer_evidence.v1"
    assert payload["observer_record_count"] == 2
    browser = payload["observer_records"][0]
    openrecall = payload["observer_records"][1]
    assert browser["openrecall_entry_refs"] == ["openrecall.entry:7"]
    assert browser["pnf_candidates"] == [pnf]
    assert browser["task_identity_residual"] == "partial"
    assert browser["kanban_projection_policy"] == "observer_only"
    assert openrecall["source_ref"] == "openrecall.entry:7"
    assert openrecall["non_authoritative"] is True
    assert payload["authority_boundary"]["observer_evidence_does_not_create_tasks"] is True
    assert "tasks" not in payload
    assert "kanban_projection" not in payload


def test_pnf_tools_return_input_error_for_invalid_payload() -> None:
    registry = build_default_registry()

    result = registry.invoke("itir.pnf.task_memory_preview", {"documents": []})

    assert result["ok"] is False
    assert result["error"]["code"] == "input_error"
