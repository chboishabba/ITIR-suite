#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


URI_RE = re.compile(r"/URI\s*\((.*?)\)")
CHAT_CONVO_URL_RE = re.compile(
    r"https?://(?:chatgpt\.com|chat\.openai\.com)/(?:c|chat)/([0-9a-fA-F-]{36})",
    re.IGNORECASE,
)
CHAT_SHARE_URL_RE = re.compile(
    r"https?://(?:chatgpt\.com|chat\.openai\.com)/share/([0-9a-fA-F-]{36})",
    re.IGNORECASE,
)
UUID_RE = re.compile(
    r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}\b"
)


@dataclass
class PdfIdResult:
    file: str
    uri_count: int
    has_chatgpt_links: bool
    conversation_ids: list[str]
    share_ids: list[str]
    uri_samples: list[str]


def _iter_pdf_paths(root: Path, recursive: bool, follow_links: bool) -> list[Path]:
    paths: list[Path] = []
    for dirpath, _, filenames in os.walk(root, followlinks=follow_links):
        for filename in filenames:
            if filename.lower().endswith(".pdf"):
                paths.append(Path(dirpath) / filename)
        if not recursive:
            break
    return sorted(paths)


def _decode_pdf_text(path: Path) -> str:
    raw = path.read_bytes()
    return raw.decode("latin-1", errors="ignore")


def _unescape_pdf_uri(uri: str) -> str:
    return (
        uri.replace(r"\(", "(")
        .replace(r"\)", ")")
        .replace(r"\\", "\\")
        .replace("\n", "")
        .strip()
    )


def extract_ids_from_pdf(path: Path) -> PdfIdResult:
    text = _decode_pdf_text(path)
    uri_matches = [_unescape_pdf_uri(item) for item in URI_RE.findall(text)]

    conversation_ids: set[str] = set()
    share_ids: set[str] = set()

    for uri in uri_matches:
        for match in CHAT_CONVO_URL_RE.findall(uri):
            conversation_ids.add(match.lower())
        for match in CHAT_SHARE_URL_RE.findall(uri):
            share_ids.add(match.lower())

    # Some exports embed URLs directly in text streams, not only as /URI objects.
    for match in CHAT_CONVO_URL_RE.findall(text):
        conversation_ids.add(match.lower())
    for match in CHAT_SHARE_URL_RE.findall(text):
        share_ids.add(match.lower())

    # Last-resort fallback: if chatgpt links exist but no /c/<id> URL survives,
    # collect UUIDs in the PDF as possible candidate conversation IDs.
    has_chatgpt_links = ("chatgpt.com" in text.lower()) or ("chat.openai.com" in text.lower())
    if has_chatgpt_links and not conversation_ids:
        for candidate in UUID_RE.findall(text):
            conversation_ids.add(candidate.lower())

    return PdfIdResult(
        file=str(path),
        uri_count=len(uri_matches),
        has_chatgpt_links=has_chatgpt_links,
        conversation_ids=sorted(conversation_ids),
        share_ids=sorted(share_ids),
        uri_samples=uri_matches[:8],
    )


def _load_db_presence(sqlite_path: Path, ids: list[str]) -> dict[str, dict[str, int | bool]]:
    if not ids:
        return {}
    if not sqlite_path.exists():
        return {cid: {"canonical_thread_messages": 0, "source_id_messages": 0, "found": False} for cid in ids}

    conn = sqlite3.connect(str(sqlite_path))
    try:
        placeholders = ",".join("?" for _ in ids)
        by_thread = {
            row[0]: int(row[1])
            for row in conn.execute(
                f"""
                SELECT canonical_thread_id, COUNT(*)
                FROM messages
                WHERE canonical_thread_id IN ({placeholders})
                GROUP BY canonical_thread_id
                """,
                ids,
            )
        }
        by_source = {
            row[0]: int(row[1])
            for row in conn.execute(
                f"""
                SELECT source_id, COUNT(*)
                FROM messages
                WHERE source_id IN ({placeholders})
                GROUP BY source_id
                """,
                ids,
            )
        }
    finally:
        conn.close()

    presence: dict[str, dict[str, int | bool]] = {}
    for cid in ids:
        thread_count = int(by_thread.get(cid, 0))
        source_count = int(by_source.get(cid, 0))
        presence[cid] = {
            "canonical_thread_messages": thread_count,
            "source_id_messages": source_count,
            "found": (thread_count + source_count) > 0,
        }
    return presence


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract ChatGPT conversation/share IDs from PDF files and optionally validate against sqlite archive."
    )
    parser.add_argument(
        "--input-dir",
        required=True,
        help="Folder containing PDF files (recursively scanned by default).",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        default=True,
        help="Recursively scan subdirectories (default: enabled).",
    )
    parser.add_argument(
        "--no-recursive",
        action="store_false",
        dest="recursive",
        help="Scan only top-level directory.",
    )
    parser.add_argument(
        "--follow-links",
        action="store_true",
        help="Follow symlinked directories while scanning.",
    )
    parser.add_argument(
        "--sqlite",
        help="Optional sqlite archive path for ID cross-check (messages table).",
    )
    parser.add_argument(
        "--json-out",
        help="Optional JSON output path for detailed report.",
    )
    args = parser.parse_args()

    input_dir = Path(args.input_dir).expanduser().resolve()
    if not input_dir.exists():
        raise SystemExit(f"input dir does not exist: {input_dir}")

    pdf_paths = _iter_pdf_paths(
        root=input_dir,
        recursive=bool(args.recursive),
        follow_links=bool(args.follow_links),
    )
    if not pdf_paths:
        raise SystemExit(f"no PDFs found in: {input_dir}")

    results = [extract_ids_from_pdf(path) for path in pdf_paths]
    all_convo_ids = sorted({cid for item in results for cid in item.conversation_ids})

    db_presence: dict[str, dict[str, int | bool]] = {}
    if args.sqlite:
        sqlite_path = Path(args.sqlite).expanduser().resolve()
        db_presence = _load_db_presence(sqlite_path, all_convo_ids)

    summary = {
        "input_dir": str(input_dir),
        "pdf_count": len(results),
        "chatgpt_pdf_count": sum(1 for item in results if item.has_chatgpt_links),
        "pdfs_with_conversation_id": sum(1 for item in results if item.conversation_ids),
        "conversation_id_count": len(all_convo_ids),
        "share_id_count": len({sid for item in results for sid in item.share_ids}),
        "conversation_ids": all_convo_ids,
    }
    if db_presence:
        summary["db_found_conversation_ids"] = sum(
            1 for cid in all_convo_ids if db_presence.get(cid, {}).get("found")
        )

    report = {
        "summary": summary,
        "db_presence": db_presence,
        "files": [asdict(item) for item in results],
    }

    if args.json_out:
        out_path = Path(args.json_out).expanduser().resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        print(out_path)

    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)
