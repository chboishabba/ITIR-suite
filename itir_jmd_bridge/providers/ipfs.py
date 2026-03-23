from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any, Callable

import requests


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def fetch_ipfs_content(
    *,
    cid: str,
    base_url: str | None = None,
    get: Callable[..., Any] | None = None,
    timeout: float = 10.0,
    allow_cli_fallback: bool = False,
) -> dict[str, Any]:
    """Fetch IPFS content via HTTP gateway, optionally falling back to ipfs cli."""
    getter = get or requests.get
    gateway = base_url.rstrip("/") if base_url else "https://ipfs.io"
    url = f"{gateway}/ipfs/{cid}"
    try:
        response = getter(url, timeout=timeout)
        if hasattr(response, "raise_for_status"):
            response.raise_for_status()
        text = response.text if hasattr(response, "text") else str(response)
        return {
            "provider": "ipfs_http",
            "url": url,
            "status_code": getattr(response, "status_code", 200),
            "text": text,
            "sha256": sha256(text.encode("utf-8")).hexdigest(),
            "fetched_at": _utc_now(),
        }
    except Exception as exc:
        if not allow_cli_fallback:
            raise
        try:
            out = subprocess.check_output(["ipfs", "cat", cid], timeout=timeout)
            text = out.decode("utf-8", "replace")
            return {
                "provider": "ipfs_cli",
                "url": url,
                "status_code": 200,
                "text": text,
                "sha256": sha256(text.encode("utf-8")).hexdigest(),
                "fetched_at": _utc_now(),
            }
        except Exception:
            raise exc
