#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
import sqlite3
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, TextIO


DEFAULT_DB = Path("/home/c/chat_archive.sqlite")
REPORT_SCHEMA = "itir.chat_archive.identity_anomaly_report.v1"


def _sqlite_ro_uri(path: Path) -> str:
    return f"file:{path.expanduser().resolve()}?mode=ro&immutable=1"


def connect_read_only(db_path: Path) -> sqlite3.Connection:
    con = sqlite3.connect(_sqlite_ro_uri(db_path), uri=True)
    con.row_factory = sqlite3.Row
    try:
        con.execute("PRAGMA query_only=ON")
        con.execute("PRAGMA temp_store=MEMORY")
    except sqlite3.Error:
        pass
    return con


def normalize_text(value: object) -> str:
    text = "" if value is None else str(value)
    return re.sub(r"\s+", " ", text).strip().lower()


def content_fingerprint(row: sqlite3.Row, *, mode: str) -> str | None:
    text = normalize_text(row["text"])
    if not text:
        return None
    role = normalize_text(row["role"])
    if mode == "text":
        return text
    if mode == "role-text":
        return f"{role}\x1f{text}"
    raise ValueError(f"unsupported fingerprint mode: {mode}")


@dataclass(frozen=True)
class SnapshotStats:
    source_id: str
    row_count: int
    distinct_source_message_count: int
    earliest_ts: str | None
    latest_ts: str | None


def _fetch_total_messages(con: sqlite3.Connection, platform: str, account: str) -> int:
    row = con.execute(
        """
        SELECT COUNT(*) AS count
        FROM messages
        WHERE platform = ? AND account_id = ?
        """,
        (platform, account),
    ).fetchone()
    return int(row["count"] or 0)


def _fetch_multi_snapshot_threads(
    con: sqlite3.Connection,
    *,
    platform: str,
    account: str,
    min_snapshots: int,
) -> list[str]:
    rows = con.execute(
        """
        SELECT source_thread_id
        FROM messages
        WHERE platform = ?
          AND account_id = ?
          AND source_thread_id IS NOT NULL
          AND TRIM(source_thread_id) <> ''
          AND source_id IS NOT NULL
          AND TRIM(source_id) <> ''
        GROUP BY source_thread_id
        HAVING COUNT(DISTINCT source_id) >= ?
        ORDER BY source_thread_id
        """,
        (platform, account, min_snapshots),
    ).fetchall()
    return [str(row["source_thread_id"]) for row in rows]


def _fetch_snapshot_stats(
    con: sqlite3.Connection,
    *,
    platform: str,
    account: str,
    source_thread_id: str,
) -> list[SnapshotStats]:
    rows = con.execute(
        """
        SELECT
            source_id,
            COUNT(*) AS row_count,
            COUNT(DISTINCT source_message_id) AS distinct_source_message_count,
            MIN(ts) AS earliest_ts,
            MAX(ts) AS latest_ts
        FROM messages
        WHERE platform = ?
          AND account_id = ?
          AND source_thread_id = ?
          AND source_id IS NOT NULL
          AND TRIM(source_id) <> ''
        GROUP BY source_id
        ORDER BY latest_ts DESC, row_count DESC, source_id DESC
        """,
        (platform, account, source_thread_id),
    ).fetchall()
    return [
        SnapshotStats(
            source_id=str(row["source_id"]),
            row_count=int(row["row_count"] or 0),
            distinct_source_message_count=int(row["distinct_source_message_count"] or 0),
            earliest_ts=row["earliest_ts"],
            latest_ts=row["latest_ts"],
        )
        for row in rows
    ]


def _iter_thread_rows(
    con: sqlite3.Connection,
    *,
    platform: str,
    account: str,
    source_thread_id: str,
) -> Iterable[sqlite3.Row]:
    yield from con.execute(
        """
        SELECT source_id, source_message_id, role, text
        FROM messages
        WHERE platform = ?
          AND account_id = ?
          AND source_thread_id = ?
          AND source_id IS NOT NULL
          AND TRIM(source_id) <> ''
        """,
        (platform, account, source_thread_id),
    )


def _overlap_metrics(
    rows: Iterable[sqlite3.Row],
    *,
    fingerprint_mode: str,
) -> dict[str, Any]:
    message_sources: dict[str, set[str]] = defaultdict(set)
    fingerprint_sources: dict[str, set[str]] = defaultdict(set)
    total_nonempty_message_ids = 0
    total_nonempty_fingerprints = 0

    for row in rows:
        source_id = str(row["source_id"])
        source_message_id = normalize_text(row["source_message_id"])
        if source_message_id:
            total_nonempty_message_ids += 1
            message_sources[source_message_id].add(source_id)
        fingerprint = content_fingerprint(row, mode=fingerprint_mode)
        if fingerprint:
            total_nonempty_fingerprints += 1
            fingerprint_sources[fingerprint].add(source_id)

    message_overlap = sum(1 for sources in message_sources.values() if len(sources) > 1)
    content_overlap = sum(1 for sources in fingerprint_sources.values() if len(sources) > 1)
    distinct_messages = len(message_sources)
    distinct_fingerprints = len(fingerprint_sources)
    return {
        "source_message_id_overlap_count": message_overlap,
        "source_message_id_distinct_count": distinct_messages,
        "source_message_id_nonempty_rows": total_nonempty_message_ids,
        "source_message_id_overlap_ratio": (
            message_overlap / distinct_messages if distinct_messages else 0.0
        ),
        "content_fingerprint_overlap_count": content_overlap,
        "content_fingerprint_distinct_count": distinct_fingerprints,
        "content_fingerprint_nonempty_rows": total_nonempty_fingerprints,
        "content_fingerprint_overlap_ratio": (
            content_overlap / distinct_fingerprints if distinct_fingerprints else 0.0
        ),
    }


def classify_thread(
    *,
    message_id_disjoint: bool,
    content_disjoint: bool,
    high_row_count_skew: bool,
) -> str:
    if content_disjoint and high_row_count_skew:
        return "strong_anomaly_candidate"
    if message_id_disjoint and not content_disjoint:
        return "likely_refetch_id_derivation"
    if message_id_disjoint or content_disjoint or high_row_count_skew:
        return "review_needed"
    return "multi_snapshot"


def analyze_thread(
    con: sqlite3.Connection,
    *,
    platform: str,
    account: str,
    source_thread_id: str,
    skew_ratio: float,
    fingerprint_mode: str,
) -> dict[str, Any]:
    snapshots = _fetch_snapshot_stats(
        con,
        platform=platform,
        account=account,
        source_thread_id=source_thread_id,
    )
    row_counts = [snapshot.row_count for snapshot in snapshots]
    min_rows = min(row_counts) if row_counts else 0
    max_rows = max(row_counts) if row_counts else 0
    total_rows = sum(row_counts)
    actual_skew_ratio = (max_rows / min_rows) if min_rows else None
    high_row_count_skew = (
        len(snapshots) > 1
        and min_rows > 0
        and actual_skew_ratio is not None
        and actual_skew_ratio >= skew_ratio
    )
    overlap = _overlap_metrics(
        _iter_thread_rows(
            con,
            platform=platform,
            account=account,
            source_thread_id=source_thread_id,
        ),
        fingerprint_mode=fingerprint_mode,
    )
    message_id_disjoint = overlap["source_message_id_overlap_count"] == 0
    content_disjoint = overlap["content_fingerprint_overlap_count"] == 0
    classification = classify_thread(
        message_id_disjoint=message_id_disjoint,
        content_disjoint=content_disjoint,
        high_row_count_skew=high_row_count_skew,
    )
    return {
        "platform": platform,
        "account_id": account,
        "source_thread_id": source_thread_id,
        "snapshot_count": len(snapshots),
        "total_rows": total_rows,
        "min_rows": min_rows,
        "max_rows": max_rows,
        "skew_ratio": actual_skew_ratio,
        "high_row_count_skew": high_row_count_skew,
        "message_id_disjoint": message_id_disjoint,
        "content_disjoint": content_disjoint,
        "classification": classification,
        **overlap,
        "snapshots": [
            {
                "source_id": snapshot.source_id,
                "row_count": snapshot.row_count,
                "distinct_source_message_count": snapshot.distinct_source_message_count,
                "earliest_ts": snapshot.earliest_ts,
                "latest_ts": snapshot.latest_ts,
            }
            for snapshot in snapshots
        ],
    }


def summarize_threads(
    *,
    total_messages: int,
    platform: str,
    account: str,
    threads: list[dict[str, Any]],
    emitted_thread_count: int,
    skew_ratio: float,
    fingerprint_mode: str,
) -> dict[str, Any]:
    source_counts: Counter[str] = Counter()
    source_rows: Counter[str] = Counter()
    for thread in threads:
        for snapshot in thread["snapshots"]:
            source_id = str(snapshot["source_id"])
            source_counts[source_id] += 1
            source_rows[source_id] += int(snapshot["row_count"] or 0)

    return {
        "schema": REPORT_SCHEMA,
        "platform": platform,
        "account_id": account,
        "total_messages_scanned": total_messages,
        "multi_snapshot_thread_count": len(threads),
        "emitted_thread_count": emitted_thread_count,
        "message_id_disjoint_thread_count": sum(1 for t in threads if t["message_id_disjoint"]),
        "content_disjoint_thread_count": sum(1 for t in threads if t["content_disjoint"]),
        "high_row_count_skew_thread_count": sum(1 for t in threads if t["high_row_count_skew"]),
        "strong_anomaly_candidate_count": sum(
            1 for t in threads if t["classification"] == "strong_anomaly_candidate"
        ),
        "likely_refetch_id_derivation_count": sum(
            1 for t in threads if t["classification"] == "likely_refetch_id_derivation"
        ),
        "skew_ratio_threshold": skew_ratio,
        "fingerprint_mode": fingerprint_mode,
        "implicated_source_ids": [
            {
                "source_id": source_id,
                "affected_thread_count": source_counts[source_id],
                "rows": source_rows[source_id],
            }
            for source_id, _ in sorted(
                source_counts.items(),
                key=lambda item: (-item[1], -source_rows[item[0]], item[0]),
            )
        ],
    }


def build_report(
    db_path: Path,
    *,
    platform: str,
    account: str,
    min_snapshots: int,
    skew_ratio: float,
    fingerprint_mode: str,
    strong_only: bool = False,
    limit: int = 0,
) -> dict[str, Any]:
    with connect_read_only(db_path) as con:
        total_messages = _fetch_total_messages(con, platform, account)
        source_thread_ids = _fetch_multi_snapshot_threads(
            con,
            platform=platform,
            account=account,
            min_snapshots=min_snapshots,
        )
        threads = [
            analyze_thread(
                con,
                platform=platform,
                account=account,
                source_thread_id=source_thread_id,
                skew_ratio=skew_ratio,
                fingerprint_mode=fingerprint_mode,
            )
            for source_thread_id in source_thread_ids
        ]

    threads.sort(
        key=lambda item: (
            item["classification"] != "strong_anomaly_candidate",
            item["classification"],
            -(item["max_rows"] or 0),
            item["source_thread_id"],
        )
    )
    summary_threads = list(threads)
    emitted_threads = list(threads)
    if strong_only:
        emitted_threads = [
            t for t in emitted_threads if t["classification"] == "strong_anomaly_candidate"
        ]
    if limit > 0:
        emitted_threads = emitted_threads[:limit]

    return {
        "summary": summarize_threads(
            total_messages=total_messages,
            platform=platform,
            account=account,
            threads=summary_threads,
            emitted_thread_count=len(emitted_threads),
            skew_ratio=skew_ratio,
            fingerprint_mode=fingerprint_mode,
        ),
        "threads": emitted_threads,
    }


def _write_json(report: dict[str, Any], out: TextIO) -> None:
    json.dump(report, out, indent=2, sort_keys=True)
    out.write("\n")


def _write_csv(report: dict[str, Any], out: TextIO) -> None:
    fieldnames = [
        "classification",
        "platform",
        "account_id",
        "source_thread_id",
        "snapshot_count",
        "total_rows",
        "min_rows",
        "max_rows",
        "skew_ratio",
        "message_id_disjoint",
        "content_disjoint",
        "high_row_count_skew",
        "source_message_id_overlap_count",
        "content_fingerprint_overlap_count",
        "source_ids",
    ]
    writer = csv.DictWriter(out, fieldnames=fieldnames)
    writer.writeheader()
    for thread in report["threads"]:
        row = {field: thread.get(field) for field in fieldnames}
        row["source_ids"] = ";".join(snapshot["source_id"] for snapshot in thread["snapshots"])
        writer.writerow(row)


def _positive_float(value: str) -> float:
    parsed = float(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return parsed


def _nonnegative_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be non-negative")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read-only inventory of multi-snapshot chat archive identity anomalies."
    )
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--platform", default="chatgpt")
    parser.add_argument("--account", default="main")
    parser.add_argument("--format", choices=("json", "csv"), default="json")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--limit", type=_nonnegative_int, default=0)
    parser.add_argument("--min-snapshots", type=int, default=2)
    parser.add_argument("--skew-ratio", type=_positive_float, default=2.0)
    parser.add_argument("--fingerprint-mode", choices=("role-text", "text"), default="role-text")
    parser.add_argument(
        "--strong-only",
        action="store_true",
        help="Emit only content-disjoint high-skew strong anomaly candidates.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = build_report(
        args.db,
        platform=args.platform,
        account=args.account,
        min_snapshots=args.min_snapshots,
        skew_ratio=args.skew_ratio,
        fingerprint_mode=args.fingerprint_mode,
        strong_only=args.strong_only,
        limit=args.limit,
    )
    writer = _write_json if args.format == "json" else _write_csv
    if args.out:
        with args.out.open("w", encoding="utf-8", newline="") as handle:
            writer(report, handle)
    else:
        writer(report, sys.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
