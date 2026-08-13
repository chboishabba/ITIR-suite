from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from casey_git_clone.cli import main  # noqa: E402
from casey_git_clone.export import export_casey_facts  # noqa: E402


def test_export_casey_facts_preserves_candidate_multiplicity() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "casey_runtime.sqlite"
        main(["init", "--db", str(db_path), "--workspace", "alice"])
        main(["workspace", "create", "--db", str(db_path), "--workspace", "bob"])
        main(
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
        main(["sync", "--db", str(db_path), "--workspace", "bob"])
        main(
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
        main(
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

        payload = export_casey_facts(db_path=db_path, workspace_id="alice")

    assert payload["casey_export_version"] == "casey.facts.v1"
    assert payload["workspace"]["ws_id"] == "alice"
    assert payload["workspace"]["head_tree_id"] != payload["tree_id"]
    assert payload["workspace"]["policy"]["prefer_author"] == "alice"
    assert payload["build"] is None
    assert len(payload["paths"]) == 1

    path_entry = payload["paths"][0]
    assert path_entry["path"] == "src/main.c"
    assert path_entry["candidate_count"] == 2
    assert len(path_entry["candidates"]) == 2
    assert path_entry["selected_fv_id"] in {c["fv_id"] for c in path_entry["candidates"]}
    assert {candidate["author"] for candidate in path_entry["candidates"]} == {"alice", "bob"}
    assert all(candidate["features"]["_version"] == "casey.features.v1" for candidate in path_entry["candidates"])
    assert all("derived.has_lineage" in candidate["features"] for candidate in path_entry["candidates"])
