from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import time
from typing import Protocol

from .executor import ExecutionOutcome, chunk_log
from .github_relay import GitHubRelay, RelayConflict
from .model import ProverResult, canonical_json_bytes, job_digest, load_result


class ExecutorLike(Protocol):
    def execute(self, job): ...


@dataclass(frozen=True)
class WorkerOutcome:
    status: str
    job_id: str | None = None
    detail: str | None = None


def _durable_path(durable_dir: Path, job_id: str) -> Path:
    return durable_dir / f"{job_id}.terminal.json"


def _retry_durable(relay: GitHubRelay, durable_dir: Path) -> WorkerOutcome | None:
    durable_dir.mkdir(parents=True, exist_ok=True)
    for path in sorted(durable_dir.glob("*.terminal.json")):
        result = load_result(json.loads(path.read_text(encoding="utf-8")))
        try:
            relay.publish_result(result)
        except OSError as exc:
            return WorkerOutcome("PUBLISH_PENDING", result.job_id, str(exc))
        path.unlink()
        return WorkerOutcome(result.status, result.job_id)
    return None


def _result_from_outcome(job, outcome: ExecutionOutcome, logs) -> ProverResult:
    finished = datetime.now(timezone.utc)
    started = finished - timedelta(seconds=outcome.elapsed_seconds)
    return ProverResult(
        schema_version="colab_prover_result_v1",
        job_id=job.job_id,
        job_digest=job_digest(job),
        repository=job.repository,
        resolved_commit_sha=outcome.resolved_commit_sha,
        status=outcome.status,
        argv=list(outcome.argv),
        started_at=started.isoformat(),
        finished_at=finished.isoformat(),
        elapsed_seconds=float(outcome.elapsed_seconds),
        exit_code=outcome.exit_code,
        runtime=dict(outcome.runtime),
        toolchain=dict(outcome.toolchain),
        logs=[x.to_dict() for x in logs],
    )


def run_one_job(
    relay: GitHubRelay,
    executor: ExecutorLike,
    worker_id: str,
    now: datetime,
    *,
    durable_dir: Path | None = None,
    log_chunk_bytes: int = 512 * 1024,
) -> WorkerOutcome:
    durable_dir = durable_dir or Path("/tmp/itir-colab-runner-pending")
    retry = _retry_durable(relay, durable_dir)
    if retry is not None:
        return retry

    pending = relay.list_pending_jobs()
    if not pending:
        return WorkerOutcome("IDLE")
    job = relay.read_job(pending[0])

    latest = relay.latest_claim(job.job_id)
    if latest is None:
        claim = relay.try_create_claim(job, worker_id, now)
        if claim is None:
            return WorkerOutcome("IDLE", job.job_id, "claim lost")
    else:
        if now < latest.lease_expires_at:
            return WorkerOutcome("IDLE", job.job_id, "already claimed")
        try:
            relay.create_takeover_claim(job, latest, worker_id, now)
        except RelayConflict:
            return WorkerOutcome("IDLE", job.job_id, "takeover lost")

    outcome = executor.execute(job)
    log_text = f"STDOUT\n{outcome.stdout}\nSTDERR\n{outcome.stderr}".encode("utf-8")
    refs = relay.publish_log_chunks(job.job_id, chunk_log(log_text, log_chunk_bytes))
    result = _result_from_outcome(job, outcome, refs)
    durable_dir.mkdir(parents=True, exist_ok=True)
    durable = _durable_path(durable_dir, job.job_id)
    durable.write_bytes(canonical_json_bytes(result))
    try:
        relay.publish_result(result)
    except OSError as exc:
        return WorkerOutcome("PUBLISH_PENDING", job.job_id, str(exc))
    durable.unlink(missing_ok=True)
    return WorkerOutcome(result.status, job.job_id)


def run_poll_loop(relay: GitHubRelay, executor: ExecutorLike, worker_id: str, *, poll_seconds: float = 10.0, durable_dir: Path | None = None) -> None:
    while True:
        run_one_job(relay, executor, worker_id, datetime.now(timezone.utc), durable_dir=durable_dir)
        time.sleep(poll_seconds)
