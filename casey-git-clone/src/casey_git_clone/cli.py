"""Minimal CLI for the Casey local testbed."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Iterable

from .export import export_casey_facts
from .models import BuildView, WorkspaceView
from .operations import build_snapshot, collapse_conflict, publish_edits, sync_workspace
from .runtime_sqlite import (
    create_workspace,
    initialize_runtime,
    load_build,
    load_current_tree,
    load_current_tree_conn,
    load_file_versions,
    load_file_versions_conn,
    load_workspace,
    load_workspace_conn,
    runtime_transaction,
    save_build,
    save_build_conn,
    save_workspace,
    save_workspace_conn,
    set_current_tree_id,
    set_current_tree_id_conn,
    store_publish_result,
    store_publish_result_conn,
)


def _candidate_ids_for_tree(tree) -> set[str]:
    return {fv_id for state in tree.paths.values() for fv_id in state.candidates}


def _default_ledger_db_path(runtime_db_path: Path) -> Path:
    return runtime_db_path.with_name("casey_ledgers.sqlite")


def _default_observer_out_root(runtime_db_path: Path) -> Path:
    return runtime_db_path.parent / "artifacts" / "casey" / "runs"


def _observer_provenance(*, command: str, runtime_db_path: Path) -> dict[str, Any]:
    return {
        "source": "casey-git-clone",
        "command": command,
        "runtime_db": str(runtime_db_path),
    }


def _attach_observer(
    *,
    args: argparse.Namespace,
    payload: dict[str, Any],
    command: str,
    workspace: WorkspaceView | None,
    operation,
    build: BuildView | None = None,
) -> dict[str, Any]:
    if getattr(args, "no_observer", False):
        return payload
    from .receipts import emit_runtime_observer_artifacts

    observer = emit_runtime_observer_artifacts(
        ledger_db_path=args.ledger_db or _default_ledger_db_path(args.db),
        workspace=workspace,
        operation=operation,
        build=build,
        provenance=_observer_provenance(command=command, runtime_db_path=args.db),
        bundle_out_root=args.observer_out_root or _default_observer_out_root(args.db),
        sb_db_path=args.sb_db,
    )
    payload["observer"] = observer
    return payload


def _print_observer_summary(observer: dict[str, Any]) -> None:
    print(f"Observer bundle: {observer['bundle_dir']}")
    print(f"Operation receipt: {observer['operation_id']}")
    if observer.get("build_id"):
        print(f"Build receipt: {observer['build_id']}")
    if observer["sb_ingested"]:
        print(f"StatiBaker ingest: {observer['sb_db_path']}")


def _render(payload: dict[str, Any], as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return

    kind = payload["kind"]
    if kind == "init":
        print(f"Initialized Casey runtime at {payload['db_path']}")
        print(f"Current tree: {payload['tree_id']}")
        print(
            f"Workspace {payload['workspace']['ws_id']} "
            f"(user {payload['workspace']['user']}) head {payload['workspace']['head']}"
        )
        return
    if kind == "workspace_create":
        print(
            f"Created workspace {payload['workspace']['ws_id']} "
            f"(user {payload['workspace']['user']}) at tree {payload['workspace']['head']}"
        )
        return
    if kind == "publish":
        print(
            f"Published {payload['path']} via workspace {payload['workspace']['ws_id']} "
            f"as {payload['new_fv_id']}"
        )
        print(f"Current tree: {payload['tree_id']}")
        print(f"Candidates for {payload['path']}: {', '.join(payload['candidates'])}")
        print(f"Workspace selection: {payload['workspace_selection']}")
        _print_observer_summary(payload["observer"])
        return
    if kind == "sync":
        print(
            f"Synced workspace {payload['workspace']['ws_id']} "
            f"to tree {payload['workspace']['head']}"
        )
        _print_selection(payload["workspace"]["selection"])
        _print_observer_summary(payload["observer"])
        return
    if kind == "show_tree":
        print(f"Current tree: {payload['tree_id']}")
        if not payload["paths"]:
            print("(empty)")
            return
        for entry in payload["paths"]:
            print(f"{entry['path']}: {', '.join(entry['candidates'])}")
        return
    if kind == "show_workspace":
        print(
            f"Workspace {payload['workspace']['ws_id']} "
            f"(user {payload['workspace']['user']}) head {payload['workspace']['head']}"
        )
        _print_selection(payload["workspace"]["selection"])
        return
    if kind == "collapse":
        print(
            f"Collapsed {payload['path']} in workspace {payload['workspace']['ws_id']} "
            f"to {payload['resolved_fv_id']}"
        )
        print(f"Current tree: {payload['tree_id']}")
        print(f"Candidates for {payload['path']}: {', '.join(payload['candidates'])}")
        _print_observer_summary(payload["observer"])
        return
    if kind == "build":
        print(
            f"Build {payload['build']['build_id']} from workspace {payload['workspace']['ws_id']} "
            f"tree {payload['build']['tree_id']}"
        )
        _print_selection(payload["build"]["selection"])
        _print_observer_summary(payload["observer"])
        return
    if kind == "export":
        print(
            f"Exported Casey facts for workspace {payload['workspace']['ws_id']} "
            f"at tree {payload['tree_id']}"
        )
        print(f"Paths: {len(payload['paths'])}")
        if payload["build"] is not None:
            print(f"Build context: {payload['build']['build_id']}")
        return
    if kind == "advisory":
        print(
            f"Advisory for workspace {payload['workspace_id']} "
            f"at tree {payload['tree_id']}"
        )
        for result in payload["path_results"]:
            print(
                f"{result['path']}: recommend {result['recommended_fv_id']} "
                f"gap={result['gap']['gap_kind']}/{result['gap']['severity']}"
            )
        return
    raise ValueError(f"Unsupported payload kind: {kind}")


def _print_selection(selection: MappingLike) -> None:
    if not selection:
        print("(no selections)")
        return
    for path in sorted(selection):
        print(f"{path}: {selection[path]}")


MappingLike = dict[str, str]


def _workspace_payload(workspace: WorkspaceView) -> dict[str, Any]:
    return {
        "ws_id": workspace.ws_id,
        "user": workspace.user,
        "head": workspace.head,
        "selection": dict(sorted(workspace.selection.items())),
        "policy": {
            "prefer_author": workspace.policy.prefer_author,
            "tie_break": workspace.policy.tie_break,
        },
    }


def _build_payload(build: BuildView) -> dict[str, Any]:
    return {
        "build_id": build.build_id,
        "tree_id": build.tree_id,
        "created_at": build.created_at,
        "selection": dict(sorted(build.selection.items())),
    }


def cmd_init(args: argparse.Namespace) -> dict[str, Any]:
    workspace = initialize_runtime(
        db_path=args.db,
        ws_id=args.workspace,
        user=args.user or args.workspace,
        prefer_author=args.prefer_author,
        tie_break=args.tie_break,
    )
    return {
        "kind": "init",
        "db_path": str(args.db),
        "tree_id": workspace.head,
        "workspace": _workspace_payload(workspace),
    }


def cmd_workspace_create(args: argparse.Namespace) -> dict[str, Any]:
    workspace = create_workspace(
        db_path=args.db,
        ws_id=args.workspace,
        user=args.user or args.workspace,
        prefer_author=args.prefer_author,
        tie_break=args.tie_break,
    )
    return {
        "kind": "workspace_create",
        "workspace": _workspace_payload(workspace),
    }


def cmd_publish(args: argparse.Namespace) -> dict[str, Any]:
    with runtime_transaction(db_path=args.db) as conn:
        tree = load_current_tree_conn(conn=conn)
        workspace = load_workspace_conn(conn=conn, ws_id=args.workspace)
        author = args.author or workspace.user
        result = publish_edits(
            tree_state=tree,
            workspace=workspace,
            edits={args.path: args.content},
            author=author,
        )
        store_publish_result_conn(
            conn=conn,
            blobs=result.blobs,
            file_versions=result.file_versions,
            tree_state=result.tree_state,
        )
        set_current_tree_id_conn(conn=conn, tree_id=result.tree_state.tree_id)
        file_versions = load_file_versions_conn(
            conn=conn,
            fv_ids=_candidate_ids_for_tree(result.tree_state),
        )
        updated = sync_workspace(
            workspace=workspace,
            tree_state=result.tree_state,
            file_versions=file_versions,
        )
        new_fv_id = next(iter(result.file_versions))
        updated.selection[args.path] = new_fv_id
        updated.head = result.tree_state.tree_id
        updated.validate_against(result.tree_state.paths)
        save_workspace_conn(conn=conn, workspace=updated)
    payload = {
        "kind": "publish",
        "workspace": _workspace_payload(updated),
        "path": args.path,
        "new_fv_id": new_fv_id,
        "tree_id": result.tree_state.tree_id,
        "candidates": list(result.tree_state.paths[args.path].candidates),
        "workspace_selection": updated.selection[args.path],
    }
    operation = None
    if not args.no_observer:
        from .receipts import operation_record

        operation = operation_record(
            operation_kind="publish",
            workspace=updated,
            path=args.path,
            tree_id_before=tree.tree_id,
            tree_id_after=result.tree_state.tree_id,
            chosen_fv_id=workspace.selection.get(args.path),
            resolved_fv_id=new_fv_id,
            actor=author,
        )
    return _attach_observer(
        args=args,
        payload=payload,
        command="publish",
        workspace=updated,
        operation=operation,
    )


def cmd_sync(args: argparse.Namespace) -> dict[str, Any]:
    with runtime_transaction(db_path=args.db) as conn:
        tree = load_current_tree_conn(conn=conn)
        workspace = load_workspace_conn(conn=conn, ws_id=args.workspace)
        file_versions = load_file_versions_conn(
            conn=conn,
            fv_ids=_candidate_ids_for_tree(tree),
        )
        updated = sync_workspace(
            workspace=workspace,
            tree_state=tree,
            file_versions=file_versions,
        )
        save_workspace_conn(conn=conn, workspace=updated)
    payload = {
        "kind": "sync",
        "workspace": _workspace_payload(updated),
    }
    operation = None
    if not args.no_observer:
        from .receipts import operation_record

        operation = operation_record(
            operation_kind="sync",
            workspace=updated,
            tree_id_before=workspace.head,
            tree_id_after=updated.head,
            actor=workspace.user,
        )
    return _attach_observer(
        args=args,
        payload=payload,
        command="sync",
        workspace=updated,
        operation=operation,
    )


def cmd_show_tree(args: argparse.Namespace) -> dict[str, Any]:
    tree = load_current_tree(db_path=args.db)
    return {
        "kind": "show_tree",
        "tree_id": tree.tree_id,
        "paths": [
            {"path": path, "candidates": list(tree.paths[path].candidates)}
            for path in sorted(tree.paths)
        ],
    }


def cmd_show_workspace(args: argparse.Namespace) -> dict[str, Any]:
    workspace = load_workspace(db_path=args.db, ws_id=args.workspace)
    return {
        "kind": "show_workspace",
        "workspace": _workspace_payload(workspace),
    }


def cmd_collapse(args: argparse.Namespace) -> dict[str, Any]:
    with runtime_transaction(db_path=args.db) as conn:
        tree = load_current_tree_conn(conn=conn)
        workspace = load_workspace_conn(conn=conn, ws_id=args.workspace)
        file_versions = load_file_versions_conn(
            conn=conn,
            fv_ids=_candidate_ids_for_tree(tree),
        )
        result = collapse_conflict(
            tree_state=tree,
            path=args.path,
            author=args.author or workspace.user,
            file_versions=file_versions,
            chosen_fv_id=args.choose,
            merged_content=args.merged_content,
        )
        store_publish_result_conn(
            conn=conn,
            blobs=result.blobs,
            file_versions=result.file_versions,
            tree_state=result.tree_state,
        )
        set_current_tree_id_conn(conn=conn, tree_id=result.tree_state.tree_id)
        resolved_fv_id = result.tree_state.paths[args.path].candidates[0]
        updated = WorkspaceView(
            ws_id=workspace.ws_id,
            user=workspace.user,
            head=result.tree_state.tree_id,
            selection=dict(workspace.selection),
            policy=workspace.policy,
        )
        updated.selection[args.path] = resolved_fv_id
        updated.validate_against(result.tree_state.paths)
        save_workspace_conn(conn=conn, workspace=updated)
    payload = {
        "kind": "collapse",
        "workspace": _workspace_payload(updated),
        "path": args.path,
        "resolved_fv_id": resolved_fv_id,
        "tree_id": result.tree_state.tree_id,
        "candidates": list(result.tree_state.paths[args.path].candidates),
    }
    operation = None
    if not args.no_observer:
        from .receipts import operation_record

        operation = operation_record(
            operation_kind="collapse",
            workspace=updated,
            path=args.path,
            tree_id_before=tree.tree_id,
            tree_id_after=result.tree_state.tree_id,
            chosen_fv_id=args.choose,
            resolved_fv_id=resolved_fv_id,
            actor=args.author or workspace.user,
        )
    return _attach_observer(
        args=args,
        payload=payload,
        command="collapse",
        workspace=updated,
        operation=operation,
    )


def cmd_build(args: argparse.Namespace) -> dict[str, Any]:
    with runtime_transaction(db_path=args.db) as conn:
        tree = load_current_tree_conn(conn=conn)
        workspace = load_workspace_conn(conn=conn, ws_id=args.workspace)
        file_versions = load_file_versions_conn(
            conn=conn,
            fv_ids=_candidate_ids_for_tree(tree),
        )
        build = build_snapshot(
            workspace=workspace,
            tree_state=tree,
            file_versions=file_versions,
        )
        save_build_conn(conn=conn, build=build)
    payload = {
        "kind": "build",
        "workspace": _workspace_payload(workspace),
        "build": _build_payload(build),
    }
    operation = None
    if not args.no_observer:
        from .receipts import operation_record

        operation = operation_record(
            operation_kind="build",
            workspace=workspace,
            tree_id_before=workspace.head,
            tree_id_after=build.tree_id,
            actor=workspace.user,
        )
    return _attach_observer(
        args=args,
        payload=payload,
        command="build",
        workspace=workspace,
        operation=operation,
        build=build,
    )


def cmd_export(args: argparse.Namespace) -> dict[str, Any]:
    payload = export_casey_facts(
        db_path=args.db,
        workspace_id=args.workspace,
        tree_id=args.tree_id,
        build_id=args.build_id,
    )
    payload["kind"] = "export"
    return payload


def _load_casey_advisory_evaluator():
    try:
        from selector_dsl.casey_adapter import evaluate_casey_export
    except ModuleNotFoundError:
        repo_root = Path(__file__).resolve().parents[3]
        fuzzymodo_src = repo_root / "fuzzymodo" / "src"
        if str(fuzzymodo_src) not in sys.path:
            sys.path.insert(0, str(fuzzymodo_src))
        from selector_dsl.casey_adapter import evaluate_casey_export
    return evaluate_casey_export


def cmd_advise(args: argparse.Namespace) -> dict[str, Any]:
    evaluator = _load_casey_advisory_evaluator()
    export_payload = export_casey_facts(
        db_path=args.db,
        workspace_id=args.workspace,
        tree_id=args.tree_id,
        build_id=args.build_id,
    )
    advisory = evaluator(export_payload, evaluated_at=args.evaluated_at)
    advisory["kind"] = "advisory"
    return advisory


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="casey")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser("init")
    init.add_argument("--db", type=Path, required=True)
    init.add_argument("--workspace", required=True)
    init.add_argument("--user")
    init.add_argument("--prefer-author")
    init.add_argument("--tie-break", default="stable_hash")
    init.set_defaults(func=cmd_init)

    workspace = subparsers.add_parser("workspace")
    workspace_sub = workspace.add_subparsers(dest="workspace_command", required=True)
    workspace_create = workspace_sub.add_parser("create")
    workspace_create.add_argument("--db", type=Path, required=True)
    workspace_create.add_argument("--workspace", required=True)
    workspace_create.add_argument("--user")
    workspace_create.add_argument("--prefer-author")
    workspace_create.add_argument("--tie-break", default="stable_hash")
    workspace_create.set_defaults(func=cmd_workspace_create)

    publish = subparsers.add_parser("publish")
    publish.add_argument("--db", type=Path, required=True)
    publish.add_argument("--workspace", required=True)
    publish.add_argument("--path", required=True)
    publish.add_argument("--content", required=True)
    publish.add_argument("--author")
    publish.add_argument("--no-observer", action="store_true")
    publish.add_argument("--ledger-db", type=Path)
    publish.add_argument("--sb-db", type=Path)
    publish.add_argument("--observer-out-root", type=Path)
    publish.set_defaults(func=cmd_publish)

    sync = subparsers.add_parser("sync")
    sync.add_argument("--db", type=Path, required=True)
    sync.add_argument("--workspace", required=True)
    sync.add_argument("--no-observer", action="store_true")
    sync.add_argument("--ledger-db", type=Path)
    sync.add_argument("--sb-db", type=Path)
    sync.add_argument("--observer-out-root", type=Path)
    sync.set_defaults(func=cmd_sync)

    show = subparsers.add_parser("show")
    show_sub = show.add_subparsers(dest="show_command", required=True)
    show_tree = show_sub.add_parser("tree")
    show_tree.add_argument("--db", type=Path, required=True)
    show_tree.set_defaults(func=cmd_show_tree)
    show_workspace = show_sub.add_parser("workspace")
    show_workspace.add_argument("--db", type=Path, required=True)
    show_workspace.add_argument("--workspace", required=True)
    show_workspace.set_defaults(func=cmd_show_workspace)

    collapse = subparsers.add_parser("collapse")
    collapse.add_argument("--db", type=Path, required=True)
    collapse.add_argument("--workspace", required=True)
    collapse.add_argument("--path", required=True)
    collapse.add_argument("--choose")
    collapse.add_argument("--merged-content")
    collapse.add_argument("--author")
    collapse.add_argument("--no-observer", action="store_true")
    collapse.add_argument("--ledger-db", type=Path)
    collapse.add_argument("--sb-db", type=Path)
    collapse.add_argument("--observer-out-root", type=Path)
    collapse.set_defaults(func=cmd_collapse)

    build = subparsers.add_parser("build")
    build.add_argument("--db", type=Path, required=True)
    build.add_argument("--workspace", required=True)
    build.add_argument("--no-observer", action="store_true")
    build.add_argument("--ledger-db", type=Path)
    build.add_argument("--sb-db", type=Path)
    build.add_argument("--observer-out-root", type=Path)
    build.set_defaults(func=cmd_build)

    export = subparsers.add_parser("export")
    export.add_argument("--db", type=Path, required=True)
    export.add_argument("--workspace", required=True)
    export.add_argument("--tree-id")
    export.add_argument("--build-id")
    export.set_defaults(func=cmd_export)

    advise = subparsers.add_parser("advise")
    advise.add_argument("--db", type=Path, required=True)
    advise.add_argument("--workspace", required=True)
    advise.add_argument("--tree-id")
    advise.add_argument("--build-id")
    advise.add_argument("--evaluated-at")
    advise.set_defaults(func=cmd_advise)

    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    if getattr(args, "command", None) == "collapse" and not (args.choose or args.merged_content):
        parser.error("collapse requires --choose or --merged-content")
    payload = args.func(args)
    _render(payload, args.json)
    return 0
