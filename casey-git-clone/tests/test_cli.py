from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from casey_git_clone.cli import main  # noqa: E402
from casey_git_clone.runtime_sqlite import load_build, load_current_tree, load_workspace  # noqa: E402


def test_cli_alice_bob_conflict_flow(capsys) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "casey_runtime.sqlite"

        assert main(["init", "--db", str(db_path), "--workspace", "alice"]) == 0
        assert main(["workspace", "create", "--db", str(db_path), "--workspace", "bob"]) == 0

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
        main(["show", "tree", "--db", str(db_path)])
        tree_output = capsys.readouterr().out
        assert "Current tree:" in tree_output
        assert "src/main.c:" in tree_output

        tree = load_current_tree(db_path=db_path)
        candidates = tree.paths["src/main.c"].candidates
        assert len(candidates) == 2

        bob_before_sync = load_workspace(db_path=db_path, ws_id="bob")
        alice_before_sync = load_workspace(db_path=db_path, ws_id="alice")
        assert bob_before_sync.selection["src/main.c"] != alice_before_sync.selection["src/main.c"]

        main(["sync", "--db", str(db_path), "--workspace", "alice"])
        alice_synced = load_workspace(db_path=db_path, ws_id="alice")
        chosen = alice_synced.selection["src/main.c"]

        main(
            [
                "collapse",
                "--db",
                str(db_path),
                "--workspace",
                "alice",
                "--path",
                "src/main.c",
                "--choose",
                chosen,
            ]
        )
        collapsed_tree = load_current_tree(db_path=db_path)
        assert collapsed_tree.paths["src/main.c"].candidates == [chosen]
        capsys.readouterr()

        main(["--json", "build", "--db", str(db_path), "--workspace", "alice"])
        build_output = capsys.readouterr().out
        payload = json.loads(build_output)
        build_id = payload["build"]["build_id"]
        stored = load_build(db_path=db_path, build_id=build_id)
        assert stored.selection["src/main.c"] == chosen


def test_cli_export_json(capsys) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "casey_runtime.sqlite"

        assert main(["init", "--db", str(db_path), "--workspace", "alice"]) == 0
        assert (
            main(
                [
                    "publish",
                    "--db",
                    str(db_path),
                    "--workspace",
                    "alice",
                    "--path",
                    "README.md",
                    "--content",
                    "hello",
                ]
            )
            == 0
        )
        capsys.readouterr()
        assert main(["--json", "export", "--db", str(db_path), "--workspace", "alice"]) == 0

        payload = json.loads(capsys.readouterr().out)

    assert payload["kind"] == "export"
    assert payload["casey_export_version"] == "casey.facts.v1"
    assert payload["workspace"]["ws_id"] == "alice"
    assert payload["paths"][0]["path"] == "README.md"


def test_cli_advise_json(capsys) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "casey_runtime.sqlite"

        assert main(["init", "--db", str(db_path), "--workspace", "alice"]) == 0
        assert main(["workspace", "create", "--db", str(db_path), "--workspace", "bob"]) == 0
        assert (
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
            == 0
        )
        assert main(["sync", "--db", str(db_path), "--workspace", "bob"]) == 0
        assert (
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
            == 0
        )
        assert (
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
            == 0
        )
        capsys.readouterr()
        assert (
            main(
                [
                    "--json",
                    "advise",
                    "--db",
                    str(db_path),
                    "--workspace",
                    "alice",
                    "--evaluated-at",
                    "2026-03-19T14:00:00Z",
                ]
            )
            == 0
        )
        payload = json.loads(capsys.readouterr().out)

    assert payload["kind"] == "advisory"
    assert payload["fuzzymodo_result_version"] == "fuzzymodo.casey.advisory.v1"
    assert payload["path_results"][0]["gap"]["gap_kind"] == "candidate_divergence"
