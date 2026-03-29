from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional


_ONLINE_THREAD_ID_FROM_URL_RE = re.compile(
    r"/c/([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})"
)


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


def load_session_token() -> Optional[str]:
    env_token = os.environ.get("CHATGPT_SESSION_TOKEN", "").strip()
    if env_token:
        return env_token

    session_file = Path.home() / ".chatgpt_session"
    if session_file.exists():
        first_line = session_file.read_text(encoding="utf-8", errors="ignore").splitlines()
        if first_line:
            token = first_line[0].strip()
            if token:
                return token

    return None


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


def run_re_gpt_action(
    action: str,
    selector: str,
    repo_root: Path,
    venv_python: Path,
    timeout: int,
) -> dict:
    token = load_session_token()
    if not token:
        return {
            "ok": False,
            "error": (
                "No token found for web fallback. Set CHATGPT_SESSION_TOKEN or create "
                "~/.chatgpt_session (first line = token)."
            ),
        }

    cmd, env = build_re_gpt_command(
        action,
        selector,
        token=token,
        repo_root=repo_root,
        venv_python=venv_python,
    )
    env["CHATGPT_SESSION_TOKEN"] = token

    def _run(cmdline: list[str]) -> subprocess.CompletedProcess:
        proc = subprocess.run(
            cmdline,
            env=env,
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
        proc = _run(cmd)
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
                    alt_proc = _run(alt_cmd)
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

    return {
        "ok": proc.returncode == 0,
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "command": redacted_command(cmd),
        "error": extra_error,
        "retried_with_python": retried_with,
    }


def run_web_view(selector: str, repo_root: Path, venv_python: Path, timeout: int) -> dict:
    return run_re_gpt_action(
        action="view",
        selector=selector,
        repo_root=repo_root,
        venv_python=venv_python,
        timeout=timeout,
    )


def run_web_download(selector: str, repo_root: Path, venv_python: Path, timeout: int) -> dict:
    return run_re_gpt_action(
        action="download",
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

    token = load_session_token()
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
