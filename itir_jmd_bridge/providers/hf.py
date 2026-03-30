from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import time
import re
import subprocess
from typing import Any, Callable

import requests


def _strip_trailing_slash(value: str) -> str:
    return value[:-1] if value.endswith("/") else value


def _is_transient_hf_upload_error(detail: str, returncode: int | None = None) -> bool:
    text = detail.lower()
    transient_markers = (
        "temporary failure in name resolution",
        "name or service not known",
        "failed to resolve",
        "connection reset",
        "connection aborted",
        "connection refused",
        "timed out",
        "timeout",
        "tlsv1 alert internal error",
        "remote disconnected",
        "network is unreachable",
    )
    if any(marker in text for marker in transient_markers):
        return True
    return returncode in {6, 7, 28}


@dataclass(frozen=True)
class HfObjectReference:
    repo_type: str
    repo_id: str
    object_path: str

    @property
    def resolve_url(self) -> str:
        return f"https://huggingface.co/{self.repo_type}/{self.repo_id}/resolve/main/{self.object_path}"

    def resolve_url_for_revision(self, revision: str) -> str:
        return f"https://huggingface.co/{self.repo_type}/{self.repo_id}/resolve/{revision}/{self.object_path}"


def parse_hf_uri(uri: str) -> HfObjectReference:
    if not uri.startswith("hf://"):
        raise ValueError(f"unsupported HF URI: {uri}")
    payload = uri[len("hf://") :]
    parts = [part for part in payload.split("/") if part]
    if len(parts) < 4:
        raise ValueError(f"HF URI must include type, repo id, and object path: {uri}")
    repo_type = parts[0]
    if repo_type not in {"datasets", "models", "spaces"}:
        raise ValueError(f"unsupported HF repo type: {repo_type}")
    repo_id = f"{parts[1]}/{parts[2]}"
    object_path = "/".join(parts[3:])
    return HfObjectReference(repo_type=repo_type, repo_id=repo_id, object_path=object_path)


def probe_hf_resolve_acknowledgement(
    *,
    hf_uri: str,
    head: Callable[..., Any] | None = None,
    timeout: float = 20.0,
) -> dict[str, Any]:
    reference = parse_hf_uri(hf_uri)
    caller = head or requests.head
    response = caller(reference.resolve_url, allow_redirects=True, timeout=timeout)
    if hasattr(response, "raise_for_status"):
        response.raise_for_status()
    history = list(getattr(response, "history", []) or [])
    chain = [
        {
            "status_code": getattr(item, "status_code", None),
            "url": getattr(item, "url", None),
            "location": getattr(item, "headers", {}).get("location"),
            "etag": getattr(item, "headers", {}).get("etag"),
            "x_repo_commit": getattr(item, "headers", {}).get("x-repo-commit"),
            "x_linked_etag": getattr(item, "headers", {}).get("x-linked-etag"),
        }
        for item in history
    ]
    final_headers = getattr(response, "headers", {})
    return {
        "repoType": reference.repo_type,
        "repoId": reference.repo_id,
        "objectPath": reference.object_path,
        "resolveUrl": reference.resolve_url,
        "statusCode": getattr(response, "status_code", 200),
        "finalUrl": getattr(response, "url", reference.resolve_url),
        "etag": final_headers.get("etag"),
        "xRepoCommit": final_headers.get("x-repo-commit"),
        "contentLength": final_headers.get("content-length"),
        "acceptRanges": final_headers.get("accept-ranges"),
        "contentDisposition": final_headers.get("content-disposition"),
        "redirectChain": chain,
    }


def fetch_hf_object(
    *,
    hf_uri: str,
    revision: str | None = None,
    get: Callable[..., Any] | None = None,
    timeout: float = 20.0,
) -> dict[str, Any]:
    reference = parse_hf_uri(hf_uri)
    caller = get or requests.get
    url = reference.resolve_url_for_revision(revision) if revision else reference.resolve_url
    response = caller(url, allow_redirects=True, timeout=timeout)
    if hasattr(response, "raise_for_status"):
        response.raise_for_status()
    content = response.content if hasattr(response, "content") else bytes(str(response), "utf-8")
    headers = getattr(response, "headers", {})
    history = list(getattr(response, "history", []) or [])
    history_headers = [getattr(item, "headers", {}) for item in history]
    x_repo_commit = headers.get("x-repo-commit")
    if x_repo_commit is None:
        for item_headers in reversed(history_headers):
            x_repo_commit = item_headers.get("x-repo-commit")
            if x_repo_commit:
                break
    effective_etag = headers.get("etag")
    if effective_etag is None:
        for item_headers in reversed(history_headers):
            effective_etag = item_headers.get("x-linked-etag") or item_headers.get("etag")
            if effective_etag:
                break
    binary_like = b"\x00" in content
    return {
        "repoType": reference.repo_type,
        "repoId": reference.repo_id,
        "objectPath": reference.object_path,
        "resolveUrl": url,
        "finalUrl": getattr(response, "url", url),
        "statusCode": getattr(response, "status_code", 200),
        "revision": revision,
        "etag": effective_etag,
        "xRepoCommit": x_repo_commit,
        "contentLength": headers.get("content-length"),
        "sha256": sha256(content).hexdigest(),
        "sizeBytes": len(content),
        "text": None if binary_like else content.decode("utf-8", "replace"),
        "textPreview": None if not binary_like else content[:64].hex(),
    }


def download_hf_object_bytes(
    *,
    hf_uri: str,
    revision: str | None = None,
    get: Callable[..., Any] | None = None,
    timeout: float = 20.0,
) -> dict[str, Any]:
    reference = parse_hf_uri(hf_uri)
    caller = get or requests.get
    url = reference.resolve_url_for_revision(revision) if revision else reference.resolve_url
    response = caller(url, allow_redirects=True, timeout=timeout)
    if hasattr(response, "raise_for_status"):
        response.raise_for_status()
    content = response.content if hasattr(response, "content") else bytes(str(response), "utf-8")
    fetched = fetch_hf_object(
        hf_uri=hf_uri,
        revision=revision,
        get=lambda *args, **kwargs: response,
    )
    return {
        "bytes": content,
        "metadata": fetched,
    }


def upload_hf_file_with_ack(
    *,
    local_path: str,
    hf_uri: str,
    commit_message: str | None = None,
    run: Callable[..., Any] | None = None,
    fetch: Callable[..., dict[str, Any]] | None = None,
    max_attempts: int = 2,
    retry_delay_seconds: float = 1.0,
) -> dict[str, Any]:
    reference = parse_hf_uri(hf_uri)
    object_path = reference.object_path
    cli = run or subprocess.run
    local_bytes = open(local_path, "rb").read()
    local_sha256 = sha256(local_bytes).hexdigest()
    repo_type_flag = {
        "datasets": "dataset",
        "models": "model",
        "spaces": "space",
    }[reference.repo_type]
    command = [
        "hf",
        "upload",
        reference.repo_id,
        local_path,
        object_path,
        "--repo-type",
        repo_type_flag,
    ]
    if commit_message:
        command.extend(["--commit-message", commit_message])
    completed = None
    last_error = None
    for attempt in range(1, max_attempts + 1):
        try:
            completed = cli(
                command,
                check=True,
                capture_output=True,
                text=True,
            )
            break
        except subprocess.CalledProcessError as error:
            stdout = getattr(error, "stdout", "") or ""
            stderr = getattr(error, "stderr", "") or ""
            detail = "\n".join(part for part in [stdout.strip(), stderr.strip()] if part)
            last_error = error
            if attempt < max_attempts and _is_transient_hf_upload_error(
                detail, error.returncode
            ):
                time.sleep(retry_delay_seconds)
                continue
            raise RuntimeError(
                f"HF upload failed for {hf_uri} with exit code {error.returncode}"
                + (f": {detail}" if detail else "")
            ) from error
    if completed is None:
        assert last_error is not None
        raise RuntimeError(f"HF upload failed for {hf_uri} after {max_attempts} attempts") from last_error
    stdout = getattr(completed, "stdout", "") or ""
    stderr = getattr(completed, "stderr", "") or ""
    combined = "\n".join(part for part in [stdout, stderr] if part)
    match = re.search(r"/commit/([0-9a-f]{40})", combined)
    if not match:
        raise RuntimeError(f"unable to parse HF commit acknowledgement from upload output: {combined}")
    revision = match.group(1)
    fetched = (fetch or fetch_hf_object)(hf_uri=hf_uri, revision=revision)
    return {
        "sink": "hf",
        "repoType": reference.repo_type,
        "repoId": reference.repo_id,
        "objectPath": object_path,
        "hfUri": hf_uri,
        "localPath": local_path,
        "acknowledgedRevision": revision,
        "localSha256": local_sha256,
        "localSizeBytes": len(local_bytes),
        "fetch": fetched,
        "verified": fetched.get("sha256") == local_sha256,
    }
