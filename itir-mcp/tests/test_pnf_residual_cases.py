from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from itir_mcp.registry import build_default_registry


def _make_run_db(path: Path) -> None:
    with sqlite3.connect(path) as db:
        db.executescript(
            """
            CREATE TABLE pnf_emission_receipts (
                run_id TEXT NOT NULL,
                receipt_id TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                PRIMARY KEY (run_id, receipt_id)
            );
            CREATE TABLE pnf_residual_receipts (
                run_id TEXT NOT NULL,
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
            """
        )
        db.executemany(
            "INSERT INTO pnf_emission_receipts VALUES (?, ?, ?)",
            [
                ("run-1", "left", json.dumps({"receipt": "left"})),
                ("run-1", "right", json.dumps({"receipt": "right"})),
            ],
        )
        db.execute(
            "INSERT INTO pnf_residual_receipts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                "run-1", "thread-1", "residual-receipt", "residual-1", "left", "right",
                "contradiction", "classification-tension", "available", json.dumps({"id": "residual-1"}),
            ),
        )


def test_residual_cases_exposes_existing_receipt_export_read_only(tmp_path: Path) -> None:
    run_db = tmp_path / "run.sqlite"
    _make_run_db(run_db)

    result = build_default_registry().invoke(
        "itir.pnf.residual_cases",
        {"run_db": str(run_db), "run_id": "run-1", "canonical_thread_id": "thread-1"},
    )

    assert result["ok"] is True
    payload = result["result"]
    assert payload["schema"] == "itir.pnf_agda_receipt_export.v0_1"
    assert payload["case_count"] == 1
    assert payload["diagnostic_count"] == 0
    assert payload["cases"][0]["residual_level"] == "contradiction"
    assert payload["cases"][0]["left_emission_receipt"] == {"receipt": "left"}
