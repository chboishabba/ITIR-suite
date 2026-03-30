from __future__ import annotations

import os
import re
import subprocess
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any, Callable
from urllib.parse import urlparse

import requests


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_ipfs_uri(uri: str) -> dict[str, str]:
    if not uri.startswith("ipfs://"):
        raise ValueError(f"unsupported IPFS URI: {uri}")
    parsed = urlparse(uri)
    cid = parsed.netloc or parsed.path.lstrip("/").split("/", 1)[0]
    path = ""
    if parsed.netloc and parsed.path:
        path = parsed.path.lstrip("/")
    elif parsed.path.lstrip("/") and "/" in parsed.path.lstrip("/"):
        path = parsed.path.lstrip("/").split("/", 1)[1]
    return {
        "cid": cid,
        "path": path,
    }


def _gateway_url(*, cid: str, path: str = "", base_url: str | None = None) -> str:
    gateway = base_url.rstrip("/") if base_url else "https://ipfs.io"
    suffix = f"/{path}" if path else ""
    return f"{gateway}/ipfs/{cid}{suffix}"


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


def probe_ipfs_gateway_acknowledgement(
    *,
    ipfs_uri: str,
    base_url: str | None = None,
    head: Callable[..., Any] | None = None,
    timeout: float = 20.0,
) -> dict[str, Any]:
    parsed = parse_ipfs_uri(ipfs_uri)
    url = _gateway_url(cid=parsed["cid"], path=parsed["path"], base_url=base_url)
    caller = head or requests.head
    response = caller(url, allow_redirects=True, timeout=timeout)
    if hasattr(response, "raise_for_status"):
        response.raise_for_status()
    history = list(getattr(response, "history", []) or [])
    chain = [
        {
            "status_code": getattr(item, "status_code", None),
            "url": getattr(item, "url", None),
            "location": getattr(item, "headers", {}).get("location"),
            "etag": getattr(item, "headers", {}).get("etag"),
        }
        for item in history
    ]
    headers = getattr(response, "headers", {})
    return {
        "cid": parsed["cid"],
        "path": parsed["path"],
        "gatewayUrl": url,
        "statusCode": getattr(response, "status_code", 200),
        "finalUrl": getattr(response, "url", url),
        "etag": headers.get("etag"),
        "contentLength": headers.get("content-length"),
        "contentType": headers.get("content-type"),
        "redirectChain": chain,
        "fetchedAt": _utc_now(),
    }


def fetch_ipfs_object(
    *,
    ipfs_uri: str,
    base_url: str | None = None,
    get: Callable[..., Any] | None = None,
    timeout: float = 20.0,
) -> dict[str, Any]:
    parsed = parse_ipfs_uri(ipfs_uri)
    url = _gateway_url(cid=parsed["cid"], path=parsed["path"], base_url=base_url)
    caller = get or requests.get
    response = caller(url, allow_redirects=True, timeout=timeout)
    if hasattr(response, "raise_for_status"):
        response.raise_for_status()
    content = response.content if hasattr(response, "content") else bytes(str(response), "utf-8")
    headers = getattr(response, "headers", {})
    binary_like = b"\x00" in content
    return {
        "cid": parsed["cid"],
        "path": parsed["path"],
        "gatewayUrl": url,
        "statusCode": getattr(response, "status_code", 200),
        "finalUrl": getattr(response, "url", url),
        "etag": headers.get("etag"),
        "contentLength": headers.get("content-length"),
        "contentType": headers.get("content-type"),
        "sha256": sha256(content).hexdigest(),
        "sizeBytes": len(content),
        "text": None if binary_like else content.decode("utf-8", "replace"),
        "textPreview": None if not binary_like else content[:64].hex(),
        "fetchedAt": _utc_now(),
    }


def download_ipfs_object_bytes(
    *,
    ipfs_uri: str,
    base_url: str | None = None,
    get: Callable[..., Any] | None = None,
    timeout: float = 20.0,
) -> dict[str, Any]:
    parsed = parse_ipfs_uri(ipfs_uri)
    url = _gateway_url(cid=parsed["cid"], path=parsed["path"], base_url=base_url)
    caller = get or requests.get
    response = caller(url, allow_redirects=True, timeout=timeout)
    if hasattr(response, "raise_for_status"):
        response.raise_for_status()
    content = response.content if hasattr(response, "content") else bytes(str(response), "utf-8")
    fetched = fetch_ipfs_object(
        ipfs_uri=ipfs_uri,
        base_url=base_url,
        get=lambda *args, **kwargs: response,
    )
    return {
        "bytes": content,
        "metadata": fetched,
    }


def publish_ipfs_file_with_ack(
    *,
    local_path: str,
    api_base_url: str = "http://127.0.0.1:5001",
    run: Callable[..., Any] | None = None,
    post: Callable[..., Any] | None = None,
    pin: bool = True,
    timeout: float = 30.0,
) -> dict[str, Any]:
    local_bytes = open(local_path, "rb").read()
    local_sha256 = sha256(local_bytes).hexdigest()
    api_post = post or requests.post
    use_api = post is not None
    if not use_api:
        try:
            version_response = api_post(
                f"{api_base_url.rstrip('/')}/api/v0/version",
                timeout=timeout,
            )
            if hasattr(version_response, "raise_for_status"):
                version_response.raise_for_status()
            use_api = True
        except Exception:
            use_api = False
    if use_api:
        with open(local_path, "rb") as handle:
            response = api_post(
                f"{api_base_url.rstrip('/')}/api/v0/add",
                files={"file": (os.path.basename(local_path), handle)},
                timeout=timeout,
            )
        if hasattr(response, "raise_for_status"):
            response.raise_for_status()
        text = response.text if hasattr(response, "text") else str(response)
    else:
        cli = run or subprocess.run
        completed = cli(
            ["ipfs", "add", "-Q", local_path],
            check=True,
            capture_output=True,
            text=True,
        )
        text = (getattr(completed, "stdout", "") or "").strip()
    match = re.search(r"(bafy[a-zA-Z0-9]+|Qm[a-zA-Z0-9]{44})", text)
    if not match:
        raise RuntimeError(f"unable to parse CID from IPFS add output: {text}")
    cid = match.group(1)
    pin_status = None
    if pin:
        if use_api:
            pin_response = api_post(
                f"{api_base_url.rstrip('/')}/api/v0/pin/add",
                params={"arg": cid},
                timeout=timeout,
            )
            if hasattr(pin_response, "raise_for_status"):
                pin_response.raise_for_status()
            pin_status = "pinned"
        else:
            cli = run or subprocess.run
            cli(["ipfs", "pin", "add", cid], check=True, capture_output=True, text=True)
            pin_status = "pinned"
    return {
        "sink": "ipfs",
        "ipfsUri": f"ipfs://{cid}",
        "cid": cid,
        "localPath": local_path,
        "localSha256": local_sha256,
        "localSizeBytes": len(local_bytes),
        "pinStatus": pin_status,
        "verified": False,
    }
