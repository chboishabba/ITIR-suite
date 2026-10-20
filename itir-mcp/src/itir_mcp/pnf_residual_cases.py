"""Read-only receipt-backed residual-case projection for formal consumers."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any


SCHEMA = "itir.pnf_agda_receipt_export.v0_1"
REQUIRED_RESIDUAL_FIELDS = (
    "left_receipt_id",
    "right_receipt_id",
    "residual_level",
    "relation",
)


def load_receipt_cases(
    run_db: Path | str,
    *,
    run_id: str,
    canonical_thread_id: str | None = None,
) -> dict[str, Any]:
    """Project complete residual cases from one batch run without mutation."""
    path = Path(run_db).expanduser()
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    try:
        where = ["r.run_id = ?"]
        params: list[Any] = [run_id]
        if canonical_thread_id:
            where.append("r.canonical_thread_id = ?")
            params.append(canonical_thread_id)
        rows = con.execute(
            f"""
            SELECT
              r.*,
              l.payload_json AS left_payload_json,
              rr.payload_json AS right_payload_json
            FROM pnf_residual_receipts r
            LEFT JOIN pnf_emission_receipts l
              ON l.run_id = r.run_id AND l.receipt_id = r.left_receipt_id
            LEFT JOIN pnf_emission_receipts rr
              ON rr.run_id = r.run_id AND rr.receipt_id = r.right_receipt_id
            WHERE {' AND '.join(where)}
            ORDER BY r.canonical_thread_id, r.residual_receipt_id
            """,
            params,
        ).fetchall()
    finally:
        con.close()

    cases = []
    diagnostics = []
    for row in rows:
        missing = [field for field in REQUIRED_RESIDUAL_FIELDS if not row[field]]
        if row["left_payload_json"] is None:
            missing.append("leftEmissionReceiptPayload")
        if row["right_payload_json"] is None:
            missing.append("rightEmissionReceiptPayload")
        case = {
            "residual_receipt_id": row["residual_receipt_id"],
            "canonical_thread_id": row["canonical_thread_id"],
            "residual_id": row["residual_id"],
            "relation": row["relation"],
            "residual_level": row["residual_level"],
            "status": row["status"],
            "left_emission_receipt": json.loads(row["left_payload_json"]) if row["left_payload_json"] else None,
            "right_emission_receipt": json.loads(row["right_payload_json"]) if row["right_payload_json"] else None,
            "payload": json.loads(row["payload_json"]),
        }
        if missing:
            diagnostics.append(
                {
                    "residual_receipt_id": row["residual_receipt_id"],
                    "missing_fields": sorted(set(missing)),
                    "status": "diagnostic",
                }
            )
        else:
            cases.append(case)
    return {
        "schema": SCHEMA,
        "run_id": run_id,
        "canonical_thread_id": canonical_thread_id,
        "case_count": len(cases),
        "diagnostic_count": len(diagnostics),
        "cases": cases,
        "diagnostics": diagnostics,
    }
