from __future__ import annotations

import base64
from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json
from typing import Protocol, Sequence
from urllib import error, parse, request

from .model import ClaimReceipt, LogChunkRef, ProverJob, ProverResult, canonical_json_bytes, job_digest, load_job, load_result

STATE_BRANCH = "colab-runner-state"


class RelayConflict(RuntimeError):
    pass


class ContentStore(Protocol):
    def create(self, path: str, content: bytes) -> bool: ...
    def read(self, path: str) -> bytes | None: ...
    def list_paths(self, prefix: str) -> list[str]: ...
    def exists(self, path: str) -> bool: ...


class InMemoryContentStore:
    def __init__(self):
        self._data: dict[str, bytes] = {}
    def create(self, path: str, content: bytes) -> bool:
        if path in self._data:
            return False
        self._data[path] = bytes(content)
        return True
    def read(self, path: str) -> bytes | None:
        return self._data.get(path)
    def list_paths(self, prefix: str) -> list[str]:
        return sorted(p for p in self._data if p.startswith(prefix))
    def exists(self, path: str) -> bool:
        return path in self._data
    def paths(self) -> list[str]:
        return sorted(self._data)


class GitHubContentsStore:
    """Minimal GitHub Contents API adapter scoped to one repository/branch."""
    def __init__(self, repository: str, token: str, branch: str = STATE_BRANCH):
        self.repository = repository
        self.token = token
        self.branch = branch
        self.base = f"https://api.github.com/repos/{repository}/contents"

    def _req(self, method: str, path: str, payload: dict | None = None):
        url = f"{self.base}/{parse.quote(path, safe='/')}"
        if method == "GET":
            url += "?" + parse.urlencode({"ref": self.branch})
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        req = request.Request(url, data=data, method=method, headers={
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
        })
        try:
            with request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except error.HTTPError as exc:
            if exc.code in (404, 409, 422):
                return None
            raise

    def create(self, path: str, content: bytes) -> bool:
        payload = {
            "message": f"colab-runner: create {path}",
            "content": base64.b64encode(content).decode("ascii"),
            "branch": self.branch,
        }
        return self._req("PUT", path, payload) is not None

    def read(self, path: str) -> bytes | None:
        obj = self._req("GET", path)
        if not obj or isinstance(obj, list):
            return None
        return base64.b64decode(obj["content"])

    def list_paths(self, prefix: str) -> list[str]:
        obj = self._req("GET", prefix.rstrip("/"))
        if not isinstance(obj, list):
            return []
        return sorted(x["path"] for x in obj if x.get("type") == "file")

    def exists(self, path: str) -> bool:
        return self.read(path) is not None


class GitHubRelay:
    def __init__(self, store: ContentStore, branch: str = STATE_BRANCH, lease_seconds: int = 3600):
        if branch != STATE_BRANCH:
            raise ValueError(f"runtime state branch must be {STATE_BRANCH}")
        self.store = store
        self.branch = branch
        self.lease_seconds = lease_seconds
        self.fail_next_result_publish = False  # injectable failure hook used by offline tests

    @staticmethod
    def _job_path(job_id: str) -> str:
        return f".itir/colab/jobs/{job_id}.json"
    @staticmethod
    def _result_path(job_id: str) -> str:
        return f".itir/colab/results/{job_id}.json"
    @staticmethod
    def _claim_path(job_id: str, generation: int) -> str:
        return f".itir/colab/claims/{job_id}.{generation:04d}.json"

    def submit_job(self, job: ProverJob) -> str:
        path = self._job_path(job.job_id)
        payload = canonical_json_bytes(job)
        if self.store.create(path, payload):
            return job_digest(job)
        existing = self.store.read(path)
        if existing != payload:
            raise RelayConflict(f"conflicting reuse of job id {job.job_id}")
        return job_digest(job)

    def list_pending_jobs(self) -> list[str]:
        ids = []
        for path in self.store.list_paths(".itir/colab/jobs/"):
            job_id = path.rsplit("/", 1)[-1].removesuffix(".json")
            if not self.store.exists(self._result_path(job_id)):
                ids.append(job_id)
        return sorted(ids)

    def read_job(self, job_id: str) -> ProverJob:
        raw = self.store.read(self._job_path(job_id))
        if raw is None:
            raise KeyError(job_id)
        return load_job(json.loads(raw.decode("utf-8")))

    def _claims(self, job_id: str) -> list[ClaimReceipt]:
        out = []
        for path in self.store.list_paths(f".itir/colab/claims/{job_id}."):
            raw = self.store.read(path)
            if raw is None:
                continue
            d = json.loads(raw.decode("utf-8"))
            out.append(ClaimReceipt(
                d["job_id"], d["job_digest"], d["worker_id"], int(d["generation"]),
                datetime.fromisoformat(d["claimed_at"]), datetime.fromisoformat(d["lease_expires_at"]),
            ))
        return sorted(out, key=lambda x: x.generation)

    def try_create_claim(self, job: ProverJob, worker_id: str, now: datetime) -> ClaimReceipt | None:
        if self._claims(job.job_id):
            return None
        claim = ClaimReceipt(job.job_id, job_digest(job), worker_id, 0, now, now + timedelta(seconds=self.lease_seconds))
        if not self.store.create(self._claim_path(job.job_id, 0), canonical_json_bytes(claim.to_dict())):
            return None
        return claim

    def create_takeover_claim(self, job: ProverJob, previous: ClaimReceipt, worker_id: str, now: datetime) -> ClaimReceipt:
        if now < previous.lease_expires_at:
            raise RelayConflict("claim lease has not expired")
        generation = previous.generation + 1
        claim = ClaimReceipt(job.job_id, job_digest(job), worker_id, generation, now, now + timedelta(seconds=self.lease_seconds))
        if not self.store.create(self._claim_path(job.job_id, generation), canonical_json_bytes(claim.to_dict())):
            raise RelayConflict("takeover generation already exists")
        return claim

    def latest_claim(self, job_id: str) -> ClaimReceipt | None:
        claims = self._claims(job_id)
        return claims[-1] if claims else None

    def publish_log_chunks(self, job_id: str, chunks: Sequence[bytes]) -> list[LogChunkRef]:
        refs = []
        for index, chunk in enumerate(chunks):
            path = f".itir/colab/logs/{job_id}/{index:04d}.txt"
            digest = sha256(chunk).hexdigest()
            if not self.store.create(path, chunk):
                if self.store.read(path) != chunk:
                    raise RelayConflict(f"conflicting log chunk {path}")
            refs.append(LogChunkRef(index, path, digest, len(chunk)))
        return refs

    def publish_result(self, result: ProverResult) -> None:
        if self.fail_next_result_publish:
            self.fail_next_result_publish = False
            raise OSError("injected result publish failure")
        path = self._result_path(result.job_id)
        payload = canonical_json_bytes(result)
        if self.store.create(path, payload):
            return
        if self.store.read(path) != payload:
            raise RelayConflict(f"conflicting terminal result for {result.job_id}")

    def read_result(self, job_id: str) -> ProverResult:
        raw = self.store.read(self._result_path(job_id))
        if raw is None:
            raise KeyError(job_id)
        return load_result(json.loads(raw.decode("utf-8")))
