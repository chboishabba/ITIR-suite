from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import shutil
import subprocess
import time
from typing import Any, Sequence

from .model import ProverJob
from .policy import build_argv, validate_job_policy
from .runtime_receipt import collect_runtime_receipt

REPO_URLS = {
    "chboishabba/dashi_lean4": "https://github.com/chboishabba/dashi_lean4.git",
    "chboishabba/dashi_agda": "https://github.com/chboishabba/dashi_agda.git",
}


@dataclass(frozen=True)
class Checkout:
    path: Path
    repository: str
    commit_sha: str


@dataclass(frozen=True)
class ExecutionOutcome:
    status: str
    argv: list[str]
    exit_code: int | None
    stdout: str
    stderr: str
    elapsed_seconds: float
    runtime: dict[str, Any]
    toolchain: dict[str, Any]
    resolved_commit_sha: str


def redact_text(text: str, secrets: Sequence[str]) -> str:
    out = text
    for secret in sorted((x for x in secrets if x), key=len, reverse=True):
        out = out.replace(secret, "[REDACTED]")
    return out


def chunk_log(data: bytes, max_bytes: int) -> list[bytes]:
    if max_bytes <= 0:
        raise ValueError("max_bytes must be positive")
    return [data[i:i + max_bytes] for i in range(0, len(data), max_bytes)] or [b""]


def _run_checked(argv: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(argv, cwd=cwd, capture_output=True, text=True, shell=False, check=True)


def prepare_checkout(repository: str, commit_sha: str, workspace: Path) -> Checkout:
    if repository not in REPO_URLS:
        raise ValueError("repository is not allowed")
    checkout = workspace / repository.replace("/", "__") / commit_sha
    if checkout.exists():
        shutil.rmtree(checkout)
    checkout.parent.mkdir(parents=True, exist_ok=True)
    _run_checked(["git", "clone", "--filter=blob:none", "--no-checkout", REPO_URLS[repository], str(checkout)])
    _run_checked(["git", "fetch", "--depth=1", "origin", commit_sha], cwd=checkout)
    _run_checked(["git", "checkout", "--detach", commit_sha], cwd=checkout)
    resolved = _run_checked(["git", "rev-parse", "HEAD"], cwd=checkout).stdout.strip()
    if resolved.lower() != commit_sha.lower():
        raise RuntimeError("checkout did not resolve to requested commit")

    if repository == "chboishabba/dashi_agda":
        for sub in ["DCHoTT-Agda", "cubical", "vendor/bishop"]:
            if (checkout / ".gitmodules").exists():
                subprocess.run(
                    ["git", "submodule", "update", "--init", "--depth=1", sub],
                    cwd=checkout,
                    capture_output=True,
                    text=True,
                    shell=False,
                )

    if repository == "chboishabba/dashi_lean4":
        if (checkout / "lakefile.toml").exists() or (checkout / "lakefile.lean").exists():
            if shutil.which("elan"):
                subprocess.run(
                    ["elan", "override", "set", "v4.28.0"],
                    cwd=checkout,
                    capture_output=True,
                    text=True,
                    shell=False,
                )
            if shutil.which("lake"):
                subprocess.run(
                    ["lake", "exe", "cache", "get"],
                    cwd=checkout,
                    capture_output=True,
                    text=True,
                    shell=False,
                )

    return Checkout(checkout, repository, resolved)


def _minimal_env() -> dict[str, str]:
    keep = {"PATH", "HOME", "LANG", "LC_ALL", "ELAN_HOME", "AGDA_DIR", "XDG_CACHE_HOME"}
    return {k: v for k, v in os.environ.items() if k in keep}


def execute_job(job: ProverJob, checkout: Checkout, secrets: Sequence[str] = ()) -> ExecutionOutcome:
    validate_job_policy(job)
    argv = build_argv(job, checkout.path)
    runtime_before = collect_runtime_receipt(job.operation, checkout.path).to_dict()
    started = time.monotonic()
    try:
        cp = subprocess.run(
            argv,
            cwd=checkout.path,
            capture_output=True,
            text=True,
            shell=False,
            timeout=job.timeout_seconds,
            env=_minimal_env(),
        )
        elapsed = time.monotonic() - started
        status = "SUCCEEDED" if cp.returncode == 0 else "FAILED"
        stdout = redact_text(cp.stdout or "", secrets)
        stderr = redact_text(cp.stderr or "", secrets)
        exit_code: int | None = cp.returncode
    except subprocess.TimeoutExpired as exc:
        elapsed = time.monotonic() - started
        status = "ABORTED"
        stdout = redact_text((exc.stdout or "") if isinstance(exc.stdout, str) else "", secrets)
        stderr = redact_text((exc.stderr or "") if isinstance(exc.stderr, str) else "", secrets)
        exit_code = None
    runtime_after = collect_runtime_receipt(job.operation, checkout.path).to_dict()
    runtime = {"before": runtime_before, "after": runtime_after}
    versions = runtime_after.get("versions", {})
    return ExecutionOutcome(
        status=status,
        argv=argv,
        exit_code=exit_code,
        stdout=stdout,
        stderr=stderr,
        elapsed_seconds=elapsed,
        runtime=runtime,
        toolchain=dict(versions),
        resolved_commit_sha=checkout.commit_sha,
    )


class Executor:
    def __init__(self, workspace: Path, secrets: Sequence[str] = ()):
        self.workspace = workspace
        self.secrets = tuple(secrets)
    def execute(self, job: ProverJob) -> ExecutionOutcome:
        checkout = prepare_checkout(job.repository, job.commit_sha, self.workspace)
        return execute_job(job, checkout, self.secrets)
