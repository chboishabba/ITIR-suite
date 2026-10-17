#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import os
from pathlib import Path
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "colab-runner" / "src"))

from itir_colab_runner.github_relay import GitHubRelay
from itir_colab_runner.github_store import GitHubContentsStore
from itir_colab_runner.model import load_job

REPOS = ["chboishabba/dashi_lean4", "chboishabba/dashi_agda"]
OPS = ["lake_build", "lake_env_lean", "agda_module"]


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Submit an exact-SHA prover job")
    p.add_argument("--repository", required=True, choices=REPOS)
    p.add_argument("--commit-sha", required=True)
    p.add_argument("--operation", required=True, choices=OPS)
    p.add_argument("--job-id", default=None)
    p.add_argument("--requested-by", default="cli")
    p.add_argument("--timeout-seconds", type=int, default=7200)
    p.add_argument("--target")
    p.add_argument("--path")
    p.add_argument("--profile", choices=["repo"], default="repo")
    return p


def _arguments(args: argparse.Namespace) -> dict[str, str]:
    if args.operation == "lake_build":
        if not args.target or args.path:
            raise SystemExit("lake_build requires --target and forbids --path")
        return {"target": args.target}
    if args.operation == "lake_env_lean":
        if not args.path or args.target:
            raise SystemExit("lake_env_lean requires --path and forbids --target")
        return {"path": args.path}
    if args.operation == "agda_module":
        if not args.path or args.target:
            raise SystemExit("agda_module requires --path and forbids --target")
        return {"path": args.path, "profile": args.profile}
    raise SystemExit("unsupported operation")


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    token = os.environ.get("ITIR_COLAB_GITHUB_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        raise SystemExit("ITIR_COLAB_GITHUB_TOKEN or GITHUB_TOKEN is required")
    job_id = args.job_id or f"job-{uuid.uuid4().hex}"
    job = load_job({
        "schema_version": "colab_prover_job_v1",
        "job_id": job_id,
        "repository": args.repository,
        "commit_sha": args.commit_sha,
        "operation": args.operation,
        "arguments": _arguments(args),
        "toolchain_policy": "repo_pinned",
        "requested_by": args.requested_by,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "resource_class": "high_mem",
        "timeout_seconds": args.timeout_seconds,
    })
    relay = GitHubRelay(GitHubContentsStore("chboishabba/ITIR-suite", token))
    digest = relay.submit_job(job)
    print(f"job_id={job.job_id}")
    print(f"digest={digest}")
    print(f"repository={job.repository}")
    print(f"commit_sha={job.commit_sha}")
    print("state_branch=colab-runner-state")
    print(f"path=.itir/colab/jobs/{job.job_id}.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
