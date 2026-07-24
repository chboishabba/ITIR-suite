from __future__ import annotations

import configparser
from dataclasses import dataclass
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse


_ONLINE_THREAD_ID_FROM_URL_RE = re.compile(
    r"/c/([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})"
)
_PERPLEXITY_THREAD_ID_FROM_URL_RE = re.compile(
    r"/search/([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})"
)
SUPPORTED_PROVIDERS = ("chatgpt", "perplexity")


@dataclass(frozen=True)
class SessionTokenInfo:
    token: str
    source: str
    path: Optional[Path] = None


def looks_like_online_thread_id(selector: str) -> bool:
    return bool(
        re.fullmatch(
            r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
            selector.strip(),
        )
    )


def looks_like_canonical_thread_id(selector: str) -> bool:
    return bool(re.fullmatch(r"[0-9a-f]{40}", selector.strip().lower()))


def extract_online_thread_id_from_url(selector: str) -> Optional[str]:
    match = _ONLINE_THREAD_ID_FROM_URL_RE.search(selector)
    if match:
        return match.group(1)
    return None


def extract_perplexity_thread_id_from_url(selector: str) -> Optional[str]:
    match = _PERPLEXITY_THREAD_ID_FROM_URL_RE.search(selector)
    if match:
        return match.group(1)
    return None


def detect_provider(selector: str, requested: str = "auto") -> Optional[str]:
    normalized_requested = requested.strip().lower()
    if normalized_requested != "auto":
        if normalized_requested not in SUPPORTED_PROVIDERS:
            raise ValueError(
                f"Unsupported provider: {requested}. "
                f"Expected auto, {', '.join(SUPPORTED_PROVIDERS)}."
            )
        return normalized_requested

    parsed = urlparse(selector.strip())
    host = parsed.netloc.lower()
    if host.endswith("perplexity.ai") and extract_perplexity_thread_id_from_url(selector):
        return "perplexity"
    if host.endswith("chatgpt.com") or host.endswith("chat.openai.com"):
        return "chatgpt"
    return None


def extract_source_thread_id_from_url(
    selector: str,
    provider: Optional[str] = None,
) -> Optional[str]:
    if provider == "perplexity":
        return extract_perplexity_thread_id_from_url(selector)
    if provider == "chatgpt":
        return extract_online_thread_id_from_url(selector)
    return extract_online_thread_id_from_url(selector) or extract_perplexity_thread_id_from_url(
        selector
    )


def build_provider_selector(selector: str, provider: Optional[str]) -> str:
    normalized = selector.strip()
    if provider == "perplexity" and looks_like_online_thread_id(normalized):
        return f"https://www.perplexity.ai/search/{normalized}"
    return normalized


def _read_stitched_session_token_file(path: Path) -> str:
    if not path.is_file():
        return ""
    parts = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not parts:
        return ""
    if len(parts) == 1:
        return parts[0]
    return "".join(parts)


def _config_candidates(repo_root: Optional[Path]) -> list[Path]:
    candidates = [Path.cwd() / "config.ini"]
    if repo_root is not None:
        candidates.extend(
            [
                repo_root / "config.ini",
                repo_root / "reverse-engineered-chatgpt" / "config.ini",
            ]
        )
    seen: set[Path] = set()
    unique: list[Path] = []
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        unique.append(candidate)
    return unique


def load_session_token_info(repo_root: Optional[Path] = None) -> Optional[SessionTokenInfo]:
    env_token = os.environ.get("CHATGPT_SESSION_TOKEN", "").strip()
    if env_token:
        return SessionTokenInfo(token=env_token, source="env:CHATGPT_SESSION_TOKEN")

    parser = configparser.ConfigParser()
    for config_path in _config_candidates(repo_root):
        if not config_path.is_file():
            continue
        parser.read(config_path)
        token = parser.get("session", "token", fallback="").strip()
        if token and token != "YOUR_SESSION_TOKEN":
            return SessionTokenInfo(token=token, source="config.ini", path=config_path)

    chunked_session_file = Path.home() / ".chatgpt_session_new"
    token = _read_stitched_session_token_file(chunked_session_file)
    if token:
        return SessionTokenInfo(
            token=token,
            source="file:~/.chatgpt_session_new",
            path=chunked_session_file,
        )

    session_file = Path.home() / ".chatgpt_session"
    if session_file.is_file():
        lines = session_file.read_text(encoding="utf-8", errors="ignore").splitlines()
        if lines:
            token = lines[0].strip()
            if token:
                return SessionTokenInfo(
                    token=token,
                    source="file:~/.chatgpt_session",
                    path=session_file,
                )

    return None


def load_session_token(repo_root: Optional[Path] = None) -> Optional[str]:
    token_info = load_session_token_info(repo_root=repo_root)
    return token_info.token if token_info else None


def _known_good_session_token_info() -> Optional[SessionTokenInfo]:
    path = Path.home() / ".chatgpt_session_new"
    token = _read_stitched_session_token_file(path)
    if not token:
        return None
    return SessionTokenInfo(token=token, source="file:~/.chatgpt_session_new", path=path)


def build_re_gpt_command(
    action: str,
    selector: str,
    token: str,
    repo_root: Path,
    venv_python: Path,
) -> tuple[list[str], dict]:
    env = os.environ.copy()
    module_path = str((repo_root / "reverse-engineered-chatgpt").resolve())
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = module_path if not existing else f"{module_path}:{existing}"
    if action == "download":
        env["HOME"] = str(repo_root)

    if action == "view":
        action_args = ["--nostore", "--view", selector]
    elif action == "download":
        action_args = ["--download", selector]
    else:
        raise ValueError(f"Unsupported re_gpt action: {action}")

    if venv_python.exists():
        return [
            str(venv_python),
            "-m",
            "re_gpt.cli",
            "--key",
            token,
            *action_args,
        ], env

    re_gpt_bin = shutil.which("re-gpt")
    if re_gpt_bin:
        return [re_gpt_bin, "--key", token, *action_args], env

    return [
        str(venv_python),
        "-m",
        "re_gpt.cli",
        "--key",
        token,
        *action_args,
    ], env


def redacted_command(command: list[str]) -> list[str]:
    redacted = list(command)
    for idx, part in enumerate(redacted):
        if part == "--key" and idx + 1 < len(redacted):
            redacted[idx + 1] = "<redacted>"
    return redacted


def _looks_like_catalog_miss(stdout: str) -> bool:
    return (
        "Could not fetch by ID, trying to match by title" in stdout
        and "Fetching conversation catalog in pages" in stdout
        and "Failed to find conversation matching" in stdout
    )


def _looks_like_auth_bootstrap_block(stderr: str) -> bool:
    return (
        "Unable to retrieve ChatGPT home page due to Cloudflare blocking the request" in stderr
        or ("UnexpectedResponseError" in stderr and "Cloudflare" in stderr)
    )


def _conversation_fetch_failed(process: subprocess.CompletedProcess) -> bool:
    return _looks_like_catalog_miss(process.stdout) or _looks_like_auth_bootstrap_block(
        process.stderr
    )


def _auth_diagnostic(
    *,
    process: subprocess.CompletedProcess,
    active_token: SessionTokenInfo,
) -> Optional[dict]:
    catalog_miss = _looks_like_catalog_miss(process.stdout)
    auth_bootstrap_block = _looks_like_auth_bootstrap_block(process.stderr)
    if not catalog_miss and not auth_bootstrap_block:
        return None
    known_good = _known_good_session_token_info()
    symptom = "catalog_miss" if catalog_miss else "auth_bootstrap_block"
    if known_good is None:
        return {
            "reason": f"{symptom}_ambiguous",
            "message": (
                "re_gpt did not fetch the conversation. This can be a true missing selector "
                "or stale ChatGPT auth; ~/.chatgpt_session_new is not available for comparison."
            ),
            "active_token_source": active_token.source,
        }
    if active_token.token != known_good.token:
        return {
            "reason": "probable_stale_token",
            "message": (
                "re_gpt did not fetch the conversation, and the active token differs from "
                "~/.chatgpt_session_new."
            ),
            "active_token_source": active_token.source,
            "known_good_token_source": known_good.source,
            "symptom": symptom,
        }
    return {
        "reason": f"{symptom}_with_known_good_token",
        "message": (
            "re_gpt did not fetch the conversation while using ~/.chatgpt_session_new."
        ),
        "active_token_source": active_token.source,
        "symptom": symptom,
    }


def run_re_gpt_action(
    action: str,
    selector: str,
    repo_root: Path,
    venv_python: Path,
    timeout: int,
) -> dict:
    token_info = load_session_token_info(repo_root=repo_root)
    if not token_info:
        return {
            "ok": False,
            "error": (
                "No token found for web fallback. Set CHATGPT_SESSION_TOKEN or create "
                "~/.chatgpt_session (first line = token)."
            ),
        }
    token = token_info.token

    cmd, env = build_re_gpt_command(
        action,
        selector,
        token=token,
        repo_root=repo_root,
        venv_python=venv_python,
    )
    env["CHATGPT_SESSION_TOKEN"] = token

    def _run(cmdline: list[str], run_env: dict) -> subprocess.CompletedProcess:
        proc = subprocess.run(
            cmdline,
            env=run_env,
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return proc

    def _missing_websockets(process: subprocess.CompletedProcess) -> bool:
        return (
            process.returncode != 0
            and "ModuleNotFoundError: No module named 'websockets'" in process.stderr
        )

    try:
        proc = _run(cmd, env)
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "error": f"Web fallback timed out after {timeout}s",
            "command": redacted_command(cmd),
        }
    except OSError as exc:
        return {
            "ok": False,
            "error": f"Failed to run web fallback: {exc}",
            "command": redacted_command(cmd),
        }

    retried_with = None
    if _missing_websockets(proc):
        alt_python = repo_root / "reverse-engineered-chatgpt/.venv/bin/python"
        if alt_python.exists():
            alt_cmd, _ = build_re_gpt_command(
                action,
                selector,
                token=token,
                repo_root=repo_root,
                venv_python=alt_python,
            )
            if alt_cmd[0] != cmd[0]:
                try:
                    alt_proc = _run(alt_cmd, env)
                    proc = alt_proc
                    cmd = alt_cmd
                    retried_with = str(alt_python)
                except (subprocess.TimeoutExpired, OSError):
                    pass

    extra_error = None
    if proc.returncode != 0 and "Could not resolve host: chatgpt.com" in proc.stderr:
        extra_error = (
            "Web fallback failed due DNS/network resolution for chatgpt.com. "
            "Run in an environment with outbound network access."
        )
    elif proc.returncode != 0 and "attempt to write a readonly database" in proc.stderr:
        extra_error = (
            "Web action failed because SQLite storage path is read-only in this environment."
        )
    elif _missing_websockets(proc):
        extra_error = (
            "Web fallback failed because dependency 'websockets' is missing in the selected "
            "Python environment. Install reverse-engineered-chatgpt requirements first."
        )

    retried_with_known_good = None
    diagnostic = _auth_diagnostic(process=proc, active_token=token_info)
    known_good = _known_good_session_token_info()
    if (
        action == "view"
        and diagnostic
        and diagnostic.get("reason") == "probable_stale_token"
        and known_good is not None
    ):
        retry_cmd, retry_env = build_re_gpt_command(
            action,
            selector,
            token=known_good.token,
            repo_root=repo_root,
            venv_python=venv_python,
        )
        retry_env["CHATGPT_SESSION_TOKEN"] = known_good.token
        try:
            retry_proc = _run(retry_cmd, retry_env)
            retried_with_known_good = known_good.source
            if not _conversation_fetch_failed(retry_proc):
                proc = retry_proc
                cmd = retry_cmd
                token_info = known_good
                diagnostic = _auth_diagnostic(process=proc, active_token=token_info)
            else:
                diagnostic = {
                    **diagnostic,
                    "known_good_retry": {
                        "ok": retry_proc.returncode == 0,
                        "returncode": retry_proc.returncode,
                        "stdout": retry_proc.stdout,
                        "stderr": retry_proc.stderr,
                        "command": redacted_command(retry_cmd),
                    },
                }
        except subprocess.TimeoutExpired:
            diagnostic = {
                **diagnostic,
                "known_good_retry_error": f"Web fallback timed out after {timeout}s",
            }
        except OSError as exc:
            diagnostic = {
                **diagnostic,
                "known_good_retry_error": f"Failed to run web fallback: {exc}",
            }

    return {
        "ok": proc.returncode == 0 and not _conversation_fetch_failed(proc),
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "command": redacted_command(cmd),
        "error": extra_error
        or (
            diagnostic.get("message")
            if diagnostic and _conversation_fetch_failed(proc)
            else None
        ),
        "retried_with_python": retried_with,
        "retried_with_known_good_token": retried_with_known_good,
        "auth_diagnostic": diagnostic,
    }


def _perplexity_export_repo(repo_root: Path) -> Path:
    configured = os.environ.get("PERPLEXITY_AI_EXPORT_DIR", "").strip()
    if configured:
        return Path(configured).expanduser()
    return repo_root.parent / "perplexity-ai-export"


def run_perplexity_export(
    selector: str,
    repo_root: Path,
    timeout: int,
    scroll_mode: str | None = None,
) -> dict:
    export_repo = _perplexity_export_repo(repo_root)
    package_json = export_repo / "package.json"
    if not package_json.exists():
        return {
            "ok": False,
            "error": f"Missing Perplexity exporter package: {package_json}",
            "command": [],
        }

    provider_selector = build_provider_selector(selector, "perplexity")
    thread_id = extract_perplexity_thread_id_from_url(provider_selector)
    if not thread_id:
        return {
            "ok": False,
            "error": (
                "Perplexity export needs a URL like "
                "https://www.perplexity.ai/search/<uuid> or a UUID with --provider perplexity."
            ),
            "command": [],
        }

    output_path = export_repo / "exports-resolver" / f"{thread_id}.itir.perplexity.json"
    cmd = [
        "npm",
        "run",
        "export:thread",
        "--",
        "--url",
        provider_selector,
        "--out",
        str(output_path),
        "--json",
    ]
    env = os.environ.copy()
    env.setdefault("HEADLESS", "true")
    env.setdefault("EXPORT_STRUCTURED_JSON", "true")
    env.setdefault("EXPORT_MARKDOWN", "false")
    if scroll_mode:
        env["PERPLEXITY_SCROLL_MODE"] = scroll_mode

    try:
        proc = subprocess.run(
            cmd,
            cwd=str(export_repo),
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "error": f"Perplexity export timed out after {timeout}s",
            "command": cmd,
            "output_path": str(output_path),
        }
    except OSError as exc:
        return {
            "ok": False,
            "error": f"Failed to run Perplexity exporter: {exc}",
            "command": cmd,
            "output_path": str(output_path),
        }

    parsed_stdout = None
    stdout = proc.stdout.strip()
    if stdout:
        try:
            parsed_stdout = json.loads(stdout)
        except json.JSONDecodeError:
            parsed_stdout = None
    parsed_output_path = (
        parsed_stdout.get("output_path")
        if isinstance(parsed_stdout, dict) and parsed_stdout.get("output_path")
        else None
    )
    if parsed_output_path:
        output_path = Path(str(parsed_output_path))

    export_diagnostic = _inspect_perplexity_export(output_path)
    extra_error = None
    if proc.returncode != 0:
        extra_error = (
            "Perplexity export failed. Refresh the saved browser auth state in "
            f"{export_repo} if the browser login or Cloudflare check blocked this run."
        )
    elif export_diagnostic.get("partial"):
        extra_error = (
            "Perplexity export appears partial: the live app loader did not reach a stable "
            "full-thread state. Refresh browser auth or rerun with a higher "
            "PERPLEXITY_MAX_SCROLL_PASSES value."
        )

    return {
        "ok": proc.returncode == 0
        and output_path.exists()
        and not export_diagnostic.get("partial"),
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "command": cmd,
        "error": extra_error,
        "output_path": str(output_path),
        "parsed_stdout": parsed_stdout,
        "export_diagnostic": export_diagnostic,
    }


def _inspect_perplexity_export(output_path: Path) -> dict:
    if not output_path.exists():
        return {"exists": False}
    try:
        payload = json.loads(output_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"exists": True, "error": str(exc)}

    messages = payload.get("messages") if isinstance(payload, dict) else None
    raw = payload.get("raw") if isinstance(payload, dict) else None
    api_response = raw.get("api_response") if isinstance(raw, dict) else None
    raw_entries = raw.get("entries") if isinstance(raw, dict) else None
    has_next_page = api_response.get("has_next_page") if isinstance(api_response, dict) else None
    extraction = api_response.get("extraction") if isinstance(api_response, dict) else None
    extraction_partial = (
        extraction.get("partial") if isinstance(extraction, dict) else None
    )
    return {
        "exists": True,
        "schema": payload.get("schema") if isinstance(payload, dict) else None,
        "source": payload.get("source") if isinstance(payload, dict) else None,
        "message_count": len(messages) if isinstance(messages, list) else None,
        "raw_entry_count": len(raw_entries) if isinstance(raw_entries, list) else None,
        "api_has_next_page": has_next_page,
        "extraction": extraction,
        "partial": extraction_partial is True
        if extraction_partial is not None
        else has_next_page is True,
    }


def run_live_view(
    provider: str,
    selector: str,
    repo_root: Path,
    venv_python: Path,
    timeout: int,
) -> dict:
    if provider == "chatgpt":
        return run_re_gpt_action(
            action="view",
            selector=selector,
            repo_root=repo_root,
            venv_python=venv_python,
            timeout=timeout,
        )
    if provider == "perplexity":
        return {
            "ok": False,
            "error": (
                "Perplexity live fetch is export-and-ingest only; use the persistence path."
            ),
            "command": [],
        }
    return {"ok": False, "error": f"Unsupported provider: {provider}", "command": []}


def run_live_download(
    provider: str,
    selector: str,
    repo_root: Path,
    venv_python: Path,
    timeout: int,
    perplexity_scroll_mode: str | None = None,
) -> dict:
    if provider == "chatgpt":
        return run_re_gpt_action(
            action="download",
            selector=selector,
            repo_root=repo_root,
            venv_python=venv_python,
            timeout=timeout,
        )
    if provider == "perplexity":
        return run_perplexity_export(
            selector=selector,
            repo_root=repo_root,
            timeout=timeout,
            scroll_mode=perplexity_scroll_mode,
        )
    return {"ok": False, "error": f"Unsupported provider: {provider}", "command": []}


def run_web_view(selector: str, repo_root: Path, venv_python: Path, timeout: int) -> dict:
    return run_live_view(
        provider="chatgpt",
        selector=selector,
        repo_root=repo_root,
        venv_python=venv_python,
        timeout=timeout,
    )


def run_web_download(selector: str, repo_root: Path, venv_python: Path, timeout: int) -> dict:
    return run_live_download(
        provider="chatgpt",
        selector=selector,
        repo_root=repo_root,
        venv_python=venv_python,
        timeout=timeout,
    )


def resolve_live_conversation(chatgpt: object, selector: str) -> Optional[dict]:
    normalized = selector.strip()
    if not normalized:
        return None
    if looks_like_online_thread_id(normalized):
        return {
            "conversation_id": normalized,
            "title": None,
            "match_type": "online_thread_id",
        }

    target = normalized.lower()
    fallback_contains: Optional[dict] = None
    offset = 0
    limit = 100
    while True:
        page = chatgpt.list_conversations_page(offset=offset, limit=limit)
        items = page.get("items", []) if isinstance(page, dict) else []
        if not items:
            break
        for item in items:
            title = (item.get("title") or "").strip()
            conversation_id = item.get("id")
            if not title or not conversation_id:
                continue
            lowered = title.lower()
            if lowered == target:
                return {
                    "conversation_id": conversation_id,
                    "title": title,
                    "match_type": "title_exact",
                }
            if target in lowered and fallback_contains is None:
                fallback_contains = {
                    "conversation_id": conversation_id,
                    "title": title,
                    "match_type": "title_contains",
                }
        offset += len(items)
        if len(items) < limit:
            break
    return fallback_contains


def fetch_web_recent_turns(
    selector: str,
    repo_root: Path,
    limit: int,
    max_text_chars: int,
    *,
    parse_message_ts,
    iso_utc_precise,
    truncate_text,
) -> dict:
    if limit <= 0:
        return {"ok": True, "recent_turns": []}

    token = load_session_token(repo_root=repo_root)
    if not token:
        return {
            "ok": False,
            "error": (
                "No token found for live message timestamp fetch. Set CHATGPT_SESSION_TOKEN "
                "or create ~/.chatgpt_session (first line = token)."
            ),
        }

    module_path = str((repo_root / "reverse-engineered-chatgpt").resolve())
    if module_path not in sys.path:
        sys.path.insert(0, module_path)

    try:
        from re_gpt.storage import extract_ordered_messages
        from re_gpt.sync_chatgpt import SyncChatGPT
    except Exception as exc:
        return {
            "ok": False,
            "error": f"Unable to import reverse-engineered-chatgpt modules: {exc}",
        }

    try:
        with SyncChatGPT(session_token=token) as chatgpt:
            resolved = resolve_live_conversation(chatgpt, selector)
            if not resolved:
                return {
                    "ok": False,
                    "error": f"Unable to resolve conversation selector for live turns: {selector}",
                }

            conversation = chatgpt.get_conversation(
                resolved["conversation_id"],
                title=resolved.get("title"),
            )
            chat = conversation.fetch_chat()
            ordered = extract_ordered_messages(chat)
            selected = ordered[-limit:]
            start_pos = max(1, len(ordered) - len(selected) + 1)
            turns: list[dict] = []
            for idx, message in enumerate(selected, start=start_pos):
                parsed_ts = parse_message_ts(message.get("create_time"))
                turns.append(
                    {
                        "position": idx,
                        "ts": message.get("create_time"),
                        "ts_utc": iso_utc_precise(parsed_ts),
                        "role": message.get("author"),
                        "text": truncate_text(
                            str(message.get("content") or ""),
                            max_text_chars,
                        ),
                    }
                )
            return {
                "ok": True,
                "conversation_id": resolved["conversation_id"],
                "title": conversation.title or resolved.get("title"),
                "match_type": resolved.get("match_type"),
                "total_message_count": len(ordered),
                "recent_turns": turns,
            }
    except Exception as exc:
        return {
            "ok": False,
            "error": f"Live turn fetch failed: {exc}",
        }
