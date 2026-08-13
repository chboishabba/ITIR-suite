from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from html import unescape
import json
import re
from typing import Any, Callable
from urllib.parse import urljoin, urlparse
import urllib.request

import requests


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _strip_trailing_slash(value: str) -> str:
    return value[:-1] if value.endswith("/") else value


def _browser_headers() -> dict[str, str]:
    return {
        "User-Agent": "Mozilla/5.0 (compatible; ITIR-JMD-Bridge/1.0)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }


def _call_getter(
    getter: Callable[..., Any],
    url: str,
    *,
    timeout: float,
    headers: dict[str, str] | None = None,
) -> Any:
    if headers:
        try:
            return getter(url, timeout=timeout, headers=headers)
        except TypeError:
            return getter(url, timeout=timeout)
    return getter(url, timeout=timeout)


@dataclass(frozen=True)
class PastebinReference:
    base_url: str
    paste_id: str
    paste_url: str
    raw_url: str


@dataclass(frozen=True)
class BrowseEntry:
    base_url: str
    paste_id: str
    title: str
    paste_url: str
    raw_url: str


def parse_paste_reference(
    *,
    paste_url: str | None = None,
    base_url: str | None = None,
    paste_id: str | None = None,
) -> PastebinReference:
    if paste_url:
        parsed = urlparse(paste_url)
        parts = [part for part in parsed.path.split("/") if part]
        if len(parts) < 2 or parts[-2] != "paste":
            raise ValueError(f"Unsupported paste URL: {paste_url}")
        resolved_paste_id = parts[-1]
        resolved_base_url = _strip_trailing_slash(f"{parsed.scheme}://{parsed.netloc}")
    elif base_url and paste_id:
        resolved_base_url = _strip_trailing_slash(base_url)
        resolved_paste_id = paste_id
    else:
        raise ValueError("Provide paste_url or both base_url and paste_id")

    return PastebinReference(
        base_url=resolved_base_url,
        paste_id=resolved_paste_id,
        paste_url=f"{resolved_base_url}/paste/{resolved_paste_id}",
        raw_url=f"{resolved_base_url}/raw/{resolved_paste_id}",
    )


def parse_paste_envelope(raw_text: str) -> dict[str, Any]:
    lines = raw_text.splitlines()
    if not lines:
        return {"metadata": {}, "body": "", "raw_text": raw_text}

    metadata: dict[str, str] = {}
    body_start_line = 0
    if lines[0].startswith("--- "):
        for idx, line in enumerate(lines[1:], start=1):
            if not line.strip():
                body_start_line = idx + 1
                break
            if ":" in line:
                key, value = line.split(":", 1)
                metadata[key.strip()] = value.strip()
        else:
            body_start_line = len(lines)

    body = "\n".join(lines[body_start_line:]).strip()
    return {"metadata": metadata, "body": body, "raw_text": raw_text}


def fetch_paste_record(
    reference: PastebinReference,
    *,
    get: Callable[..., Any] | None = None,
    timeout: float = 10.0,
) -> dict[str, Any]:
    getter = get or requests.get
    response = _call_getter(getter, reference.raw_url, timeout=timeout)
    if hasattr(response, "raise_for_status"):
        response.raise_for_status()
    raw_text = response.text if hasattr(response, "text") else str(response)
    parsed = parse_paste_envelope(raw_text)
    raw_sha = sha256(raw_text.encode("utf-8")).hexdigest()
    body_sha = sha256(parsed["body"].encode("utf-8")).hexdigest()
    return {
        "reference": {
            "provider": "kant-zk-pastebin",
            "base_url": reference.base_url,
            "paste_id": reference.paste_id,
            "paste_url": reference.paste_url,
            "raw_url": reference.raw_url,
        },
        "raw_text": raw_text,
        "body": parsed["body"],
        "metadata": parsed["metadata"],
        "retrieval": {
            "fetched_at": _utc_now(),
            "source_url": reference.raw_url,
            "status_code": getattr(response, "status_code", 200),
            "raw_text_sha256": raw_sha,
            "body_text_sha256": body_sha,
        },
    }


def fetch_ipfs_proxy_record(
    *,
    base_url: str,
    cid: str,
    get: Callable[..., Any] | None = None,
    timeout: float = 10.0,
) -> dict[str, Any]:
    getter = get or requests.get
    url = f"{_strip_trailing_slash(base_url)}/ipfs/{cid}"
    response = _call_getter(getter, url, timeout=timeout)
    if hasattr(response, "raise_for_status"):
        response.raise_for_status()
    raw_text = response.text if hasattr(response, "text") else str(response)
    return {
        "url": url,
        "text": raw_text,
        "status_code": getattr(response, "status_code", 200),
        "sha256": sha256(raw_text.encode("utf-8")).hexdigest(),
        "fetched_at": _utc_now(),
    }


def parse_browse_html(base_url: str, html: str, *, limit: int | None = None) -> list[BrowseEntry]:
    entries: list[BrowseEntry] = []
    pattern = re.compile(r'<a href="(?P<href>/paste/[^"]+)">(?P<title>.*?)</a>', re.IGNORECASE | re.DOTALL)
    resolved_base_url = _strip_trailing_slash(base_url)
    for match in pattern.finditer(html):
        href = unescape(match.group("href"))
        title = " ".join(unescape(match.group("title")).split())
        if not href.startswith("/paste/"):
            continue
        paste_id = href.rsplit("/", 1)[-1]
        entries.append(
            BrowseEntry(
                base_url=resolved_base_url,
                paste_id=paste_id,
                title=title,
                paste_url=urljoin(resolved_base_url + "/", href.lstrip("/")),
                raw_url=f"{resolved_base_url}/raw/{paste_id}",
            )
        )
        if limit is not None and len(entries) >= limit:
            break
    return entries


def fetch_browse_listing(
    *,
    base_url: str,
    limit: int = 5,
    get: Callable[..., Any] | None = None,
    timeout: float = 10.0,
) -> dict[str, Any]:
    getter = get or requests.get
    resolved_base_url = _strip_trailing_slash(base_url)
    attempts: list[dict[str, Any]] = []
    last_error: Exception | None = None
    for path in ("/browse", "/browse/"):
        url = f"{resolved_base_url}{path}"
        attempt: dict[str, Any] = {"url": url}
        attempts.append(attempt)
        try:
            response = _call_getter(getter, url, timeout=timeout, headers=_browser_headers())
            status_code = getattr(response, "status_code", 200)
            attempt["status_code"] = status_code
            if hasattr(response, "raise_for_status"):
                response.raise_for_status()
            html = response.text if hasattr(response, "text") else str(response)
            entries = parse_browse_html(resolved_base_url, html, limit=limit)
            return {
                "base_url": resolved_base_url,
                "browse_url": url,
                "fetched_at": _utc_now(),
                "status_code": status_code,
                "attempts": attempts,
                "entries": [
                    {
                        "base_url": entry.base_url,
                        "paste_id": entry.paste_id,
                        "title": entry.title,
                        "paste_url": entry.paste_url,
                        "raw_url": entry.raw_url,
                    }
                    for entry in entries
                ],
            }
        except Exception as exc:
            attempt["error"] = str(exc)
            last_error = exc
    if last_error is None:
        raise RuntimeError(f"Unable to fetch browse listing from {resolved_base_url}")

    try:
        url = f"{resolved_base_url}/browse/"
        attempt = {"url": url, "provider": "urllib"}
        attempts.append(attempt)
        req = urllib.request.Request(url, headers=_browser_headers())
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            html = resp.read().decode("utf-8", "replace")
            entries = parse_browse_html(resolved_base_url, html, limit=limit)
            attempt["status_code"] = getattr(resp, "status", 200)
            return {
                "base_url": resolved_base_url,
                "browse_url": url,
                "fetched_at": _utc_now(),
                "status_code": attempt["status_code"],
                "attempts": attempts,
                "entries": [
                    {
                        "base_url": entry.base_url,
                        "paste_id": entry.paste_id,
                        "title": entry.title,
                        "paste_url": entry.paste_url,
                        "raw_url": entry.raw_url,
                    }
                    for entry in entries
                ],
            }
    except Exception as exc:
        attempts[-1]["error"] = str(exc)
        last_error = exc

    raise RuntimeError(f"Unable to fetch browse listing from {resolved_base_url}: {last_error}")


def discover_host_capabilities(
    *,
    base_url: str,
    get: Callable[..., Any] | None = None,
    timeout: float = 10.0,
) -> dict[str, Any]:
    getter = get or requests.get
    resolved_base_url = _strip_trailing_slash(base_url)
    attempts: list[dict[str, Any]] = []

    def record_attempt(url: str, surface: str) -> dict[str, Any]:
        attempt = {"url": url, "surface": surface}
        attempts.append(attempt)
        return attempt

    documented_paths: list[str] = []
    openapi_error: str | None = None
    openapi_url = f"{resolved_base_url}/openapi.json"
    openapi_attempt = record_attempt(openapi_url, "openapi")
    try:
        response = _call_getter(getter, openapi_url, timeout=timeout, headers=_browser_headers())
        openapi_attempt["status_code"] = getattr(response, "status_code", 200)
        if hasattr(response, "raise_for_status"):
            response.raise_for_status()
        payload = response.json() if hasattr(response, "json") else json.loads(response.text)
        documented_paths = sorted((payload.get("paths") or {}).keys())
        openapi_attempt["documented_path_count"] = len(documented_paths)
    except Exception as exc:
        openapi_attempt["error"] = str(exc)
        openapi_error = str(exc)
        try:
            fallback_attempt = record_attempt(openapi_url, "openapi_urllib")
            req = urllib.request.Request(openapi_url, headers=_browser_headers())
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                fallback_attempt["status_code"] = getattr(resp, "status", 200)
                payload = json.loads(resp.read().decode("utf-8", "replace"))
                documented_paths = sorted((payload.get("paths") or {}).keys())
                fallback_attempt["documented_path_count"] = len(documented_paths)
                openapi_error = None
        except Exception as fallback_exc:
            attempts[-1]["error"] = str(fallback_exc)
            openapi_error = str(fallback_exc)

    documented_set = set(documented_paths)
    observed_surfaces: list[dict[str, Any]] = []

    def record_observed(surface: str, path: str, status_code: int) -> None:
        documented = path in documented_set
        observed_surfaces.append(
            {
                "surface": surface,
                "path": path,
                "status_code": status_code,
                "documented": documented,
            }
        )

    for surface, path, headers in (
        ("browse_html", "/browse", _browser_headers()),
        ("raw_template", "/raw/example-probe", None),
        ("ipfs_template", "/ipfs/example-probe", None),
        ("index_jsonl", "/index.jsonl", None),
    ):
        url = f"{resolved_base_url}{path}"
        attempt = record_attempt(url, surface)
        try:
            response = _call_getter(getter, url, timeout=timeout, headers=headers)
            attempt["status_code"] = getattr(response, "status_code", 200)
            observed = attempt["status_code"] != 404
            if observed:
                record_observed(surface, path, attempt["status_code"])
        except Exception as exc:
            attempt["error"] = str(exc)

    browse_path = "/browse"
    if not any(item["path"] == browse_path for item in observed_surfaces):
        try:
            url = f"{resolved_base_url}{browse_path}"
            attempt = record_attempt(url, "browse_html_urllib")
            req = urllib.request.Request(url, headers=_browser_headers())
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                attempt["status_code"] = getattr(resp, "status", 200)
                if attempt["status_code"] != 404:
                    record_observed("browse_html", browse_path, attempt["status_code"])
        except Exception as exc:
            attempts[-1]["error"] = str(exc)

    undeclared = [item for item in observed_surfaces if not item["documented"]]
    return {
        "base_url": resolved_base_url,
        "fetched_at": _utc_now(),
        "openapi_url": openapi_url,
        "documented_paths": documented_paths,
        "observed_surfaces": observed_surfaces,
        "undeclared_observed_surfaces": undeclared,
        "attempts": attempts,
        "warnings": ([] if openapi_error is None else [f"openapi_unavailable: {openapi_error}"])
        + [
            f"undeclared_surface:{item['path']}"
            for item in undeclared
        ],
    }
