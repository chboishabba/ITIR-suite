from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "colab-runner" / "src"))

from itir_colab_runner.executor import ExecutionOutcome, redact_text, chunk_log
from itir_colab_runner.github_relay import InMemoryContentStore, GitHubRelay
from itir_colab_runner.model import load_job
from itir_colab_runner.worker import run_one_job

SHA = "a" * 40


def job():
    return load_job({
        "schema_version": "colab_prover_job_v1", "job_id": "job-1",
        "repository": "chboishabba/dashi_lean4", "commit_sha": SHA,
        "operation": "lake_build", "arguments": {"target": "QuantumMereology"},
        "toolchain_policy": "repo_pinned", "requested_by": "pytest",
        "created_at": "2026-10-17T12:00:00Z", "resource_class": "high_mem",
        "timeout_seconds": 7200,
    })


class FakeExecutor:
    def __init__(self, exit_code=0):
        self.calls = 0; self.exit_code = exit_code
    def execute(self, j):
        self.calls += 1
        return ExecutionOutcome(
            status="SUCCEEDED" if self.exit_code == 0 else "FAILED",
            argv=["lake", "build", "QuantumMereology"],
            exit_code=self.exit_code, stdout="ok\n", stderr="", elapsed_seconds=1.0,
            runtime={}, toolchain={"lake": "fake"}, resolved_commit_sha=j.commit_sha,
        )


def prepared_relay():
    r = GitHubRelay(InMemoryContentStore(), branch="colab-runner-state")
    r.submit_job(job())
    return r


def test_secret_redaction_removes_configured_token_values():
    assert "SECRET" not in redact_text("token=SECRET", ["SECRET"])


def test_log_chunking_respects_max_bytes_and_reassembles_exactly():
    data = b"abcdefghij"
    chunks = chunk_log(data, 3)
    assert all(len(x) <= 3 for x in chunks)
    assert b"".join(chunks) == data


def test_worker_claims_before_execution():
    r = prepared_relay(); e = FakeExecutor()
    out = run_one_job(r, e, "w1", datetime.now(timezone.utc))
    assert out.status == "SUCCEEDED"
    assert e.calls == 1
    assert r.store.exists(".itir/colab/claims/job-1.0000.json")


def test_claim_loser_does_not_execute():
    r = prepared_relay(); j = job(); now = datetime.now(timezone.utc)
    assert r.try_create_claim(j, "w1", now)
    e = FakeExecutor()
    out = run_one_job(r, e, "w2", now)
    assert out.status == "IDLE"
    assert e.calls == 0


def test_compiler_nonzero_publishes_failed_result():
    r = prepared_relay(); e = FakeExecutor(exit_code=2)
    out = run_one_job(r, e, "w1", datetime.now(timezone.utc))
    assert out.status == "FAILED"
    assert r.read_result("job-1").status == "FAILED"


def test_publish_failure_retains_local_terminal_result_for_retry_without_reexecution(tmp_path: Path):
    r = prepared_relay(); e = FakeExecutor()
    r.fail_next_result_publish = True
    out1 = run_one_job(r, e, "w1", datetime.now(timezone.utc), durable_dir=tmp_path)
    assert out1.status == "PUBLISH_PENDING"
    assert e.calls == 1
    out2 = run_one_job(r, e, "w1", datetime.now(timezone.utc), durable_dir=tmp_path)
    assert out2.status == "SUCCEEDED"
    assert e.calls == 1


def test_worker_never_mutates_source_repository_or_pr_state():
    r = prepared_relay(); e = FakeExecutor()
    run_one_job(r, e, "w1", datetime.now(timezone.utc))
    assert all(path.startswith(".itir/colab/") for path in r.store.paths())
