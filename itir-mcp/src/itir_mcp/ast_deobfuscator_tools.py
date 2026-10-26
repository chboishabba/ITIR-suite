"""Static JavaScript/HTML AST and closure analysis tool for anti-abuse client bundles."""

from __future__ import annotations

from pathlib import Path
import re
from typing import Any, Mapping

from .contracts import ToolInputError, ToolSpec

SCHEMA_VERSION_AST = "itir.ast.analyze_bundle.v1"

_DEFAULT_ENDPOINTS = [
    "/backend-api/conversation",
    "/sentinel/chat-requirements",
    "/backend-api/",
    "/backend-anon/",
    "/api/auth/session",
]

_TELEMETRY_PATTERNS = {
    "crypto_subtle": re.compile(r"\b(?:crypto\.subtle|SubtleCrypto)\.(?:digest|sign|importKey|encrypt)\b"),
    "user_agent_data": re.compile(r"\bnavigator\.userAgentData\b"),
    "webdriver_check": re.compile(r"\bnavigator\.webdriver\b"),
    "turnstile_call": re.compile(r"\bturnstile\.(?:render|execute|getResponse|reset)\b"),
    "timing_check": re.compile(r"\b(?:performance\.now|Date\.now)\(\)"),
    "wasm_instantiate": re.compile(r"\bWebAssembly\.(?:instantiate|instantiateStreaming|compile)\b"),
    "worker_spawn": re.compile(r"\bnew\s+Worker\s*\("),
    "post_message": re.compile(r"\b(?:postMessage|addEventListener\s*\(\s*['\"]message['\"])"),
}

_SENTINEL_PROP_PATTERNS = {
    "chat_requirements_token": re.compile(r"\b(?:chat_requirements_token|requirements_token|token)\b"),
    "turnstile_dx": re.compile(r"\b(?:turnstile|dx)\b"),
    "proof_of_work": re.compile(r"\b(?:proofofwork|proof_token|difficulty|seed)\b"),
    "prepare_token": re.compile(r"\bprepare_token\b"),
    "header_sentinel_chat": re.compile(r"openai-sentinel-chat-requirements-token", re.IGNORECASE),
    "header_sentinel_turnstile": re.compile(r"openai-sentinel-turnstile-token", re.IGNORECASE),
    "header_sentinel_proof": re.compile(r"openai-sentinel-proof-token", re.IGNORECASE),
}


def _load_script_content(payload: Mapping[str, Any]) -> tuple[str, str]:
    if "code" in payload and isinstance(payload["code"], str) and payload["code"].strip():
        return payload["code"], "inline_code"

    raw_path = payload.get("bundle_path")
    if not raw_path or not isinstance(raw_path, str):
        raise ToolInputError("Expected non-empty string for 'bundle_path' or 'code'")

    path = Path(raw_path).expanduser().resolve()
    if not path.is_file():
        raise ToolInputError(f"Script bundle not found: {path}")

    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        raise ToolInputError(f"Failed to read script bundle from {path}: {exc}") from exc

    return content, str(path)


def _extract_scripts_from_html(html_text: str) -> list[dict[str, Any]]:
    scripts: list[dict[str, Any]] = []
    script_re = re.compile(r"<script(?P<attrs>[^>]*)>(?P<code>.*?)</script>", re.DOTALL | re.IGNORECASE)
    src_re = re.compile(r'src=["\'](?P<src>[^"\']+)["\']', re.IGNORECASE)

    for match in script_re.finditer(html_text):
        attrs = match.group("attrs") or ""
        code = match.group("code") or ""
        src_match = src_re.search(attrs)
        src = src_match.group("src") if src_match else None

        scripts.append({
            "src": src,
            "inline": bool(code.strip()),
            "code": code.strip(),
            "start_offset": match.start(),
            "end_offset": match.end(),
        })
    return scripts


def _find_surrounding_closure(text: str, match_index: int, window: int = 250) -> dict[str, Any]:
    start = max(0, match_index - window)
    end = min(len(text), match_index + window)
    snippet = text[start:end]

    # Approximate enclosing function / statement boundary
    brace_stack = 0
    fn_start = start
    for i in range(match_index - 1, max(0, match_index - 800), -1):
        if text[i] == "}":
            brace_stack += 1
        elif text[i] == "{":
            if brace_stack == 0:
                fn_start = i
                break
            brace_stack -= 1

    return {
        "snippet": snippet.strip(),
        "offset": match_index,
        "enclosing_block_start": fn_start,
    }


def analyze_bundle(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Parse and analyze JavaScript / HTML bundles for endpoints, telemetry hooks, and preflight dependencies."""
    content, source_id = _load_script_content(payload)

    target_endpoints = payload.get("target_endpoints")
    if not target_endpoints or not isinstance(target_endpoints, list):
        target_endpoints = _DEFAULT_ENDPOINTS

    is_html = content.lstrip().startswith("<!DOCTYPE") or "<html" in content[:400].lower() or "<script" in content[:1000].lower()
    html_scripts = _extract_scripts_from_html(content) if is_html else []

    # If it is HTML, we also analyze each script block separately
    codes_to_analyze: list[tuple[str, str]] = []
    if html_scripts:
        for idx, s in enumerate(html_scripts):
            if s["code"]:
                codes_to_analyze.append((s["code"], f"{source_id}#script_{idx}"))
    else:
        codes_to_analyze.append((content, source_id))

    endpoint_findings: list[dict[str, Any]] = []
    for code, scope_name in codes_to_analyze:
        for endpoint in target_endpoints:
            pattern = re.compile(re.escape(endpoint), re.IGNORECASE)
            for m in pattern.finditer(code):
                closure_info = _find_surrounding_closure(code, m.start())
                # Check for nearby call patterns
                nearby = code[max(0, m.start() - 80):min(len(code), m.end() + 150)]
                is_fetch = "fetch(" in nearby or "http" in nearby or "post(" in nearby or "request(" in nearby

                endpoint_findings.append({
                    "scope": scope_name,
                    "endpoint": endpoint,
                    "matched_at_offset": m.start(),
                    "is_call_site": is_fetch,
                    "context_snippet": closure_info["snippet"],
                })

    # Telemetry and Crypto API detection
    telemetry_detections: dict[str, list[dict[str, Any]]] = {}
    for api_name, pattern in _TELEMETRY_PATTERNS.items():
        matches = []
        for code, scope_name in codes_to_analyze:
            for m in pattern.finditer(code):
                snippet = code[max(0, m.start() - 60):min(len(code), m.end() + 80)].strip()
                matches.append({
                    "scope": scope_name,
                    "offset": m.start(),
                    "matched_text": m.group(0),
                    "snippet": snippet,
                })
        if matches:
            telemetry_detections[api_name] = matches

    # Data dependency tracing (preflight response properties vs outgoing mutation headers)
    dependencies: list[dict[str, Any]] = []
    for dep_name, pattern in _SENTINEL_PROP_PATTERNS.items():
        matches = []
        for code, scope_name in codes_to_analyze:
            for m in pattern.finditer(code):
                snippet = code[max(0, m.start() - 50):min(len(code), m.end() + 70)].strip()
                matches.append({
                    "scope": scope_name,
                    "offset": m.start(),
                    "token": m.group(0),
                    "snippet": snippet,
                })
        if matches:
            dependencies.append({
                "property_class": dep_name,
                "occurrences": len(matches),
                "samples": matches[:5],
            })

    return {
        "version": SCHEMA_VERSION_AST,
        "source": source_id,
        "is_html": is_html,
        "html_script_tags": len(html_scripts),
        "endpoint_references": endpoint_findings,
        "telemetry_detections": telemetry_detections,
        "data_dependencies": dependencies,
        "summary": {
            "total_endpoints_referenced": len(endpoint_findings),
            "telemetry_apis_detected": list(telemetry_detections.keys()),
            "preflight_dependency_properties": [d["property_class"] for d in dependencies],
        },
    }


def get_ast_tools() -> list[tuple[ToolSpec, Any]]:
    return [
        (
            ToolSpec(
                name="itir.ast.analyze_bundle",
                title="Static JavaScript AST & closure analysis of anti-abuse bundles",
                description="Ingest script bundles (index-*.js, runner.html), trace identifiers referencing endpoints, and extract preflight-to-commit data dependencies.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "bundle_path": {"type": "string", "description": "Path to JS bundle or HTML file"},
                        "code": {"type": "string", "description": "Direct JavaScript or HTML source string"},
                        "target_endpoints": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of endpoint paths to trace (defaults to conversation & sentinel endpoints)",
                        },
                    },
                },
                read_only=True,
            ),
            analyze_bundle,
        ),
    ]
