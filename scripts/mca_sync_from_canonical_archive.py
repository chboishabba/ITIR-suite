#!/usr/bin/env python3
"""Bridge a canonical chat archive into MyChatArchive through a JSON wrapper."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).name
DEFAULT_MCA_REPO = Path("/home/c/Documents/code/mychatarchive")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def emit(payload: dict[str, Any], code: int = 0) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))
    raise SystemExit(code)


def env_first(*names: str) -> str | None:
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return None


def resolve_mca_repo(value: str | None) -> Path:
    return Path(value or os.environ.get("MYCHATARCHIVE_REPO") or DEFAULT_MCA_REPO).expanduser()


def resolve_mca_python(value: str | None, repo: Path) -> Path:
    if value:
        return Path(value).expanduser()
    env_value = os.environ.get("MYCHATARCHIVE_PYTHON")
    if env_value:
        return Path(env_value).expanduser()
    venv_python = repo / ".venv" / "bin" / "python"
    return venv_python if venv_python.exists() else Path(sys.executable)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Import canonical archive rows into MyChatArchive when the MCA bridge "
            "module is available. Always emits JSON."
        )
    )
    parser.add_argument(
        "--canonical-db",
        default=env_first("CHAT_EXPORT_STRUCTURER_DB", "CHAT_ARCHIVE_DB"),
        help="Canonical chat archive SQLite DB. Env fallback: CHAT_EXPORT_STRUCTURER_DB, CHAT_ARCHIVE_DB.",
    )
    parser.add_argument(
        "--mca-db",
        default=env_first("MYCHATARCHIVE_DB", "MCA_DB"),
        help="MyChatArchive SQLite DB. Env fallback: MYCHATARCHIVE_DB, MCA_DB.",
    )
    parser.add_argument("--mca-repo", default=None, help="MyChatArchive repo path.")
    parser.add_argument("--mca-python", default=None, help="Python executable for MyChatArchive.")
    parser.add_argument("--limit", type=int, default=None, help="Optional bridge row limit.")
    parser.add_argument("--dry-run", action="store_true", help="Ask the bridge to report without writing.")
    parser.add_argument("--json", action="store_true", help="Accepted for agent compatibility; output is always JSON.")
    args = parser.parse_args()
    args.mca_repo = resolve_mca_repo(args.mca_repo)
    args.mca_python = resolve_mca_python(args.mca_python, args.mca_repo)
    args.canonical_db = Path(args.canonical_db).expanduser() if args.canonical_db else None
    args.mca_db = Path(args.mca_db).expanduser() if args.mca_db else None
    return args


def base_payload(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "ok": False,
        "script": SCRIPT,
        "operation": "mca_sync_from_canonical_archive",
        "timestamp": utc_now(),
        "inputs": {
            "canonical_db": str(args.canonical_db) if args.canonical_db else None,
            "mca_db": str(args.mca_db) if args.mca_db else None,
            "limit": args.limit,
            "dry_run": args.dry_run,
        },
        "mca": {
            "repo": str(args.mca_repo),
            "python": str(args.mca_python),
            "bridge_module": "mychatarchive.ingest_bridge",
        },
    }


def main() -> None:
    args = parse_args()
    payload = base_payload(args)

    missing: list[str] = []
    if args.canonical_db is None:
        missing.append("--canonical-db")
    if args.mca_db is None:
        missing.append("--mca-db")
    if missing:
        payload["error"] = {
            "code": "missing_required_db_args",
            "message": f"Missing required argument(s): {', '.join(missing)}.",
        }
        emit(payload, 2)
    if not args.canonical_db.exists():
        payload["error"] = {
            "code": "canonical_db_not_found",
            "message": f"Canonical DB does not exist: {args.canonical_db}",
        }
        emit(payload, 2)
    if not args.mca_repo.exists():
        payload["error"] = {
            "code": "mca_repo_not_found",
            "message": f"MyChatArchive repo does not exist: {args.mca_repo}",
        }
        emit(payload, 2)
    if not args.mca_python.exists():
        payload["error"] = {
            "code": "mca_python_not_found",
            "message": f"MyChatArchive Python executable does not exist: {args.mca_python}",
        }
        emit(payload, 2)

    env = os.environ.copy()
    src = args.mca_repo / "src"
    env["PYTHONPATH"] = str(src) + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")

    probe = subprocess.run(
        [str(args.mca_python), "-c", "import mychatarchive.ingest_bridge"],
        cwd=args.mca_repo,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    if probe.returncode != 0:
        payload.update(
            {
                "returncode": probe.returncode,
                "stdout": probe.stdout,
                "stderr": probe.stderr,
                "error": {
                    "code": "mca_bridge_unavailable",
                    "message": "mychatarchive.ingest_bridge is not importable yet.",
                },
            }
        )
        emit(payload, 69)

    cmd = [
        str(args.mca_python),
        "-m",
        "mychatarchive.ingest_bridge",
        "--canonical-db",
        str(args.canonical_db),
        "--mca-db",
        str(args.mca_db),
        "--json",
    ]
    if args.limit is not None:
        cmd.extend(["--limit", str(args.limit)])
    if args.dry_run:
        cmd.append("--dry-run")

    completed = subprocess.run(
        cmd,
        cwd=args.mca_repo,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    parsed_stdout: Any = None
    try:
        parsed_stdout = json.loads(completed.stdout) if completed.stdout.strip() else None
    except json.JSONDecodeError:
        parsed_stdout = None
    payload.update(
        {
            "ok": completed.returncode == 0,
            "command": cmd,
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "bridge_result": parsed_stdout,
        }
    )
    if completed.returncode != 0:
        payload["error"] = {
            "code": "mca_bridge_failed",
            "message": "MyChatArchive canonical bridge command failed.",
        }
    emit(payload, completed.returncode)


if __name__ == "__main__":
    main()
