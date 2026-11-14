from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "tools" / "colab-runner" / "src"
sys.path.insert(0, str(SRC))

from itir_colab_runner.model import job_digest, load_job, load_result
from itir_colab_runner.policy import build_argv, validate_relative_source_path

LEAN_REPO = "chboishabba/dashi_lean4"
AGDA_REPO = "chboishabba/dashi_agda"
SHA = "a" * 40


def _job(**overrides):
    value = {
        "schema_version": "colab_prover_job_v1",
        "job_id": "job-001",
        "repository": LEAN_REPO,
        "commit_sha": SHA,
        "operation": "lake_build",
        "arguments": {"target": "QuantumMereology"},
        "toolchain_policy": "repo_pinned",
        "requested_by": "pytest",
        "created_at": "2026-10-17T12:00:00Z",
        "resource_class": "high_mem",
        "timeout_seconds": 7200,
    }
    value.update(overrides)
    return value


def test_valid_lake_build_job_round_trips():
    job = load_job(_job())
    assert job.repository == LEAN_REPO
    assert job.operation == "lake_build"
    assert job.arguments == {"target": "QuantumMereology"}


def test_valid_agda_module_job_round_trips():
    job = load_job(_job(repository=AGDA_REPO, operation="agda_module", arguments={"path": "DASHI/Physics/CanonicalClayFrontierExact.agda", "profile": "repo"}))
    assert job.repository == AGDA_REPO
    assert job.operation == "agda_module"


def test_job_requires_exact_40_hex_sha():
    with pytest.raises(ValueError):
        load_job(_job(commit_sha="main"))


def test_unknown_repository_is_rejected():
    with pytest.raises(ValueError):
        load_job(_job(repository="example/evil"))


def test_unknown_operation_is_rejected():
    with pytest.raises(ValueError):
        load_job(_job(operation="shell", arguments={"command": "id"}))


def test_canonical_job_digest_is_stable_across_key_order():
    a = _job()
    b = dict(reversed(list(a.items())))
    assert job_digest(load_job(a)) == job_digest(load_job(b))


def test_result_status_is_limited_to_terminal_v1_values():
    base = {
        "schema_version": "colab_prover_result_v1",
        "job_id": "job-001",
        "job_digest": "b" * 64,
        "repository": LEAN_REPO,
        "resolved_commit_sha": SHA,
        "status": "SUCCEEDED",
        "argv": ["lake", "build", "QuantumMereology"],
        "started_at": "2026-10-17T12:00:00Z",
        "finished_at": "2026-10-17T12:01:00Z",
        "elapsed_seconds": 60.0,
        "exit_code": 0,
        "runtime": {},
        "toolchain": {},
        "logs": [],
    }
    assert load_result(base).status == "SUCCEEDED"
    base["status"] = "MAYBE"
    with pytest.raises(ValueError):
        load_result(base)


def test_lake_build_argv_is_vector_not_shell_string(tmp_path: Path):
    job = load_job(_job())
    assert build_argv(job, tmp_path) == ["lake", "build", "QuantumMereology"]


def test_lake_env_lean_rejects_absolute_path(tmp_path: Path):
    with pytest.raises(ValueError):
        validate_relative_source_path(tmp_path, "/tmp/x.lean", ".lean")


def test_lake_env_lean_rejects_parent_traversal(tmp_path: Path):
    with pytest.raises(ValueError):
        validate_relative_source_path(tmp_path, "../x.lean", ".lean")


def test_lake_env_lean_rejects_wrong_suffix(tmp_path: Path):
    p = tmp_path / "x.agda"
    p.write_text("", encoding="utf-8")
    with pytest.raises(ValueError):
        validate_relative_source_path(tmp_path, "x.agda", ".lean")


def test_agda_module_rejects_parent_traversal(tmp_path: Path):
    job = load_job(_job(repository=AGDA_REPO, operation="agda_module", arguments={"path": "../x.agda", "profile": "repo"}))
    with pytest.raises(ValueError):
        build_argv(job, tmp_path)


def test_shell_metacharacters_do_not_create_shell_execution_surface(tmp_path: Path):
    job = load_job(_job(arguments={"target": "X; touch PWNED"}))
    with pytest.raises(ValueError):
        build_argv(job, tmp_path)


def test_symlink_escape_is_rejected(tmp_path: Path):
    outside = tmp_path.parent / "outside.lean"
    outside.write_text("", encoding="utf-8")
    link = tmp_path / "link.lean"
    link.symlink_to(outside)
    with pytest.raises(ValueError):
        validate_relative_source_path(tmp_path, "link.lean", ".lean")


def test_operator_docs_pin_required_launcher_contract():
    readme = (ROOT / "tools" / "colab-runner" / "README.md").read_text(encoding="utf-8")
    notebook = (ROOT / "docs" / "colab-prover-runner-notebook.md").read_text(encoding="utf-8")
    joined = readme + notebook
    for needle in [
        "python scripts/colab_bootstrap_provers.py",
        "python scripts/colab_worker.py --poll",
        "colab-runner-state",
        "Colab Secrets",
        "006ff96ac2d0e4dcfb702467a76493d687929be8",
        "b9ab3899e0f1fa493390b1fd6d54aa2e464ecdf1",
        "launcher",
    ]:
        assert needle in joined
    assert "run Lean locally" not in joined
