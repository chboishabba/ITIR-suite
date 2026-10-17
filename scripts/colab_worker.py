#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import os
from pathlib import Path
import socket
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "colab-runner" / "src"))

from itir_colab_runner.executor import Executor
from itir_colab_runner.github_relay import GitHubRelay
from itir_colab_runner.github_store import GitHubContentsStore
from itir_colab_runner.worker import run_one_job, run_poll_loop


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Run the ITIR Colab prover worker")
    p.add_argument("--poll", action="store_true", help="poll continuously; otherwise process at most one job")
    p.add_argument("--poll-seconds", type=float, default=10.0)
    p.add_argument("--worker-id", default=f"colab-{socket.gethostname()}")
    p.add_argument("--workspace", type=Path, default=Path("/content/itir-prover-work"))
    p.add_argument("--durable-dir", type=Path, default=Path("/content/itir-prover-pending"))
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    token = os.environ.get("ITIR_COLAB_GITHUB_TOKEN")
    if not token:
        raise SystemExit("ITIR_COLAB_GITHUB_TOKEN must be injected from Colab Secrets")
    store = GitHubContentsStore("chboishabba/ITIR-suite", token)
    relay = GitHubRelay(store)
    executor = Executor(args.workspace, secrets=[token])
    if args.poll:
        run_poll_loop(relay, executor, args.worker_id, poll_seconds=args.poll_seconds, durable_dir=args.durable_dir)
        return 0
    outcome = run_one_job(relay, executor, args.worker_id, datetime.now(timezone.utc), durable_dir=args.durable_dir)
    print(outcome)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
