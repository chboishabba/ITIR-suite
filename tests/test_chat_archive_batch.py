from __future__ import annotations

import json
import importlib.util
import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))


def _load_script_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


batch = _load_script_module("itir_chat_archive_batch", REPO_ROOT / "scripts" / "chat_archive_batch.py")
receipt_exporter = _load_script_module("itir_export_pnf_agda_receipts", REPO_ROOT / "scripts" / "export_pnf_agda_receipts.py")


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
        CREATE VIRTUAL TABLE messages_fts USING fts5(text);
        CREATE TABLE messages_fts_docids (
          rowid INTEGER PRIMARY KEY,
          message_id TEXT NOT NULL
        );
        """
    )
    rows = [
        (
            "a1",
            "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "chatgpt",
            "acct",
            "2026-06-01T00:00:00Z",
            "user",
            "Dart resolver is a worker, not a planner.",
            "Dart Resolver",
            "src",
            "11111111-1111-1111-1111-111111111111",
            "sa1",
            None,
            None,
            None,
        ),
        (
            "a2",
            "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "chatgpt",
            "acct",
            "2026-06-01T00:01:00Z",
            "assistant",
            "We should chunk the archive at turn boundaries before PNF.",
            "Dart Resolver",
            "src",
            "11111111-1111-1111-1111-111111111111",
            "sa2",
            None,
            None,
            None,
        ),
        (
            "a3",
            "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "chatgpt",
            "acct",
            "2026-06-01T00:02:00Z",
            "user",
            "The implementation worker needs receipts.",
            "Dart Resolver",
            "src",
            "11111111-1111-1111-1111-111111111111",
            "sa3",
            None,
            None,
            None,
        ),
        (
            "b1",
            "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "chatgpt",
            "acct",
            "2026-06-02T00:00:00Z",
            "user",
            "Timeline documentation should order unrelated threads.",
            "Timeline Docs",
            "src",
            "22222222-2222-2222-2222-222222222222",
            "sb1",
            None,
            None,
            None,
        ),
        (
            "b2",
            "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "chatgpt",
            "acct",
            "2026-06-02T00:01:00Z",
            "assistant",
            "StatiBaker can observe process receipts.",
            "Timeline Docs",
            "src",
            "22222222-2222-2222-2222-222222222222",
            "sb2",
            None,
            None,
            None,
        ),
    ]
    con.executemany(
        """
        INSERT INTO messages (
          message_id, canonical_thread_id, platform, account_id, ts, role, text,
          title, source_id, source_thread_id, source_message_id, source_path,
          source_bucket, provenance_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )
    for rowid, (message_id, *_rest) in enumerate(rows, start=1):
        text = _rest[5]
        con.execute("INSERT INTO messages_fts(rowid, text) VALUES (?, ?)", (rowid, text))
        con.execute("INSERT INTO messages_fts_docids(rowid, message_id) VALUES (?, ?)", (rowid, message_id))
    con.commit()
    con.close()


def test_select_threads_uses_fts_and_explicit_thread_ids(tmp_path: Path) -> None:
    db_path = tmp_path / "archive.sqlite"
    _make_archive(db_path)

    manifest = batch.select_threads(
        db_path,
        terms=["dart"],
        thread_ids=["bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"],
        limit=10,
    )

    ids = [row["canonical_thread_id"] for row in manifest["selected_threads"]]
    assert ids == [
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
    ]
    assert manifest["selected_threads"][0]["selection_reason"] == "fts_term"
    assert manifest["selected_threads"][0]["hit_count"] == 1
    assert manifest["selected_threads"][1]["selection_reason"] == "explicit_thread_id"


def test_plan_thread_chunks_respects_message_boundaries(tmp_path: Path) -> None:
    db_path = tmp_path / "archive.sqlite"
    _make_archive(db_path)

    plan = batch.plan_thread_chunks(
        db_path,
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        target_chars=1400,
        hard_max_chars=1400,
        max_messages=2,
    )

    assert plan["message_count"] == 3
    assert [item["message_count"] for item in plan["chunk_plan"]] == [2, 1]
    assert plan["chunk_plan"][0]["start_message_index"] == 1
    assert plan["chunk_plan"][0]["end_message_index"] == 2
    assert plan["chunk_plan"][1]["start_message_index"] == 3


def test_sqlite_queue_is_parallel_across_threads_but_sequential_per_thread(tmp_path: Path) -> None:
    db_path = tmp_path / "archive.sqlite"
    run_db = tmp_path / "run.sqlite"
    _make_archive(db_path)
    selection = batch.select_threads(
        db_path,
        terms=[],
        thread_ids=[
            "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        ],
        limit=10,
    )
    run_id = batch.create_run(
        run_db,
        db_path,
        selection,
        mode="pnf-hybrid",
        pnf_first=True,
        target_chars=700,
        hard_max_chars=700,
        max_messages=1,
    )

    first = batch.claim_next_chunk(run_db, run_id, "w1")
    second = batch.claim_next_chunk(run_db, run_id, "w2")
    assert first is not None
    assert second is not None
    assert first.canonical_thread_id != second.canonical_thread_id

    third = batch.claim_next_chunk(run_db, run_id, "w3")
    assert third is None


def test_run_workers_persists_pnf_state_atoms_and_timeline(tmp_path: Path) -> None:
    db_path = tmp_path / "archive.sqlite"
    run_db = tmp_path / "run.sqlite"
    _make_archive(db_path)
    selection = batch.select_threads(
        db_path,
        terms=["dart"],
        thread_ids=[],
        limit=1,
    )
    run_id = batch.create_run(
        run_db,
        db_path,
        selection,
        mode="pnf-hybrid",
        pnf_first=True,
        target_chars=1400,
        hard_max_chars=1400,
        max_messages=2,
    )

    status = batch.run_workers(
        run_db,
        db_path,
        run_id,
        mode="pnf-hybrid",
        pnf_first=True,
        max_workers=2,
    )

    assert status["progress"]["completed_chunks"] == status["progress"]["total_chunks"]
    con = sqlite3.connect(run_db)
    try:
        delta_count = con.execute("SELECT COUNT(*) FROM conversation_vm_deltas").fetchone()[0]
        state_count = con.execute("SELECT COUNT(*) FROM conversation_vm_states").fetchone()[0]
        atom_count = con.execute("SELECT COUNT(*) FROM pnf_atoms").fetchone()[0]
        event_count = con.execute("SELECT COUNT(*) FROM timeline_events").fetchone()[0]
    finally:
        con.close()
    assert delta_count == 3
    assert state_count == 2
    assert atom_count > 0
    assert event_count == 3


def test_run_workers_persists_pnf_receipts_and_exporter_cases(tmp_path: Path) -> None:
    db_path = tmp_path / "archive.sqlite"
    run_db = tmp_path / "run.sqlite"
    _make_archive(db_path)
    selection = batch.select_threads(
        db_path,
        terms=["dart"],
        thread_ids=[],
        limit=1,
    )
    run_id = batch.create_run(
        run_db,
        db_path,
        selection,
        mode="pnf-hybrid",
        pnf_first=True,
        target_chars=1400,
        hard_max_chars=1400,
        max_messages=2,
    )

    batch.run_workers(
        run_db,
        db_path,
        run_id,
        mode="pnf-hybrid",
        pnf_first=True,
        max_workers=1,
    )

    con = sqlite3.connect(run_db)
    try:
        emission_count = con.execute("SELECT COUNT(*) FROM pnf_emission_receipts").fetchone()[0]
        residual_rows = con.execute(
            "SELECT relation, residual_level, status FROM pnf_residual_receipts"
        ).fetchall()
    finally:
        con.close()

    assert emission_count > 0
    assert ("classification-tension", "contradiction", "available_without_hecke_candidate_pool") in residual_rows
    payload = receipt_exporter.load_receipt_cases(run_db, run_id=run_id)
    assert payload["case_count"] >= 1
    assert any(case["relation"] == "classification-tension" for case in payload["cases"])
    assert receipt_exporter.agda_module(payload, "RuntimePNFReceiptExport").startswith("module RuntimePNFReceiptExport where")


def test_run_workers_emits_sidecar_perf_matrix_rows(tmp_path: Path) -> None:
    db_path = tmp_path / "archive.sqlite"
    run_db = tmp_path / "run.sqlite"
    perf_path = tmp_path / "perf.jsonl"
    _make_archive(db_path)
    selection = batch.select_threads(db_path, terms=["dart"], thread_ids=[], limit=1)
    run_id = batch.create_run(
        run_db,
        db_path,
        selection,
        mode="pnf-hybrid",
        pnf_first=True,
        target_chars=1400,
        hard_max_chars=1400,
        max_messages=2,
    )

    writer = batch.PerfMatrixWriter(perf_path)
    batch.run_workers(
        run_db,
        db_path,
        run_id,
        mode="pnf-hybrid",
        pnf_first=True,
        max_workers=1,
        perf_matrix=writer,
    )

    rows = [json.loads(line) for line in perf_path.read_text(encoding="utf-8").splitlines()]
    stages = {row["stage"] for row in rows}
    assert {"claim", "load", "slice_plan", "resume", "compile", "reduce", "flush", "final_persist"} <= stages
    assert all(row["schema"] == batch.PERF_MATRIX_SCHEMA for row in rows)


def test_run_status_can_summarize_perf_matrix(tmp_path: Path) -> None:
    db_path = tmp_path / "archive.sqlite"
    run_db = tmp_path / "run.sqlite"
    perf_path = tmp_path / "perf.jsonl"
    _make_archive(db_path)
    selection = batch.select_threads(db_path, terms=["dart"], thread_ids=[], limit=1)
    run_id = batch.create_run(
        run_db,
        db_path,
        selection,
        mode="pnf-hybrid",
        pnf_first=True,
        target_chars=1400,
        hard_max_chars=1400,
        max_messages=2,
    )
    batch.PerfMatrixWriter(perf_path).record("select", run_id=run_id)

    status = batch.run_status(run_db, run_id, perf_matrix_path=perf_path)

    assert status["perf_matrix"]["row_count"] == 1
    assert status["perf_matrix"]["stage_counts"]["select"] == 1


def test_interrupted_chunk_keeps_message_outputs_and_resumes(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "archive.sqlite"
    run_db = tmp_path / "run.sqlite"
    _make_archive(db_path)
    selection = batch.select_threads(
        db_path,
        terms=["dart"],
        thread_ids=[],
        limit=1,
    )
    run_id = batch.create_run(
        run_db,
        db_path,
        selection,
        mode="pnf-hybrid",
        pnf_first=True,
        target_chars=10_000,
        hard_max_chars=10_000,
        max_messages=10,
    )

    def interrupted_compile(turn):
        if str(turn["turn_id"]) == "a2":
            raise KeyboardInterrupt("simulated stop")
        return {"id": f"delta-{turn['turn_id']}", "predicate_atoms": []}

    monkeypatch.setattr(batch, "compile_turn", interrupted_compile)
    monkeypatch.setattr(batch, "step_state", lambda state, delta: {**state, "last_delta_id": delta["id"]})

    claim = batch.claim_next_chunk(run_db, run_id, "w1")
    assert claim is not None
    try:
        batch.process_chunk(run_db, db_path, claim, mode="pnf-hybrid", pnf_first=True)
    except KeyboardInterrupt:
        pass

    con = sqlite3.connect(run_db)
    try:
        assert con.execute("SELECT COUNT(*) FROM message_outputs").fetchone()[0] == 1
        assert con.execute("SELECT status FROM chunks WHERE chunk_id = ?", (claim.chunk_id,)).fetchone()[0] == "partial"
        assert con.execute("SELECT COUNT(*) FROM chunk_progress").fetchone()[0] == 1
    finally:
        con.close()

    monkeypatch.setattr(batch, "compile_turn", lambda turn: {"id": f"delta-{turn['turn_id']}", "predicate_atoms": []})
    resumed = batch.claim_next_chunk(run_db, run_id, "w2")
    assert resumed is not None
    assert resumed.chunk_id == claim.chunk_id
    batch.process_chunk(run_db, db_path, resumed, mode="pnf-hybrid", pnf_first=True)

    status = batch.run_status(run_db, run_id)
    assert status["progress"]["partial_rows"] == 3
    assert status["status_counts"]["done"]["count"] == 1
    con = sqlite3.connect(run_db)
    try:
        rows = con.execute(
            "SELECT message_index, slice_index FROM message_outputs ORDER BY message_index, slice_index"
        ).fetchall()
    finally:
        con.close()
    assert rows == [(1, 0), (2, 0), (3, 0)]


def test_oversized_messages_are_sliced_with_source_spans(tmp_path: Path) -> None:
    db_path = tmp_path / "archive.sqlite"
    run_db = tmp_path / "run.sqlite"
    _make_archive(db_path)
    long_text = "abcdefghijklmnopqrstuvwxyz"
    con = sqlite3.connect(db_path)
    try:
        con.execute("UPDATE messages SET text = ? WHERE message_id = 'a1'", (long_text,))
        con.commit()
    finally:
        con.close()
    selection = batch.select_threads(
        db_path,
        terms=[],
        thread_ids=["aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"],
        limit=1,
    )
    run_id = batch.create_run(
        run_db,
        db_path,
        selection,
        mode="pnf-hybrid",
        pnf_first=False,
        target_chars=10_000,
        hard_max_chars=10_000,
        max_messages=10,
    )

    claim = batch.claim_next_chunk(run_db, run_id, "w1")
    assert claim is not None
    batch.process_chunk(
        run_db,
        db_path,
        claim,
        mode="pnf-hybrid",
        pnf_first=False,
        message_hard_max_chars=10,
        slice_target_chars=7,
    )

    con = sqlite3.connect(run_db)
    try:
        rows = con.execute(
            """
            SELECT slice_index, slice_count, source_start_char, source_end_char, char_count
            FROM message_outputs
            WHERE message_id = 'a1'
            ORDER BY slice_index
            """
        ).fetchall()
    finally:
        con.close()
    assert rows == [(0, 4, 0, 7, 7), (1, 4, 7, 14, 7), (2, 4, 14, 21, 7), (3, 4, 21, 26, 5)]


def test_tool_messages_are_skipped_by_default_and_recorded(tmp_path: Path) -> None:
    db_path = tmp_path / "archive.sqlite"
    run_db = tmp_path / "run.sqlite"
    _make_archive(db_path)
    con = sqlite3.connect(db_path)
    try:
        con.execute("UPDATE messages SET role = 'tool' WHERE message_id = 'a2'")
        con.commit()
    finally:
        con.close()
    selection = batch.select_threads(
        db_path,
        terms=[],
        thread_ids=["aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"],
        limit=1,
    )
    run_id = batch.create_run(
        run_db,
        db_path,
        selection,
        mode="pnf-hybrid",
        pnf_first=False,
        target_chars=10_000,
        hard_max_chars=10_000,
        max_messages=10,
    )

    claim = batch.claim_next_chunk(run_db, run_id, "w1")
    assert claim is not None
    batch.process_chunk(run_db, db_path, claim, mode="pnf-hybrid", pnf_first=False)

    con = sqlite3.connect(run_db)
    try:
        skipped = con.execute("SELECT message_id, reason FROM skipped_inputs").fetchall()
        statuses = con.execute(
            "SELECT message_id, status FROM message_outputs ORDER BY message_index"
        ).fetchall()
    finally:
        con.close()
    assert skipped == [("a2", "tool_message")]
    assert statuses == [("a1", "processed"), ("a2", "skipped"), ("a3", "processed")]


def test_read_thread_list_accepts_json_manifest(tmp_path: Path) -> None:
    manifest = tmp_path / "threads.json"
    manifest.write_text(
        json.dumps(
            {
                "selected_threads": [
                    {"canonical_thread_id": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"},
                    {"thread_id": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"},
                ]
            }
        ),
        encoding="utf-8",
    )

    assert batch.read_thread_list(manifest) == [
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
    ]
