from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
import json
import re
from typing import Any, Mapping

ALLOWED_REPOSITORIES = {
    "chboishabba/dashi_lean4",
    "chboishabba/dashi_agda",
}
ALLOWED_OPERATIONS = {"lake_build", "lake_env_lean", "agda_module"}
TERMINAL_STATUSES = {"SUCCEEDED", "FAILED", "REJECTED", "ABORTED"}
SHA40 = re.compile(r"^[0-9a-fA-F]{40}$")
ID_RE = re.compile(r"^[A-Za-z0-9._-]{1,128}$")


@dataclass(frozen=True)
class ProverJob:
    schema_version: str
    job_id: str
    repository: str
    commit_sha: str
    operation: str
    arguments: dict[str, Any]
    toolchain_policy: str
    requested_by: str
    created_at: str
    resource_class: str
    timeout_seconds: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ClaimReceipt:
    job_id: str
    job_digest: str
    worker_id: str
    generation: int
    claimed_at: datetime
    lease_expires_at: datetime

    def to_dict(self) -> dict[str, Any]:
        return {
            "job_id": self.job_id,
            "job_digest": self.job_digest,
            "worker_id": self.worker_id,
            "generation": self.generation,
            "claimed_at": self.claimed_at.isoformat(),
            "lease_expires_at": self.lease_expires_at.isoformat(),
        }


@dataclass(frozen=True)
class LogChunkRef:
    index: int
    path: str
    sha256: str
    size_bytes: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ProverResult:
    schema_version: str
    job_id: str
    job_digest: str
    repository: str
    resolved_commit_sha: str
    status: str
    argv: list[str]
    started_at: str
    finished_at: str
    elapsed_seconds: float
    exit_code: int | None
    runtime: dict[str, Any]
    toolchain: dict[str, Any]
    logs: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def minimal_success(cls, job: ProverJob, argv: list[str]) -> "ProverResult":
        now = datetime.now(timezone.utc).isoformat()
        return cls("colab_prover_result_v1", job.job_id, job_digest(job), job.repository,
                   job.commit_sha, "SUCCEEDED", argv, now, now, 0.0, 0, {}, {}, [])

    @classmethod
    def minimal_failure(cls, job: ProverJob, argv: list[str], exit_code: int) -> "ProverResult":
        now = datetime.now(timezone.utc).isoformat()
        return cls("colab_prover_result_v1", job.job_id, job_digest(job), job.repository,
                   job.commit_sha, "FAILED", argv, now, now, 0.0, exit_code, {}, {}, [])


def canonical_json_bytes(value: object) -> bytes:
    if hasattr(value, "to_dict"):
        value = value.to_dict()
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def job_digest(job: ProverJob) -> str:
    return sha256(canonical_json_bytes(job)).hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def load_job(data: Mapping[str, object]) -> ProverJob:
    required = {
        "schema_version", "job_id", "repository", "commit_sha", "operation",
        "arguments", "toolchain_policy", "requested_by", "created_at",
        "resource_class", "timeout_seconds",
    }
    _require(set(data) == required, "job keys do not match v1 schema")
    _require(data["schema_version"] == "colab_prover_job_v1", "invalid job schema_version")
    _require(isinstance(data["job_id"], str) and bool(ID_RE.fullmatch(data["job_id"])), "invalid job_id")
    _require(data["repository"] in ALLOWED_REPOSITORIES, "repository is not allowed")
    _require(isinstance(data["commit_sha"], str) and bool(SHA40.fullmatch(data["commit_sha"])), "commit_sha must be exact 40-hex")
    _require(data["operation"] in ALLOWED_OPERATIONS, "operation is not allowed")
    _require(isinstance(data["arguments"], dict), "arguments must be an object")
    _require(data["toolchain_policy"] == "repo_pinned", "unsupported toolchain policy")
    _require(data["resource_class"] == "high_mem", "unsupported resource class")
    _require(isinstance(data["timeout_seconds"], int) and 1 <= data["timeout_seconds"] <= 21600, "invalid timeout")
    _require(isinstance(data["requested_by"], str) and bool(data["requested_by"]), "requested_by required")
    _require(isinstance(data["created_at"], str) and bool(data["created_at"]), "created_at required")
    return ProverJob(**dict(data))  # type: ignore[arg-type]


def load_result(data: Mapping[str, object]) -> ProverResult:
    required = {
        "schema_version", "job_id", "job_digest", "repository", "resolved_commit_sha",
        "status", "argv", "started_at", "finished_at", "elapsed_seconds", "exit_code",
        "runtime", "toolchain", "logs",
    }
    _require(set(data) == required, "result keys do not match v1 schema")
    _require(data["schema_version"] == "colab_prover_result_v1", "invalid result schema_version")
    _require(data["status"] in TERMINAL_STATUSES, "invalid terminal result status")
    _require(data["repository"] in ALLOWED_REPOSITORIES, "repository is not allowed")
    _require(isinstance(data["resolved_commit_sha"], str) and bool(SHA40.fullmatch(data["resolved_commit_sha"])), "invalid resolved sha")
    _require(isinstance(data["job_digest"], str) and bool(re.fullmatch(r"[0-9a-f]{64}", data["job_digest"])), "invalid job digest")
    _require(isinstance(data["argv"], list) and all(isinstance(x, str) for x in data["argv"]), "argv must be string list")
    return ProverResult(**dict(data))  # type: ignore[arg-type]
