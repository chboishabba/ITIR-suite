#!/usr/bin/env python3
"""Run MyChatArchive embedding through a stable JSON wrapper."""

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


def build_base(script: str, args: argparse.Namespace) -> dict[str, Any]:
    return {
        "ok": False,
        "script": script,
        "operation": "mca_embed_missing",
        "timestamp": utc_now(),
        "inputs": {
            "mca_db": str(args.mca_db) if args.mca_db else None,
            "batch_size": args.batch_size,
            "max_messages": args.max_messages,
            "max_chunks": args.max_chunks,
            "progress_interval": args.progress_interval,
            "force": args.force,
        },
        "mca": {
            "repo": str(args.mca_repo),
            "python": str(args.mca_python),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Embed missing MyChatArchive rows and emit a stable JSON envelope."
    )
    parser.add_argument(
        "--mca-db",
        default=env_first("MYCHATARCHIVE_DB", "MCA_DB"),
        help="MyChatArchive SQLite DB. Env fallback: MYCHATARCHIVE_DB, MCA_DB.",
    )
    parser.add_argument("--mca-repo", default=None, help="MyChatArchive repo path.")
    parser.add_argument("--mca-python", default=None, help="Python executable for MyChatArchive.")
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--max-messages", type=int, default=None)
    parser.add_argument("--max-chunks", type=int, default=None)
    parser.add_argument("--progress-interval", type=int, default=10)
    parser.add_argument("--force", action="store_true", help="Re-embed all rows.")
    parser.add_argument("--json", action="store_true", help="Accepted for agent compatibility; output is always JSON.")
    args = parser.parse_args()
    args.mca_repo = resolve_mca_repo(args.mca_repo)
    args.mca_python = resolve_mca_python(args.mca_python, args.mca_repo)
    args.mca_db = Path(args.mca_db).expanduser() if args.mca_db else None
    return args


def main() -> None:
    args = parse_args()
    payload = build_base(SCRIPT, args)

    if args.mca_db is None:
        payload["error"] = {
            "code": "missing_mca_db",
            "message": "Pass --mca-db or set MYCHATARCHIVE_DB/MCA_DB.",
        }
        emit(payload, 2)
    if not args.mca_db.exists():
        payload["error"] = {
            "code": "mca_db_not_found",
            "message": f"MyChatArchive DB does not exist: {args.mca_db}",
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

    cmd = [
        str(args.mca_python),
        "-m",
        "mychatarchive",
        "embed",
        "--db",
        str(args.mca_db),
        "--batch-size",
        str(args.batch_size),
    ]
    if args.max_messages is not None:
        cmd.extend(["--max-messages", str(args.max_messages)])
    if args.max_chunks is not None:
        cmd.extend(["--max-chunks", str(args.max_chunks)])
    cmd.extend(["--progress-interval", str(args.progress_interval)])
    if args.force:
        cmd.append("--force")

    env = os.environ.copy()
    src = args.mca_repo / "src"
    env["PYTHONPATH"] = str(src) + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")

    completed = subprocess.run(
        cmd,
        cwd=args.mca_repo,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=None,
        check=False,
    )
    payload.update(
        {
            "ok": completed.returncode == 0,
            "command": cmd,
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": None,
        }
    )
    if completed.returncode != 0:
        payload["error"] = {
            "code": "mca_embed_failed",
            "message": "MyChatArchive embed command failed.",
        }
    emit(payload, completed.returncode)


if __name__ == "__main__":
    main()
