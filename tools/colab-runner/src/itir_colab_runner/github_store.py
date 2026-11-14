from __future__ import annotations

import base64
import json
from pathlib import PurePosixPath
from urllib import error, parse, request

from .github_relay import STATE_BRANCH


class GitHubContentsStore:
    """GitHub Contents adapter with prefix filtering over directory listings.

    GitHub lists directories rather than arbitrary filename prefixes. This adapter
    converts a requested prefix to its parent directory, lists that directory,
    then filters returned file paths by the original prefix.
    """

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
        for _ in range(3):
            result = self._req("PUT", path, payload)
            if result is not None:
                return True
            if self.read(path) is not None:
                return False
        return False

    def read(self, path: str) -> bytes | None:
        obj = self._req("GET", path)
        if not obj or isinstance(obj, list):
            return None
        return base64.b64decode(obj["content"])

    def list_paths(self, prefix: str) -> list[str]:
        clean = prefix.rstrip("/")
        if prefix.endswith("/"):
            directory = clean
        else:
            directory = str(PurePosixPath(clean).parent)
        obj = self._req("GET", directory)
        if not isinstance(obj, list):
            return []
        return sorted(
            x["path"] for x in obj
            if x.get("type") == "file" and x.get("path", "").startswith(prefix)
        )

    def exists(self, path: str) -> bool:
        return self.read(path) is not None
