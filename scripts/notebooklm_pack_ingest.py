from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_NOTEBOOKLM_MAX_WORDS = 500_000
DEFAULT_NOTEBOOKLM_MAX_BYTES = 200 * 1024 * 1024


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def compute_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def build_pack_run_id() -> str:
    return f"notebooklm-pack-run:{uuid4()}"


def load_manifest(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("manifest must be a JSON object")
    if "manifest" not in payload or not isinstance(payload["manifest"], list):
        raise ValueError("manifest payload must include a 'manifest' list")
    return payload


def require_int_field(entry: dict[str, Any], field: str, source_file: str) -> int:
    value = entry.get(field)
    if not isinstance(value, int):
        raise ValueError(f"manifest entry for {source_file!r} must include integer '{field}'")
    return value


def run_notebooklm_pack(
    notebooklm_pack_repo: Path,
    repo_input: Path,
    output_dir: Path,
    max_sources: int,
) -> subprocess.CompletedProcess[str]:
    cargo = shutil.which("cargo")
    if cargo is None:
        raise RuntimeError("cargo is required to run notebooklm-pack")
    cmd = [
        cargo,
        "run",
        "--quiet",
        "--",
        str(repo_input),
        str(output_dir),
        "--max-sources",
        str(max_sources),
    ]
    return subprocess.run(
        cmd,
        cwd=notebooklm_pack_repo,
        text=True,
        capture_output=True,
        check=True,
    )


@dataclass
class NotebookContextPlan:
    notebook_id: str | None
    notebook_title: str | None
    create_if_missing: bool


def normalize_manifest(
    manifest_path: Path,
    *,
    input_mode: str | None,
    input_ref: str | None,
    repo_scan_root: str | None,
    max_sources: int | None,
    max_words_per_source: int = DEFAULT_NOTEBOOKLM_MAX_WORDS,
    max_bytes_per_source: int = DEFAULT_NOTEBOOKLM_MAX_BYTES,
    pack_run_id: str | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    payload = load_manifest(manifest_path)
    source_dir = manifest_path.parent
    run_id = pack_run_id or build_pack_run_id()
    created = created_at or utc_now_iso()

    normalized_sources: list[dict[str, Any]] = []
    for index, entry in enumerate(payload["manifest"], start=1):
        source_file = source_dir / entry["file"]
        words = require_int_field(entry, "words", entry["file"])
        source_bytes = require_int_field(entry, "bytes", entry["file"])
        if words > max_words_per_source:
            raise ValueError(
                f"packed source {entry['file']!r} exceeds NotebookLM word limit: "
                f"{words} > {max_words_per_source}"
            )
        if source_bytes > max_bytes_per_source:
            raise ValueError(
                f"packed source {entry['file']!r} exceeds NotebookLM byte limit: "
                f"{source_bytes} > {max_bytes_per_source}"
            )
        normalized_sources.append(
            {
                "source_index": index,
                "source_file": entry["file"],
                "source_path": str(source_file.resolve()),
                "source_file_hash": compute_sha256(source_file),
                "repos": list(entry.get("repos", [])),
                "words": words,
                "bytes": source_bytes,
            }
        )

    return {
        "pack_run": {
            "pack_run_id": run_id,
            "created_at": created,
            "manifest_path": str(manifest_path.resolve()),
            "input_mode": input_mode,
            "input_ref": input_ref,
            "repo_scan_root": repo_scan_root,
            "max_sources": max_sources,
            "source_count": payload.get("sources", len(normalized_sources)),
            "max_words_per_source": max_words_per_source,
            "max_bytes_per_source": max_bytes_per_source,
        },
        "packed_sources": normalized_sources,
    }


def build_command_plan(
    normalized: dict[str, Any],
    *,
    notebook_context: NotebookContextPlan,
    wait_timeout: int,
    wait_interval: int,
) -> list[dict[str, Any]]:
    plan: list[dict[str, Any]] = []
    notebook_ref = notebook_context.notebook_id or "__NOTEBOOK_ID__"

    if notebook_context.create_if_missing:
        title = notebook_context.notebook_title or "NotebookLM Pack Import"
        plan.append(
            {
                "step": "create_notebook",
                "command": ["notebooklm", "create", title, "--json"],
                "notebook_ref": "__NOTEBOOK_ID__",
            }
        )

    for source in normalized["packed_sources"]:
        add_cmd = [
            "notebooklm",
            "source",
            "add",
            source["source_path"],
            "--notebook",
            notebook_ref,
            "--json",
        ]
        plan.append(
            {
                "step": "add_source",
                "source_file": source["source_file"],
                "source_file_hash": source["source_file_hash"],
                "command": add_cmd,
                "notebook_ref": notebook_ref,
            }
        )
        plan.append(
            {
                "step": "wait_source",
                "source_file": source["source_file"],
                "source_ref": "__SOURCE_ID__",
                "command": [
                    "notebooklm",
                    "source",
                    "wait",
                    "__SOURCE_ID__",
                    "-n",
                    notebook_ref,
                    "--timeout",
                    str(wait_timeout),
                ],
                "notebook_ref": notebook_ref,
                "wait_interval_seconds": wait_interval,
            }
        )

    plan.extend(
        [
            {
                "step": "list_sources",
                "command": ["notebooklm", "source", "list", "--notebook", notebook_ref, "--json"],
                "notebook_ref": notebook_ref,
            },
            {
                "step": "list_artifacts",
                "command": ["notebooklm", "artifact", "list", "--notebook", notebook_ref, "--json"],
                "notebook_ref": notebook_ref,
            },
            {
                "step": "status",
                "command": ["notebooklm", "status", "--json"],
                "notebook_ref": notebook_ref,
            },
        ]
    )
    return plan


def run_json_command(cmd: list[str]) -> dict[str, Any]:
    result = subprocess.run(cmd, text=True, capture_output=True, check=True)
    return json.loads(result.stdout)


def resolve_notebooklm_cli(explicit_path: str | None = None) -> str:
    candidates: list[Path] = []
    if explicit_path:
        candidates.append(Path(explicit_path))
    env_path = os.environ.get("NOTEBOOKLM_CLI")
    if env_path:
        candidates.append(Path(env_path))
    candidates.extend(
        [
            REPO_ROOT / ".venv" / "bin" / "notebooklm",
            REPO_ROOT / "notebooklm-py" / ".venv" / "bin" / "notebooklm",
        ]
    )
    for candidate in candidates:
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
    on_path = shutil.which("notebooklm")
    if on_path:
        return on_path
    raise RuntimeError("notebooklm CLI is required for live execution")


def require_nested_id(payload: dict[str, Any], key: str) -> tuple[str, dict[str, Any]]:
    nested = payload.get(key)
    if not isinstance(nested, dict):
        raise ValueError(f"expected '{key}' object in notebooklm JSON response")
    nested_id = nested.get("id")
    if not isinstance(nested_id, str) or not nested_id:
        raise ValueError(f"expected '{key}.id' in notebooklm JSON response")
    return nested_id, nested


def execute_notebooklm_plan(
    normalized: dict[str, Any],
    *,
    notebook_context: NotebookContextPlan,
    wait_timeout: int,
    wait_interval: int,
    notebooklm_cli: str | None = None,
) -> dict[str, Any]:
    del wait_interval
    notebooklm_bin = resolve_notebooklm_cli(notebooklm_cli)

    notebook_id = notebook_context.notebook_id
    notebook_title = notebook_context.notebook_title
    if notebook_id is None:
        created = run_json_command(
            [notebooklm_bin, "create", notebook_title or "NotebookLM Pack Import", "--json"]
        )
        notebook_id, notebook_record = require_nested_id(created, "notebook")
        notebook_title = notebook_record.get("title", notebook_title)

    links: list[dict[str, Any]] = []
    for source in normalized["packed_sources"]:
        added = run_json_command(
            [
                notebooklm_bin,
                "source",
                "add",
                source["source_path"],
                "--notebook",
                notebook_id,
                "--json",
            ]
        )
        source_id, source_record = require_nested_id(added, "source")
        subprocess.run(
            [
                notebooklm_bin,
                "source",
                "wait",
                source_id,
                "-n",
                notebook_id,
                "--timeout",
                str(wait_timeout),
            ],
            text=True,
            capture_output=True,
            check=True,
        )
        links.append(
            {
                "pack_run_id": normalized["pack_run"]["pack_run_id"],
                "source_file": source["source_file"],
                "source_file_hash": source["source_file_hash"],
                "repos": source["repos"],
                "notebook_id": notebook_id,
                "notebook_title": notebook_title,
                "notebook_source_id": source_id,
                "notebook_source_title": source_record.get("title"),
                "captured_at": utc_now_iso(),
            }
        )

    sources_state = run_json_command(
        [notebooklm_bin, "source", "list", "--notebook", notebook_id, "--json"]
    )
    artifacts_state = run_json_command(
        [notebooklm_bin, "artifact", "list", "--notebook", notebook_id, "--json"]
    )
    status_state = run_json_command([notebooklm_bin, "status", "--json"])

    return {
        "notebook": {"notebook_id": notebook_id, "notebook_title": notebook_title},
        "notebooklm_cli": notebooklm_bin,
        "links": links,
        "sources_state": sources_state,
        "artifacts_state": artifacts_state,
        "status_state": status_state,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Normalize notebooklm-pack output and optionally ingest it through notebooklm-py.",
    )
    parser.add_argument("--manifest", type=Path, default=None, help="Path to notebooklm-pack manifest.json")
    parser.add_argument(
        "--run-pack",
        action="store_true",
        help="Run sibling notebooklm-pack before normalizing the manifest",
    )
    parser.add_argument(
        "--notebooklm-pack-repo",
        type=Path,
        default=Path("../notebooklm-pack"),
        help="Path to the sibling notebooklm-pack repo",
    )
    parser.add_argument("--repo-input", type=Path, default=None, help="Repo list file or scan root for notebooklm-pack")
    parser.add_argument("--pack-output-dir", type=Path, default=None, help="Output dir for notebooklm-pack")
    parser.add_argument("--max-sources", type=int, default=50, help="Max sources for notebooklm-pack")
    parser.add_argument("--input-mode", choices=["repo_list", "scan_root"], default=None)
    parser.add_argument("--input-ref", default=None, help="Operator-friendly input reference label")
    parser.add_argument("--repo-scan-root", default=None, help="Original repo scan root, if different from input-ref")
    parser.add_argument(
        "--max-words-per-source",
        type=int,
        default=DEFAULT_NOTEBOOKLM_MAX_WORDS,
        help="Hard NotebookLM per-source word cap enforced before upload",
    )
    parser.add_argument(
        "--max-bytes-per-source",
        type=int,
        default=DEFAULT_NOTEBOOKLM_MAX_BYTES,
        help="Hard NotebookLM per-source local-upload byte cap enforced before upload",
    )
    parser.add_argument("--notebook-id", default=None, help="Existing NotebookLM notebook id")
    parser.add_argument("--notebook-title", default=None, help="Notebook title to create if notebook id is absent")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Perform live notebooklm create/add/list operations instead of dry-run planning only",
    )
    parser.add_argument("--wait-timeout", type=int, default=300, help="Timeout for source wait in seconds")
    parser.add_argument("--wait-interval", type=int, default=5, help="Poll interval for source wait in seconds")
    parser.add_argument("--notebooklm-cli", default=None, help="Path to notebooklm CLI binary")
    parser.add_argument("--output", type=Path, required=True, help="Output JSON path")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])

    manifest_path = args.manifest
    pack_run_stdout: str | None = None
    if args.run_pack:
        if args.repo_input is None or args.pack_output_dir is None:
            raise SystemExit("--run-pack requires --repo-input and --pack-output-dir")
        args.pack_output_dir.mkdir(parents=True, exist_ok=True)
        result = run_notebooklm_pack(
            args.notebooklm_pack_repo.resolve(),
            args.repo_input.resolve(),
            args.pack_output_dir.resolve(),
            args.max_sources,
        )
        pack_run_stdout = result.stdout
        manifest_path = args.pack_output_dir / "manifest.json"

    if manifest_path is None:
        raise SystemExit("either --manifest or --run-pack must be supplied")

    normalized = normalize_manifest(
        manifest_path.resolve(),
        input_mode=args.input_mode,
        input_ref=args.input_ref or (str(args.repo_input.resolve()) if args.repo_input else None),
        repo_scan_root=args.repo_scan_root,
        max_sources=args.max_sources,
        max_words_per_source=args.max_words_per_source,
        max_bytes_per_source=args.max_bytes_per_source,
    )

    notebook_context = NotebookContextPlan(
        notebook_id=args.notebook_id,
        notebook_title=args.notebook_title,
        create_if_missing=args.notebook_id is None,
    )
    command_plan = build_command_plan(
        normalized,
        notebook_context=notebook_context,
        wait_timeout=args.wait_timeout,
        wait_interval=args.wait_interval,
    )

    output: dict[str, Any] = {
        **normalized,
        "mode": "execute" if args.execute else "dry_run",
        "command_plan": command_plan,
    }
    if pack_run_stdout is not None:
        output["pack_run"]["pack_stdout"] = pack_run_stdout

    if args.execute:
        output["execution"] = execute_notebooklm_plan(
            normalized,
            notebook_context=notebook_context,
            wait_timeout=args.wait_timeout,
            wait_interval=args.wait_interval,
            notebooklm_cli=args.notebooklm_cli,
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
