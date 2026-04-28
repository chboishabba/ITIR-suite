import json

from itir_mcp import build_default_registry


def test_itir_job_status_projects_running_partial_state(tmp_path) -> None:
    registry = build_default_registry()
    partial_path = tmp_path / "demo.partial.json"
    partial_path.write_text(
        json.dumps(
            {
                "status": "running",
                "last_event": {
                    "stage": "demo_pdf_extracting",
                    "details": {
                        "overall_elapsed_seconds": 12.5,
                        "overall_eta_seconds": 3.25,
                        "overall_words_seen": 500,
                        "overall_total_words": 1000,
                        "predicate_atom_count": 7,
                        "signal_atom_count": 11,
                        "provenance_ref_count": 13,
                    },
                },
            }
        ),
        encoding="utf-8",
    )

    result = registry.invoke(
        "sensiblaw.itir_job_status",
        {"job_id": "job-demo", "state_path": str(partial_path)},
    )

    assert result["ok"] is True
    payload = result["result"]
    assert payload["version"] == "itir.job_status.v1"
    assert payload["job_id"] == "job-demo"
    assert payload["state"] == "running"
    assert payload["elapsed_seconds"] == 12.5
    assert payload["eta_seconds"] == 3.25
    assert payload["work_unit"] == "words"
    assert payload["work_completed"] == 500
    assert payload["work_total"] == 1000
    assert payload["predicate_atom_count"] == 7
    assert payload["signal_atom_count"] == 11
    assert payload["provenance_ref_count"] == 13
    assert payload["last_partial_ref"] == str(partial_path)
    assert payload["can_resume"] is True


def test_itir_job_status_maps_interrupted_to_partial_when_resumable() -> None:
    registry = build_default_registry()
    result = registry.invoke(
        "sensiblaw.itir_job_status",
        {
            "job_id": "job-feed",
            "run_state": {
                "status": "interrupted",
                "last_event": {
                    "stage": "demo_pdf_feed_progress",
                    "details": {
                        "elapsed_seconds": 18.4,
                        "eta_seconds": 7.2,
                        "work_unit": "words",
                        "work_completed": 52221,
                        "work_total": 84986,
                        "predicate_atom_count": 6179,
                        "signal_atom_count": 178658,
                        "provenance_ref_count": 197195,
                    },
                },
            },
            "last_partial_ref": "/tmp/feed.partial.json",
        },
    )

    assert result["ok"] is True
    payload = result["result"]
    assert payload["state"] == "partial"
    assert payload["can_resume"] is True
    assert payload["work_unit"] == "words"
    assert payload["work_completed"] == 52221
    assert payload["work_total"] == 84986
    assert payload["last_partial_ref"] == "/tmp/feed.partial.json"


def test_obligations_query_returns_deterministic_payload() -> None:
    registry = build_default_registry()
    result = registry.invoke(
        "sensiblaw.obligations_query",
        {
            "text": "The tenant must pay rent on time.",
            "source_id": "demo",
        },
    )
    assert result["ok"] is True
    payload = result["result"]
    assert payload["version"] == "obligation.query.v1"
    assert payload["results"]
    assert payload["results"][0]["modality"] == "must"


def test_unknown_tool_returns_contract_error() -> None:
    registry = build_default_registry()
    result = registry.invoke("sensiblaw.unknown_tool", {"text": "abc"})

    assert result["ok"] is False
    assert result["error"]["code"] == "tool_error"
    assert "Unknown tool" in result["error"]["message"]
