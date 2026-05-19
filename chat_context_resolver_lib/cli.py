from __future__ import annotations

import argparse


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
        "--provider",
        choices=("auto", "chatgpt", "perplexity"),
        default="auto",
        help=(
            "Live provider for URL/export fallback. auto detects supported provider URLs; "
            "bare UUID live fallback requires an explicit provider."
        ),
    )
    parser.add_argument(
        "--perplexity-scroll-mode",
        choices=("step", "end", "hybrid"),
        default=None,
        help=(
            "Perplexity loader scroll strategy. step is safest for full-history loads; "
            "end is a fast tail probe; hybrid alternates stepped loading with end probes."
        ),
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
        "--semantic",
        action="store_true",
        help=(
            "Opt in to MyChatArchive semantic candidate retrieval. "
            "Default DB/web resolver behavior is unchanged unless this flag is set."
        ),
    )
    parser.add_argument(
        "--hybrid",
        action="store_true",
        help=(
            "Opt in to MyChatArchive hybrid FTS + vector candidate retrieval. "
            "Default DB/web resolver behavior is unchanged unless this flag is set."
        ),
    )
    parser.add_argument(
        "--mca-db",
        help="Path to the MyChatArchive SQLite DB for --semantic/--hybrid retrieval.",
    )
    parser.add_argument(
        "--mca-limit",
        type=int,
        default=10,
        help="Max MyChatArchive candidates for --semantic/--hybrid retrieval (default: %(default)s).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Max rows for cross-thread analysis results (default: %(default)s).",
    )
    return parser
