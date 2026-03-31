from __future__ import annotations

import argparse
import datetime as dt
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional


@dataclass(frozen=True)
class RuntimeOptions:
    selector_input: str
    selector_for_db: str
    selector_for_web: str
    db_path: Path
    venv_python_path: Path
    analysis_terms: list[str]
    thread_range: tuple[int, int] | None
    message_range: tuple[int, int] | None
    analysis_requested: bool
    threshold: Optional[dt.datetime]


@dataclass(frozen=True)
class ParsedInvocation:
    args: argparse.Namespace
    runtime: RuntimeOptions


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Resolve conversation context by querying structurer DB first, then "
            "fallback to re-gpt --view when missing/stale."
        )
    )
    parser.add_argument(
        "selector",
        help="Conversation selector: online_thread_id, canonical_thread_id, or title",
    )
    parser.add_argument(
        "--db",
        default="~/chat_archive.sqlite",
        help="Path to canonical chat archive SQLite DB (default: %(default)s)",
    )
    parser.add_argument(
        "--if-newer-than",
        help=(
            "Datetime (ISO8601 or epoch). If this is newer than DB latest timestamp, "
            "force web fallback."
        ),
    )
    parser.add_argument(
        "--venv-python",
        default=".venv/bin/python",
        help="Python interpreter for module fallback to re_gpt.cli (default: %(default)s)",
    )
    parser.add_argument(
        "--web-timeout",
        type=int,
        default=120,
        help="Timeout seconds for web fallback command (default: %(default)s)",
    )
    parser.add_argument(
        "--no-web",
        action="store_true",
        help="Do not run web fallback; fail if DB does not satisfy the request.",
    )
    parser.add_argument(
        "--persist-web-miss",
        action="store_true",
        help=(
            "When DB lookup misses and web fallback runs, also run export download + "
            "ingest into structurer DB. Disabled by default for faster lookups."
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON output.",
    )
    parser.add_argument(
        "--max-text-chars",
        type=int,
        default=1200,
        help=(
            "Max characters of latest DB message to return/print "
            "(default: %(default)s, use 0 for unlimited)."
        ),
    )
    parser.add_argument(
        "--latest-paragraphs",
        action="store_true",
        help="Include latest DB message split into a paragraph list.",
    )
    parser.add_argument(
        "--recent-turns",
        type=int,
        default=0,
        help=(
            "Include the most recent N turns with per-message timestamps "
            "(DB when source=db; live fetch when source=web)."
        ),
    )
    parser.add_argument(
        "--check-web-newer",
        action="store_true",
        help=(
            "When DB has a match, fetch live recent turn timestamps and prefer web "
            "if web appears newer than DB."
        ),
    )
    parser.add_argument(
        "--analyze-term",
        action="append",
        default=[],
        help="Analyze one or more terms (comma-separated allowed) against the resolved thread or cross-thread result set.",
    )
    parser.add_argument(
        "--term-file",
        help="Read additional analysis terms from a file (one term per line).",
    )
    parser.add_argument(
        "--case-sensitive",
        action="store_true",
        help="Use case-sensitive term matching for analysis mode.",
    )
    parser.add_argument(
        "--regex",
        action="store_true",
        help="Treat analysis terms as regular expressions instead of exact substrings.",
    )
    parser.add_argument(
        "--range",
        dest="thread_range",
        help="Restrict thread-local analysis to stitched transcript lines START:END.",
    )
    parser.add_argument(
        "--message-range",
        help="Restrict thread-local analysis to message ordinals START:END.",
    )
    parser.add_argument(
        "--show-lines",
        action="store_true",
        help="Include stitched transcript lines in thread-local analysis output.",
    )
    parser.add_argument(
        "--show-line-context",
        type=int,
        default=0,
        help="For each mention, include N surrounding stitched transcript lines.",
    )
    parser.add_argument(
        "--term-frequency",
        action="store_true",
        help="Emit term frequency statistics for analysis terms.",
    )
    parser.add_argument(
        "--mention-density",
        action="store_true",
        help="Emit mention density metrics for analysis terms.",
    )
    parser.add_argument(
        "--top-terms",
        type=int,
        default=0,
        help="Include the top N simple lexical terms for the selected transcript slice.",
    )
    parser.add_argument(
        "--cross-thread",
        action="store_true",
        help="Run archive-wide ranking for the analysis terms instead of a single resolved thread.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Max rows for cross-thread analysis results (default: %(default)s).",
    )
    return parser


def resolve_runtime_options(
    args: argparse.Namespace,
    *,
    repo_root: Path,
    parse_terms: Callable[[list[str]], list[str]],
    parse_range_spec: Callable[[str, str], tuple[int, int]],
    parse_datetime: Callable[[str], dt.datetime],
    extract_online_thread_id: Callable[[str], Optional[str]],
) -> RuntimeOptions:
    db_path = Path(args.db).expanduser()
    if not db_path.is_absolute():
        db_path = repo_root / db_path

    venv_python_input = Path(args.venv_python).expanduser()
    if venv_python_input.is_absolute():
        venv_python_path = venv_python_input
    else:
        venv_python_path = repo_root / venv_python_input

    analysis_terms = parse_terms(list(args.analyze_term or []))
    if args.term_file:
        term_file = Path(args.term_file).expanduser()
        if not term_file.is_absolute():
            term_file = repo_root / term_file
        if not term_file.exists():
            raise ValueError(f"Term file does not exist: {term_file}")
        file_terms = [line.strip() for line in term_file.read_text(encoding="utf-8").splitlines() if line.strip()]
        analysis_terms.extend(parse_terms(file_terms))
        analysis_terms = parse_terms(analysis_terms)

    selector_input = (args.selector or "").strip()
    extracted_online_id = extract_online_thread_id(selector_input)
    selector_for_db = extracted_online_id or selector_input
    selector_for_web = extracted_online_id or selector_input

    thread_range: tuple[int, int] | None = None
    message_range: tuple[int, int] | None = None
    if args.thread_range:
        thread_range = parse_range_spec(args.thread_range, "--range")
    if args.message_range:
        message_range = parse_range_spec(args.message_range, "--message-range")

    threshold: Optional[dt.datetime] = None
    if args.if_newer_than:
        try:
            threshold = parse_datetime(args.if_newer_than)
        except ValueError as exc:
            raise ValueError(f"Invalid --if-newer-than: {exc}") from exc

    analysis_requested = bool(
        analysis_terms
        or args.top_terms > 0
        or args.show_lines
        or args.show_line_context > 0
        or thread_range
        or message_range
        or args.cross_thread
        or args.term_frequency
        or args.mention_density
    )

    return RuntimeOptions(
        selector_input=selector_input,
        selector_for_db=selector_for_db,
        selector_for_web=selector_for_web,
        db_path=db_path,
        venv_python_path=venv_python_path,
        analysis_terms=analysis_terms,
        thread_range=thread_range,
        message_range=message_range,
        analysis_requested=analysis_requested,
        threshold=threshold,
    )


def parse_invocation(
    *,
    parser: argparse.ArgumentParser,
    argv: list[str] | None,
    repo_root: Path,
    parse_terms: Callable[[list[str]], list[str]],
    parse_range_spec: Callable[[str, str], tuple[int, int]],
    parse_datetime: Callable[[str], dt.datetime],
    extract_online_thread_id: Callable[[str], Optional[str]],
) -> ParsedInvocation:
    args = parser.parse_args(argv)
    runtime = resolve_runtime_options(
        args,
        repo_root=repo_root,
        parse_terms=parse_terms,
        parse_range_spec=parse_range_spec,
        parse_datetime=parse_datetime,
        extract_online_thread_id=extract_online_thread_id,
    )
    return ParsedInvocation(args=args, runtime=runtime)
