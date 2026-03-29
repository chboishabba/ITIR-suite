from __future__ import annotations

import re

from .transcript import TranscriptLine, window_excerpt


TOKEN_RE = re.compile(r"[A-Za-z0-9_]{2,}")
DEFAULT_STOPWORDS = {
    "the",
    "and",
    "for",
    "that",
    "with",
    "this",
    "from",
    "have",
    "your",
    "were",
    "what",
    "when",
    "where",
    "which",
    "would",
    "could",
    "should",
    "into",
    "about",
    "there",
    "their",
    "they",
    "them",
    "then",
    "than",
    "just",
    "also",
    "because",
    "while",
    "been",
    "being",
    "over",
    "under",
    "more",
    "most",
    "some",
    "will",
    "need",
    "next",
    "task",
}


def split_paragraphs(text: str) -> list[str]:
    return [chunk.strip() for chunk in re.split(r"\n\s*\n+", text) if chunk.strip()]


def parse_terms(values: list[str]) -> list[str]:
    terms: list[str] = []
    seen: set[str] = set()
    for raw in values:
        for chunk in str(raw or "").split(","):
            term = chunk.strip()
            if not term:
                continue
            key = term.casefold()
            if key in seen:
                continue
            seen.add(key)
            terms.append(term)
    return terms


def compile_pattern(term: str, *, regex: bool, case_sensitive: bool) -> re.Pattern[str]:
    flags = 0 if case_sensitive else re.IGNORECASE
    return re.compile(term if regex else re.escape(term), flags)


def parse_range_spec(spec: str, label: str) -> tuple[int, int]:
    match = re.fullmatch(r"\s*(\d+)\s*:\s*(\d+)\s*", spec or "")
    if not match:
        raise ValueError(f"Invalid {label}: expected START:END")
    start = int(match.group(1))
    end = int(match.group(2))
    if start <= 0 or end <= 0:
        raise ValueError(f"Invalid {label}: values must be >= 1")
    if start > end:
        raise ValueError(f"Invalid {label}: start must be <= end")
    return start, end


def analyze_thread_terms(
    transcript: list[TranscriptLine],
    *,
    terms: list[str],
    regex: bool,
    case_sensitive: bool,
    show_line_context: int,
) -> dict:
    text_joined = "\n".join(line.text for line in transcript)
    message_ids = {line.message_id for line in transcript}
    message_count = len({line.message_index for line in transcript})
    line_count = len(transcript)
    char_count = len(text_joined)
    term_stats: list[dict] = []
    mentions: list[dict] = []
    for term in terms:
        pattern = compile_pattern(term, regex=regex, case_sensitive=case_sensitive)
        raw_count = 0
        line_hits: set[int] = set()
        message_hits: set[int] = set()
        for line in transcript:
            matches = list(pattern.finditer(line.text))
            if not matches:
                continue
            raw_count += len(matches)
            line_hits.add(line.thread_line)
            message_hits.add(line.message_index)
            for match in matches:
                mention = {
                    "term": term,
                    "thread_line_start": line.thread_line,
                    "thread_line_end": line.thread_line,
                    "message_index": line.message_index,
                    "message_id": line.message_id,
                    "message_line_start": line.message_line,
                    "message_line_end": line.message_line,
                    "role": line.role,
                    "ts": line.ts,
                    "ts_utc": line.ts_utc,
                    "matched_text": match.group(0),
                    "line_text": line.text,
                }
                if show_line_context > 0:
                    mention["line_context"] = window_excerpt(
                        transcript,
                        line,
                        before=show_line_context,
                        after=show_line_context,
                    )
                mentions.append(mention)
        term_stats.append(
            {
                "term": term,
                "raw_count": raw_count,
                "line_hit_count": len(line_hits),
                "message_hit_count": len(message_hits),
                "density_per_100_lines": round((raw_count / line_count) * 100, 3) if line_count else 0.0,
                "density_per_1000_chars": round((raw_count / char_count) * 1000, 3) if char_count else 0.0,
                "density_per_100_messages": round((raw_count / message_count) * 100, 3) if message_count else 0.0,
            }
        )
    return {
        "transcript_stats": {
            "message_count": message_count,
            "stitched_line_count": line_count,
            "character_count": char_count,
            "message_id_count": len(message_ids),
        },
        "term_stats": term_stats,
        "mentions": mentions,
    }


def top_terms(transcript: list[TranscriptLine], limit: int) -> list[dict]:
    counts: dict[str, int] = {}
    for line in transcript:
        for token in TOKEN_RE.findall(line.text.casefold()):
            if token in DEFAULT_STOPWORDS:
                continue
            counts[token] = counts.get(token, 0) + 1
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:limit]
    return [{"term": term, "count": count} for term, count in ranked]
