"""HAR inspection, differential flow comparison, and token lineage tracing tools."""

from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any, Mapping
from urllib.parse import urlsplit

from .contracts import ToolInputError, ToolSpec

SCHEMA_VERSION_INSPECT = "itir.har.inspect.v1"
SCHEMA_VERSION_DIFF = "itir.har.diff.v1"
SCHEMA_VERSION_LINEAGE = "itir.har.token_lineage.v1"


def _load_har(payload: Mapping[str, Any]) -> dict[str, Any]:
    if "har_data" in payload and isinstance(payload["har_data"], Mapping):
        return dict(payload["har_data"])

    raw_path = payload.get("har_path")
    if not raw_path or not isinstance(raw_path, str):
        raise ToolInputError("Expected non-empty string for 'har_path' or dict for 'har_data'")

    path = Path(raw_path).expanduser().resolve()
    if not path.is_file():
        raise ToolInputError(f"HAR file not found: {path}")

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ToolInputError(f"Failed to parse HAR JSON from {path}: {exc}") from exc

    if not isinstance(data, Mapping) or "log" not in data:
        raise ToolInputError(f"Invalid HAR format: missing root 'log' object in {path}")
    return dict(data)


def _safe_json_decode(text: str | None) -> Any:
    if not text or not isinstance(text, str):
        return None
    stripped = text.strip()
    if (stripped.startswith("{") and stripped.endswith("}")) or (stripped.startswith("[") and stripped.endswith("]")):
        try:
            return json.loads(stripped)
        except Exception:
            return text
    return text


def _extract_flow(entry: Mapping[str, Any], index: int) -> dict[str, Any]:
    req = entry.get("request") or {}
    resp = entry.get("response") or {}

    url = str(req.get("url") or "")
    parsed_url = urlsplit(url)

    req_headers = {
        str(h.get("name") or "").lower(): str(h.get("value") or "")
        for h in req.get("headers") or []
        if isinstance(h, Mapping) and h.get("name")
    }
    resp_headers = {
        str(h.get("name") or "").lower(): str(h.get("value") or "")
        for h in resp.get("headers") or []
        if isinstance(h, Mapping) and h.get("name")
    }

    req_cookies = {
        str(c.get("name") or ""): str(c.get("value") or "")
        for c in req.get("cookies") or []
        if isinstance(c, Mapping) and c.get("name")
    }
    resp_cookies = {
        str(c.get("name") or ""): str(c.get("value") or "")
        for c in resp.get("cookies") or []
        if isinstance(c, Mapping) and c.get("name")
    }

    query_params = {
        str(q.get("name") or ""): str(q.get("value") or "")
        for q in req.get("queryString") or []
        if isinstance(q, Mapping) and q.get("name")
    }

    req_post = req.get("postData") or {}
    req_body = _safe_json_decode(req_post.get("text"))

    resp_content = resp.get("content") or {}
    resp_body = _safe_json_decode(resp_content.get("text"))

    return {
        "index": index,
        "started_at": entry.get("startedDateTime"),
        "time_ms": entry.get("time"),
        "method": str(req.get("method") or "").upper(),
        "url": url,
        "path": parsed_url.path or "/",
        "status": int(resp.get("status") or 0),
        "status_text": str(resp.get("statusText") or ""),
        "request_headers": req_headers,
        "request_cookies": req_cookies,
        "query_params": query_params,
        "request_body": req_body,
        "response_headers": resp_headers,
        "response_cookies": resp_cookies,
        "response_body": resp_body,
    }


def har_inspect(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Parse a .har file into normalized chronological flows with decoded JSON bodies."""
    har = _load_har(payload)
    entries = (har.get("log") or {}).get("entries") or []
    if not isinstance(entries, list):
        raise ToolInputError("HAR log.entries must be an array")

    url_filter = payload.get("url_filter")
    method_filter = payload.get("method_filter")
    status_filter = payload.get("status_filter")
    limit = max(1, min(int(payload.get("limit", 100)), 500))
    offset = max(0, int(payload.get("offset", 0)))

    flows: list[dict[str, Any]] = []
    matched_count = 0

    for i, entry in enumerate(entries):
        if not isinstance(entry, Mapping):
            continue
        req = entry.get("request") or {}
        resp = entry.get("response") or {}

        url = str(req.get("url") or "")
        method = str(req.get("method") or "").upper()
        status = int(resp.get("status") or 0)

        if url_filter and str(url_filter).lower() not in url.lower():
            continue
        if method_filter and str(method_filter).upper() != method:
            continue
        if status_filter is not None and int(status_filter) != status:
            continue

        matched_count += 1
        if matched_count > offset and len(flows) < limit:
            flows.append(_extract_flow(entry, i))

    return {
        "version": SCHEMA_VERSION_INSPECT,
        "har_path": payload.get("har_path"),
        "total_entries": len(entries),
        "matched_entries": matched_count,
        "limit": limit,
        "offset": offset,
        "flows": flows,
    }


def _normalize_flow_for_diff(flow_or_obs: Mapping[str, Any]) -> dict[str, Any]:
    """Normalize either a HAR flow dict or a ProtocolObservation dict into a comparable shape."""
    if "request_headers" in flow_or_obs or "url" in flow_or_obs:
        # Standard HAR flow shape
        req_headers = {str(k).lower(): str(v) for k, v in (flow_or_obs.get("request_headers") or {}).items()}
        req_cookies = {str(k): str(v) for k, v in (flow_or_obs.get("request_cookies") or {}).items()}
        return {
            "method": str(flow_or_obs.get("method") or "").upper(),
            "path": str(flow_or_obs.get("path") or ""),
            "url": str(flow_or_obs.get("url") or ""),
            "status": int(flow_or_obs.get("status") or 0),
            "headers": req_headers,
            "cookies": req_cookies,
            "body": flow_or_obs.get("request_body"),
            "time_ms": flow_or_obs.get("time_ms"),
        }
    else:
        # ProtocolObservation dict shape
        headers = {str(k).lower(): str(v) for k, v in (flow_or_obs.get("headers") or {}).items()}
        cookies = {str(k): str(v) for k, v in (flow_or_obs.get("cookies") or {}).items()}
        return {
            "method": str(flow_or_obs.get("method") or "").upper(),
            "path": str(flow_or_obs.get("path") or ""),
            "url": str(flow_or_obs.get("path") or ""),
            "status": int(flow_or_obs.get("status") or 0),
            "headers": headers,
            "cookies": cookies,
            "body": flow_or_obs.get("payload"),
            "time_ms": flow_or_obs.get("elapsed_ms"),
        }


def har_diff(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Compare two flows (or a HAR transaction against a ProtocolObservation) and emit typed deltas."""
    flow_a_raw = payload.get("flow_a")
    flow_b_raw = payload.get("flow_b")

    har_path = payload.get("har_path")
    has_har_data = "har_data" in payload
    index_a = payload.get("index_a")
    index_b = payload.get("index_b")

    if (har_path or has_har_data) and (index_a is not None or index_b is not None):
        har = _load_har(payload)
        entries = (har.get("log") or {}).get("entries") or []
        if index_a is not None and flow_a_raw is None:
            if index_a < 0 or index_a >= len(entries):
                raise ToolInputError(f"index_a ({index_a}) out of range (0..{len(entries)-1})")
            flow_a_raw = _extract_flow(entries[index_a], index_a)
        if index_b is not None and flow_b_raw is None:
            if index_b < 0 or index_b >= len(entries):
                raise ToolInputError(f"index_b ({index_b}) out of range (0..{len(entries)-1})")
            flow_b_raw = _extract_flow(entries[index_b], index_b)

    if not isinstance(flow_a_raw, Mapping) or not isinstance(flow_b_raw, Mapping):
        raise ToolInputError("har_diff requires two flows to compare (flow_a, flow_b or har_path with index_a, index_b)")

    a = _normalize_flow_for_diff(flow_a_raw)
    b = _normalize_flow_for_diff(flow_b_raw)

    method_match = (a["method"] == b["method"])
    path_match = (a["path"] == b["path"]) or (a["path"].rstrip("/") == b["path"].rstrip("/"))
    status_match = (a["status"] == b["status"])

    a_hdrs, b_hdrs = a["headers"], b["headers"]
    missing_in_b_hdrs = sorted(set(a_hdrs) - set(b_hdrs))
    missing_in_a_hdrs = sorted(set(b_hdrs) - set(a_hdrs))
    common_hdrs = set(a_hdrs) & set(b_hdrs)
    hdr_val_diffs = [
        {"header": k, "a": a_hdrs[k], "b": b_hdrs[k]}
        for k in sorted(common_hdrs)
        if a_hdrs[k] != b_hdrs[k]
    ]

    a_cookies, b_cookies = a["cookies"], b["cookies"]
    missing_in_b_cookies = sorted(set(a_cookies) - set(b_cookies))
    missing_in_a_cookies = sorted(set(b_cookies) - set(a_cookies))
    common_cookies = set(a_cookies) & set(b_cookies)
    cookie_val_diffs = [
        {"cookie": k, "a": a_cookies[k], "b": b_cookies[k]}
        for k in sorted(common_cookies)
        if a_cookies[k] != b_cookies[k]
    ]

    body_match = (a["body"] == b["body"])

    return {
        "version": SCHEMA_VERSION_DIFF,
        "flow_a_summary": {"method": a["method"], "path": a["path"], "status": a["status"]},
        "flow_b_summary": {"method": b["method"], "path": b["path"], "status": b["status"]},
        "matches": {
            "method": method_match,
            "path": path_match,
            "status": status_match,
            "body": body_match,
        },
        "status_delta": {"a": a["status"], "b": b["status"]},
        "headers": {
            "missing_in_b": missing_in_b_hdrs,
            "missing_in_a": missing_in_a_hdrs,
            "value_differences": hdr_val_diffs,
        },
        "cookies": {
            "missing_in_b": missing_in_b_cookies,
            "missing_in_a": missing_in_a_cookies,
            "value_differences": cookie_val_diffs,
        },
    }


def _search_nested(value: Any, token_pattern: re.Pattern, current_path: str = "") -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    if isinstance(value, str):
        if token_pattern.search(value):
            findings.append({"path": current_path or "root", "sample": value[:120]})
    elif isinstance(value, Mapping):
        for k, v in value.items():
            child_path = f"{current_path}.{k}" if current_path else str(k)
            if token_pattern.search(str(k)):
                findings.append({"path": f"{child_path} (key)", "sample": str(k)})
            findings.extend(_search_nested(v, token_pattern, child_path))
    elif isinstance(value, (list, tuple)):
        for i, item in enumerate(value):
            child_path = f"{current_path}[{i}]"
            findings.extend(_search_nested(item, token_pattern, child_path))
    return findings


def har_token_lineage(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Follow any token string or regex backward to its exact origin in earlier requests/responses."""
    token = payload.get("token")
    if not token or not isinstance(token, str):
        raise ToolInputError("Expected non-empty string for 'token'")

    har = _load_har(payload)
    entries = (har.get("log") or {}).get("entries") or []

    case_sensitive = payload.get("case_sensitive", True)
    flags = 0 if case_sensitive else re.IGNORECASE
    token_pattern = re.compile(re.escape(token), flags)

    occurrences: list[dict[str, Any]] = []

    for i, entry in enumerate(entries):
        if not isinstance(entry, Mapping):
            continue
        flow = _extract_flow(entry, i)

        # 1. Incoming: response body
        if flow["response_body"] is not None:
            matches = _search_nested(flow["response_body"], token_pattern)
            for m in matches:
                occurrences.append({
                    "entry_index": i,
                    "timestamp": flow["started_at"],
                    "method": flow["method"],
                    "url": flow["url"],
                    "direction": "incoming",
                    "channel": "response_body",
                    "key_path": m["path"],
                    "sample": m["sample"],
                })

        # 2. Incoming: response headers / set-cookie
        for h_name, h_val in flow["response_headers"].items():
            if token_pattern.search(h_val):
                occurrences.append({
                    "entry_index": i,
                    "timestamp": flow["started_at"],
                    "method": flow["method"],
                    "url": flow["url"],
                    "direction": "incoming",
                    "channel": "response_header",
                    "key_path": h_name,
                    "sample": h_val[:120],
                })

        # 3. Outgoing: request URL / query string
        for q_name, q_val in flow["query_params"].items():
            if token_pattern.search(q_val) or token_pattern.search(q_name):
                occurrences.append({
                    "entry_index": i,
                    "timestamp": flow["started_at"],
                    "method": flow["method"],
                    "url": flow["url"],
                    "direction": "outgoing",
                    "channel": "query_param",
                    "key_path": q_name,
                    "sample": q_val[:120],
                })

        # 4. Outgoing: request headers
        for h_name, h_val in flow["request_headers"].items():
            if token_pattern.search(h_val):
                occurrences.append({
                    "entry_index": i,
                    "timestamp": flow["started_at"],
                    "method": flow["method"],
                    "url": flow["url"],
                    "direction": "outgoing",
                    "channel": "request_header",
                    "key_path": h_name,
                    "sample": h_val[:120],
                })

        # 5. Outgoing: request cookies
        for c_name, c_val in flow["request_cookies"].items():
            if token_pattern.search(c_val) or token_pattern.search(c_name):
                occurrences.append({
                    "entry_index": i,
                    "timestamp": flow["started_at"],
                    "method": flow["method"],
                    "url": flow["url"],
                    "direction": "outgoing",
                    "channel": "request_cookie",
                    "key_path": c_name,
                    "sample": c_val[:120],
                })

        # 6. Outgoing: request body
        if flow["request_body"] is not None:
            matches = _search_nested(flow["request_body"], token_pattern)
            for m in matches:
                occurrences.append({
                    "entry_index": i,
                    "timestamp": flow["started_at"],
                    "method": flow["method"],
                    "url": flow["url"],
                    "direction": "outgoing",
                    "channel": "request_body",
                    "key_path": m["path"],
                    "sample": m["sample"],
                })

    origin = occurrences[0] if occurrences else None
    transmitted = [o for o in occurrences if o["direction"] == "outgoing"]

    return {
        "version": SCHEMA_VERSION_LINEAGE,
        "token_query": token,
        "total_occurrences": len(occurrences),
        "origin": origin,
        "summary": {
            "first_observed_index": origin["entry_index"] if origin else None,
            "first_observed_channel": origin["channel"] if origin else None,
            "first_observed_endpoint": origin["url"] if origin else None,
            "times_transmitted": len(transmitted),
            "last_transmitted_index": transmitted[-1]["entry_index"] if transmitted else None,
        },
        "lineage": occurrences,
    }


def get_har_tools() -> list[tuple[ToolSpec, Any]]:
    return [
        (
            ToolSpec(
                name="itir.har.inspect",
                title="Inspect HTTP traffic from a HAR capture",
                description="Parse a .har file into normalized chronological flows with decoded JSON bodies, query params, and status codes.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "har_path": {"type": "string", "description": "Absolute or home-relative path to .har file"},
                        "har_data": {"type": "object", "description": "Direct in-memory HAR JSON object"},
                        "url_filter": {"type": "string", "description": "Optional substring filter on request URL"},
                        "method_filter": {"type": "string", "description": "Optional HTTP method filter (e.g. POST, GET)"},
                        "status_filter": {"type": "integer", "description": "Optional HTTP status filter (e.g. 200, 403)"},
                        "limit": {"type": "integer", "default": 100},
                        "offset": {"type": "integer", "default": 0},
                    },
                },
                read_only=True,
            ),
            har_inspect,
        ),
        (
            ToolSpec(
                name="itir.har.diff",
                title="Compare two HTTP flows",
                description="Compare two flows (or a .har transaction against a ProtocolObservation record) and emit a typed delta of headers, cookies, and timing.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "har_path": {"type": "string", "description": "Path to HAR file containing the flows"},
                        "index_a": {"type": "integer", "description": "Entry index of first flow in HAR"},
                        "index_b": {"type": "integer", "description": "Entry index of second flow in HAR"},
                        "flow_a": {"type": "object", "description": "First flow or ProtocolObservation object"},
                        "flow_b": {"type": "object", "description": "Second flow or ProtocolObservation object"},
                    },
                },
                read_only=True,
            ),
            har_diff,
        ),
        (
            ToolSpec(
                name="itir.har.token_lineage",
                title="Trace token lifecycle across HTTP traffic",
                description="Follow any token string (or regex) backward from a failing request to its exact point of origin in earlier requests, responses, or set-cookie headers.",
                input_schema={
                    "type": "object",
                    "required": ["token"],
                    "properties": {
                        "token": {"type": "string", "description": "Token, nonce, or secret substring to trace"},
                        "har_path": {"type": "string", "description": "Path to HAR file"},
                        "har_data": {"type": "object", "description": "Direct in-memory HAR JSON object"},
                        "case_sensitive": {"type": "boolean", "default": True},
                    },
                },
                read_only=True,
            ),
            har_token_lineage,
        ),
    ]
