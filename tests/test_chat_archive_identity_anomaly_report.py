from __future__ import annotations

import csv
import importlib.util
import json
import sqlite3
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_script_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


reporter = _load_script_module(
    "itir_chat_archive_identity_anomaly_report",
    REPO_ROOT / "scripts" / "chat_archive_identity_anomaly_report.py",
)


def _make_archive(path: Path) -> None:
    con = sqlite3.connect(path)
    con.executescript(
        """
        CREATE TABLE messages (
          message_id TEXT PRIMARY KEY,
          canonical_thread_id TEXT NOT NULL,
          platform TEXT NOT NULL,
          account_id TEXT NOT NULL,
          ts TEXT NOT NULL,
          role TEXT NOT NULL,
          text TEXT NOT NULL,
          title TEXT,
          source_id TEXT NOT NULL,
          source_thread_id TEXT,
          source_message_id TEXT,
          source_path TEXT,
          source_bucket TEXT,
          provenance_json TEXT
        );
        """
    )
    rows = [
        # Proper refetch: source_message_id and content both overlap.
        (
            "same-a-1",
            "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "chatgpt",
            "main",
            "2026-01-01T00:00:00Z",
            "user",
            "Refetch same question",
            "Same Thread",
            "same-old",
            "thread-same",
            "same-msg-1",
        ),
        (
            "same-a-2",
            "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "chatgpt",
            "main",
            "2026-01-01T00:01:00Z",
            "assistant",
            "Refetch same answer",
            "Same Thread",
            "same-old",
            "thread-same",
            "same-msg-2",
        ),
        (
            "same-b-1",
            "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "chatgpt",
            "main",
            "2026-01-01T00:00:00Z",
            "user",
            "Refetch same question",
            "Same Thread",
            "same-new",
            "thread-same",
            "same-msg-1",
        ),
        (
            "same-b-2",
            "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "chatgpt",
            "main",
            "2026-01-01T00:01:00Z",
            "assistant",
            "Refetch same answer",
            "Same Thread",
            "same-new",
            "thread-same",
            "same-msg-2",
        ),
        # Likely ID derivation mismatch: IDs changed, content still overlaps.
        (
            "ids-a-1",
            "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "chatgpt",
            "main",
            "2026-01-02T00:00:00Z",
            "user",
            "Stable text with old id",
            "Changed IDs",
            "ids-old",
            "thread-changed-ids",
            "old-msg-1",
        ),
        (
            "ids-b-1",
            "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "chatgpt",
            "main",
            "2026-01-02T00:00:00Z",
            "user",
            "  stable   text with OLD id  ",
            "Changed IDs",
            "ids-new",
            "thread-changed-ids",
            "new-msg-1",
        ),
        # Strong anomaly: content disjoint and row count skew >= 2x.
        (
            "bad-a-1",
            "cccccccccccccccccccccccccccccccccccccccc",
            "chatgpt",
            "main",
            "2026-01-03T00:00:00Z",
            "user",
            "Tiny unrelated snapshot",
            "Bad Thread",
            "bad-old",
            "thread-bad",
            "bad-old-msg-1",
        ),
        (
            "bad-b-1",
            "cccccccccccccccccccccccccccccccccccccccc",
            "chatgpt",
            "main",
            "2026-01-03T01:00:00Z",
            "user",
            "Large unrelated first",
            "Bad Thread",
            "bad-new",
            "thread-bad",
            "bad-new-msg-1",
        ),
        (
            "bad-b-2",
            "cccccccccccccccccccccccccccccccccccccccc",
            "chatgpt",
            "main",
            "2026-01-03T01:01:00Z",
            "assistant",
            "Large unrelated second",
            "Bad Thread",
            "bad-new",
            "thread-bad",
            "bad-new-msg-2",
        ),
        (
            "bad-b-3",
            "cccccccccccccccccccccccccccccccccccccccc",
            "chatgpt",
            "main",
            "2026-01-03T01:02:00Z",
            "user",
            "Large unrelated third",
            "Bad Thread",
            "bad-new",
            "thread-bad",
            "bad-new-msg-3",
        ),
        # Filter guard: same shape on another platform should not appear.
        (
            "other-a-1",
            "dddddddddddddddddddddddddddddddddddddddd",
            "perplexity",
            "main",
            "2026-01-04T00:00:00Z",
            "user",
            "Other platform",
            "Other",
            "other-old",
            "thread-other",
            "other-old-msg",
        ),
        (
            "other-b-1",
            "dddddddddddddddddddddddddddddddddddddddd",
            "perplexity",
            "main",
            "2026-01-04T01:00:00Z",
            "user",
            "Other platform two",
            "Other",
            "other-new",
            "thread-other",
            "other-new-msg",
        ),
    ]
    con.executemany(
        """
        INSERT INTO messages (
          message_id, canonical_thread_id, platform, account_id, ts, role, text,
          title, source_id, source_thread_id, source_message_id, source_path,
          source_bucket, provenance_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL, NULL)
        """,
        rows,
    )
    con.commit()
    con.close()


def _threads_by_source_id(report: dict) -> dict[str, dict]:
    return {thread["source_thread_id"]: thread for thread in report["threads"]}


def test_report_classifies_refetch_id_derivation_and_strong_anomaly(tmp_path: Path) -> None:
    db = tmp_path / "chat_archive.sqlite"
    _make_archive(db)

    report = reporter.build_report(
        db,
        platform="chatgpt",
        account="main",
        min_snapshots=2,
        skew_ratio=2.0,
        fingerprint_mode="role-text",
    )

    threads = _threads_by_source_id(report)
    assert set(threads) == {"thread-same", "thread-changed-ids", "thread-bad"}

    assert threads["thread-same"]["classification"] == "multi_snapshot"
    assert threads["thread-same"]["message_id_disjoint"] is False
    assert threads["thread-same"]["content_disjoint"] is False

    assert threads["thread-changed-ids"]["classification"] == "likely_refetch_id_derivation"
    assert threads["thread-changed-ids"]["message_id_disjoint"] is True
    assert threads["thread-changed-ids"]["content_disjoint"] is False
    assert threads["thread-changed-ids"]["content_fingerprint_overlap_count"] == 1

    assert threads["thread-bad"]["classification"] == "strong_anomaly_candidate"
    assert threads["thread-bad"]["message_id_disjoint"] is True
    assert threads["thread-bad"]["content_disjoint"] is True
    assert threads["thread-bad"]["high_row_count_skew"] is True

    summary = report["summary"]
    assert summary["total_messages_scanned"] == 10
    assert summary["multi_snapshot_thread_count"] == 3
    assert summary["message_id_disjoint_thread_count"] == 2
    assert summary["content_disjoint_thread_count"] == 1
    assert summary["strong_anomaly_candidate_count"] == 1
    assert summary["likely_refetch_id_derivation_count"] == 1


def test_strong_only_and_limit_filter_reported_threads(tmp_path: Path) -> None:
    db = tmp_path / "chat_archive.sqlite"
    _make_archive(db)

    report = reporter.build_report(
        db,
        platform="chatgpt",
        account="main",
        min_snapshots=2,
        skew_ratio=2.0,
        fingerprint_mode="role-text",
        strong_only=True,
        limit=1,
    )

    assert [thread["source_thread_id"] for thread in report["threads"]] == ["thread-bad"]
    assert report["summary"]["multi_snapshot_thread_count"] == 3
    assert report["summary"]["emitted_thread_count"] == 1
    assert report["summary"]["strong_anomaly_candidate_count"] == 1


def test_main_writes_json_and_csv_outputs(tmp_path: Path) -> None:
    db = tmp_path / "chat_archive.sqlite"
    _make_archive(db)
    json_out = tmp_path / "report.json"
    csv_out = tmp_path / "report.csv"

    assert reporter.main(["--db", str(db), "--out", str(json_out)]) == 0
    payload = json.loads(json_out.read_text(encoding="utf-8"))
    assert payload["summary"]["schema"] == reporter.REPORT_SCHEMA
    assert payload["summary"]["platform"] == "chatgpt"

    assert (
        reporter.main(
            [
                "--db",
                str(db),
                "--format",
                "csv",
                "--out",
                str(csv_out),
                "--strong-only",
            ]
        )
        == 0
    )
    rows = list(csv.DictReader(csv_out.read_text(encoding="utf-8").splitlines()))
    assert len(rows) == 1
    assert rows[0]["classification"] == "strong_anomaly_candidate"
    assert rows[0]["source_thread_id"] == "thread-bad"
