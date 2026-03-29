from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_URL_RE = re.compile(r"/notebook/([a-f0-9-]+)")


def extract_notebook_id(value: str) -> str:
    compact = str(value or "").strip()
    if not compact:
        raise ValueError("notebook id/url is required")
    match = NOTEBOOK_URL_RE.search(compact)
    if match:
        return match.group(1)
    if compact.startswith("http://") or compact.startswith("https://"):
        raise ValueError(f"could not extract notebook id from URL: {compact}")
    return compact


def parse_item(text: str) -> tuple[str, str]:
    if ":" not in text:
        raise ValueError(f"item must be CATEGORY:TEXT, got: {text!r}")
    category, content = text.split(":", 1)
    category = category.strip()
    content = content.strip()
    if not category or not content:
        raise ValueError(f"item must include non-empty CATEGORY and TEXT, got: {text!r}")
    return category, content


def build_clarify_prompt(
    *,
    items: list[tuple[str, str]],
    context: str | None = None,
    agent_message: str | None = None,
    preface: str = "Please clarify:",
) -> str:
    lines: list[str] = [preface.strip() or "Please clarify:"]
    for category, content in items:
        lines.append(f"{category}: {content}")
    if context:
        lines.extend(["", "Context:", context.strip()])
    if agent_message:
        lines.extend(["", "Additional request:", agent_message.strip()])
    return "\n".join(lines).strip()


def resolve_notebooklm_cli(explicit: str | None = None) -> str:
    candidates: list[str] = []
    if explicit:
        candidates.append(explicit)
    candidates.extend(
        [
            str(REPO_ROOT / ".venv" / "bin" / "notebooklm"),
            str(REPO_ROOT / "notebooklm-py" / ".venv" / "bin" / "notebooklm"),
        ]
    )
    found = shutil.which("notebooklm")
    if found:
        candidates.append(found)
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return candidate
    raise RuntimeError("could not find notebooklm CLI; checked repo venv, notebooklm-py venv, and PATH")


def build_ask_command(
    *,
    notebook_id: str,
    question: str,
    notebooklm_cli: str,
    conversation_id: str | None = None,
    new_conversation: bool = False,
) -> list[str]:
    cmd = [notebooklm_cli, "ask", "--notebook", notebook_id]
    if conversation_id:
        cmd.extend(["--conversation-id", conversation_id])
    elif new_conversation:
        cmd.append("--new")
    cmd.extend(["--question", question])
    return cmd


def execute_command(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.setdefault("PYTHONUNBUFFERED", "1")
    return subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ask a NotebookLM notebook to clarify structured category/string inputs.")
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--notebook-id")
    target.add_argument("--notebook-url")
    parser.add_argument("--item", action="append", default=[], help="Repeat CATEGORY:TEXT items to build a structured clarify prompt.")
    parser.add_argument("--context", help="Optional shared context appended under a Context block.")
    parser.add_argument("--agent-message", help="Optional extra request appended under Additional request.")
    parser.add_argument("--question", help="Use an explicit question instead of building one from --item entries.")
    parser.add_argument("--preface", default="Please clarify:", help="Prompt preface when building a structured question.")
    parser.add_argument("--conversation-id", help="Continue a specific NotebookLM conversation id.")
    parser.add_argument("--new", action="store_true", help="Force a new conversation instead of the default persisted route.")
    parser.add_argument("--notebooklm-cli", help="Override notebooklm CLI path.")
    parser.add_argument("--dry-run", action="store_true", help="Print the planned command and prompt without executing.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    notebook_id = extract_notebook_id(args.notebook_url or args.notebook_id)
    items = [parse_item(text) for text in args.item]
    if args.question:
        question = str(args.question).strip()
    else:
        if not items:
            raise SystemExit("either --question or at least one --item CATEGORY:TEXT is required")
        question = build_clarify_prompt(
            items=items,
            context=args.context,
            agent_message=args.agent_message,
            preface=str(args.preface),
        )

    notebooklm_cli = resolve_notebooklm_cli(args.notebooklm_cli)
    cmd = build_ask_command(
        notebook_id=notebook_id,
        question=question,
        notebooklm_cli=notebooklm_cli,
        conversation_id=args.conversation_id,
        new_conversation=bool(args.new),
    )
    payload: dict[str, Any] = {
        "mode": "dry_run" if args.dry_run else "executed",
        "notebook_id": notebook_id,
        "question": question,
        "command": cmd,
    }
    if args.dry_run:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    result = execute_command(cmd)
    payload["returncode"] = result.returncode
    payload["stdout"] = result.stdout
    payload["stderr"] = result.stderr
    print(json.dumps(payload, indent=2, sort_keys=True))
    return int(result.returncode)


if __name__ == "__main__":
    raise SystemExit(main())
