#!/usr/bin/env python
from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import hashlib
import html
import json
import re
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse
from typing import Any


def _sqlite_ro_uri(path: Path) -> str:
    resolved = path.expanduser().resolve()
    return f"file:{resolved}?mode=ro&immutable=1"


def _connect_ro(db_path: Path) -> sqlite3.Connection:
    con = sqlite3.connect(_sqlite_ro_uri(db_path), uri=True)
    con.row_factory = sqlite3.Row
    try:
        con.execute("PRAGMA temp_store=MEMORY")
        con.execute("PRAGMA query_only=ON")
    except sqlite3.Error:
        pass
    return con


def _utc_now() -> str:
    return dt.datetime.now(tz=dt.timezone.utc).replace(microsecond=0).isoformat()


def _parse_ts(value: object) -> dt.datetime | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return dt.datetime.fromtimestamp(float(text), tz=dt.timezone.utc)
    except ValueError:
        normalized = text[:-1] + "+00:00" if text.endswith("Z") else text
        try:
            parsed = dt.datetime.fromisoformat(normalized)
        except ValueError:
            return None
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=dt.timezone.utc)
        return parsed.astimezone(dt.timezone.utc)


def _iso_utc(value: object) -> str | None:
    parsed = _parse_ts(value)
    if parsed is None:
        return None
    return parsed.isoformat().replace("+00:00", "Z")


def _slug(value: str, fallback: str) -> str:
    chars = [char.lower() if char.isalnum() or char in "._-" else "-" for char in value.strip()]
    text = "-".join(part for part in "".join(chars).split("-") if part).strip("-._")
    return text[:80] or fallback


def _split_prompt_heading(text: str, fallback: str) -> tuple[str, str]:
    stripped = text.strip()
    if not stripped:
        return fallback, ""

    first_breaks = [idx for idx in (stripped.find("\n"), stripped.find("\r")) if idx >= 0]
    first_line_end = min(first_breaks) if first_breaks else -1
    sentence_end = -1
    for idx, char in enumerate(stripped[:-1]):
        if char in ".!?" and stripped[idx + 1].isspace():
            sentence_end = idx + 1
            break

    candidates = [idx for idx in (first_line_end, sentence_end) if idx > 0]
    split_at = min(candidates) if candidates else len(stripped)
    heading = " ".join(stripped[:split_at].strip().split())
    remainder = stripped[split_at:].lstrip()
    return heading or fallback, remainder


def _plain_text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return " ".join(str(value).split())


def _iter_fenced_segments(text: str) -> list[tuple[bool, str]]:
    segments: list[tuple[bool, str]] = []
    in_fence = False
    current: list[str] = []
    for line in text.splitlines(keepends=True):
        stripped = line.lstrip()
        if stripped.startswith(("```", "~~~")):
            if current:
                segments.append((in_fence, "".join(current)))
                current = []
            segments.append((in_fence, line))
            in_fence = not in_fence
            continue
        current.append(line)
    if current:
        segments.append((in_fence, "".join(current)))
    return segments


def _compact_url_label(url: str, *, max_len: int = 72) -> str:
    if len(url) <= max_len:
        return url
    parsed = urlparse(url)
    host = parsed.netloc or parsed.scheme or "link"
    path = parsed.path.rstrip("/")
    if path and path != "/":
        tail = path.rsplit("/", 1)[-1] or path
        label = f"{host}/.../{tail}"
    else:
        label = host
    if parsed.query:
        label += "?..."
    if len(label) > max_len:
        label = label[: max_len - 1].rstrip() + "..."
    return label


def _has_private_use_icon(text: str) -> bool:
    return bool(_PRIVATE_USE_RE.search(text))


def _has_pathish_char(text: str) -> bool:
    return any(char.isalnum() or char in "_.-" for char in text)


def _is_short_status_line(text: str) -> bool:
    if not text or len(text) > 4:
        return False
    return all(char in " MADRCU?!" for char in text)


def _is_option_name(text: str) -> bool:
    if not text or not text[0].isalpha():
        return False
    return all(char.isalnum() or char == "-" for char in text)


def _is_split_letter_label(text: str) -> bool:
    return len(text) >= 4 and text[0] == "-" and text[1].isspace() and text[2].isupper() and text[3] == ":"


def _compact_display_links(markdown: str) -> str:
    def compact_markdown_link(match: re.Match[str]) -> str:
        label = match.group("label")
        url = match.group("url")
        if label.startswith(("http://", "https://")) and len(label) > 72:
            label = _compact_url_label(label)
        return f"[{label}]({url})"

    def compact_bare_url(match: re.Match[str]) -> str:
        url = match.group(0)
        if len(url) <= 72:
            return url
        return f"[{_compact_url_label(url)}]({url})"

    out: list[str] = []
    for in_fence, segment in _iter_fenced_segments(markdown):
        if in_fence:
            out.append(segment)
            continue
        segment = re.sub(
            r"\[(?P<label>https?://[^\]\s]+)\]\((?P<url>https?://[^)\s]+)\)",
            compact_markdown_link,
            segment,
        )
        segment = re.sub(r"(?<!\]\()https?://[^\s<>)\]]{73,}", compact_bare_url, segment)
        out.append(segment)
    return "".join(out)


def _normalize_math_delimiters(markdown: str) -> str:
    out: list[str] = []
    for in_fence, segment in _iter_fenced_segments(markdown):
        if in_fence:
            out.append(segment)
            continue
        segment = re.sub(r"\\\[(.*?)\\\]", lambda m: "\n$$\n" + m.group(1).strip() + "\n$$\n", segment, flags=re.S)
        segment = re.sub(r"\\\((.*?)\\\)", lambda m: "$" + m.group(1).strip() + "$", segment, flags=re.S)
        out.append(segment)
    return "".join(out)


def _diagnose_markdown(markdown: str) -> list[dict[str, Any]]:
    diagnostics: list[dict[str, Any]] = []
    non_code = "".join(segment for in_fence, segment in _iter_fenced_segments(markdown) if not in_fence)
    if len(re.findall(r"(?<!\\)\$", non_code)) % 2:
        diagnostics.append(
            {
                "level": "warning",
                "kind": "math_delimiter_balance",
                "message": "Odd number of unescaped dollar math delimiters outside fenced code.",
            }
        )
    if non_code.count(r"\[") != non_code.count(r"\]"):
        diagnostics.append(
            {
                "level": "warning",
                "kind": "display_math_delimiter_balance",
                "message": "Mismatched \\[...\\] display math delimiters outside fenced code.",
            }
        )
    if non_code.count(r"\(") != non_code.count(r"\)"):
        diagnostics.append(
            {
                "level": "warning",
                "kind": "inline_math_delimiter_balance",
                "message": "Mismatched \\(...\\) inline math delimiters outside fenced code.",
            }
        )
    for line_no, line in enumerate(markdown.splitlines(), start=1):
        if "http" in line and re.search(r"\[[^\]]+\]\(https?://[^)\s]*$", line):
            diagnostics.append(
                {
                    "level": "warning",
                    "kind": "possibly_truncated_markdown_link",
                    "line": line_no,
                    "message": "Markdown link destination appears unterminated.",
                }
            )
    return diagnostics


_DATE_TIME_LINE_RE = re.compile(r"^\d{1,2}\s+[A-Z][a-z]{2}\s+\d{1,2}:\d{2}$")
_SIZE_LINE_RE = re.compile(r"^\d+(?:\.\d+)?\s*(?:[KMGTPE]?i?B|[KMGTPEkmgtpe])?$")
_PERM_FRAGMENT_RE = re.compile(r"^(?:[dl.]|[rwxstST-]{1,4})$")
_FILENAME_LINE_RE = re.compile(r"(^|[/\s])[^/\s]+\.[A-Za-z0-9][A-Za-z0-9._-]*$")
_DOTFILE_LINE_RE = re.compile(r"^\.[A-Za-z0-9][A-Za-z0-9._-]*$")
_PATH_SEGMENT_LINE_RE = re.compile(r"^(?=.*[._/-])[A-Za-z0-9_./-]{2,80}$")
_PLAIN_PATH_NAME_RE = re.compile(r"^[A-Za-z0-9_-]{2,80}$")
_PRIVATE_USE_RE = re.compile(r"[\ue000-\uf8ff\U000f0000-\U000ffffd]")
_SHELL_WORDS = {"ls", "cd", "pwd"}


def _is_fragmented_listing_token(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return True
    if stripped in _SHELL_WORDS:
        return False
    if len(stripped) > 96:
        return False
    if _DATE_TIME_LINE_RE.match(stripped):
        return True
    if _SIZE_LINE_RE.match(stripped):
        return True
    if _PERM_FRAGMENT_RE.match(stripped):
        return True
    if _FILENAME_LINE_RE.search(stripped) or _DOTFILE_LINE_RE.match(stripped) or _PATH_SEGMENT_LINE_RE.match(stripped):
        return True
    if len(stripped) <= 3:
        return True
    if _has_private_use_icon(stripped) and len(stripped) <= 80:
        return True
    return False


def _parse_fragmented_listing_rows(lines: list[str]) -> tuple[list[str], int, float]:
    tokens = [line.strip() for line in lines if line.strip()]
    rows: list[str] = []
    consumed = 0
    index = 0

    def date_offset(start: int, *, max_scan: int = 16) -> int:
        for offset in range(0, min(max_scan, len(tokens) - start)):
            if _DATE_TIME_LINE_RE.match(tokens[start + offset]):
                return offset
        return -1

    def prefix_can_start_row(prefix: list[str]) -> bool:
        if not prefix:
            return True
        body = prefix
        if len(body[-1]) <= 3 and not _PERM_FRAGMENT_RE.match(body[-1]):
            body = body[:-1]
        return all(_PERM_FRAGMENT_RE.match(token) for token in body)

    def row_start_at(start: int) -> bool:
        offset = date_offset(start)
        if offset < 0:
            return False
        prefix = tokens[start : start + offset]
        return prefix_can_start_row(prefix)

    def token_has_private_icon(token: str) -> bool:
        return _has_private_use_icon(token)

    def is_name_token(token: str) -> bool:
        if _PERM_FRAGMENT_RE.match(token) or _SIZE_LINE_RE.match(token):
            return False
        without_icon = _PRIVATE_USE_RE.sub("", token).strip()
        return bool(
            _FILENAME_LINE_RE.search(token)
            or _DOTFILE_LINE_RE.match(token)
            or _PATH_SEGMENT_LINE_RE.match(token)
            or _FILENAME_LINE_RE.search(without_icon)
            or _DOTFILE_LINE_RE.match(without_icon)
            or _PATH_SEGMENT_LINE_RE.match(without_icon)
        )

    def name_leading_row_start_at(start: int) -> bool:
        if start >= len(tokens) or not is_name_token(tokens[start]):
            return False
        pos = start + 1
        offset = date_offset(pos, max_scan=14)
        if offset < 0:
            return False
        between = tokens[pos : pos + offset]
        if not between:
            return False
        saw_perm = False
        for token in between:
            if _PERM_FRAGMENT_RE.match(token):
                saw_perm = True
                continue
            if _SIZE_LINE_RE.match(token):
                continue
            if len(token) <= 3:
                continue
            return False
        return saw_perm

    def parse_name_leading_row(start: int) -> tuple[str | None, int, int]:
        if start >= len(tokens) or not is_name_token(tokens[start]):
            return None, start + 1, 0
        name_parts = [tokens[start]]
        pos = start + 1
        perm_parts: list[str] = []
        size = ""
        status = ""
        date_time = ""
        while pos < len(tokens):
            token = tokens[pos]
            if _DATE_TIME_LINE_RE.match(token):
                date_time = token
                pos += 1
                break
            if _PERM_FRAGMENT_RE.match(token):
                perm_parts.append(token)
                pos += 1
                continue
            if _SIZE_LINE_RE.match(token):
                size = token
                pos += 1
                continue
            if len(token) <= 3:
                status = token
                pos += 1
                continue
            return None, start + 1, 0
        if not date_time or not perm_parts:
            return None, start + 1, 0
        columns = [date_time]
        if status:
            columns.append(status)
        columns.append(_plain_text(" ".join(name_parts)))
        columns.append("".join(perm_parts))
        if size:
            columns.append(size)
        return "  ".join(columns), pos, 1 + len(perm_parts) + (1 if size else 0) + (1 if status else 0) + 1

    while index < len(tokens):
        name_row, next_index, row_consumed = parse_name_leading_row(index)
        if name_row is not None:
            rows.append(name_row)
            consumed += row_consumed
            index = next_index
            continue
        if index + 1 < len(tokens) and rows and token_has_private_icon(tokens[index]) and _PLAIN_PATH_NAME_RE.match(tokens[index + 1]):
            rows.append(f"{tokens[index]} {tokens[index + 1]}")
            consumed += 2
            index += 2
            continue
        if rows and token_has_private_icon(tokens[index]) and _has_pathish_char(tokens[index]):
            rows.append(tokens[index])
            consumed += 1
            index += 1
            continue

        status = ""
        perm_parts: list[str] = []
        offset = date_offset(index)
        if offset < 0:
            index += 1
            continue
        prefix = tokens[index : index + offset]
        if prefix and not prefix_can_start_row(prefix):
            index += 1
            continue
        if prefix and len(prefix[-1]) <= 3 and not _PERM_FRAGMENT_RE.match(prefix[-1]):
            status = prefix[-1]
            prefix = prefix[:-1]
        elif prefix and prefix[-1] == "c":
            status = prefix[-1]
            prefix = prefix[:-1]
        perm_parts.extend(token for token in prefix if _PERM_FRAGMENT_RE.match(token))
        index += offset
        date_time = tokens[index]
        index += 1

        name_parts: list[str] = []
        size = ""
        while index < len(tokens) and len(name_parts) < 4:
            token = tokens[index]
            if row_start_at(index) or _DATE_TIME_LINE_RE.match(token):
                break
            if _SIZE_LINE_RE.match(token):
                size = token
                index += 1
                break
            if name_parts and _PERM_FRAGMENT_RE.match(token):
                break
            name_parts.append(token)
            index += 1
            if _PLAIN_PATH_NAME_RE.match(token) and index < len(tokens) and token_has_private_icon(tokens[index]):
                break
            if (
                _FILENAME_LINE_RE.search(" ".join(name_parts))
                or any(_DOTFILE_LINE_RE.match(part) or _PATH_SEGMENT_LINE_RE.match(part) for part in name_parts)
            ) and (
                index >= len(tokens) or _SIZE_LINE_RE.match(tokens[index]) or row_start_at(index)
            ):
                break
        if not name_parts:
            continue

        while index < len(tokens):
            token = tokens[index]
            if row_start_at(index) or name_leading_row_start_at(index) or _DATE_TIME_LINE_RE.match(token):
                break
            if _SIZE_LINE_RE.match(token):
                size = token
                index += 1
                break
            if _PERM_FRAGMENT_RE.match(token):
                if len("".join(perm_parts)) >= 10:
                    break
                perm_parts.append(token)
                index += 1
                continue
            break

        name = _plain_text(" ".join(name_parts))
        perm = "".join(perm_parts)
        columns = [date_time]
        if status:
            columns.append(status)
        columns.append(name)
        if perm:
            columns.append(perm)
        if size:
            columns.append(size)
        rows.append("  ".join(columns))
        consumed += 1 + (1 if status else 0) + len(name_parts) + len(perm_parts) + (1 if size else 0)

    if not rows:
        return [], 0, 0.0
    confidence = min(0.99, 0.55 + 0.08 * len(rows) + 0.25 * (consumed / max(1, len(tokens))))
    return rows, consumed, confidence


def _repair_fragmented_listing_markdown(
    markdown: str,
    *,
    policy: str,
) -> tuple[str, list[dict[str, Any]]]:
    if policy == "off":
        return markdown, []

    min_rows = 2 if policy == "aggressive" else 3
    min_confidence = 0.72 if policy == "aggressive" else 0.85
    diagnostics: list[dict[str, Any]] = []
    output: list[str] = []
    global_line = 1

    def can_continue_with_plain_name(candidate: list[str], line: str) -> bool:
        stripped = line.strip()
        if not candidate or stripped in _SHELL_WORDS or not _PLAIN_PATH_NAME_RE.match(stripped):
            return False
        previous = next((item.strip() for item in reversed(candidate) if item.strip()), "")
        if previous and _has_private_use_icon(previous):
            return True
        tokens = [item.strip() for item in candidate if item.strip()]
        last_date_index = -1
        for pos in range(len(tokens) - 1, -1, -1):
            if _DATE_TIME_LINE_RE.match(tokens[pos]):
                last_date_index = pos
                break
        if last_date_index < 0:
            return False
        tail = tokens[last_date_index + 1 :]
        # Plain names like "artifacts" have too little evidence by themselves.
        # Accept them only as the missing name of the latest timestamped row,
        # never as a candidate starter or after a row already has a name/size.
        if len(tail) > 1:
            return False
        return all(
            len(token) <= 3 or _has_private_use_icon(token)
            for token in tail
        )

    for in_fence, segment in _iter_fenced_segments(markdown):
        if in_fence:
            output.append(segment)
            global_line += segment.count("\n")
            continue

        lines = segment.splitlines()
        repaired_lines: list[str] = []
        index = 0
        while index < len(lines):
            line = lines[index]
            if (
                line.startswith(("#", "|", ">", "-", "*", "+"))
                and line.strip() not in {"-", "--", "---", "."}
            ) or (
                line.startswith(("    ", "- ", "* ", "+ "))
                or line.startswith("    ")
                or line.strip().startswith(("$$", r"\[", r"\("))
                or not _is_fragmented_listing_token(line)
            ):
                repaired_lines.append(line)
                index += 1
                continue

            start = index
            candidate: list[str] = []
            while index < len(lines) and (
                _is_fragmented_listing_token(lines[index])
                or can_continue_with_plain_name(candidate, lines[index])
            ):
                candidate.append(lines[index])
                index += 1
            rows, consumed, confidence = _parse_fragmented_listing_rows(candidate)
            token_count = len([item for item in candidate if item.strip()])
            if len(rows) >= min_rows and confidence >= min_confidence and consumed >= max(8, token_count // 2):
                repaired_lines.append("```text")
                repaired_lines.extend(rows)
                repaired_lines.append("```")
                diagnostics.append(
                    {
                        "level": "info",
                        "kind": "fragmented_listing_repair",
                        "line": global_line + start,
                        "end_line": global_line + index - 1,
                        "rows_repaired": len(rows),
                        "confidence": round(confidence, 3),
                        "message": "Reflowed a high-confidence fragmented terminal/file listing for display only.",
                    }
                )
            else:
                nonblank_candidate = [item.strip() for item in candidate if item.strip()]
                if (
                    len(nonblank_candidate) == 1
                    and _has_private_use_icon(nonblank_candidate[0])
                    and repaired_lines
                    and repaired_lines[-1] == "```"
                ):
                    repaired_lines.pop()
                    repaired_lines.append(nonblank_candidate[0])
                    repaired_lines.append("```")
                else:
                    repaired_lines.extend(candidate)

        output.append("\n".join(repaired_lines))
        if segment.endswith("\n"):
            output.append("\n")
        global_line += segment.count("\n")

    repaired = "".join(output)
    repaired = re.sub(
        r"```\n+\s*([^\n]*[\ue000-\uf8ff\U000f0000-\U000ffffd][^\n]*)\s*\n+```text\n",
        r"\1\n",
        repaired,
    )
    return repaired, diagnostics


_CODEX_TOOL_MARKERS = {"Ran", "Explored", "Edited", "Read", "Search", "Waited for background terminal"}


def _repair_codex_transcript_markdown(markdown: str) -> tuple[str, list[dict[str, Any]]]:
    diagnostics: list[dict[str, Any]] = []
    output: list[str] = []
    global_line = 1

    def is_separator(line: str) -> bool:
        stripped = line.strip()
        return len(stripped) >= 20 and set(stripped) <= {"─", "-"}

    def next_nonblank(lines: list[str], start: int) -> tuple[int, str] | None:
        for pos in range(start, len(lines)):
            if lines[pos].strip():
                return pos, lines[pos].strip()
        return None

    def looks_like_tool_block_start(lines: list[str], index: int) -> bool:
        stripped = lines[index].strip()
        if stripped in _CODEX_TOOL_MARKERS:
            return True
        if stripped != "•":
            return False
        nxt = next_nonblank(lines, index + 1)
        return bool(nxt and nxt[1] in _CODEX_TOOL_MARKERS)

    def collect_tool_block(lines: list[str], start: int) -> tuple[list[str], int]:
        block: list[str] = []
        index = start
        while index < len(lines):
            stripped = lines[index].strip()
            if index > start and is_separator(stripped):
                break
            if index > start and _is_split_letter_label(stripped):
                break
            if index > start and stripped == "•":
                break
            block.append(lines[index])
            index += 1
        return block, index

    def normalize_tool_block(block: list[str]) -> list[str]:
        normalized = [line.strip() for line in block if line.strip()]
        if normalized and normalized[0] == "•" and len(normalized) > 1:
            normalized[0] = f"• {normalized[1]}"
            del normalized[1]
        if normalized and normalized[0] == "• Ran":
            command_parts: list[str] = []
            rest_start = 1
            for pos in range(1, len(normalized)):
                token = normalized[pos]
                if (
                    token.startswith(("└", "│", "…"))
                    or token.startswith("?? ")
                    or (_is_short_status_line(token.split(None, 1)[0]) and len(token.split(None, 1)) > 1)
                    or token in {"{", "}", "["}
                ):
                    rest_start = pos
                    break
                command_parts.append(token)
            else:
                rest_start = len(normalized)
            command: list[str] = []
            index = 0
            while index < len(command_parts):
                if (
                    command_parts[index] == "--"
                    and index + 1 < len(command_parts)
                    and _is_option_name(command_parts[index + 1])
                ):
                    command.append("--" + command_parts[index + 1])
                    index += 2
                    continue
                command.append(command_parts[index])
                index += 1
            if command:
                normalized = [normalized[0], " ".join(command), *normalized[rest_start:]]
        return normalized

    def collapse_split_bullets(text: str) -> str:
        lines = text.splitlines()
        out: list[str] = []
        index = 0
        while index < len(lines):
            stripped = lines[index].strip()
            if stripped != "-":
                out.append(lines[index])
                index += 1
                continue
            lookahead = index + 1
            while lookahead < len(lines) and not lines[lookahead].strip():
                lookahead += 1
            if lookahead >= len(lines):
                out.append(lines[index])
                index += 1
                continue
            item = lines[lookahead].strip()
            after = lookahead + 1
            while after < len(lines) and not lines[after].strip():
                after += 1
            if after < len(lines) and lines[after].strip().startswith(":"):
                out.append(f"- {item}{lines[after].strip()}")
                index = after + 1
                continue
            if "/" in item or "." in item:
                out.append(f"- {item}")
                index = lookahead + 1
                continue
            out.append(lines[index])
            index += 1
        return "\n".join(out)

    for in_fence, segment in _iter_fenced_segments(markdown):
        if in_fence:
            output.append(segment)
            global_line += segment.count("\n")
            continue

        segment = re.sub(r"(?m)^-\n+\s*([A-Z])\n\s*:\s*", r"- \1: ", segment)
        segment = re.sub(r"(?m)^(\d+)\.\n+\s*([^\n:]{2,80})\n\s*:\s*", r"\1. **\2**: ", segment)
        segment = re.sub(r"(?m)^##\s*\n+", "", segment)
        segment = collapse_split_bullets(segment)
        lines = segment.splitlines()
        repaired_lines: list[str] = []
        index = 0
        while index < len(lines):
            if looks_like_tool_block_start(lines, index):
                start = index
                block, index = collect_tool_block(lines, index)
                normalized = normalize_tool_block(block)
                if len(normalized) >= 3:
                    repaired_lines.append("```text")
                    repaired_lines.extend(normalized)
                    repaired_lines.append("```")
                    diagnostics.append(
                        {
                            "level": "info",
                            "kind": "codex_transcript_repair",
                            "line": global_line + start,
                            "end_line": global_line + index - 1,
                            "message": "Reflowed a high-confidence Codex tool transcript for display only.",
                        }
                    )
                else:
                    repaired_lines.extend(block)
                continue
            repaired_lines.append(lines[index])
            index += 1

        output.append("\n".join(repaired_lines))
        if segment.endswith("\n"):
            output.append("\n")
        global_line += segment.count("\n")

    return "".join(output), diagnostics


def _paragraph_blocks(text: str) -> list[str]:
    blocks: list[str] = []
    current: list[str] = []
    for line in text.strip().splitlines():
        if line.strip():
            current.append(line)
            continue
        if current:
            blocks.append("\n".join(current).strip())
            current = []
    if current:
        blocks.append("\n".join(current).strip())
    return blocks


def _norm_block(text: str) -> str:
    return _plain_text(text)


def _collapse_repeated_prefix_blocks(text: str, *, min_run: int = 5) -> str:
    blocks = _paragraph_blocks(text)
    if len(blocks) < min_run * 2:
        return text
    normalized = [_norm_block(block) for block in blocks]
    for start in range(1, len(blocks) - min_run + 1):
        matched = 0
        while (
            start + matched < len(blocks)
            and matched < start
            and normalized[matched] == normalized[start + matched]
        ):
            matched += 1
        if matched >= min_run:
            return "\n\n".join(blocks[:start]).rstrip() + "\n"
    return text


def _json_default(value: object) -> str:
    if isinstance(value, Path):
        return str(value)
    raise TypeError(f"{type(value).__name__} is not JSON serializable")


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _has_table(con: sqlite3.Connection, name: str) -> bool:
    row = con.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
        (name,),
    ).fetchone()
    return row is not None


def _thread_filter_sql(args: argparse.Namespace) -> tuple[str, tuple[object, ...], str]:
    if args.canonical_thread_id:
        return "LOWER(canonical_thread_id) = LOWER(?)", (args.canonical_thread_id,), "canonical_thread_id"
    if args.source_thread_id:
        return "LOWER(source_thread_id) = LOWER(?)", (args.source_thread_id,), "source_thread_id"
    if args.title:
        if args.title_exact:
            return "LOWER(title) = LOWER(?)", (args.title,), "title_exact"
        return "LOWER(title) LIKE LOWER(?)", (f"%{args.title}%",), "title_contains"
    if args.selector:
        selector = args.selector.strip()
        if re.fullmatch(r"[0-9a-fA-F]{40}", selector):
            return "LOWER(canonical_thread_id) = LOWER(?)", (selector,), "canonical_thread_id"
        if re.fullmatch(
            r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
            selector,
        ):
            return "LOWER(source_thread_id) = LOWER(?)", (selector,), "source_thread_id"
        return "LOWER(title) LIKE LOWER(?)", (f"%{selector}%",), "title_contains"
    raise SystemExit("provide --selector, --canonical-thread-id, --source-thread-id, or --title")


def _resolve_thread(con: sqlite3.Connection, args: argparse.Namespace) -> dict[str, Any]:
    where_sql, params, match_type = _thread_filter_sql(args)
    platform_sql = ""
    platform_params: tuple[object, ...] = ()
    if args.platform:
        platform_sql = "AND LOWER(platform) = LOWER(?)"
        platform_params = (args.platform,)

    rows = con.execute(
        f"""
        SELECT
            canonical_thread_id,
            source_thread_id,
            COALESCE(
                (
                    SELECT NULLIF(m2.title, '')
                    FROM messages m2
                    WHERE LOWER(m2.canonical_thread_id) = LOWER(messages.canonical_thread_id)
                      AND (m2.source_thread_id IS messages.source_thread_id OR LOWER(m2.source_thread_id) = LOWER(messages.source_thread_id))
                      AND LOWER(m2.platform) = LOWER(messages.platform)
                      AND LOWER(m2.account_id) = LOWER(messages.account_id)
                      AND NULLIF(m2.title, '') IS NOT NULL
                    ORDER BY m2.ts DESC, m2.rowid DESC
                    LIMIT 1
                ),
                '(no title)'
            ) AS title,
            platform,
            account_id,
            COUNT(*) AS message_count,
            MIN(ts) AS earliest_ts,
            MAX(ts) AS latest_ts
        FROM messages
        WHERE {where_sql}
          {platform_sql}
        GROUP BY canonical_thread_id, source_thread_id, platform, account_id
        ORDER BY latest_ts DESC, message_count DESC
        LIMIT ?
        """,
        params + platform_params + (args.resolve_limit,),
    ).fetchall()
    if not rows:
        raise SystemExit("no matching thread in archive DB")
    if len(rows) > 1 and not args.pick_first:
        candidates = [
            {
                "canonical_thread_id": row["canonical_thread_id"],
                "source_thread_id": row["source_thread_id"],
                "title": row["title"],
                "platform": row["platform"],
                "account_id": row["account_id"],
                "message_count": row["message_count"],
                "earliest_ts": _iso_utc(row["earliest_ts"]),
                "latest_ts": _iso_utc(row["latest_ts"]),
            }
            for row in rows
        ]
        raise SystemExit(
            "selector matched multiple threads; rerun with --pick-first or a stricter ID:\n"
            + json.dumps(candidates, indent=2)
        )
    row = rows[0]
    return {
        "match_type": match_type,
        "canonical_thread_id": row["canonical_thread_id"],
        "source_thread_id": row["source_thread_id"],
        "title": row["title"],
        "platform": row["platform"],
        "account_id": row["account_id"],
        "message_count": int(row["message_count"] or 0),
        "earliest_ts": _iso_utc(row["earliest_ts"]),
        "latest_ts": _iso_utc(row["latest_ts"]),
    }


def _load_messages(
    con: sqlite3.Connection,
    canonical_thread_id: str,
    *,
    clean_perplexity_duplicates: bool,
) -> list[dict[str, Any]]:
    rows = con.execute(
        """
        SELECT
            message_id,
            canonical_thread_id,
            platform,
            account_id,
            ts,
            role,
            text,
            title,
            source_id,
            source_thread_id,
            source_message_id,
            source_path,
            source_bucket,
            provenance_json,
            rowid AS archive_rowid
        FROM messages
        WHERE LOWER(canonical_thread_id) = LOWER(?)
        ORDER BY ts ASC, rowid ASC
        """,
        (canonical_thread_id,),
    ).fetchall()
    messages: list[dict[str, Any]] = []
    for index, row in enumerate(rows, start=1):
        provenance: Any = None
        if row["provenance_json"]:
            try:
                provenance = json.loads(row["provenance_json"])
            except json.JSONDecodeError:
                provenance = row["provenance_json"]
        text = row["text"] or ""
        if clean_perplexity_duplicates and str(row["platform"]).lower() == "perplexity":
            text = _collapse_repeated_prefix_blocks(text)
        messages.append(
            {
                "index": index,
                "message_id": row["message_id"],
                "canonical_thread_id": row["canonical_thread_id"],
                "platform": row["platform"],
                "account_id": row["account_id"],
                "ts": row["ts"],
                "ts_utc": _iso_utc(row["ts"]),
                "role": row["role"],
                "text": text,
                "title": row["title"],
                "source_id": row["source_id"],
                "source_thread_id": row["source_thread_id"],
                "source_message_id": row["source_message_id"],
                "source_path": row["source_path"],
                "source_bucket": row["source_bucket"],
                "provenance": provenance,
                "archive_rowid": row["archive_rowid"],
            }
        )
    return messages


def _load_blocks(con: sqlite3.Connection, message_ids: list[str]) -> dict[str, list[dict[str, Any]]]:
    if not message_ids or not _has_table(con, "message_blocks"):
        return {}
    blocks: dict[str, list[dict[str, Any]]] = {message_id: [] for message_id in message_ids}
    for start in range(0, len(message_ids), 500):
        batch = message_ids[start : start + 500]
        placeholders = ",".join("?" for _ in batch)
        rows = con.execute(
            f"""
            SELECT
                message_id,
                block_index,
                block_type,
                text_value,
                ref_path,
                actor,
                emoji,
                target,
                metadata_json
            FROM message_blocks
            WHERE message_id IN ({placeholders})
            ORDER BY message_id, block_index
            """,
            tuple(batch),
        ).fetchall()
        for row in rows:
            metadata: Any = None
            if row["metadata_json"]:
                try:
                    metadata = json.loads(row["metadata_json"])
                except json.JSONDecodeError:
                    metadata = row["metadata_json"]
            blocks.setdefault(row["message_id"], []).append(
                {
                    "block_index": row["block_index"],
                    "block_type": row["block_type"],
                    "text_value": row["text_value"],
                    "ref_path": row["ref_path"],
                    "actor": row["actor"],
                    "emoji": row["emoji"],
                    "target": row["target"],
                    "metadata": metadata,
                }
            )
    return blocks


def build_payload(db_path: Path, args: argparse.Namespace) -> dict[str, Any]:
    con = _connect_ro(db_path)
    try:
        if not _has_table(con, "messages"):
            raise SystemExit("archive DB has no messages table")
        thread = _resolve_thread(con, args)
        messages = _load_messages(
            con,
            thread["canonical_thread_id"],
            clean_perplexity_duplicates=not args.no_clean_perplexity_duplicates,
        )
        if args.include_blocks:
            blocks = _load_blocks(con, [item["message_id"] for item in messages])
            for item in messages:
                item["blocks"] = blocks.get(item["message_id"], [])
    finally:
        con.close()

    return {
        "schema": "itir.chat_archive.thread_export.v1",
        "generated_at": _utc_now(),
        "source_db": str(db_path.expanduser().resolve()),
        "thread": thread,
        "messages": messages,
    }


def _message_export_weight(message: dict[str, Any]) -> int:
    text = str(message.get("text") or "")
    # Markdown/HTML wrappers, comments, and static KaTeX expansion add overhead.
    return len(text.encode("utf-8")) + 600


def plan_message_chunks(
    messages: list[dict[str, Any]],
    *,
    max_messages: int,
    target_bytes: int,
) -> list[dict[str, Any]]:
    if max_messages <= 0:
        raise ValueError("max_messages must be positive")
    if target_bytes <= 0:
        raise ValueError("target_bytes must be positive")

    chunks: list[dict[str, Any]] = []
    start = 0
    count = 0
    weight = 0
    for offset, message in enumerate(messages):
        item_weight = _message_export_weight(message)
        if count and (count >= max_messages or weight + item_weight > target_bytes):
            chunks.append(
                {
                    "chunk_index": len(chunks) + 1,
                    "start_message_index": int(messages[start]["index"]),
                    "end_message_index": int(messages[offset - 1]["index"]),
                    "message_count": count,
                    "estimated_bytes": weight,
                }
            )
            start = offset
            count = 0
            weight = 0
        count += 1
        weight += item_weight
    if count:
        chunks.append(
            {
                "chunk_index": len(chunks) + 1,
                "start_message_index": int(messages[start]["index"]),
                "end_message_index": int(messages[-1]["index"]),
                "message_count": count,
                "estimated_bytes": weight,
            }
        )
    return chunks


def _chunk_payload(payload: dict[str, Any], plan_item: dict[str, Any]) -> dict[str, Any]:
    start = int(plan_item["start_message_index"])
    end = int(plan_item["end_message_index"])
    messages = [message for message in payload["messages"] if start <= int(message["index"]) <= end]
    thread = dict(payload["thread"])
    thread["chunk"] = plan_item
    return {
        "schema": payload["schema"],
        "generated_at": payload["generated_at"],
        "source_db": payload["source_db"],
        "thread": thread,
        "messages": messages,
    }


def _frontmatter(payload: dict[str, Any]) -> str:
    thread = payload["thread"]
    fields = {
        "schema": payload["schema"],
        "generated_at": payload["generated_at"],
        "source_db": payload["source_db"],
        "canonical_thread_id": thread.get("canonical_thread_id"),
        "source_thread_id": thread.get("source_thread_id"),
        "platform": thread.get("platform"),
        "account_id": thread.get("account_id"),
        "title": thread.get("title"),
        "message_count": len(payload["messages"]),
        "earliest_ts": thread.get("earliest_ts"),
        "latest_ts": thread.get("latest_ts"),
    }
    lines = ["---"]
    for key, value in fields.items():
        escaped = json.dumps(value, ensure_ascii=False)
        lines.append(f"{key}: {escaped}")
    lines.append("---")
    return "\n".join(lines)


def render_markdown_transcript(payload: dict[str, Any]) -> str:
    title = str(payload["thread"].get("title") or "(no title)")
    out = [_frontmatter(payload), "", f"# {title}", ""]
    for message in payload["messages"]:
        role = str(message.get("role") or "unknown").strip() or "unknown"
        role_title = role[:1].upper() + role[1:]
        ts = message.get("ts_utc") or message.get("ts") or ""
        out.extend(
            [
                f"## {message['index']}. {role_title}",
                "",
                f"<!-- message_id={message.get('message_id')} source_message_id={message.get('source_message_id')} ts={ts} -->",
                "",
            ]
        )
        text = str(message.get("text") or "").rstrip()
        out.append(text)
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def render_markdown_perplexity_doc(payload: dict[str, Any], *, include_logo: bool = False) -> str:
    thread = payload["thread"]
    title = str(thread.get("title") or "(no title)")
    out: list[str] = []
    if include_logo:
        out.extend(
            [
                '<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>',
                "",
            ]
        )
    out.extend(
        [
            f"<!-- schema={payload['schema']} generated_at={payload['generated_at']} source_db={payload['source_db']} -->",
            f"<!-- canonical_thread_id={thread.get('canonical_thread_id')} source_thread_id={thread.get('source_thread_id')} platform={thread.get('platform')} -->",
            "",
        ]
    )

    wrote_section = False
    pending_assistant_heading = title
    for message in payload["messages"]:
        role = str(message.get("role") or "unknown").lower()
        text = str(message.get("text") or "").rstrip()
        if role == "user":
            if wrote_section:
                out.extend(["", "---", ""])
            heading, prompt_body = _split_prompt_heading(text, title)
            out.extend(
                [
                    f"# {heading}",
                    "",
                    f"<!-- message_id={message.get('message_id')} source_message_id={message.get('source_message_id')} ts={message.get('ts_utc') or message.get('ts') or ''} role=user -->",
                    "",
                ]
            )
            if prompt_body:
                out.extend([prompt_body, ""])
            wrote_section = True
            pending_assistant_heading = heading
            continue

        if not wrote_section:
            out.extend([f"# {pending_assistant_heading}", ""])
            wrote_section = True
        out.extend(
            [
                f"<!-- message_id={message.get('message_id')} source_message_id={message.get('source_message_id')} ts={message.get('ts_utc') or message.get('ts') or ''} role={role} -->",
                "",
            ]
        )
        if role not in {"assistant", "bot"}:
            out.extend([f"**{role[:1].upper() + role[1:]}**", ""])
        out.extend([text, ""])

    if not payload["messages"]:
        out.extend([f"# {title}", ""])
    return "\n".join(out).rstrip() + "\n"


def render_markdown(payload: dict[str, Any], *, style: str, include_logo: bool = False) -> str:
    if style == "transcript":
        return render_markdown_transcript(payload)
    return render_markdown_perplexity_doc(payload, include_logo=include_logo)


def render_html(payload: dict[str, Any]) -> str:
    thread = payload["thread"]
    title = str(thread.get("title") or "(no title)")
    metadata = {
        "canonical_thread_id": thread.get("canonical_thread_id"),
        "source_thread_id": thread.get("source_thread_id"),
        "platform": thread.get("platform"),
        "account_id": thread.get("account_id"),
        "message_count": len(payload["messages"]),
        "earliest_ts": thread.get("earliest_ts"),
        "latest_ts": thread.get("latest_ts"),
        "source_db": payload.get("source_db"),
        "generated_at": payload.get("generated_at"),
    }
    meta_rows = "\n".join(
        f"<tr><th>{html.escape(str(key))}</th><td>{html.escape(str(value or ''))}</td></tr>"
        for key, value in metadata.items()
    )
    message_html: list[str] = []
    for message in payload["messages"]:
        role = str(message.get("role") or "unknown").strip() or "unknown"
        ts = str(message.get("ts_utc") or message.get("ts") or "")
        text = html.escape(str(message.get("text") or "")).replace("\n", "<br>\n")
        message_html.append(
            "\n".join(
                [
                    '<article class="message">',
                    "  <header>",
                    f'    <h2>{message["index"]}. {html.escape(role[:1].upper() + role[1:])}</h2>',
                    f'    <p>{html.escape(ts)} · message_id={html.escape(str(message.get("message_id") or ""))}</p>',
                    "  </header>",
                    f'  <div class="body">{text}</div>',
                    "</article>",
                ]
            )
        )
    return (
        "<!doctype html>\n"
        '<html lang="en">\n'
        "<head>\n"
        '  <meta charset="utf-8">\n'
        f"  <title>{html.escape(title)}</title>\n"
        "  <style>\n"
        "    :root { color-scheme: light; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }\n"
        "    body { margin: 0; color: #172026; background: #f6f7f8; }\n"
        "    main { max-width: 980px; margin: 0 auto; padding: 36px 24px 64px; }\n"
        "    h1 { font-size: 30px; line-height: 1.2; margin: 0 0 20px; }\n"
        "    table { width: 100%; border-collapse: collapse; margin: 0 0 28px; font-size: 13px; background: #fff; }\n"
        "    th, td { text-align: left; vertical-align: top; border: 1px solid #d7dde2; padding: 8px 10px; }\n"
        "    th { width: 210px; color: #4b5863; background: #eef1f3; font-weight: 600; }\n"
        "    .message { break-inside: avoid; background: #fff; border: 1px solid #d7dde2; margin: 0 0 14px; padding: 16px 18px; }\n"
        "    .message h2 { font-size: 16px; margin: 0; }\n"
        "    .message header p { color: #66727d; font-size: 12px; margin: 5px 0 14px; }\n"
        "    .body { font-size: 14px; line-height: 1.55; white-space: normal; overflow-wrap: anywhere; }\n"
        "    @media print { body { background: #fff; } main { max-width: none; padding: 0; } .message { border-color: #bbb; } }\n"
        "  </style>\n"
        "</head>\n"
        "<body>\n"
        "  <main>\n"
        f"    <h1>{html.escape(title)}</h1>\n"
        f"    <table>{meta_rows}</table>\n"
        f"    {''.join(message_html)}\n"
        "  </main>\n"
        "</body>\n"
        "</html>\n"
    )


def _markdown_to_html(markdown: str) -> str:
    try:
        from markdown_it import MarkdownIt  # type: ignore[import-not-found]
    except ImportError:
        pass
    else:
        return MarkdownIt("commonmark", {"html": True}).enable("table").render(markdown)
    try:
        import markdown as markdown_lib  # type: ignore[import-not-found]
    except ImportError:
        escaped = html.escape(markdown).replace("\n", "<br>\n")
        return f"<p>{escaped}</p>"
    return markdown_lib.markdown(
        markdown,
        extensions=["extra", "tables", "fenced_code", "sane_lists"],
        output_format="html5",
    )


def _find_katex_dist(explicit: str | None = None) -> Path | None:
    candidates: list[Path] = []
    if explicit:
        candidates.append(Path(explicit).expanduser())
    candidates.extend(
        [
            Path("/home/c/.bun/install/cache/katex@0.16.27@@@1/dist"),
            Path("/home/c/.bun/install/cache/katex@0.16.22@@@1/dist"),
        ]
    )
    for candidate in candidates:
        if (
            (candidate / "katex.min.css").exists()
            and (candidate / "katex.min.js").exists()
            and (candidate / "contrib" / "auto-render.min.js").exists()
        ):
            return candidate
    return None


def _render_katex_batch(expressions: list[dict[str, Any]], katex: Path, *, timeout_seconds: int) -> list[str] | None:
    if not expressions:
        return []
    node = shutil.which("node")
    if not node:
        return None
    script = """
const katex = require(process.argv[1]);
let input = "";
process.stdin.setEncoding("utf8");
process.stdin.on("data", chunk => input += chunk);
process.stdin.on("end", () => {
  const expressions = JSON.parse(input);
  const rendered = expressions.map((item) => {
    try {
      return katex.renderToString(item.tex, {
        displayMode: !!item.display,
        throwOnError: false,
        strict: "warn"
      });
    } catch (err) {
      const escaped = String(item.tex)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
      return `<span class="katex-error">${escaped}</span>`;
    }
  });
  process.stdout.write(JSON.stringify(rendered));
});
"""
    try:
        completed = subprocess.run(
            [node, "-e", script, str(katex / "katex.min.js")],
            input=json.dumps(expressions),
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired:
        return None
    if completed.returncode != 0:
        return None
    try:
        data = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return None
    if not isinstance(data, list) or not all(isinstance(item, str) for item in data):
        return None
    return data


def _prerender_math_static(markdown: str, katex: Path | None, *, timeout_seconds: int) -> tuple[str, bool]:
    if katex is None:
        return markdown, False

    expressions: list[dict[str, Any]] = []
    placeholders: list[str] = []

    def add_expression(tex: str, display: bool) -> str:
        token = f"@@ITIR_KATEX_{len(expressions)}@@"
        expressions.append({"tex": tex.strip(), "display": display})
        placeholders.append(token)
        return token

    transformed_segments: list[str] = []
    for in_fence, segment in _iter_fenced_segments(markdown):
        if in_fence:
            transformed_segments.append(segment)
            continue
        segment = re.sub(
            r"(?<!\\)\$\$(.+?)(?<!\\)\$\$",
            lambda m: "\n\n" + add_expression(m.group(1), True) + "\n\n",
            segment,
            flags=re.S,
        )
        segment = re.sub(
            r"(?<!\\)\$(?!\s)(.+?)(?<!\\)\$",
            lambda m: add_expression(m.group(1), False),
            segment,
            flags=re.S,
        )
        transformed_segments.append(segment)

    if not expressions:
        return markdown, True
    rendered = _render_katex_batch(expressions, katex, timeout_seconds=timeout_seconds)
    if rendered is None:
        return markdown, False
    transformed = "".join(transformed_segments)
    for token, rendered_html in zip(placeholders, rendered, strict=True):
        transformed = transformed.replace(token, rendered_html)
    return transformed, True


def render_html_document(
    payload: dict[str, Any],
    *,
    markdown_style: str,
    include_logo: bool = False,
    katex_dir: str | None = None,
    compact_links: bool = True,
    whitespace_repair: str = "conservative",
    math_render: str = "static",
    math_timeout_seconds: int = 30,
) -> str:
    thread = payload["thread"]
    title = str(thread.get("title") or "(no title)")
    markdown = render_markdown(payload, style=markdown_style, include_logo=include_logo)
    diagnostics = _diagnose_markdown(markdown)
    display_markdown = _normalize_math_delimiters(markdown)
    display_markdown, repair_diagnostics = _repair_fragmented_listing_markdown(
        display_markdown,
        policy=whitespace_repair,
    )
    diagnostics.extend(repair_diagnostics)
    display_markdown, transcript_diagnostics = _repair_codex_transcript_markdown(display_markdown)
    diagnostics.extend(transcript_diagnostics)
    if compact_links:
        display_markdown = _compact_display_links(display_markdown)
    katex = _find_katex_dist(katex_dir)
    static_math = False
    if math_render in {"static", "auto"}:
        display_markdown, static_math = _prerender_math_static(
            display_markdown,
            katex,
            timeout_seconds=math_timeout_seconds,
        )
    body = _markdown_to_html(display_markdown)
    body = re.sub(
        r"</code></pre>\s*<p>([^<]*[\ue000-\uf8ff\U000f0000-\U000ffffd][^<]*)</p>\s*<pre><code class=\"language-text\">",
        r"\n\1\n",
        body,
    )
    katex_assets = ""
    render_script = ""
    use_browser_math = katex and math_render in {"browser", "auto"} and not static_math
    if katex:
        katex_uri = katex.resolve().as_uri()
        katex_assets = f'  <link rel="stylesheet" href="{katex_uri}/katex.min.css">\n'
        if use_browser_math:
            katex_assets += (
                f'  <script defer src="{katex_uri}/katex.min.js"></script>\n'
                f'  <script defer src="{katex_uri}/contrib/auto-render.min.js"></script>\n'
            )
    if use_browser_math:
        render_script = """
  <script>
    document.addEventListener("DOMContentLoaded", function () {
      renderMathInElement(document.body, {
        delimiters: [
          {left: "$$", right: "$$", display: true},
          {left: "$", right: "$", display: false}
        ],
        throwOnError: false,
        strict: "warn"
      });
    });
  </script>
"""
    diagnostics_html = ""
    if diagnostics:
        items = "\n".join(
            f"<li><strong>{html.escape(item['kind'])}</strong>: {html.escape(item['message'])}</li>"
            for item in diagnostics
        )
        diagnostics_html = f"<aside class=\"diagnostics\"><h2>Export diagnostics</h2><ul>{items}</ul></aside>"
    return (
        "<!doctype html>\n"
        '<html lang="en">\n'
        "<head>\n"
        '  <meta charset="utf-8">\n'
        f"  <title>{html.escape(title)}</title>\n"
        f"{katex_assets}"
        "  <style>\n"
        "    :root { color-scheme: light; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }\n"
        "    body { margin: 0; color: #172026; background: #fff; }\n"
        "    main { max-width: 920px; margin: 0 auto; padding: 36px 30px 72px; }\n"
        "    h1 { font-size: 26px; line-height: 1.22; margin: 34px 0 16px; page-break-after: avoid; }\n"
        "    h1:first-child { margin-top: 0; }\n"
        "    h2 { font-size: 20px; line-height: 1.3; margin: 28px 0 12px; page-break-after: avoid; }\n"
        "    h3 { font-size: 16px; line-height: 1.35; margin: 22px 0 10px; page-break-after: avoid; }\n"
        "    p, li, td, th { font-size: 14px; line-height: 1.55; }\n"
        "    p { margin: 0 0 13px; }\n"
        "    a { color: #155e75; overflow-wrap: anywhere; }\n"
        "    table { width: 100%; border-collapse: collapse; margin: 16px 0 22px; }\n"
        "    th, td { text-align: left; vertical-align: top; border: 1px solid #cfd8df; padding: 6px 8px; }\n"
        "    th { background: #eef3f5; }\n"
        "    pre { white-space: pre-wrap; overflow-wrap: anywhere; border: 1px solid #d8dee4; background: #f6f8fa; padding: 10px 12px; font-size: 12px; line-height: 1.45; }\n"
        "    code { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 0.92em; }\n"
        "    blockquote { border-left: 3px solid #c7d0d7; color: #34404a; margin: 16px 0; padding-left: 14px; }\n"
        "    hr { border: 0; border-top: 1px solid #ccd5db; margin: 30px 0; }\n"
        "    .diagnostics { border: 1px solid #f0c36d; background: #fff8e1; padding: 12px 14px; margin: 0 0 24px; }\n"
        "    .diagnostics h2 { font-size: 15px; margin: 0 0 8px; }\n"
        "    .katex-error { color: #b42318; background: #fff1f0; padding: 0 2px; }\n"
        "    @page { margin: 16mm 15mm; }\n"
        "    @media print { main { max-width: none; padding: 0; } a { color: #111; text-decoration-color: #888; } }\n"
        "  </style>\n"
        f"{render_script}"
        "</head>\n"
        "<body>\n"
        "  <main>\n"
        f"{diagnostics_html}\n"
        f"{body}\n"
        "  </main>\n"
        "</body>\n"
        "</html>\n"
    )


def _write_manifest(
    out_dir: Path,
    files: list[Path],
    payload: dict[str, Any],
    *,
    display_policy: dict[str, Any] | None = None,
) -> Path:
    manifest = {
        "schema": "itir.chat_archive.thread_export_manifest.v1",
        "generated_at": payload["generated_at"],
        "source_db": payload["source_db"],
        "thread": payload["thread"],
        "files": [
            {
                "path": path.name,
                "bytes": path.stat().st_size,
                "sha256": _sha256(path),
            }
            for path in files
        ],
    }
    if display_policy is not None:
        manifest["html_pdf_display_policy"] = display_policy
    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return manifest_path


def _write_manifest_with_chunks(
    out_dir: Path,
    files: list[Path],
    payload: dict[str, Any],
    chunk_plan: list[dict[str, Any]] | None,
    *,
    display_policy: dict[str, Any] | None = None,
) -> Path:
    manifest_path = _write_manifest(out_dir, files, payload, display_policy=display_policy)
    if not chunk_plan:
        return manifest_path
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["chunk_plan"] = chunk_plan
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return manifest_path


def _render_pdf_with_chrome(html_path: Path, pdf_path: Path, *, timeout_seconds: int) -> dict[str, Any]:
    chrome = shutil.which("google-chrome-stable") or shutil.which("chromium") or shutil.which("chromium-browser")
    if not chrome:
        return {"ok": False, "error": "chrome_not_found"}
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        chrome,
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--allow-file-access-from-files",
        "--virtual-time-budget=5000",
        f"--print-to-pdf={pdf_path}",
        html_path.resolve().as_uri(),
    ]
    try:
        completed = subprocess.run(
            cmd,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "ok": False,
            "error": "chrome_timeout",
            "timeout_seconds": timeout_seconds,
            "command": cmd,
            "stderr_tail": "\n".join((exc.stderr or "").splitlines()[-12:]) if isinstance(exc.stderr, str) else "",
        }
    return {
        "ok": completed.returncode == 0 and pdf_path.exists(),
        "returncode": completed.returncode,
        "command": cmd,
        "stderr_tail": "\n".join(completed.stderr.splitlines()[-12:]),
    }


def _render_pdf_with_weasyprint(html_path: Path, pdf_path: Path) -> dict[str, Any]:
    try:
        from weasyprint import HTML  # type: ignore[import-not-found]
    except ImportError:
        return {"ok": False, "error": "weasyprint_not_installed"}
    try:
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        HTML(filename=str(html_path)).write_pdf(str(pdf_path))
    except Exception as exc:  # pragma: no cover - depends on optional native renderer.
        return {"ok": False, "error": "weasyprint_failed", "detail": str(exc)}
    return {"ok": pdf_path.exists()}


def _render_pdf(html_path: Path, pdf_path: Path, *, engine: str, timeout_seconds: int) -> dict[str, Any]:
    engines = ["weasyprint", "chrome"] if engine == "auto" else [engine]
    failures: list[dict[str, Any]] = []
    for candidate in engines:
        if candidate == "weasyprint":
            result = _render_pdf_with_weasyprint(html_path, pdf_path)
        elif candidate == "chrome":
            result = _render_pdf_with_chrome(html_path, pdf_path, timeout_seconds=timeout_seconds)
        else:
            result = {"ok": False, "error": f"unknown_pdf_engine:{candidate}"}
        if result.get("ok"):
            result["engine"] = candidate
            return result
        result["engine"] = candidate
        failures.append(result)
    return {"ok": False, "error": "pdf_render_failed", "failures": failures}


def _render_pdf_jobs(
    jobs: list[tuple[Path, Path]],
    *,
    engine: str,
    timeout_seconds: int,
    workers: int,
) -> tuple[list[Path], list[dict[str, Any]]]:
    if not jobs:
        return [], []
    written: list[Path] = []
    failures: list[dict[str, Any]] = []
    max_workers = max(1, min(workers, len(jobs)))
    print(
        f"pdf: rendering {len(jobs)} chunk(s) with {max_workers} worker(s), engine={engine}, timeout={timeout_seconds}s",
        file=sys.stderr,
    )
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
        future_map = {
            pool.submit(_render_pdf, html_path, pdf_path, engine=engine, timeout_seconds=timeout_seconds): (
                html_path,
                pdf_path,
            )
            for html_path, pdf_path in jobs
        }
        for future in concurrent.futures.as_completed(future_map):
            html_path, pdf_path = future_map[future]
            result = future.result()
            if result.get("ok"):
                written.append(pdf_path)
                print(f"pdf: done {len(written) + len(failures)}/{len(jobs)} {pdf_path.name}", file=sys.stderr)
            else:
                failures.append(
                    {
                        "html": str(html_path),
                        "pdf": str(pdf_path),
                        "result": result,
                    }
                )
                print(f"pdf: failed {len(written) + len(failures)}/{len(jobs)} {pdf_path.name}", file=sys.stderr)
    return sorted(written), failures


def write_export(
    payload: dict[str, Any],
    out: Path,
    formats: set[str],
    bundle: bool,
    *,
    markdown_style: str,
    html_style: str,
    include_logo: bool,
    katex_dir: str | None,
    compact_links: bool,
    whitespace_repair: str,
    render_pdf: bool,
    pdf_engine: str,
    pdf_timeout_seconds: int,
    pdf_workers: int,
    math_render: str,
    math_timeout_seconds: int,
    chunk_messages: int | None,
    chunk_target_bytes: int,
) -> dict[str, Any]:
    thread = payload["thread"]
    base = _slug(str(thread.get("title") or ""), str(thread["canonical_thread_id"])[:12])
    if bundle:
        out.mkdir(parents=True, exist_ok=True)
        stem = base
    else:
        out.parent.mkdir(parents=True, exist_ok=True)
        stem = out.stem

    written: list[Path] = []
    chunk_plan: list[dict[str, Any]] | None = None
    pdf_failures: list[dict[str, Any]] = []
    target_dir = out if bundle else out.parent
    if "json" in formats:
        json_path = target_dir / f"{stem}.json"
        json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=_json_default) + "\n", encoding="utf-8")
        written.append(json_path)
    if "markdown" in formats:
        md_path = target_dir / f"{stem}.md"
        md_path.write_text(
            render_markdown(payload, style=markdown_style, include_logo=include_logo),
            encoding="utf-8",
        )
        written.append(md_path)
    if "html" in formats and not chunk_messages:
        html_path = target_dir / f"{stem}.html"
        if html_style == "transcript":
            rendered = render_html(payload)
        else:
            rendered = render_html_document(
                payload,
                markdown_style=markdown_style,
                include_logo=include_logo,
                katex_dir=katex_dir,
                compact_links=compact_links,
                whitespace_repair=whitespace_repair,
                math_render=math_render,
                math_timeout_seconds=math_timeout_seconds,
            )
        html_path.write_text(rendered, encoding="utf-8")
        written.append(html_path)
        if render_pdf:
            pdf_path = target_dir / f"{stem}.pdf"
            pdf_result = _render_pdf(
                html_path,
                pdf_path,
                engine=pdf_engine,
                timeout_seconds=pdf_timeout_seconds,
            )
            if pdf_result.get("ok"):
                written.append(pdf_path)
            else:
                pdf_failures.append({"html": str(html_path), "pdf": str(pdf_path), "result": pdf_result})
                print(f"warning: PDF render failed: {json.dumps(pdf_result, ensure_ascii=False)}", file=sys.stderr)
    elif "html" in formats and chunk_messages:
        chunk_plan = plan_message_chunks(
            payload["messages"],
            max_messages=chunk_messages,
            target_bytes=chunk_target_bytes,
        )
        print(
            f"html: writing {len(chunk_plan)} chunk(s), max_messages={chunk_messages}, target_bytes={chunk_target_bytes}",
            file=sys.stderr,
        )
        pdf_jobs: list[tuple[Path, Path]] = []
        for plan_item in chunk_plan:
            chunk_payload = _chunk_payload(payload, plan_item)
            chunk_index = int(plan_item["chunk_index"])
            chunk_stem = f"{stem}.part-{chunk_index:03d}"
            html_path = target_dir / f"{chunk_stem}.html"
            print(
                "html: chunk "
                f"{chunk_index}/{len(chunk_plan)} messages={plan_item['message_count']} "
                f"bytes~={plan_item['estimated_bytes']}",
                file=sys.stderr,
            )
            if html_style == "transcript":
                rendered = render_html(chunk_payload)
            else:
                rendered = render_html_document(
                    chunk_payload,
                    markdown_style=markdown_style,
                    include_logo=include_logo,
                    katex_dir=katex_dir,
                    compact_links=compact_links,
                    whitespace_repair=whitespace_repair,
                    math_render=math_render,
                    math_timeout_seconds=math_timeout_seconds,
                )
            html_path.write_text(rendered, encoding="utf-8")
            written.append(html_path)
            if render_pdf:
                pdf_jobs.append((html_path, target_dir / f"{chunk_stem}.pdf"))
        pdf_written, pdf_failures = _render_pdf_jobs(
            pdf_jobs,
            engine=pdf_engine,
            timeout_seconds=pdf_timeout_seconds,
            workers=pdf_workers,
        )
        written.extend(pdf_written)
        for failure in pdf_failures:
            print(f"warning: PDF render failed: {json.dumps(failure, ensure_ascii=False)}", file=sys.stderr)
    display_policy = {
        "compact_display_links": compact_links,
        "whitespace_repair": whitespace_repair,
        "whitespace_repair_scope": "HTML/PDF display only; canonical JSON and Markdown exports are unchanged.",
    }
    manifest_path = (
        _write_manifest_with_chunks(target_dir, written, payload, chunk_plan, display_policy=display_policy)
        if bundle
        else None
    )
    return {
        "ok": True,
        "thread": thread,
        "message_count": len(payload["messages"]),
        "written": [str(path) for path in written],
        "manifest": str(manifest_path) if manifest_path else None,
        "chunk_plan": chunk_plan,
        "pdf_failures": pdf_failures,
        "html_pdf_display_policy": display_policy,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export a canonical chat archive thread to deterministic Markdown/JSON."
    )
    parser.add_argument("--db", default="/home/c/chat_archive.sqlite", help="Canonical chat archive SQLite DB.")
    parser.add_argument("--selector", help="Canonical thread ID, source/online thread UUID, or title substring.")
    parser.add_argument("--canonical-thread-id")
    parser.add_argument("--source-thread-id")
    parser.add_argument("--title")
    parser.add_argument("--title-exact", action="store_true")
    parser.add_argument("--platform", help="Optional platform filter, e.g. perplexity.")
    parser.add_argument("--resolve-limit", type=int, default=8)
    parser.add_argument("--pick-first", action="store_true", help="Use latest match when a title selector is ambiguous.")
    parser.add_argument("--include-blocks", action="store_true", help="Include message_blocks in JSON output when present.")
    parser.add_argument("--format", choices=["markdown", "json", "html", "both", "all"], default="both")
    parser.add_argument(
        "--markdown-style",
        choices=["perplexity-doc", "transcript"],
        default="perplexity-doc",
        help="Markdown layout: Perplexity-like document turns or explicit role transcript.",
    )
    parser.add_argument(
        "--include-logo",
        action="store_true",
        help="Include the Perplexity logo image tag in Markdown output.",
    )
    parser.add_argument(
        "--html-style",
        choices=["document", "transcript"],
        default="document",
        help="HTML layout: rendered Markdown document with local KaTeX when available, or escaped transcript.",
    )
    parser.add_argument(
        "--katex-dir",
        help="Optional local KaTeX dist directory containing katex.min.css/js and contrib/auto-render.min.js.",
    )
    parser.add_argument(
        "--no-compact-display-links",
        action="store_true",
        help="Do not shorten long visible URL labels in rendered HTML/PDF. Link targets are never changed.",
    )
    parser.add_argument(
        "--whitespace-repair",
        choices=["off", "conservative", "aggressive"],
        default="conservative",
        help=(
            "Display-only repair for high-confidence fragmented terminal/file listings in rendered HTML/PDF. "
            "Canonical JSON and Markdown exports are unchanged."
        ),
    )
    parser.add_argument(
        "--pdf",
        action="store_true",
        help="Also render the HTML export to PDF with the selected local PDF engine.",
    )
    parser.add_argument(
        "--pdf-engine",
        choices=["auto", "weasyprint", "chrome"],
        default="auto",
        help="PDF engine. auto tries WeasyPrint first, then Chrome/Chromium.",
    )
    parser.add_argument(
        "--pdf-timeout-seconds",
        type=int,
        default=180,
        help="Maximum time to wait for Chrome PDF rendering before keeping HTML/JSON/Markdown only.",
    )
    parser.add_argument(
        "--pdf-workers",
        type=int,
        default=2,
        help="Maximum parallel PDF render jobs for chunked exports.",
    )
    parser.add_argument(
        "--chunk-messages",
        type=int,
        help="Split HTML/PDF exports into chunks with at most this many messages per chunk.",
    )
    parser.add_argument(
        "--chunk-target-bytes",
        type=int,
        default=1_200_000,
        help="Estimated per-chunk source byte budget used with --chunk-messages.",
    )
    parser.add_argument(
        "--chunk-plan-only",
        action="store_true",
        help="Resolve the thread and print the chunk plan JSON without writing export files.",
    )
    parser.add_argument(
        "--math-render",
        choices=["auto", "static", "browser", "none"],
        default="auto",
        help="Math rendering mode for document HTML/PDF. auto pre-renders static KaTeX when possible, then falls back to browser rendering.",
    )
    parser.add_argument(
        "--math-timeout-seconds",
        type=int,
        default=30,
        help="Maximum time to wait for static KaTeX pre-rendering.",
    )
    parser.add_argument(
        "--no-clean-perplexity-duplicates",
        action="store_true",
        help="Disable cleanup for repeated Perplexity DOM/export text blocks.",
    )
    parser.add_argument("--out", required=True, help="Output file base path or bundle directory.")
    parser.add_argument("--bundle", action="store_true", help="Treat --out as a directory and write manifest.json.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable summary to stdout.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    db_path = Path(args.db).expanduser()
    if not db_path.exists():
        raise SystemExit(f"archive DB not found: {db_path}")
    if args.format == "both":
        formats = {"markdown", "json"}
    elif args.format == "all":
        formats = {"markdown", "json", "html"}
    else:
        formats = {args.format}
    if args.pdf:
        formats.add("html")
    payload = build_payload(db_path, args)
    if args.chunk_plan_only:
        plan = plan_message_chunks(
            payload["messages"],
            max_messages=args.chunk_messages or 80,
            target_bytes=args.chunk_target_bytes,
        )
        print(
            json.dumps(
                {
                    "ok": True,
                    "thread": payload["thread"],
                    "message_count": len(payload["messages"]),
                    "chunk_plan": plan,
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return 0
    summary = write_export(
        payload,
        Path(args.out).expanduser(),
        formats,
        args.bundle,
        markdown_style=args.markdown_style,
        html_style=args.html_style,
        include_logo=args.include_logo,
        katex_dir=args.katex_dir,
        compact_links=not args.no_compact_display_links,
        whitespace_repair=args.whitespace_repair,
        render_pdf=args.pdf,
        pdf_engine=args.pdf_engine,
        pdf_timeout_seconds=args.pdf_timeout_seconds,
        pdf_workers=args.pdf_workers,
        math_render=args.math_render,
        math_timeout_seconds=args.math_timeout_seconds,
        chunk_messages=args.chunk_messages,
        chunk_target_bytes=args.chunk_target_bytes,
    )
    if args.json:
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    else:
        for path in summary["written"]:
            print(path)
        if summary["manifest"]:
            print(summary["manifest"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
