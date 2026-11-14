from __future__ import annotations

import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "colab-runner" / "src"))

from itir_colab_runner.github_relay import InMemoryContentStore, GitHubRelay, RelayConflict
from itir_colab_runner.github_store import GitHubContentsStore
from itir_colab_runner.model import load_job, ProverResult

SHA = "a" * 40


def job(job_id="job-1"):
    return load_job({
        "schema_version": "colab_prover_job_v1",
        "job_id": job_id,
        "repository": "chboishabba/dashi_lean4",
        "commit_sha": SHA,
        "operation": "lake_build",
        "arguments": {"target": "QuantumMereology"},
        "toolchain_policy": "repo_pinned",
        "requested_by": "pytest",
        "created_at": "2026-10-17T12:00:00Z",
        "resource_class": "high_mem",
        "timeout_seconds": 7200,
    })


def relay():
    return GitHubRelay(InMemoryContentStore(), branch="colab-runner-state")


def test_submit_is_idempotent_for_same_job_id_and_digest():
    r = relay(); j = job()
    assert r.submit_job(j) == r.submit_job(j)


def test_conflicting_job_id_reuse_is_rejected():
    r = relay(); r.submit_job(job())
    j2 = job(); object.__setattr__(j2, "commit_sha", "b" * 40)
    with pytest.raises(RelayConflict):
        r.submit_job(j2)


def test_only_one_worker_wins_initial_claim():
    r = relay(); j = job(); r.submit_job(j)
    now = datetime.now(timezone.utc)
    assert r.try_create_claim(j, "w1", now) is not None
    assert r.try_create_claim(j, "w2", now) is None


def test_claim_generation_paths_are_append_only():
    r = relay(); j = job(); r.submit_job(j)
    c0 = r.try_create_claim(j, "w1", datetime.now(timezone.utc))
    assert c0.generation == 0
    c1 = r.create_takeover_claim(j, c0, "w2", c0.claimed_at + timedelta(hours=2))
    assert c1.generation == 1
    assert r.store.exists(".itir/colab/claims/job-1.0000.json")
    assert r.store.exists(".itir/colab/claims/job-1.0001.json")


def test_log_chunks_have_deterministic_order_and_sha256():
    r = relay()
    refs = r.publish_log_chunks("job-1", [b"abc", b"def"])
    assert [x.index for x in refs] == [0, 1]
    assert all(len(x.sha256) == 64 for x in refs)


def test_publish_result_is_idempotent_for_same_terminal_receipt():
    r = relay()
    result = ProverResult.minimal_success(job(), ["lake", "build", "QuantumMereology"])
    r.publish_result(result); r.publish_result(result)


def test_publish_result_rejects_conflicting_terminal_receipt():
    r = relay()
    a = ProverResult.minimal_success(job(), ["lake", "build", "QuantumMereology"])
    b = ProverResult.minimal_failure(job(), ["lake", "build", "QuantumMereology"], 1)
    r.publish_result(a)
    with pytest.raises(RelayConflict):
        r.publish_result(b)


def test_github_store_translates_filename_prefix_to_parent_directory_listing():
    class FakeGitHubStore(GitHubContentsStore):
        def __init__(self):
            super().__init__("owner/repo", "token")
            self.requested = []
        def _req(self, method, path, payload=None):
            self.requested.append((method, path))
            assert method == "GET"
            assert path == ".itir/colab/claims"
            return [
                {"type": "file", "path": ".itir/colab/claims/job-1.0000.json"},
                {"type": "file", "path": ".itir/colab/claims/job-2.0000.json"},
            ]
    store = FakeGitHubStore()
    assert store.list_paths(".itir/colab/claims/job-1.") == [
        ".itir/colab/claims/job-1.0000.json"
    ]
