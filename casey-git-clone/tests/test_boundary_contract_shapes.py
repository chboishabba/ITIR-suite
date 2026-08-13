from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT.parent / "fuzzymodo" / "src"))

from casey_git_clone.cli import main as casey_main  # noqa: E402
from casey_git_clone.export import export_casey_facts  # noqa: E402
from selector_dsl.casey_adapter import evaluate_casey_export  # noqa: E402


def test_casey_facts_and_advisory_contract_shapes() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "casey_runtime.sqlite"

        assert casey_main(["init", "--db", str(db_path), "--workspace", "alice"]) == 0
        assert casey_main(["workspace", "create", "--db", str(db_path), "--workspace", "bob"]) == 0

        assert (
            casey_main(
                [
                    "publish",
                    "--db",
                    str(db_path),
                    "--workspace",
                    "alice",
                    "--path",
                    "src/main.c",
                    "--content",
                    "base",
                ]
            )
            == 0
        )
        assert casey_main(["sync", "--db", str(db_path), "--workspace", "bob"]) == 0
        assert (
            casey_main(
                [
                    "publish",
                    "--db",
                    str(db_path),
                    "--workspace",
                    "alice",
                    "--path",
                    "src/main.c",
                    "--content",
                    "alice-edit",
                ]
            )
            == 0
        )
        assert (
            casey_main(
                [
                    "publish",
                    "--db",
                    str(db_path),
                    "--workspace",
                    "bob",
                    "--path",
                    "src/main.c",
                    "--content",
                    "bob-edit",
                ]
            )
            == 0
        )

        export_payload = export_casey_facts(db_path=db_path, workspace_id="alice")
        advisory = evaluate_casey_export(export_payload, evaluated_at="2026-03-26T10:00:00Z")

    assert export_payload["casey_export_version"] == "casey.facts.v1"
    assert export_payload["tree_id"]
    workspace = export_payload["workspace"]
    assert workspace["ws_id"] == "alice"
    assert workspace["policy"]["tie_break"]
    assert isinstance(workspace["selection"], list)
    path_entry = export_payload["paths"][0]
    assert path_entry["candidate_count"] == len(path_entry["candidates"])
    assert path_entry["candidate_count"] == 2
    for candidate in path_entry["candidates"]:
        assert candidate["features"]["_version"] == "casey.features.v1"

    assert advisory["fuzzymodo_result_version"] == "fuzzymodo.casey.advisory.v1"
    assert advisory["workspace_id"] == "alice"
    assert advisory["path_results"] and len(advisory["path_results"]) == 1

    result = advisory["path_results"][0]
    assert result["path"] == "src/main.c"
    assert "candidate_rankings" in result
    assert result["candidate_rankings"]
    assert result["gap"]["gap_kind"] == "candidate_divergence"
    assert result["gap"]["primary_axis"] in {"author", "lineage", "feature_context", "selection", "candidate_count"}
    assert result["gap"]["gap_items"]
    assert result["gap"]["suggested_actions"]
    assert advisory["evaluation_digest"]
    assert advisory == evaluate_casey_export(export_payload, evaluated_at="2026-03-26T10:00:00Z")
