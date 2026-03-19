#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import sqlite3
import statistics
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_THIS_DIR = Path(__file__).resolve().parent
_CASEY_ROOT = _THIS_DIR.parent
_SRC_ROOT = _CASEY_ROOT / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from casey_git_clone.models import WorkspaceView
from casey_git_clone.operations import build_snapshot, publish_edits, sync_workspace
from casey_git_clone.receipts import emit_runtime_observer_artifacts, operation_record
from casey_git_clone.runtime_sqlite import (
    create_workspace,
    initialize_runtime,
    load_current_tree,
    load_file_versions,
    load_workspace,
    save_build,
    save_workspace,
    set_current_tree_id,
    store_publish_result,
)


@dataclass(frozen=True)
class TierSpec:
    name: str
    ballast_files: int
    ballast_bytes: int
    update_bytes: int


TIERS: dict[str, TierSpec] = {
    "small": TierSpec(name="small", ballast_files=4, ballast_bytes=256, update_bytes=512),
    "medium": TierSpec(name="medium", ballast_files=16, ballast_bytes=2048, update_bytes=4096),
    "large": TierSpec(name="large", ballast_files=64, ballast_bytes=8192, update_bytes=16384),
}

LANES = ("baseline_linear", "divergence_native", "build_freeze", "traceability_cost")
SURFACES = ("cli", "library")


def _content(label: str, size: int) -> str:
    seed = (label + "|").encode("utf-8")
    repeated = (seed * ((size // len(seed)) + 1))[:size]
    return repeated.decode("utf-8", errors="ignore")


def _seed_files(spec: TierSpec) -> dict[str, str]:
    payload = {}
    for index in range(spec.ballast_files):
        payload[f"tree/file_{index:03d}.txt"] = _content(f"{spec.name}:ballast:{index}", spec.ballast_bytes)
    payload["src/main.txt"] = _content(f"{spec.name}:main:base", spec.ballast_bytes)
    return payload


def _updated_content(spec: TierSpec, label: str) -> str:
    return _content(f"{spec.name}:{label}", spec.update_bytes)


def _write_payload_tree(root: Path, files: dict[str, str]) -> int:
    total = 0
    for rel_path, content in files.items():
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        total += len(content.encode("utf-8"))
    return total


def _dir_size(path: Path) -> int:
    if not path.exists():
        return 0
    if path.is_file():
        return path.stat().st_size
    total = 0
    for child in path.rglob("*"):
        if child.is_file():
            total += child.stat().st_size
    return total


def _file_sizes_by_name(path: Path) -> dict[str, int]:
    out: dict[str, int] = {}
    if not path.exists():
        return out
    for child in path.rglob("*"):
        if child.is_file():
            out[child.name] = out.get(child.name, 0) + child.stat().st_size
    return out


def _working_tree_bytes(root: Path) -> int:
    total = 0
    for child in root.rglob("*"):
        if child.is_file() and ".git" not in child.parts:
            total += child.stat().st_size
    return total


def _sqlite_metrics(path: Path, tables: list[str]) -> dict[str, Any]:
    if not path.exists():
        return {
            "exists": False,
            "total_bytes": 0,
            "page_count": 0,
            "page_size": 0,
            "row_counts": {table: 0 for table in tables},
        }
    with sqlite3.connect(str(path)) as conn:
        page_count = int(conn.execute("PRAGMA page_count").fetchone()[0])
        page_size = int(conn.execute("PRAGMA page_size").fetchone()[0])
        row_counts = {}
        for table in tables:
            exists = conn.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name = ?",
                (table,),
            ).fetchone()
            row_counts[table] = int(conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]) if exists else 0
    return {
        "exists": True,
        "total_bytes": path.stat().st_size,
        "page_count": page_count,
        "page_size": page_size,
        "row_counts": row_counts,
    }


def _git_count_objects(repo: Path) -> dict[str, int]:
    proc = subprocess.run(
        ["git", "count-objects", "-v"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    out: dict[str, int] = {}
    for line in proc.stdout.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        try:
            out[key.strip()] = int(value.strip())
        except ValueError:
            continue
    return out


def _markdown_table(results: list[dict[str, Any]]) -> str:
    lines = [
        "| tier | lane | surface | casey median ms | git median ms | casey persisted delta | git persisted delta | verdict |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in results:
        lines.append(
            "| {tier} | {lane} | {surface} | {casey_ms:.3f} | {git_ms:.3f} | {casey_bytes} | {git_bytes} | {verdict} |".format(
                tier=row["tier"],
                lane=row["lane"],
                surface=row["surface"],
                casey_ms=row["casey"]["elapsed_ms"]["median"],
                git_ms=row["git"]["elapsed_ms"]["median"],
                casey_bytes=row["casey"]["persisted_bytes_delta"]["median"],
                git_bytes=row["git"]["persisted_bytes_delta"]["median"],
                verdict=row["verdict"],
            )
        )
    return "\n".join(lines)


def _median(values: list[float | int]) -> float:
    return float(statistics.median(values)) if values else 0.0


def _aggregate_numeric(samples: list[dict[str, Any]], key: str) -> dict[str, float]:
    values = [float(sample[key]) for sample in samples]
    return {
        "min": min(values),
        "median": _median(values),
        "max": max(values),
    }


def _compute_ratio(numerator: float, denominator: float) -> float | None:
    if denominator <= 0:
        return None
    return round(numerator / denominator, 6)


def _casey_snapshot(runtime_db: Path, ledger_db: Path, bundle_root: Path) -> dict[str, Any]:
    runtime = _sqlite_metrics(
        runtime_db,
        [
            "casey_runtime_blobs",
            "casey_runtime_file_versions",
            "casey_runtime_trees",
            "casey_runtime_tree_candidates",
            "casey_runtime_workspaces",
            "casey_runtime_workspace_selections",
            "casey_runtime_builds",
            "casey_runtime_build_selections",
        ],
    )
    ledger = _sqlite_metrics(
        ledger_db,
        ["casey_operation_ledger", "casey_build_ledger", "casey_build_selection_refs"],
    )
    bundle_total = _dir_size(bundle_root)
    bundle_files = _file_sizes_by_name(bundle_root)
    return {
        "runtime": runtime,
        "ledger": ledger,
        "bundle_total_bytes": bundle_total,
        "bundle_file_sizes": bundle_files,
        "bundle_file_count": len(bundle_files),
    }


def _git_snapshot(repo: Path, trace_root: Path) -> dict[str, Any]:
    git_dir = repo / ".git"
    trace_total = _dir_size(trace_root)
    trace_files = _file_sizes_by_name(trace_root)
    return {
        "git_dir_total_bytes": _dir_size(git_dir),
        "git_object_counts": _git_count_objects(repo),
        "working_tree_bytes": _working_tree_bytes(repo),
        "trace_total_bytes": trace_total,
        "trace_file_sizes": trace_files,
        "trace_file_count": len(trace_files),
    }


def _run_git(repo: Path, args: list[str]) -> str:
    proc = subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)
    return proc.stdout.strip()


def _setup_git_repo(root: Path, spec: TierSpec) -> tuple[Path, dict[str, str]]:
    repo = root / "git_repo"
    repo.mkdir(parents=True, exist_ok=True)
    _run_git(repo, ["init"])
    _run_git(repo, ["config", "user.name", "Casey Bench"])
    _run_git(repo, ["config", "user.email", "bench@example.com"])
    files = _seed_files(spec)
    _write_payload_tree(repo, files)
    return repo, files


def _setup_casey_runtime_paths(root: Path) -> tuple[Path, Path, Path]:
    runtime_db = root / "casey_runtime.sqlite"
    ledger_db = root / "casey_ledgers.sqlite"
    bundle_root = root / "artifacts" / "casey" / "runs"
    return runtime_db, ledger_db, bundle_root


def _run_casey_cli(root: Path, argv: list[str]) -> dict[str, Any]:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(_SRC_ROOT)
    proc = subprocess.run(
        [sys.executable, "-m", "casey_git_clone", "--json", *argv],
        cwd=root,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(proc.stdout)


def _casey_cli_receipt_args(command: str, ledger_db: Path, bundle_root: Path) -> list[str]:
    if command not in {"publish", "sync", "collapse", "build"}:
        return []
    return ["--ledger-db", str(ledger_db), "--observer-out-root", str(bundle_root)]


def _casey_cli_lane_args(lane: str, command: str, ledger_db: Path, bundle_root: Path) -> list[str]:
    if command not in {"publish", "sync", "collapse", "build"}:
        return []
    if lane != "traceability_cost":
        return ["--no-observer"]
    return _casey_cli_receipt_args(command, ledger_db, bundle_root)


def _clear_observer_state(ledger_db: Path, bundle_root: Path) -> None:
    if ledger_db.exists():
        ledger_db.unlink()
    if bundle_root.exists():
        shutil.rmtree(bundle_root)


def _emit_git_trace_bundle(trace_root: Path, payload: dict[str, Any]) -> None:
    trace_root.mkdir(parents=True, exist_ok=True)
    (trace_root / "operation.json").write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    (trace_root / "meta.json").write_text(
        json.dumps({"kind": "git_trace_v1", "commit": payload.get("commit")}, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n",
        encoding="utf-8",
    )


def _casey_lane_cli(spec: TierSpec, lane: str) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix=f"casey-bench-{lane}-cli-") as tmp:
        root = Path(tmp)
        runtime_db, ledger_db, bundle_root = _setup_casey_runtime_paths(root)
        command_count = 0

        def run(argv: list[str]) -> dict[str, Any]:
            nonlocal command_count
            command_count += 1
            command = argv[0]
            return _run_casey_cli(
                _CASEY_ROOT,
                argv + _casey_cli_lane_args(lane, command, ledger_db, bundle_root),
            )

        run(["init", "--db", str(runtime_db), "--workspace", "alice"])
        if lane == "divergence_native":
            run(["workspace", "create", "--db", str(runtime_db), "--workspace", "bob"])

        files = _seed_files(spec)
        for path, content in files.items():
            run(["publish", "--db", str(runtime_db), "--workspace", "alice", "--path", path, "--content", content])

        if lane == "divergence_native":
            run(["sync", "--db", str(runtime_db), "--workspace", "bob"])

        logical_bytes = len(_updated_content(spec, lane).encode("utf-8"))
        _clear_observer_state(ledger_db, bundle_root)
        before = _casey_snapshot(runtime_db, ledger_db, bundle_root)
        command_count = 0
        start = time.perf_counter()

        if lane == "baseline_linear":
            run(["publish", "--db", str(runtime_db), "--workspace", "alice", "--path", "src/main.txt", "--content", _updated_content(spec, "baseline")])
        elif lane == "divergence_native":
            run(["publish", "--db", str(runtime_db), "--workspace", "alice", "--path", "src/main.txt", "--content", _updated_content(spec, "alice-edit")])
            run(["publish", "--db", str(runtime_db), "--workspace", "bob", "--path", "src/main.txt", "--content", _updated_content(spec, "bob-edit")])
            logical_bytes = len(_updated_content(spec, "alice-edit").encode("utf-8")) + len(
                _updated_content(spec, "bob-edit").encode("utf-8")
            )
        elif lane == "build_freeze":
            run(["build", "--db", str(runtime_db), "--workspace", "alice"])
            logical_bytes = 0
        elif lane == "traceability_cost":
            run(
                [
                    "publish",
                    "--db",
                    str(runtime_db),
                    "--workspace",
                    "alice",
                    "--path",
                    "src/main.txt",
                    "--content",
                    _updated_content(spec, "trace"),
                    "--sb-db",
                    str(root / "sb.sqlite"),
                ]
            )
        else:
            raise ValueError(lane)
        elapsed_ms = round((time.perf_counter() - start) * 1000.0, 3)
        after = _casey_snapshot(runtime_db, ledger_db, bundle_root)
        tree = load_current_tree(db_path=runtime_db)
        candidate_count = len(tree.paths.get("src/main.txt").candidates) if "src/main.txt" in tree.paths else 0

        runtime_delta = after["runtime"]["total_bytes"] - before["runtime"]["total_bytes"]
        ledger_delta = after["ledger"]["total_bytes"] - before["ledger"]["total_bytes"]
        bundle_delta = after["bundle_total_bytes"] - before["bundle_total_bytes"]
        persisted_delta = runtime_delta + ledger_delta + bundle_delta
        metadata_delta = ledger_delta + bundle_delta
        return {
            "elapsed_ms": elapsed_ms,
            "logical_content_bytes": logical_bytes,
            "working_tree_payload_bytes": sum(len(v.encode("utf-8")) for v in files.values()),
            "command_count": command_count,
            "paths_touched": 1,
            "candidate_count": candidate_count,
            "runtime_db_total_bytes": after["runtime"]["total_bytes"],
            "runtime_db_delta_bytes": runtime_delta,
            "runtime_db_page_count": after["runtime"]["page_count"],
            "runtime_db_page_size": after["runtime"]["page_size"],
            "runtime_row_counts": after["runtime"]["row_counts"],
            "ledger_db_total_bytes": after["ledger"]["total_bytes"],
            "ledger_db_delta_bytes": ledger_delta,
            "ledger_row_counts": after["ledger"]["row_counts"],
            "observer_bundle_total_bytes": after["bundle_total_bytes"],
            "observer_bundle_delta_bytes": bundle_delta,
            "observer_bundle_file_count": after["bundle_file_count"],
            "observer_bundle_file_sizes": after["bundle_file_sizes"],
            "workspace_ref_count": 1,
            "operation_ref_count": after["ledger"]["row_counts"]["casey_operation_ledger"],
            "build_ref_count": after["ledger"]["row_counts"]["casey_build_ledger"],
            "persisted_bytes_delta": persisted_delta,
            "metadata_bytes_delta": metadata_delta,
            "persisted_to_logical_ratio": _compute_ratio(persisted_delta, logical_bytes),
            "metadata_to_logical_ratio": _compute_ratio(metadata_delta, logical_bytes),
        }


def _seed_casey_library_runtime(runtime_db: Path, spec: TierSpec, include_bob: bool) -> tuple[WorkspaceView, dict[str, str]]:
    initialize_runtime(db_path=runtime_db, ws_id="alice", user="alice")
    files = _seed_files(spec)
    workspace = load_workspace(db_path=runtime_db, ws_id="alice")
    tree = load_current_tree(db_path=runtime_db)
    publish = publish_edits(tree_state=tree, workspace=workspace, edits=files, author="alice")
    store_publish_result(db_path=runtime_db, blobs=publish.blobs, file_versions=publish.file_versions, tree_state=publish.tree_state)
    set_current_tree_id(db_path=runtime_db, tree_id=publish.tree_state.tree_id)
    versions = load_file_versions(db_path=runtime_db, fv_ids={fv_id for state in publish.tree_state.paths.values() for fv_id in state.candidates})
    updated = sync_workspace(workspace=workspace, tree_state=publish.tree_state, file_versions=versions)
    save_workspace(db_path=runtime_db, workspace=updated)
    if include_bob:
        create_workspace(db_path=runtime_db, ws_id="bob", user="bob")
    return updated, files


def _casey_lane_library(spec: TierSpec, lane: str) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix=f"casey-bench-{lane}-lib-") as tmp:
        root = Path(tmp)
        runtime_db, ledger_db, bundle_root = _setup_casey_runtime_paths(root)
        api_call_count = 0

        workspace, files = _seed_casey_library_runtime(runtime_db, spec, include_bob=(lane == "divergence_native"))
        if lane == "divergence_native":
            bob = load_workspace(db_path=runtime_db, ws_id="bob")
            versions = load_file_versions(
                db_path=runtime_db,
                fv_ids={fv_id for state in load_current_tree(db_path=runtime_db).paths.values() for fv_id in state.candidates},
            )
            bob = sync_workspace(workspace=bob, tree_state=load_current_tree(db_path=runtime_db), file_versions=versions)
            save_workspace(db_path=runtime_db, workspace=bob)

        before = _casey_snapshot(runtime_db, ledger_db, bundle_root)
        start = time.perf_counter()
        logical_bytes = len(_updated_content(spec, lane).encode("utf-8"))

        if lane == "baseline_linear":
            tree = load_current_tree(db_path=runtime_db)
            alice = load_workspace(db_path=runtime_db, ws_id="alice")
            publish = publish_edits(
                tree_state=tree,
                workspace=alice,
                edits={"src/main.txt": _updated_content(spec, "baseline")},
                author="alice",
            )
            api_call_count += 1
            store_publish_result(db_path=runtime_db, blobs=publish.blobs, file_versions=publish.file_versions, tree_state=publish.tree_state)
            set_current_tree_id(db_path=runtime_db, tree_id=publish.tree_state.tree_id)
            versions = load_file_versions(
                db_path=runtime_db,
                fv_ids={fv_id for state in publish.tree_state.paths.values() for fv_id in state.candidates},
            )
            updated = sync_workspace(workspace=alice, tree_state=publish.tree_state, file_versions=versions)
            save_workspace(db_path=runtime_db, workspace=updated)
        elif lane == "divergence_native":
            tree = load_current_tree(db_path=runtime_db)
            alice = load_workspace(db_path=runtime_db, ws_id="alice")
            bob = load_workspace(db_path=runtime_db, ws_id="bob")
            publish_alice = publish_edits(
                tree_state=tree,
                workspace=alice,
                edits={"src/main.txt": _updated_content(spec, "alice-edit")},
                author="alice",
            )
            api_call_count += 1
            store_publish_result(db_path=runtime_db, blobs=publish_alice.blobs, file_versions=publish_alice.file_versions, tree_state=publish_alice.tree_state)
            set_current_tree_id(db_path=runtime_db, tree_id=publish_alice.tree_state.tree_id)
            versions_alice = load_file_versions(
                db_path=runtime_db,
                fv_ids={fv_id for state in publish_alice.tree_state.paths.values() for fv_id in state.candidates},
            )
            updated_alice = sync_workspace(workspace=alice, tree_state=publish_alice.tree_state, file_versions=versions_alice)
            save_workspace(db_path=runtime_db, workspace=updated_alice)
            publish_bob = publish_edits(
                tree_state=publish_alice.tree_state,
                workspace=bob,
                edits={"src/main.txt": _updated_content(spec, "bob-edit")},
                author="bob",
            )
            api_call_count += 1
            store_publish_result(db_path=runtime_db, blobs=publish_bob.blobs, file_versions=publish_bob.file_versions, tree_state=publish_bob.tree_state)
            set_current_tree_id(db_path=runtime_db, tree_id=publish_bob.tree_state.tree_id)
            logical_bytes = len(_updated_content(spec, "alice-edit").encode("utf-8")) + len(
                _updated_content(spec, "bob-edit").encode("utf-8")
            )
        elif lane == "build_freeze":
            tree = load_current_tree(db_path=runtime_db)
            alice = load_workspace(db_path=runtime_db, ws_id="alice")
            versions = load_file_versions(
                db_path=runtime_db,
                fv_ids={fv_id for state in tree.paths.values() for fv_id in state.candidates},
            )
            build = build_snapshot(workspace=alice, tree_state=tree, file_versions=versions)
            api_call_count += 1
            save_build(db_path=runtime_db, build=build)
            logical_bytes = 0
        elif lane == "traceability_cost":
            tree = load_current_tree(db_path=runtime_db)
            alice = load_workspace(db_path=runtime_db, ws_id="alice")
            publish = publish_edits(
                tree_state=tree,
                workspace=alice,
                edits={"src/main.txt": _updated_content(spec, "trace")},
                author="alice",
            )
            api_call_count += 1
            store_publish_result(db_path=runtime_db, blobs=publish.blobs, file_versions=publish.file_versions, tree_state=publish.tree_state)
            set_current_tree_id(db_path=runtime_db, tree_id=publish.tree_state.tree_id)
            versions = load_file_versions(
                db_path=runtime_db,
                fv_ids={fv_id for state in publish.tree_state.paths.values() for fv_id in state.candidates},
            )
            updated = sync_workspace(workspace=alice, tree_state=publish.tree_state, file_versions=versions)
            save_workspace(db_path=runtime_db, workspace=updated)
            emit_runtime_observer_artifacts(
                ledger_db_path=ledger_db,
                workspace=updated,
                operation=operation_record(
                    operation_kind="publish",
                    workspace=updated,
                    path="src/main.txt",
                    tree_id_before=tree.tree_id,
                    tree_id_after=publish.tree_state.tree_id,
                    chosen_fv_id=alice.selection.get("src/main.txt"),
                    resolved_fv_id=updated.selection.get("src/main.txt"),
                    actor="alice",
                ),
                build=None,
                provenance={"source": "casey-benchmark", "lane": lane},
                bundle_out_root=bundle_root,
                sb_db_path=root / "sb.sqlite",
            )
            api_call_count += 1
        else:
            raise ValueError(lane)

        elapsed_ms = round((time.perf_counter() - start) * 1000.0, 3)
        after = _casey_snapshot(runtime_db, ledger_db, bundle_root)
        tree = load_current_tree(db_path=runtime_db)
        candidate_count = len(tree.paths.get("src/main.txt").candidates) if "src/main.txt" in tree.paths else 0
        runtime_delta = after["runtime"]["total_bytes"] - before["runtime"]["total_bytes"]
        ledger_delta = after["ledger"]["total_bytes"] - before["ledger"]["total_bytes"]
        bundle_delta = after["bundle_total_bytes"] - before["bundle_total_bytes"]
        persisted_delta = runtime_delta + ledger_delta + bundle_delta
        metadata_delta = ledger_delta + bundle_delta
        return {
            "elapsed_ms": elapsed_ms,
            "logical_content_bytes": logical_bytes,
            "working_tree_payload_bytes": sum(len(v.encode("utf-8")) for v in files.values()),
            "command_count": api_call_count,
            "paths_touched": 1,
            "candidate_count": candidate_count,
            "runtime_db_total_bytes": after["runtime"]["total_bytes"],
            "runtime_db_delta_bytes": runtime_delta,
            "runtime_db_page_count": after["runtime"]["page_count"],
            "runtime_db_page_size": after["runtime"]["page_size"],
            "runtime_row_counts": after["runtime"]["row_counts"],
            "ledger_db_total_bytes": after["ledger"]["total_bytes"],
            "ledger_db_delta_bytes": ledger_delta,
            "ledger_row_counts": after["ledger"]["row_counts"],
            "observer_bundle_total_bytes": after["bundle_total_bytes"],
            "observer_bundle_delta_bytes": bundle_delta,
            "observer_bundle_file_count": after["bundle_file_count"],
            "observer_bundle_file_sizes": after["bundle_file_sizes"],
            "workspace_ref_count": 1,
            "operation_ref_count": after["ledger"]["row_counts"]["casey_operation_ledger"],
            "build_ref_count": after["ledger"]["row_counts"]["casey_build_ledger"],
            "persisted_bytes_delta": persisted_delta,
            "metadata_bytes_delta": metadata_delta,
            "persisted_to_logical_ratio": _compute_ratio(persisted_delta, logical_bytes),
            "metadata_to_logical_ratio": _compute_ratio(metadata_delta, logical_bytes),
        }


def _git_lane(spec: TierSpec, lane: str) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix=f"git-bench-{lane}-") as tmp:
        root = Path(tmp)
        repo, files = _setup_git_repo(root, spec)
        _run_git(repo, ["add", "."])
        _run_git(repo, ["commit", "-m", "seed"])
        trace_root = root / "artifacts" / "git" / "runs"
        before = _git_snapshot(repo, trace_root)
        command_count = 0
        start = time.perf_counter()
        logical_bytes = len(_updated_content(spec, lane).encode("utf-8"))

        if lane == "baseline_linear":
            (repo / "src/main.txt").write_text(_updated_content(spec, "baseline"), encoding="utf-8")
            _run_git(repo, ["add", "src/main.txt"])
            _run_git(repo, ["commit", "-m", "baseline"])
            command_count += 2
        elif lane == "divergence_native":
            _run_git(repo, ["branch", "bob"])
            _run_git(repo, ["checkout", "-b", "alice"])
            (repo / "src/main.txt").write_text(_updated_content(spec, "alice-edit"), encoding="utf-8")
            _run_git(repo, ["add", "src/main.txt"])
            _run_git(repo, ["commit", "-m", "alice"])
            _run_git(repo, ["checkout", "bob"])
            (repo / "src/main.txt").write_text(_updated_content(spec, "bob-edit"), encoding="utf-8")
            _run_git(repo, ["add", "src/main.txt"])
            _run_git(repo, ["commit", "-m", "bob"])
            merge = subprocess.run(["git", "merge", "alice"], cwd=repo, capture_output=True, text=True)
            command_count += 7
            logical_bytes = len(_updated_content(spec, "alice-edit").encode("utf-8")) + len(
                _updated_content(spec, "bob-edit").encode("utf-8")
            )
            if merge.returncode == 0:
                raise RuntimeError("expected merge conflict benchmark setup to conflict")
        elif lane == "build_freeze":
            _run_git(repo, ["rev-parse", "HEAD"])
            command_count += 1
            logical_bytes = 0
        elif lane == "traceability_cost":
            (repo / "src/main.txt").write_text(_updated_content(spec, "trace"), encoding="utf-8")
            _run_git(repo, ["add", "src/main.txt"])
            _run_git(repo, ["commit", "-m", "trace"])
            commit = _run_git(repo, ["rev-parse", "HEAD"])
            _emit_git_trace_bundle(
                trace_root / "trace",
                {"commit": commit, "lane": lane, "path": "src/main.txt"},
            )
            command_count += 3
        else:
            raise ValueError(lane)

        elapsed_ms = round((time.perf_counter() - start) * 1000.0, 3)
        after = _git_snapshot(repo, trace_root)
        git_delta = after["git_dir_total_bytes"] - before["git_dir_total_bytes"]
        trace_delta = after["trace_total_bytes"] - before["trace_total_bytes"]
        persisted_delta = git_delta + trace_delta
        metadata_delta = trace_delta
        return {
            "elapsed_ms": elapsed_ms,
            "logical_content_bytes": logical_bytes,
            "working_tree_payload_bytes": after["working_tree_bytes"],
            "command_count": command_count,
            "paths_touched": 1,
            "git_dir_total_bytes": after["git_dir_total_bytes"],
            "git_dir_delta_bytes": git_delta,
            "git_object_counts": after["git_object_counts"],
            "trace_total_bytes": after["trace_total_bytes"],
            "trace_delta_bytes": trace_delta,
            "trace_file_count": after["trace_file_count"],
            "trace_file_sizes": after["trace_file_sizes"],
            "persisted_bytes_delta": persisted_delta,
            "metadata_bytes_delta": metadata_delta,
            "persisted_to_logical_ratio": _compute_ratio(persisted_delta, logical_bytes),
            "metadata_to_logical_ratio": _compute_ratio(metadata_delta, logical_bytes),
        }


def _aggregate_case(samples: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "elapsed_ms": _aggregate_numeric(samples, "elapsed_ms"),
        "persisted_bytes_delta": _aggregate_numeric(samples, "persisted_bytes_delta"),
        "metadata_bytes_delta": _aggregate_numeric(samples, "metadata_bytes_delta"),
        "logical_content_bytes": samples[0]["logical_content_bytes"],
        "working_tree_payload_bytes": samples[0]["working_tree_payload_bytes"],
        "command_count": samples[0]["command_count"],
        "paths_touched": samples[0]["paths_touched"],
        "candidate_count": samples[0].get("candidate_count"),
        "runtime_db_total_bytes": samples[0].get("runtime_db_total_bytes"),
        "runtime_db_delta_bytes": samples[0].get("runtime_db_delta_bytes"),
        "runtime_db_page_count": samples[0].get("runtime_db_page_count"),
        "runtime_db_page_size": samples[0].get("runtime_db_page_size"),
        "runtime_row_counts": samples[0].get("runtime_row_counts"),
        "ledger_db_total_bytes": samples[0].get("ledger_db_total_bytes"),
        "ledger_db_delta_bytes": samples[0].get("ledger_db_delta_bytes"),
        "ledger_row_counts": samples[0].get("ledger_row_counts"),
        "observer_bundle_total_bytes": samples[0].get("observer_bundle_total_bytes"),
        "observer_bundle_delta_bytes": samples[0].get("observer_bundle_delta_bytes"),
        "observer_bundle_file_count": samples[0].get("observer_bundle_file_count"),
        "observer_bundle_file_sizes": samples[0].get("observer_bundle_file_sizes"),
        "operation_ref_count": samples[0].get("operation_ref_count"),
        "build_ref_count": samples[0].get("build_ref_count"),
        "persisted_to_logical_ratio": samples[0]["persisted_to_logical_ratio"],
        "metadata_to_logical_ratio": samples[0]["metadata_to_logical_ratio"],
        "samples": samples,
    }


def _aggregate_git(samples: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "elapsed_ms": _aggregate_numeric(samples, "elapsed_ms"),
        "persisted_bytes_delta": _aggregate_numeric(samples, "persisted_bytes_delta"),
        "metadata_bytes_delta": _aggregate_numeric(samples, "metadata_bytes_delta"),
        "logical_content_bytes": samples[0]["logical_content_bytes"],
        "working_tree_payload_bytes": samples[0]["working_tree_payload_bytes"],
        "command_count": samples[0]["command_count"],
        "paths_touched": samples[0]["paths_touched"],
        "git_dir_total_bytes": samples[0]["git_dir_total_bytes"],
        "git_dir_delta_bytes": samples[0]["git_dir_delta_bytes"],
        "git_object_counts": samples[0]["git_object_counts"],
        "trace_total_bytes": samples[0]["trace_total_bytes"],
        "trace_delta_bytes": samples[0]["trace_delta_bytes"],
        "trace_file_count": samples[0]["trace_file_count"],
        "trace_file_sizes": samples[0]["trace_file_sizes"],
        "persisted_to_logical_ratio": samples[0]["persisted_to_logical_ratio"],
        "metadata_to_logical_ratio": samples[0]["metadata_to_logical_ratio"],
        "samples": samples,
    }


def _verdict(casey: dict[str, Any], git: dict[str, Any]) -> str:
    casey_ms = casey["elapsed_ms"]["median"]
    git_ms = git["elapsed_ms"]["median"]
    casey_bytes = casey["persisted_bytes_delta"]["median"]
    git_bytes = git["persisted_bytes_delta"]["median"]
    if casey_ms < git_ms and casey_bytes <= git_bytes:
        return "casey_ahead"
    if git_ms < casey_ms and git_bytes <= casey_bytes:
        return "git_ahead"
    return "mixed"


def _run_case(spec: TierSpec, lane: str, surface: str, samples: int) -> dict[str, Any]:
    casey_samples: list[dict[str, Any]] = []
    git_samples: list[dict[str, Any]] = []
    for _ in range(samples):
        if surface == "cli":
            casey_samples.append(_casey_lane_cli(spec, lane))
        elif surface == "library":
            casey_samples.append(_casey_lane_library(spec, lane))
        else:
            raise ValueError(surface)
        git_samples.append(_git_lane(spec, lane))
    casey = _aggregate_case(casey_samples)
    git = _aggregate_git(git_samples)
    return {
        "tier": spec.name,
        "lane": lane,
        "surface": surface,
        "casey": casey,
        "git": git,
        "verdict": _verdict(casey, git),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Benchmark Casey against local git on Casey-native workflows.")
    parser.add_argument("--tiers", nargs="+", choices=sorted(TIERS), default=sorted(TIERS))
    parser.add_argument("--lanes", nargs="+", choices=LANES, default=list(LANES))
    parser.add_argument("--surfaces", nargs="+", choices=SURFACES, default=list(SURFACES))
    parser.add_argument("--samples", type=int, default=3)
    parser.add_argument("--markdown-out", type=Path, default=None)
    args = parser.parse_args(argv)

    results = []
    for tier_name in args.tiers:
        spec = TIERS[tier_name]
        for lane in args.lanes:
            for surface in args.surfaces:
                results.append(_run_case(spec, lane, surface, max(args.samples, 1)))

    markdown = _markdown_table(results)
    payload = {
        "benchmark_version": "casey_vs_git.v1",
        "tiers": list(args.tiers),
        "lanes": list(args.lanes),
        "surfaces": list(args.surfaces),
        "samples": int(args.samples),
        "results": results,
        "markdown_summary": markdown,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    print(markdown, file=sys.stderr)
    if args.markdown_out is not None:
        args.markdown_out.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_out.write_text(markdown + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
