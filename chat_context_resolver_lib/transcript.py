from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Optional


def truncate_text(text: str, max_chars: int) -> str:
    if max_chars <= 0 or len(text) <= max_chars:
        return text
    omitted = len(text) - max_chars
    return f"{text[:max_chars]}\n...[truncated {omitted} chars]"


def latest_turn_datetime(
    turns: list[dict],
    *,
    parse_message_ts,
) -> Optional[dt.datetime]:
    latest: Optional[dt.datetime] = None
    for turn in turns:
        parsed = parse_message_ts(turn.get("ts_utc") or turn.get("ts"))
        if parsed is None:
            continue
        if latest is None or parsed > latest:
            latest = parsed
    return latest


@dataclass
class TranscriptLine:
    thread_line: int
    message_index: int
    message_id: str
    role: str
    ts: str
    ts_utc: Optional[str]
    message_line: int
    text: str


def build_stitched_transcript(
    rows: list[dict],
    *,
    max_text_chars: int = 0,
    parse_message_ts,
    iso_utc_precise,
) -> list[TranscriptLine]:
    transcript: list[TranscriptLine] = []
    thread_line = 0
    for message_index, row in enumerate(rows, start=1):
        raw_text = str(row.get("text") or "")
        lines = raw_text.splitlines() or [raw_text]
        parsed_ts = parse_message_ts(row.get("ts"))
        for message_line, line_text in enumerate(lines, start=1):
            thread_line += 1
            transcript.append(
                TranscriptLine(
                    thread_line=thread_line,
                    message_index=message_index,
                    message_id=str(row.get("message_id") or f"thread-msg-{message_index}"),
                    role=str(row.get("role") or ""),
                    ts=str(row.get("ts") or ""),
                    ts_utc=iso_utc_precise(parsed_ts),
                    message_line=message_line,
                    text=truncate_text(line_text, max_text_chars) if max_text_chars else line_text,
                )
            )
    return transcript


def filter_transcript_lines(
    transcript: list[TranscriptLine],
    *,
    thread_range: tuple[int, int] | None,
    message_range: tuple[int, int] | None,
) -> list[TranscriptLine]:
    out: list[TranscriptLine] = []
    for line in transcript:
        if thread_range and not (thread_range[0] <= line.thread_line <= thread_range[1]):
            continue
        if message_range and not (message_range[0] <= line.message_index <= message_range[1]):
            continue
        out.append(line)
    return out


def window_excerpt(
    transcript: list[TranscriptLine],
    line: TranscriptLine,
    before: int,
    after: int,
) -> list[dict]:
    start = max(1, line.thread_line - before)
    end = min(len(transcript), line.thread_line + after)
    return [
        {
            "thread_line": item.thread_line,
            "message_index": item.message_index,
            "message_line": item.message_line,
            "role": item.role,
            "ts": item.ts,
            "text": item.text,
        }
        for item in transcript[start - 1 : end]
    ]

