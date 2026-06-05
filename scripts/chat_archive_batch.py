#!/usr/bin/env python3
"""Batch selected chat archive threads through turn-bound chunks and PNF surfaces."""

from __future__ import annotations

import argparse
import calendar
import concurrent.futures
import json
import sqlite3
import sys
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from threading import Event, Lock, Thread
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_ROOT = REPO_ROOT / "scripts"
SENSIBLAW_ROOT = REPO_ROOT / "SensibLaw"
for item in (REPO_ROOT, SCRIPTS_ROOT, SENSIBLAW_ROOT):
    if str(item) not in sys.path:
        sys.path.insert(0, str(item))

import export_chat_archive_thread as exporter
from chat_context_resolver_lib.db_lookup import connect_sqlite_ro, query_db_fts_candidates
from src.sensiblaw.conversation_vm import compile_turn, empty_state, step_state


SCHEMA = "itir.chat_archive.batch_run.v0_1"
DEFAULT_CHUNK_TARGET_CHARS = 24_000
DEFAULT_CHUNK_HARD_MAX_CHARS = 32_000
DEFAULT_MAX_MESSAGES = 80
DEFAULT_MESSAGE_HARD_MAX_CHARS = 8_000
DEFAULT_SLICE_TARGET_CHARS = 4_000
PERF_MATRIX_SCHEMA = "itir.pnf_perf_matrix.v0_1"
DEFAULT_PERF_MATRIX_DIR = REPO_ROOT / ".cache_local" / "itir_pnf_perf_matrix"


@dataclass(frozen=True)
class ChunkClaim:
    chunk_id: int
    run_id: str
    canonical_thread_id: str
    chunk_index: int
    start_message_index: int
    end_message_index: int
    worker_id: str


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _json_dumps(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True)


class PerfMatrixWriter:
    def __init__(self, path: Path | None, *, strict: bool = False) -> None:
        self.path = path.expanduser() if path else None
        self.strict = strict
        self._lock = Lock()
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)

    @classmethod
    def for_run(cls, path: Path | None, matrix_dir: Path, run_id: str | None, *, disabled: bool, strict: bool) -> "PerfMatrixWriter | None":
        if disabled:
            return None
        resolved = path.expanduser() if path else matrix_dir.expanduser() / f"{run_id or 'archive'}-{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}.jsonl"
        return cls(resolved, strict=strict)

    def record(self, stage: str, **fields: Any) -> None:
        if self.path is None:
            return
        row = {
            "schema": PERF_MATRIX_SCHEMA,
            "ts": utc_now(),
            "suite": "chat_archive_batch",
            "stage": stage,
            **fields,
        }
        try:
            with self._lock:
                with self.path.open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps(row, sort_keys=True) + "\n")
        except Exception as exc:
            if self.strict:
                raise
            sys.stderr.write(f"perf-matrix write failed: {exc}\n")

    def callback(self, *, run_id: str, chunk_id: int, canonical_thread_id: str, phase: str) -> Any:
        def _emit(metric: dict[str, Any]) -> None:
            self.record(
                phase,
                run_id=run_id,
                chunk_id=chunk_id,
                canonical_thread_id=canonical_thread_id,
                component=metric.get("component"),
                metric_stage=metric.get("stage"),
                elapsed_ms=metric.get("elapsed_ms"),
                metrics={key: value for key, value in metric.items() if key not in {"component", "stage", "elapsed_ms"}},
            )

        return _emit


class StageTimer:
    def __init__(self, writer: PerfMatrixWriter | None, stage: str, **fields: Any) -> None:
        self.writer = writer
        self.stage = stage
        self.fields = fields
        self.started = 0.0

    def __enter__(self) -> "StageTimer":
        self.started = time.perf_counter()
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        if self.writer is None:
            return
        fields = dict(self.fields)
        fields["elapsed_ms"] = round((time.perf_counter() - self.started) * 1000, 6)
        if exc is not None:
            fields["status"] = "error"
            fields["error_type"] = type(exc).__name__
        else:
            fields.setdefault("status", "ok")
        self.writer.record(self.stage, **fields)


def _sqlite_metric_snapshot(path: Path) -> dict[str, Any]:
    wal_path = Path(str(path) + "-wal")
    snapshot: dict[str, Any] = {"db_path": str(path), "wal_bytes": wal_path.stat().st_size if wal_path.exists() else 0}
    if not path.exists():
        return snapshot
    try:
        con = sqlite3.connect(path)
        for table in (
            "runs",
            "selected_threads",
            "chunks",
            "message_outputs",
            "partial_errors",
            "conversation_vm_deltas",
            "conversation_vm_states",
            "pnf_atoms",
            "pnf_emission_receipts",
            "pnf_residual_receipts",
            "timeline_events",
        ):
            try:
                snapshot[f"{table}_count"] = int(con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
            except sqlite3.Error:
                pass
        try:
            snapshot["total_changes"] = int(con.total_changes)
        finally:
            con.close()
    except sqlite3.Error as exc:
        snapshot["probe_error"] = str(exc)
    return snapshot


def read_thread_list(path: Path) -> list[str]:
    text = path.expanduser().read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        payload = json.loads(text)
        if isinstance(payload, dict):
            rows = payload.get("thread_ids") or payload.get("threads") or payload.get("selected_threads") or []
        else:
            rows = payload
        result: list[str] = []
        for row in rows:
            if isinstance(row, str):
                result.append(row)
            elif isinstance(row, dict):
                value = row.get("canonical_thread_id") or row.get("thread_id") or row.get("source_thread_id")
                if value:
                    result.append(str(value))
        return result
    return [line.strip() for line in text.splitlines() if line.strip() and not line.strip().startswith("#")]


def _thread_metadata(cur: sqlite3.Cursor, thread_id: str) -> dict[str, Any] | None:
    cur.execute(
        """
        SELECT
            canonical_thread_id,
            source_thread_id,
            COALESCE(NULLIF(title, ''), '(no title)') AS title,
            MIN(ts) AS earliest_ts,
            MAX(ts) AS latest_ts,
            COUNT(*) AS message_count
        FROM messages
        WHERE LOWER(canonical_thread_id) = LOWER(?)
           OR LOWER(source_thread_id) = LOWER(?)
        GROUP BY canonical_thread_id, source_thread_id, title
        ORDER BY latest_ts DESC
        LIMIT 1
        """,
        (thread_id, thread_id),
    )
    row = cur.fetchone()
    return dict(row) if row else None


def select_threads(
    db_path: Path,
    *,
    terms: list[str],
    thread_ids: list[str],
    limit: int,
) -> dict[str, Any]:
    db_path = db_path.expanduser()
    selected: dict[str, dict[str, Any]] = {}
    con = connect_sqlite_ro(db_path)
    try:
        cur = con.cursor()
        rank = 0
        for raw_id in thread_ids:
            meta = _thread_metadata(cur, raw_id)
            if not meta:
                continue
            tid = str(meta["canonical_thread_id"])
            rank += 1
            selected[tid] = {
                **meta,
                "rank": rank,
                "selection_reason": "explicit_thread_id",
                "hit_count": None,
                "query_terms": [],
            }
        for term in terms:
            for candidate in query_db_fts_candidates(cur, term, limit=limit):
                tid = str(candidate["canonical_thread_id"])
                meta = _thread_metadata(cur, tid) or candidate
                if tid not in selected:
                    rank += 1
                    selected[tid] = {
                        **meta,
                        "rank": rank,
                        "selection_reason": "fts_term",
                        "hit_count": 0,
                        "query_terms": [],
                    }
                selected[tid]["hit_count"] = int(selected[tid].get("hit_count") or 0) + int(
                    candidate.get("hit_count") or 0
                )
                selected[tid].setdefault("query_terms", []).append(term)
    finally:
        con.close()

    rows = sorted(selected.values(), key=lambda row: (-(int(row.get("hit_count") or 0)), int(row["rank"])))
    if limit > 0:
        rows = rows[:limit]
    for idx, row in enumerate(rows, start=1):
        row["rank"] = idx
        row["query_terms"] = sorted(set(row.get("query_terms") or []))
    return {
        "schema": SCHEMA,
        "type": "thread_selection_manifest",
        "generated_at": utc_now(),
        "source_db": str(db_path.expanduser()),
        "terms": terms,
        "selected_threads": rows,
    }


def _export_args(db_path: Path, thread_id: str) -> argparse.Namespace:
    return argparse.Namespace(
        db=str(db_path.expanduser()),
        selector=None,
        canonical_thread_id=thread_id,
        source_thread_id=None,
        title=None,
        title_exact=False,
        platform=None,
        resolve_limit=8,
        pick_first=True,
        include_blocks=False,
        no_clean_perplexity_duplicates=False,
    )


def load_thread_payload(db_path: Path, thread_id: str) -> dict[str, Any]:
    return exporter.build_payload(db_path.expanduser(), _export_args(db_path, thread_id))


def plan_thread_chunks(
    db_path: Path,
    thread_id: str,
    *,
    target_chars: int = DEFAULT_CHUNK_TARGET_CHARS,
    hard_max_chars: int = DEFAULT_CHUNK_HARD_MAX_CHARS,
    max_messages: int = DEFAULT_MAX_MESSAGES,
) -> dict[str, Any]:
    if target_chars <= 0:
        raise ValueError("target_chars must be positive")
    if hard_max_chars <= 0:
        raise ValueError("hard_max_chars must be positive")
    payload = load_thread_payload(db_path, thread_id)
    plan = exporter.plan_message_chunks(
        payload["messages"],
        max_messages=max_messages,
        target_bytes=min(target_chars, hard_max_chars),
    )
    for item in plan:
        messages = [
            message
            for message in payload["messages"]
            if int(item["start_message_index"]) <= int(message["index"]) <= int(item["end_message_index"])
        ]
        item["estimated_chars"] = sum(len(str(message.get("text") or "")) for message in messages)
        item["ts_start"] = messages[0].get("ts") if messages else None
        item["ts_end"] = messages[-1].get("ts") if messages else None
    return {
        "schema": SCHEMA,
        "type": "thread_chunk_plan",
        "thread": payload["thread"],
        "message_count": len(payload["messages"]),
        "chunk_target_chars": target_chars,
        "chunk_hard_max_chars": hard_max_chars,
        "chunk_plan": plan,
    }


def init_run_db(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    try:
        con.executescript(
            """
            PRAGMA journal_mode=WAL;
            CREATE TABLE IF NOT EXISTS runs (
              run_id TEXT PRIMARY KEY,
              schema TEXT NOT NULL,
              mode TEXT NOT NULL,
              source_db TEXT NOT NULL,
              pnf_first INTEGER NOT NULL,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS selected_threads (
              run_id TEXT NOT NULL,
              canonical_thread_id TEXT NOT NULL,
              source_thread_id TEXT,
              title TEXT,
              earliest_ts TEXT,
              latest_ts TEXT,
              message_count INTEGER,
              rank INTEGER,
              selection_reason TEXT,
              hit_count INTEGER,
              query_terms_json TEXT NOT NULL DEFAULT '[]',
              PRIMARY KEY (run_id, canonical_thread_id)
            );
            CREATE TABLE IF NOT EXISTS chunks (
              chunk_id INTEGER PRIMARY KEY AUTOINCREMENT,
              run_id TEXT NOT NULL,
              canonical_thread_id TEXT NOT NULL,
              chunk_index INTEGER NOT NULL,
              start_message_index INTEGER NOT NULL,
              end_message_index INTEGER NOT NULL,
              message_count INTEGER NOT NULL,
              estimated_chars INTEGER NOT NULL,
              estimated_bytes INTEGER NOT NULL,
              ts_start TEXT,
              ts_end TEXT,
              status TEXT NOT NULL DEFAULT 'queued',
              worker_id TEXT,
              started_at TEXT,
              completed_at TEXT,
              error_text TEXT,
              UNIQUE (run_id, canonical_thread_id, chunk_index)
            );
            CREATE TABLE IF NOT EXISTS worker_claims (
              claim_id INTEGER PRIMARY KEY AUTOINCREMENT,
              run_id TEXT NOT NULL,
              chunk_id INTEGER NOT NULL,
              worker_id TEXT NOT NULL,
              claimed_at TEXT NOT NULL,
              released_at TEXT,
              status TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS chunk_outputs (
              run_id TEXT NOT NULL,
              chunk_id INTEGER NOT NULL,
              output_type TEXT NOT NULL,
              payload_json TEXT NOT NULL,
              created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS chunk_progress (
              run_id TEXT NOT NULL,
              chunk_id INTEGER NOT NULL,
              canonical_thread_id TEXT NOT NULL,
              chunk_index INTEGER NOT NULL,
              worker_id TEXT,
              phase TEXT NOT NULL,
              current_message_index INTEGER,
              current_message_id TEXT,
              current_slice_index INTEGER,
              chars_done INTEGER NOT NULL DEFAULT 0,
              chars_total INTEGER NOT NULL DEFAULT 0,
              elapsed_s REAL NOT NULL DEFAULT 0,
              rate_chars_s REAL,
              eta_s REAL,
              partial_rows INTEGER NOT NULL DEFAULT 0,
              skipped_count INTEGER NOT NULL DEFAULT 0,
              last_output_ref TEXT,
              last_heartbeat_at TEXT NOT NULL,
              started_at TEXT NOT NULL,
              updated_at TEXT NOT NULL,
              PRIMARY KEY (run_id, chunk_id)
            );
            CREATE TABLE IF NOT EXISTS message_outputs (
              run_id TEXT NOT NULL,
              chunk_id INTEGER NOT NULL,
              canonical_thread_id TEXT NOT NULL,
              message_index INTEGER NOT NULL,
              message_id TEXT,
              slice_index INTEGER NOT NULL DEFAULT 0,
              slice_count INTEGER NOT NULL DEFAULT 1,
              source_start_char INTEGER NOT NULL DEFAULT 0,
              source_end_char INTEGER NOT NULL DEFAULT 0,
              char_count INTEGER NOT NULL DEFAULT 0,
              status TEXT NOT NULL,
              delta_json TEXT NOT NULL,
              state_json TEXT,
              output_json TEXT NOT NULL,
              created_at TEXT NOT NULL,
              PRIMARY KEY (run_id, chunk_id, message_index, slice_index)
            );
            CREATE INDEX IF NOT EXISTS idx_message_outputs_resume
              ON message_outputs (run_id, chunk_id, message_index, slice_index);
            CREATE TABLE IF NOT EXISTS partial_errors (
              error_id INTEGER PRIMARY KEY AUTOINCREMENT,
              run_id TEXT NOT NULL,
              chunk_id INTEGER NOT NULL,
              canonical_thread_id TEXT NOT NULL,
              message_index INTEGER,
              message_id TEXT,
              slice_index INTEGER,
              phase TEXT NOT NULL,
              error_type TEXT NOT NULL,
              error_text TEXT NOT NULL,
              payload_json TEXT NOT NULL,
              created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS skipped_inputs (
              run_id TEXT NOT NULL,
              chunk_id INTEGER NOT NULL,
              canonical_thread_id TEXT NOT NULL,
              message_index INTEGER NOT NULL,
              message_id TEXT,
              slice_index INTEGER NOT NULL DEFAULT 0,
              reason TEXT NOT NULL,
              char_count INTEGER NOT NULL DEFAULT 0,
              payload_json TEXT NOT NULL,
              created_at TEXT NOT NULL,
              PRIMARY KEY (run_id, chunk_id, message_index, slice_index)
            );
            CREATE TABLE IF NOT EXISTS conversation_vm_deltas (
              run_id TEXT NOT NULL,
              chunk_id INTEGER NOT NULL,
              canonical_thread_id TEXT NOT NULL,
              message_index INTEGER NOT NULL,
              message_id TEXT,
              delta_json TEXT NOT NULL,
              created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS conversation_vm_states (
              run_id TEXT NOT NULL,
              chunk_id INTEGER NOT NULL,
              canonical_thread_id TEXT NOT NULL,
              chunk_index INTEGER NOT NULL,
              state_json TEXT NOT NULL,
              created_at TEXT NOT NULL,
              PRIMARY KEY (run_id, canonical_thread_id, chunk_index)
            );
            CREATE TABLE IF NOT EXISTS pnf_atoms (
              run_id TEXT NOT NULL,
              chunk_id INTEGER NOT NULL,
              canonical_thread_id TEXT NOT NULL,
              atom_id TEXT NOT NULL,
              predicate TEXT,
              arguments_json TEXT NOT NULL,
              receipt_ids_json TEXT NOT NULL,
              payload_json TEXT NOT NULL,
              PRIMARY KEY (run_id, atom_id)
            );
            CREATE TABLE IF NOT EXISTS pnf_edges (
              run_id TEXT NOT NULL,
              chunk_id INTEGER NOT NULL,
              canonical_thread_id TEXT NOT NULL,
              edge_type TEXT NOT NULL,
              source_id TEXT NOT NULL,
              target_id TEXT NOT NULL,
              payload_json TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS pnf_emission_receipts (
              run_id TEXT NOT NULL,
              chunk_id INTEGER NOT NULL,
              canonical_thread_id TEXT NOT NULL,
              receipt_id TEXT NOT NULL,
              atom_id TEXT,
              pnf_id TEXT,
              parser_profile TEXT,
              reducer_profile TEXT,
              payload_json TEXT NOT NULL,
              PRIMARY KEY (run_id, receipt_id)
            );
            CREATE TABLE IF NOT EXISTS pnf_residual_receipts (
              run_id TEXT NOT NULL,
              chunk_id INTEGER NOT NULL,
              canonical_thread_id TEXT NOT NULL,
              residual_receipt_id TEXT NOT NULL,
              residual_id TEXT,
              left_receipt_id TEXT,
              right_receipt_id TEXT,
              residual_level TEXT,
              relation TEXT,
              status TEXT,
              payload_json TEXT NOT NULL,
              PRIMARY KEY (run_id, residual_receipt_id)
            );
            CREATE TABLE IF NOT EXISTS task_memory_candidates (
              run_id TEXT NOT NULL,
              chunk_id INTEGER NOT NULL,
              canonical_thread_id TEXT NOT NULL,
              candidate_id TEXT NOT NULL,
              status TEXT NOT NULL,
              payload_json TEXT NOT NULL,
              PRIMARY KEY (run_id, candidate_id)
            );
            CREATE TABLE IF NOT EXISTS kanban_projection_rows (
              run_id TEXT NOT NULL,
              chunk_id INTEGER NOT NULL,
              canonical_thread_id TEXT NOT NULL,
              row_id TEXT NOT NULL,
              column_name TEXT NOT NULL,
              payload_json TEXT NOT NULL,
              PRIMARY KEY (run_id, row_id)
            );
            CREATE TABLE IF NOT EXISTS timeline_events (
              run_id TEXT NOT NULL,
              chunk_id INTEGER NOT NULL,
              canonical_thread_id TEXT NOT NULL,
              message_index INTEGER,
              message_id TEXT,
              ts TEXT,
              event_type TEXT NOT NULL,
              summary TEXT NOT NULL,
              payload_json TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS implementation_findings (
              run_id TEXT NOT NULL,
              chunk_id INTEGER NOT NULL,
              canonical_thread_id TEXT NOT NULL,
              finding_id TEXT NOT NULL,
              status TEXT NOT NULL,
              payload_json TEXT NOT NULL,
              PRIMARY KEY (run_id, finding_id)
            );
            """
        )
        con.commit()
    finally:
        con.close()


def create_run(
    run_db: Path,
    source_db: Path,
    selection: dict[str, Any],
    *,
    mode: str,
    pnf_first: bool,
    target_chars: int,
    hard_max_chars: int,
    max_messages: int,
) -> str:
    init_run_db(run_db)
    run_id = f"archive-{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}-{uuid.uuid4().hex[:8]}"
    now = utc_now()
    con = sqlite3.connect(run_db)
    try:
        con.execute(
            """
            INSERT INTO runs (run_id, schema, mode, source_db, pnf_first, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (run_id, SCHEMA, mode, str(source_db.expanduser()), int(pnf_first), now, now),
        )
        for row in selection.get("selected_threads", []):
            tid = str(row["canonical_thread_id"])
            con.execute(
                """
                INSERT INTO selected_threads (
                  run_id, canonical_thread_id, source_thread_id, title, earliest_ts, latest_ts,
                  message_count, rank, selection_reason, hit_count, query_terms_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    tid,
                    row.get("source_thread_id"),
                    row.get("title"),
                    row.get("earliest_ts"),
                    row.get("latest_ts"),
                    row.get("message_count"),
                    row.get("rank"),
                    row.get("selection_reason"),
                    row.get("hit_count"),
                    json.dumps(row.get("query_terms") or [], sort_keys=True),
                ),
            )
            chunk_plan = plan_thread_chunks(
                source_db,
                tid,
                target_chars=target_chars,
                hard_max_chars=hard_max_chars,
                max_messages=max_messages,
            )
            for chunk in chunk_plan["chunk_plan"]:
                con.execute(
                    """
                    INSERT INTO chunks (
                      run_id, canonical_thread_id, chunk_index, start_message_index,
                      end_message_index, message_count, estimated_chars, estimated_bytes,
                      ts_start, ts_end
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        run_id,
                        tid,
                        chunk["chunk_index"],
                        chunk["start_message_index"],
                        chunk["end_message_index"],
                        chunk["message_count"],
                        chunk.get("estimated_chars") or 0,
                        chunk.get("estimated_bytes") or 0,
                        chunk.get("ts_start"),
                        chunk.get("ts_end"),
                    ),
                )
        con.commit()
    finally:
        con.close()
    return run_id


def claim_next_chunk(run_db: Path, run_id: str, worker_id: str) -> ChunkClaim | None:
    con = sqlite3.connect(run_db, timeout=30)
    con.row_factory = sqlite3.Row
    try:
        con.execute("BEGIN IMMEDIATE")
        row = con.execute(
            """
            SELECT c.*
            FROM chunks c
            WHERE c.run_id = ?
              AND c.status IN ('queued', 'partial', 'partial_timeout')
              AND NOT EXISTS (
                SELECT 1
                FROM chunks prior
                WHERE prior.run_id = c.run_id
                  AND prior.canonical_thread_id = c.canonical_thread_id
                  AND prior.chunk_index < c.chunk_index
                  AND prior.status <> 'done'
              )
            ORDER BY c.chunk_index ASC, c.ts_start ASC, c.chunk_id ASC
            LIMIT 1
            """,
            (run_id,),
        ).fetchone()
        if row is None:
            con.rollback()
            return None
        now = utc_now()
        con.execute(
            """
            UPDATE chunks
            SET status = 'running',
                worker_id = ?,
                started_at = COALESCE(started_at, ?),
                completed_at = NULL
            WHERE chunk_id = ?
            """,
            (worker_id, now, row["chunk_id"]),
        )
        con.execute(
            """
            INSERT INTO worker_claims (run_id, chunk_id, worker_id, claimed_at, status)
            VALUES (?, ?, ?, ?, 'running')
            """,
            (run_id, row["chunk_id"], worker_id, now),
        )
        con.commit()
        return ChunkClaim(
            chunk_id=int(row["chunk_id"]),
            run_id=str(row["run_id"]),
            canonical_thread_id=str(row["canonical_thread_id"]),
            chunk_index=int(row["chunk_index"]),
            start_message_index=int(row["start_message_index"]),
            end_message_index=int(row["end_message_index"]),
            worker_id=worker_id,
        )
    finally:
        con.close()


def _previous_state(con: sqlite3.Connection, claim: ChunkClaim) -> dict[str, Any]:
    row = con.execute(
        """
        SELECT state_json
        FROM conversation_vm_states
        WHERE run_id = ?
          AND canonical_thread_id = ?
          AND chunk_index < ?
        ORDER BY chunk_index DESC
        LIMIT 1
        """,
        (claim.run_id, claim.canonical_thread_id, claim.chunk_index),
    ).fetchone()
    if row is None:
        return empty_state()
    return json.loads(row[0])


def _message_turn(thread: dict[str, Any], message: dict[str, Any]) -> dict[str, Any]:
    return {
        "turn_id": str(message.get("message_id") or f"{thread['canonical_thread_id']}:{message.get('index')}"),
        "speaker": message.get("role"),
        "text": message.get("text") or "",
        "source": {
            "canonical_thread_id": thread.get("canonical_thread_id"),
            "source_thread_id": thread.get("source_thread_id"),
            "title": thread.get("title"),
            "message_id": message.get("message_id"),
            "message_index": message.get("index"),
            "ts": message.get("ts"),
        },
    }


def _message_slices(message: dict[str, Any], *, target_chars: int, hard_max_chars: int) -> list[dict[str, Any]]:
    text = str(message.get("text") or "")
    if len(text) <= hard_max_chars:
        return [{"slice_index": 0, "slice_count": 1, "start": 0, "end": len(text), "text": text}]
    slices: list[dict[str, Any]] = []
    start = 0
    width = min(target_chars, hard_max_chars)
    while start < len(text):
        end = min(len(text), start + width)
        slices.append({"slice_index": len(slices), "start": start, "end": end, "text": text[start:end]})
        start = end
    for item in slices:
        item["slice_count"] = len(slices)
    return slices


def _turn_slice(thread: dict[str, Any], message: dict[str, Any], message_slice: dict[str, Any]) -> dict[str, Any]:
    turn = _message_turn(thread, message)
    if int(message_slice["slice_count"]) > 1:
        turn["turn_id"] = f"{turn['turn_id']}:slice-{message_slice['slice_index']}"
        turn["text"] = message_slice["text"]
        turn["source"]["slice_index"] = message_slice["slice_index"]
        turn["source"]["slice_count"] = message_slice["slice_count"]
        turn["source"]["source_start_char"] = message_slice["start"]
        turn["source"]["source_end_char"] = message_slice["end"]
        turn["source"]["original_message_id"] = message.get("message_id")
    return turn


def _skip_reason(message: dict[str, Any], *, skip_tool_messages: bool) -> str | None:
    if not skip_tool_messages:
        return None
    role = str(message.get("role") or "").lower()
    if role in {"tool", "function"}:
        return "tool_message"
    metadata = message.get("metadata")
    if isinstance(metadata, dict) and str(metadata.get("recipient") or metadata.get("tool") or ""):
        return "tool_message"
    return None


def _completed_units(con: sqlite3.Connection, claim: ChunkClaim) -> set[tuple[int, int]]:
    rows = con.execute(
        """
        SELECT message_index, slice_index
        FROM message_outputs
        WHERE run_id = ? AND chunk_id = ? AND status IN ('processed', 'skipped')
        """,
        (claim.run_id, claim.chunk_id),
    ).fetchall()
    return {(int(row[0]), int(row[1])) for row in rows}


def _resume_state(con: sqlite3.Connection, claim: ChunkClaim) -> dict[str, Any]:
    row = con.execute(
        """
        SELECT state_json
        FROM message_outputs
        WHERE run_id = ? AND chunk_id = ? AND state_json IS NOT NULL
        ORDER BY message_index DESC, slice_index DESC
        LIMIT 1
        """,
        (claim.run_id, claim.chunk_id),
    ).fetchone()
    if row and row[0]:
        return json.loads(row[0])
    return _previous_state(con, claim)


def _run_with_timeout(fn: Any, *args: Any, timeout_s: float | None = None) -> Any:
    if not timeout_s or timeout_s <= 0:
        return fn(*args)
    pool = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    future = pool.submit(fn, *args)
    try:
        return future.result(timeout=timeout_s)
    except concurrent.futures.TimeoutError as exc:
        future.cancel()
        raise TimeoutError(f"{getattr(fn, '__name__', 'call')} exceeded {timeout_s}s") from exc
    finally:
        pool.shutdown(wait=False, cancel_futures=True)


def _compile_turn_observed(turn: dict[str, Any], metrics_callback: Any | None) -> dict[str, Any]:
    if metrics_callback is None:
        return compile_turn(turn)
    try:
        return compile_turn(turn, metrics_callback=metrics_callback)
    except TypeError as exc:
        if "metrics_callback" not in str(exc):
            raise
        return compile_turn(turn)


def _step_state_observed(state: dict[str, Any], delta: dict[str, Any], metrics_callback: Any | None) -> dict[str, Any]:
    if metrics_callback is None:
        return step_state(state, delta)
    try:
        return step_state(state, delta, metrics_callback=metrics_callback)
    except TypeError as exc:
        if "metrics_callback" not in str(exc):
            raise
        return step_state(state, delta)


def _progress_counts(con: sqlite3.Connection, claim: ChunkClaim) -> tuple[int, int]:
    partial_rows = con.execute(
        "SELECT COUNT(*) FROM message_outputs WHERE run_id = ? AND chunk_id = ?",
        (claim.run_id, claim.chunk_id),
    ).fetchone()[0]
    skipped_count = con.execute(
        "SELECT COUNT(*) FROM skipped_inputs WHERE run_id = ? AND chunk_id = ?",
        (claim.run_id, claim.chunk_id),
    ).fetchone()[0]
    return int(partial_rows), int(skipped_count)


def _update_progress(
    con: sqlite3.Connection,
    claim: ChunkClaim,
    *,
    phase: str,
    started_monotonic: float,
    started_at: str,
    chars_done: int,
    chars_total: int,
    message: dict[str, Any] | None = None,
    slice_index: int | None = None,
    last_output_ref: str | None = None,
) -> None:
    now = utc_now()
    elapsed = max(0.001, time.monotonic() - started_monotonic)
    rate = chars_done / elapsed if chars_done > 0 else None
    eta = (max(0, chars_total - chars_done) / rate) if rate else None
    partial_rows, skipped_count = _progress_counts(con, claim)
    con.execute(
        """
        INSERT OR REPLACE INTO chunk_progress (
          run_id, chunk_id, canonical_thread_id, chunk_index, worker_id, phase,
          current_message_index, current_message_id, current_slice_index,
          chars_done, chars_total, elapsed_s, rate_chars_s, eta_s,
          partial_rows, skipped_count, last_output_ref, last_heartbeat_at, started_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            claim.run_id,
            claim.chunk_id,
            claim.canonical_thread_id,
            claim.chunk_index,
            claim.worker_id,
            phase,
            int(message["index"]) if message else None,
            message.get("message_id") if message else None,
            slice_index,
            chars_done,
            chars_total,
            round(elapsed, 3),
            round(rate, 3) if rate else None,
            round(eta, 3) if eta is not None else None,
            partial_rows,
            skipped_count,
            last_output_ref,
            now,
            started_at,
            now,
        ),
    )


def _record_partial_error(
    con: sqlite3.Connection,
    claim: ChunkClaim,
    *,
    message: dict[str, Any] | None,
    slice_index: int | None,
    phase: str,
    exc: BaseException,
) -> None:
    con.execute(
        """
        INSERT INTO partial_errors (
          run_id, chunk_id, canonical_thread_id, message_index, message_id, slice_index,
          phase, error_type, error_text, payload_json, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            claim.run_id,
            claim.chunk_id,
            claim.canonical_thread_id,
            int(message["index"]) if message else None,
            message.get("message_id") if message else None,
            slice_index,
            phase,
            type(exc).__name__,
            str(exc),
            _json_dumps({"recoverable": isinstance(exc, Exception)}),
            utc_now(),
        ),
    )


def process_chunk(
    run_db: Path,
    source_db: Path,
    claim: ChunkClaim,
    *,
    mode: str,
    pnf_first: bool,
    partial_flush_messages: int = 1,
    message_hard_max_chars: int = DEFAULT_MESSAGE_HARD_MAX_CHARS,
    slice_target_chars: int = DEFAULT_SLICE_TARGET_CHARS,
    skip_tool_messages: bool = True,
    fail_fast: bool = False,
    compile_timeout_s: float | None = None,
    step_timeout_s: float | None = None,
    perf_matrix: PerfMatrixWriter | None = None,
) -> None:
    con = sqlite3.connect(run_db, timeout=30)
    try:
        with StageTimer(perf_matrix, "load", run_id=claim.run_id, chunk_id=claim.chunk_id, canonical_thread_id=claim.canonical_thread_id):
            payload = load_thread_payload(source_db, claim.canonical_thread_id)
        thread = payload["thread"]
        messages = [
            message
            for message in payload["messages"]
            if claim.start_message_index <= int(message["index"]) <= claim.end_message_index
        ]
        with StageTimer(perf_matrix, "slice_plan", run_id=claim.run_id, chunk_id=claim.chunk_id, canonical_thread_id=claim.canonical_thread_id):
            units: list[tuple[dict[str, Any], dict[str, Any]]] = []
            for message in messages:
                for message_slice in _message_slices(
                    message,
                    target_chars=slice_target_chars,
                    hard_max_chars=message_hard_max_chars,
                ):
                    units.append((message, message_slice))
        chars_total = sum(len(message_slice["text"]) for _, message_slice in units)
        completed = _completed_units(con, claim)
        with StageTimer(perf_matrix, "resume", run_id=claim.run_id, chunk_id=claim.chunk_id, canonical_thread_id=claim.canonical_thread_id, completed_units=len(completed)):
            state = _resume_state(con, claim)
        chars_done = sum(
            len(message_slice["text"])
            for message, message_slice in units
            if (int(message["index"]), int(message_slice["slice_index"])) in completed
        )
        started_monotonic = time.monotonic()
        started_at = utc_now()
        _update_progress(
            con,
            claim,
            phase="loading",
            started_monotonic=started_monotonic,
            started_at=started_at,
            chars_done=chars_done,
            chars_total=chars_total,
        )
        con.commit()
        flushed = 0
        for message in messages:
            reason = _skip_reason(message, skip_tool_messages=skip_tool_messages)
            slices = _message_slices(message, target_chars=slice_target_chars, hard_max_chars=message_hard_max_chars)
            for message_slice in slices:
                slice_index = int(message_slice["slice_index"])
                unit_key = (int(message["index"]), slice_index)
                if unit_key in completed:
                    continue
                turn = _turn_slice(thread, message, message_slice)
                now = utc_now()
                last_output_ref = f"{claim.chunk_id}:{message['index']}:{slice_index}"
                try:
                    _update_progress(
                        con,
                        claim,
                        phase="skipping" if reason else "compiling",
                        started_monotonic=started_monotonic,
                        started_at=started_at,
                        chars_done=chars_done,
                        chars_total=chars_total,
                        message=message,
                        slice_index=slice_index,
                        last_output_ref=last_output_ref,
                    )
                    if reason:
                        delta = {"schema": "skipped", "reason": reason, "turn": turn}
                        status = "skipped"
                        con.execute(
                            """
                            INSERT OR REPLACE INTO skipped_inputs (
                              run_id, chunk_id, canonical_thread_id, message_index, message_id,
                              slice_index, reason, char_count, payload_json, created_at
                            )
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                claim.run_id,
                                claim.chunk_id,
                                claim.canonical_thread_id,
                                int(message["index"]),
                                message.get("message_id"),
                                slice_index,
                                reason,
                                len(message_slice["text"]),
                                _json_dumps({"turn": turn}),
                                now,
                            ),
                        )
                    else:
                        if pnf_first:
                            compile_metrics = perf_matrix.callback(
                                run_id=claim.run_id,
                                chunk_id=claim.chunk_id,
                                canonical_thread_id=claim.canonical_thread_id,
                                phase="compile",
                            ) if perf_matrix else None
                            with StageTimer(
                                perf_matrix,
                                "compile",
                                run_id=claim.run_id,
                                chunk_id=claim.chunk_id,
                                canonical_thread_id=claim.canonical_thread_id,
                                message_index=int(message["index"]),
                                slice_index=slice_index,
                                input_chars=len(message_slice["text"]),
                            ):
                                delta = _run_with_timeout(
                                    lambda item: _compile_turn_observed(item, compile_metrics),
                                    turn,
                                    timeout_s=compile_timeout_s,
                                )
                        else:
                            delta = {"schema": "disabled", "turn": turn}
                        if pnf_first:
                            _update_progress(
                                con,
                                claim,
                                phase="reducing",
                                started_monotonic=started_monotonic,
                                started_at=started_at,
                                chars_done=chars_done,
                                chars_total=chars_total,
                                message=message,
                                slice_index=slice_index,
                                last_output_ref=last_output_ref,
                            )
                            reduce_metrics = perf_matrix.callback(
                                run_id=claim.run_id,
                                chunk_id=claim.chunk_id,
                                canonical_thread_id=claim.canonical_thread_id,
                                phase="reduce",
                            ) if perf_matrix else None
                            with StageTimer(
                                perf_matrix,
                                "reduce",
                                run_id=claim.run_id,
                                chunk_id=claim.chunk_id,
                                canonical_thread_id=claim.canonical_thread_id,
                                message_index=int(message["index"]),
                                slice_index=slice_index,
                            ):
                                state = _run_with_timeout(
                                    lambda current, item: _step_state_observed(current, item, reduce_metrics),
                                    state,
                                    delta,
                                    timeout_s=step_timeout_s,
                                )
                        status = "processed"
                        con.execute(
                            """
                            INSERT OR REPLACE INTO conversation_vm_deltas (
                              run_id, chunk_id, canonical_thread_id, message_index, message_id, delta_json, created_at
                            )
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                claim.run_id,
                                claim.chunk_id,
                                claim.canonical_thread_id,
                                int(message["index"]),
                                message.get("message_id"),
                                _json_dumps(delta),
                                now,
                            ),
                        )
                    con.execute(
                        """
                        INSERT INTO timeline_events (
                          run_id, chunk_id, canonical_thread_id, message_index, message_id, ts,
                          event_type, summary, payload_json
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            claim.run_id,
                            claim.chunk_id,
                            claim.canonical_thread_id,
                            int(message["index"]),
                            message.get("message_id"),
                            message.get("ts"),
                            "conversation_turn_slice" if int(message_slice["slice_count"]) > 1 else "conversation_turn",
                            f"{message.get('role') or 'unknown'} turn",
                            _json_dumps({"mode": mode, "turn": turn, "status": status}),
                        ),
                    )
                    con.execute(
                        """
                        INSERT OR REPLACE INTO message_outputs (
                          run_id, chunk_id, canonical_thread_id, message_index, message_id,
                          slice_index, slice_count, source_start_char, source_end_char, char_count,
                          status, delta_json, state_json, output_json, created_at
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            claim.run_id,
                            claim.chunk_id,
                            claim.canonical_thread_id,
                            int(message["index"]),
                            message.get("message_id"),
                            slice_index,
                            int(message_slice["slice_count"]),
                            int(message_slice["start"]),
                            int(message_slice["end"]),
                            len(message_slice["text"]),
                            status,
                            _json_dumps(delta),
                            _json_dumps(state) if pnf_first else None,
                            _json_dumps({"mode": mode, "turn": turn, "delta": delta}),
                            now,
                        ),
                    )
                    chars_done += len(message_slice["text"])
                    flushed += 1
                    _update_progress(
                        con,
                        claim,
                        phase="flushed",
                        started_monotonic=started_monotonic,
                        started_at=started_at,
                        chars_done=chars_done,
                        chars_total=chars_total,
                        message=message,
                        slice_index=slice_index,
                        last_output_ref=last_output_ref,
                    )
                    if flushed >= max(1, partial_flush_messages):
                        with StageTimer(perf_matrix, "flush", run_id=claim.run_id, chunk_id=claim.chunk_id, canonical_thread_id=claim.canonical_thread_id, **_sqlite_metric_snapshot(run_db)):
                            con.commit()
                        flushed = 0
                except Exception as exc:
                    _record_partial_error(con, claim, message=message, slice_index=slice_index, phase="unit", exc=exc)
                    with StageTimer(perf_matrix, "error_persist", run_id=claim.run_id, chunk_id=claim.chunk_id, canonical_thread_id=claim.canonical_thread_id, **_sqlite_metric_snapshot(run_db)):
                        con.commit()
                    if fail_fast:
                        raise
                    chars_done += len(message_slice["text"])
                    _update_progress(
                        con,
                        claim,
                        phase="recoverable_error",
                        started_monotonic=started_monotonic,
                        started_at=started_at,
                        chars_done=chars_done,
                        chars_total=chars_total,
                        message=message,
                        slice_index=slice_index,
                        last_output_ref=last_output_ref,
                    )
                    with StageTimer(perf_matrix, "error_persist", run_id=claim.run_id, chunk_id=claim.chunk_id, canonical_thread_id=claim.canonical_thread_id, **_sqlite_metric_snapshot(run_db)):
                        con.commit()
        if pnf_first:
            con.execute(
                """
                INSERT OR REPLACE INTO conversation_vm_states (
                  run_id, chunk_id, canonical_thread_id, chunk_index, state_json, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    claim.run_id,
                    claim.chunk_id,
                    claim.canonical_thread_id,
                    claim.chunk_index,
                    _json_dumps(state),
                    utc_now(),
                ),
            )
            for atom in state.get("predicate_atoms", []):
                con.execute(
                    """
                    INSERT OR REPLACE INTO pnf_atoms (
                      run_id, chunk_id, canonical_thread_id, atom_id, predicate,
                      arguments_json, receipt_ids_json, payload_json
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        claim.run_id,
                        claim.chunk_id,
                        claim.canonical_thread_id,
                        atom.get("id"),
                        atom.get("predicate"),
                        _json_dumps(atom.get("arguments") or []),
                        _json_dumps(atom.get("receipt_ids") or []),
                        _json_dumps(atom),
                    ),
                )
            for pnf in state.get("predicate_pnfs", []):
                if pnf.get("atom_id") and pnf.get("id"):
                    con.execute(
                        """
                        INSERT INTO pnf_edges (
                          run_id, chunk_id, canonical_thread_id, edge_type, source_id, target_id, payload_json
                        )
                        VALUES (?, ?, ?, 'atom_pnf', ?, ?, ?)
                        """,
                        (
                            claim.run_id,
                            claim.chunk_id,
                            claim.canonical_thread_id,
                            pnf.get("atom_id"),
                            pnf.get("id"),
                            _json_dumps(pnf),
                        ),
                    )
            for receipt_payload in state.get("pnf_emission_receipts", []):
                con.execute(
                    """
                    INSERT OR REPLACE INTO pnf_emission_receipts (
                      run_id, chunk_id, canonical_thread_id, receipt_id, atom_id, pnf_id,
                      parser_profile, reducer_profile, payload_json
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        claim.run_id,
                        claim.chunk_id,
                        claim.canonical_thread_id,
                        receipt_payload.get("id"),
                        receipt_payload.get("atom_id"),
                        receipt_payload.get("pnf_id"),
                        receipt_payload.get("parser_profile"),
                        receipt_payload.get("reducer_profile"),
                        _json_dumps(receipt_payload),
                    ),
                )
            for residual_receipt in state.get("pnf_residual_receipts", []):
                con.execute(
                    """
                    INSERT OR REPLACE INTO pnf_residual_receipts (
                      run_id, chunk_id, canonical_thread_id, residual_receipt_id, residual_id,
                      left_receipt_id, right_receipt_id, residual_level, relation, status,
                      payload_json
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        claim.run_id,
                        claim.chunk_id,
                        claim.canonical_thread_id,
                        residual_receipt.get("id"),
                        residual_receipt.get("residual_id"),
                        residual_receipt.get("left_emission_receipt_id"),
                        residual_receipt.get("right_emission_receipt_id"),
                        residual_receipt.get("residual_level"),
                        residual_receipt.get("relation"),
                        residual_receipt.get("status"),
                        _json_dumps(residual_receipt),
                    ),
                )
        con.execute(
            """
            INSERT INTO chunk_outputs (run_id, chunk_id, output_type, payload_json, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                claim.run_id,
                claim.chunk_id,
                "chunk_summary",
                _json_dumps(
                    {
                        "mode": mode,
                        "pnf_first": pnf_first,
                        "message_count": len(messages),
                        "message_output_count": len(units),
                        "predicate_atom_count": len(state.get("predicate_atoms", [])) if pnf_first else 0,
                    }
                ),
                utc_now(),
            ),
        )
        _update_progress(
            con,
            claim,
            phase="done",
            started_monotonic=started_monotonic,
            started_at=started_at,
            chars_done=chars_done,
            chars_total=chars_total,
        )
        con.execute(
            "UPDATE chunks SET status = 'done', completed_at = ?, error_text = NULL WHERE chunk_id = ?",
            (utc_now(), claim.chunk_id),
        )
        con.execute(
            """
            UPDATE worker_claims
            SET status = 'done', released_at = ?
            WHERE run_id = ? AND chunk_id = ? AND worker_id = ? AND released_at IS NULL
            """,
            (utc_now(), claim.run_id, claim.chunk_id, claim.worker_id),
        )
        with StageTimer(perf_matrix, "final_persist", run_id=claim.run_id, chunk_id=claim.chunk_id, canonical_thread_id=claim.canonical_thread_id, **_sqlite_metric_snapshot(run_db)):
            con.commit()
    except BaseException as exc:
        con.rollback()
        try:
            _record_partial_error(con, claim, message=None, slice_index=None, phase="chunk", exc=exc)
        except Exception:
            pass
        con.execute(
            "UPDATE chunks SET status = ?, completed_at = ?, error_text = ? WHERE chunk_id = ?",
            ("failed" if isinstance(exc, Exception) and fail_fast else "partial", utc_now(), str(exc), claim.chunk_id),
        )
        con.execute(
            """
            UPDATE worker_claims
            SET status = ?, released_at = ?
            WHERE run_id = ? AND chunk_id = ? AND worker_id = ? AND released_at IS NULL
            """,
            ("failed" if isinstance(exc, Exception) and fail_fast else "partial", utc_now(), claim.run_id, claim.chunk_id, claim.worker_id),
        )
        with StageTimer(perf_matrix, "error_persist", run_id=claim.run_id, chunk_id=claim.chunk_id, canonical_thread_id=claim.canonical_thread_id, **_sqlite_metric_snapshot(run_db)):
            con.commit()
        raise
    finally:
        con.close()


def run_workers(
    run_db: Path,
    source_db: Path,
    run_id: str,
    *,
    mode: str,
    pnf_first: bool,
    max_workers: int,
    progress: bool = False,
    progress_interval: float = 2.0,
    partial_flush_messages: int = 1,
    message_hard_max_chars: int = DEFAULT_MESSAGE_HARD_MAX_CHARS,
    slice_target_chars: int = DEFAULT_SLICE_TARGET_CHARS,
    skip_tool_messages: bool = True,
    fail_fast: bool = False,
    compile_timeout_s: float | None = None,
    step_timeout_s: float | None = None,
    perf_matrix: PerfMatrixWriter | None = None,
) -> dict[str, Any]:
    started = time.monotonic()
    stop_progress = Event()

    def emit_progress() -> None:
        try:
            status = run_status(run_db, run_id)
            sys.stderr.write(json.dumps(status["progress"], sort_keys=True) + "\n")
            sys.stderr.flush()
        except Exception as exc:
            if fail_fast:
                raise
            sys.stderr.write(json.dumps({"progress_error": str(exc)}, sort_keys=True) + "\n")
            sys.stderr.flush()

    def progress_monitor() -> None:
        interval = progress_interval if progress_interval > 0 else 1.0
        while not stop_progress.wait(interval):
            emit_progress()

    def worker(worker_index: int) -> int:
        worker_id = f"worker-{worker_index}"
        completed = 0
        while True:
            with StageTimer(perf_matrix, "claim", run_id=run_id, worker_id=worker_id, **_sqlite_metric_snapshot(run_db)):
                claim = claim_next_chunk(run_db, run_id, worker_id)
            if claim is None:
                return completed
            process_chunk(
                run_db,
                source_db,
                claim,
                mode=mode,
                pnf_first=pnf_first,
                partial_flush_messages=partial_flush_messages,
                message_hard_max_chars=message_hard_max_chars,
                slice_target_chars=slice_target_chars,
                skip_tool_messages=skip_tool_messages,
                fail_fast=fail_fast,
                compile_timeout_s=compile_timeout_s,
                step_timeout_s=step_timeout_s,
                perf_matrix=perf_matrix,
            )
            completed += 1
            if progress:
                emit_progress()

    workers = max(1, max_workers)
    monitor: Thread | None = None
    if progress:
        emit_progress()
        monitor = Thread(target=progress_monitor, daemon=True)
        monitor.start()
    try:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            completed_counts = list(pool.map(worker, range(1, workers + 1)))
    finally:
        stop_progress.set()
        if monitor is not None:
            monitor.join(timeout=2)
    status = run_status(run_db, run_id)
    status["worker_completed_chunks"] = completed_counts
    status["elapsed_s"] = round(time.monotonic() - started, 3)
    if progress:
        sys.stderr.write(json.dumps(status["progress"], sort_keys=True) + "\n")
        sys.stderr.flush()
    return status


def _perf_matrix_summary(path: Path) -> dict[str, Any]:
    summary: dict[str, Any] = {"path": str(path), "exists": path.exists(), "row_count": 0, "stage_counts": {}}
    if not path.exists():
        return summary
    stage_counts: dict[str, int] = {}
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            summary["row_count"] += 1
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                stage = "<invalid>"
            else:
                stage = str(row.get("stage") or "<missing>")
            stage_counts[stage] = stage_counts.get(stage, 0) + 1
    summary["stage_counts"] = stage_counts
    return summary


def run_status(run_db: Path, run_id: str, *, perf_matrix_path: Path | None = None) -> dict[str, Any]:
    con = sqlite3.connect(run_db)
    con.row_factory = sqlite3.Row
    try:
        run = con.execute("SELECT * FROM runs WHERE run_id = ?", (run_id,)).fetchone()
        if not run:
            raise SystemExit(f"run not found: {run_id}")
        status_rows = con.execute(
            "SELECT status, COUNT(*) AS count, COALESCE(SUM(estimated_chars), 0) AS chars FROM chunks WHERE run_id = ? GROUP BY status",
            (run_id,),
        ).fetchall()
        totals = {row["status"]: {"count": int(row["count"]), "estimated_chars": int(row["chars"])} for row in status_rows}
        total = con.execute(
            "SELECT COUNT(*) AS chunks, COALESCE(SUM(estimated_chars), 0) AS chars FROM chunks WHERE run_id = ?",
            (run_id,),
        ).fetchone()
        done = totals.get("done", {"count": 0, "estimated_chars": 0})
        first_start = con.execute(
            "SELECT MIN(started_at) AS started_at FROM chunks WHERE run_id = ? AND started_at IS NOT NULL",
            (run_id,),
        ).fetchone()["started_at"]
        partial_rows = con.execute(
            "SELECT COUNT(*) FROM message_outputs WHERE run_id = ?",
            (run_id,),
        ).fetchone()[0]
        skipped_count = con.execute(
            "SELECT COUNT(*) FROM skipped_inputs WHERE run_id = ?",
            (run_id,),
        ).fetchone()[0]
        error_count = con.execute(
            "SELECT COUNT(*) FROM partial_errors WHERE run_id = ?",
            (run_id,),
        ).fetchone()[0]
        running_rows = con.execute(
            """
            SELECT *
            FROM chunk_progress
            WHERE run_id = ?
              AND phase <> 'done'
            ORDER BY updated_at DESC
            LIMIT 16
            """,
            (run_id,),
        ).fetchall()
        latest_output = con.execute(
            """
            SELECT chunk_id, message_index, message_id, slice_index, created_at
            FROM message_outputs
            WHERE run_id = ?
            ORDER BY created_at DESC, chunk_id DESC, message_index DESC, slice_index DESC
            LIMIT 1
            """,
            (run_id,),
        ).fetchone()
        eta_s = None
        if first_start and done["estimated_chars"] > 0:
            # Coarse wall-clock ETA; enough for long-running progress reporting.
            elapsed = max(0.001, time.time() - calendar.timegm(time.strptime(first_start, "%Y-%m-%dT%H:%M:%SZ")))
            rate = done["estimated_chars"] / elapsed
            remaining = int(total["chars"] or 0) - done["estimated_chars"]
            eta_s = round(max(0, remaining) / rate, 3) if rate > 0 else None
        payload = {
            "schema": SCHEMA,
            "run_id": run_id,
            "mode": run["mode"],
            "pnf_first": bool(run["pnf_first"]),
            "source_db": run["source_db"],
            "chunks_total": int(total["chunks"] or 0),
            "estimated_chars_total": int(total["chars"] or 0),
            "status_counts": totals,
            "progress": {
                "completed_chunks": done["count"],
                "total_chunks": int(total["chunks"] or 0),
                "completed_estimated_chars": done["estimated_chars"],
                "eta_s": eta_s,
                "partial_rows": int(partial_rows),
                "skipped_count": int(skipped_count),
                "partial_error_count": int(error_count),
                "last_useful_output": dict(latest_output) if latest_output else None,
                "running_workers": [dict(row) for row in running_rows],
            },
        }
        if perf_matrix_path:
            payload["perf_matrix"] = _perf_matrix_summary(perf_matrix_path.expanduser())
        return payload
    finally:
        con.close()


def _write_or_print(payload: dict[str, Any], output: Path | None) -> None:
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    select = sub.add_parser("select", help="Build a thread selection manifest.")
    select.add_argument("--db", default="~/chat_archive.sqlite")
    select.add_argument("--term", action="append", default=[])
    select.add_argument("--thread-id", action="append", default=[])
    select.add_argument("--thread-list", type=Path)
    select.add_argument("--limit", type=int, default=10)
    select.add_argument("--output", "-o", type=Path)

    plan = sub.add_parser("plan", help="Plan chunks for one thread.")
    plan.add_argument("--db", default="~/chat_archive.sqlite")
    plan.add_argument("--thread-id", required=True)
    plan.add_argument("--chunk-target-chars", type=int, default=DEFAULT_CHUNK_TARGET_CHARS)
    plan.add_argument("--chunk-hard-max-chars", type=int, default=DEFAULT_CHUNK_HARD_MAX_CHARS)
    plan.add_argument("--max-messages", type=int, default=DEFAULT_MAX_MESSAGES)
    plan.add_argument("--output", "-o", type=Path)

    run = sub.add_parser("run", help="Create a run DB and process queued chunks.")
    run.add_argument("--db", default="~/chat_archive.sqlite")
    run.add_argument("--run-db", type=Path)
    run.add_argument("--resume-run-id")
    run.add_argument("--selection", type=Path)
    run.add_argument("--term", action="append", default=[])
    run.add_argument("--thread-id", action="append", default=[])
    run.add_argument("--thread-list", type=Path)
    run.add_argument("--limit", type=int, default=10)
    run.add_argument("--mode", choices=["timeline", "implementation", "pnf-hybrid"], default="pnf-hybrid")
    run.add_argument("--no-pnf-first", action="store_true")
    run.add_argument("--chunk-target-chars", type=int, default=DEFAULT_CHUNK_TARGET_CHARS)
    run.add_argument("--chunk-hard-max-chars", type=int, default=DEFAULT_CHUNK_HARD_MAX_CHARS)
    run.add_argument("--max-messages", type=int, default=DEFAULT_MAX_MESSAGES)
    run.add_argument("--max-workers", type=int, default=4)
    run.add_argument("--progress", action="store_true")
    run.add_argument("--progress-interval", type=float, default=2.0)
    run.add_argument("--partial-flush-messages", type=int, default=1)
    run.add_argument("--message-hard-max-chars", type=int, default=DEFAULT_MESSAGE_HARD_MAX_CHARS)
    run.add_argument("--slice-target-chars", type=int, default=DEFAULT_SLICE_TARGET_CHARS)
    run.add_argument("--skip-tool-messages", dest="skip_tool_messages", action="store_true", default=True)
    run.add_argument("--include-tool-messages", dest="skip_tool_messages", action="store_false")
    run.add_argument("--fail-fast", action="store_true")
    run.add_argument("--compile-timeout-s", type=float)
    run.add_argument("--step-timeout-s", type=float)
    run.add_argument("--perf-matrix", type=Path)
    run.add_argument("--perf-matrix-dir", type=Path, default=DEFAULT_PERF_MATRIX_DIR)
    run.add_argument("--no-perf-matrix", action="store_true")
    run.add_argument("--perf-matrix-strict", action="store_true")
    run.add_argument("--output", "-o", type=Path)

    status = sub.add_parser("status", help="Print run progress.")
    status.add_argument("--run-db", type=Path, required=True)
    status.add_argument("--run-id", required=True)
    status.add_argument("--perf-matrix", type=Path)
    status.add_argument("--output", "-o", type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    if args.command == "select":
        thread_ids = list(args.thread_id)
        if args.thread_list:
            thread_ids.extend(read_thread_list(args.thread_list))
        _write_or_print(
            select_threads(Path(args.db), terms=args.term, thread_ids=thread_ids, limit=args.limit),
            args.output,
        )
        return 0
    if args.command == "plan":
        _write_or_print(
            plan_thread_chunks(
                Path(args.db),
                args.thread_id,
                target_chars=args.chunk_target_chars,
                hard_max_chars=args.chunk_hard_max_chars,
                max_messages=args.max_messages,
            ),
            args.output,
        )
        return 0
    if args.command == "run":
        source_db = Path(args.db)
        run_db = args.run_db or REPO_ROOT / ".autonomous-orchestrator" / "archive_runs" / "latest.sqlite"
        early_perf = PerfMatrixWriter(args.perf_matrix, strict=args.perf_matrix_strict) if args.perf_matrix and not args.no_perf_matrix else None
        if args.resume_run_id:
            init_run_db(run_db)
            con = sqlite3.connect(run_db)
            con.row_factory = sqlite3.Row
            try:
                run_row = con.execute("SELECT * FROM runs WHERE run_id = ?", (args.resume_run_id,)).fetchone()
                if run_row is None:
                    raise SystemExit(f"run not found: {args.resume_run_id}")
                run_id = args.resume_run_id
                source_db = Path(str(run_row["source_db"]))
                run_mode = str(run_row["mode"])
                run_pnf_first = bool(run_row["pnf_first"])
            finally:
                con.close()
        else:
            if args.selection:
                with StageTimer(early_perf, "select", source_db=str(source_db), selection_file=str(args.selection)):
                    selection = json.loads(args.selection.expanduser().read_text(encoding="utf-8"))
            else:
                thread_ids = list(args.thread_id)
                if args.thread_list:
                    thread_ids.extend(read_thread_list(args.thread_list))
                with StageTimer(early_perf, "select", source_db=str(source_db), term_count=len(args.term), thread_id_count=len(thread_ids)):
                    selection = select_threads(source_db, terms=args.term, thread_ids=thread_ids, limit=args.limit)
            perf_matrix = PerfMatrixWriter.for_run(
                args.perf_matrix,
                args.perf_matrix_dir,
                None,
                disabled=args.no_perf_matrix,
                strict=args.perf_matrix_strict,
            )
            with StageTimer(perf_matrix, "plan", source_db=str(source_db), run_db=str(run_db), selected_thread_count=len(selection.get("selected_threads", []))):
                run_id = create_run(
                    run_db,
                    source_db,
                    selection,
                    mode=args.mode,
                    pnf_first=not args.no_pnf_first,
                    target_chars=args.chunk_target_chars,
                    hard_max_chars=args.chunk_hard_max_chars,
                    max_messages=args.max_messages,
                )
            perf_matrix.record("plan", run_id=run_id, source_db=str(source_db), **_sqlite_metric_snapshot(run_db)) if perf_matrix else None
            run_mode = args.mode
            run_pnf_first = not args.no_pnf_first
        if args.resume_run_id:
            perf_matrix = PerfMatrixWriter.for_run(
                args.perf_matrix,
                args.perf_matrix_dir,
                run_id,
                disabled=args.no_perf_matrix,
                strict=args.perf_matrix_strict,
            )
        status = run_workers(
            run_db,
            source_db,
            run_id,
            mode=run_mode,
            pnf_first=run_pnf_first,
            max_workers=args.max_workers,
            progress=args.progress,
            progress_interval=args.progress_interval,
            partial_flush_messages=args.partial_flush_messages,
            message_hard_max_chars=args.message_hard_max_chars,
            slice_target_chars=args.slice_target_chars,
            skip_tool_messages=args.skip_tool_messages,
            fail_fast=args.fail_fast,
            compile_timeout_s=args.compile_timeout_s,
            step_timeout_s=args.step_timeout_s,
            perf_matrix=perf_matrix,
        )
        status["run_db"] = str(run_db)
        if perf_matrix and perf_matrix.path:
            status["perf_matrix"] = str(perf_matrix.path)
        _write_or_print(status, args.output)
        return 0
    if args.command == "status":
        _write_or_print(run_status(args.run_db, args.run_id, perf_matrix_path=args.perf_matrix), args.output)
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
