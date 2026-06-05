#!/usr/bin/env python3
"""Export receipt-backed PNF residual cases from a chat archive batch DB."""

from __future__ import annotations

import argparse
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


def _json_dumps(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=True, sort_keys=True, indent=2)


def load_receipt_cases(
    run_db: Path,
    *,
    run_id: str,
    canonical_thread_id: str | None = None,
) -> dict[str, Any]:
    con = sqlite3.connect(f"file:{run_db.expanduser()}?mode=ro", uri=True)
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
        payload = json.loads(row["payload_json"])
        case = {
            "residual_receipt_id": row["residual_receipt_id"],
            "canonical_thread_id": row["canonical_thread_id"],
            "residual_id": row["residual_id"],
            "relation": row["relation"],
            "residual_level": row["residual_level"],
            "status": row["status"],
            "left_emission_receipt": json.loads(row["left_payload_json"]) if row["left_payload_json"] else None,
            "right_emission_receipt": json.loads(row["right_payload_json"]) if row["right_payload_json"] else None,
            "payload": payload,
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


def agda_module(payload: dict[str, Any], module_name: str) -> str:
    contradiction_count = sum(1 for item in payload["cases"] if item.get("residual_level") == "contradiction")
    no_typed_meet_count = sum(1 for item in payload["cases"] if item.get("residual_level") == "no_typed_meet")
    return "\n".join(
        [
            f"module {module_name} where",
            "",
            "open import Agda.Builtin.Nat",
            "",
            "-- Generated evidence summary. Full runtime payload is emitted as JSON by the exporter.",
            f"runtimePNFCaseCount : Nat",
            f"runtimePNFCaseCount = {int(payload['case_count'])}",
            "",
            "runtimeContradictionCount : Nat",
            f"runtimeContradictionCount = {contradiction_count}",
            "",
            "runtimeNoTypedMeetCount : Nat",
            f"runtimeNoTypedMeetCount = {no_typed_meet_count}",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-db", required=True, type=Path)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--canonical-thread-id")
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--agda-out", type=Path)
    parser.add_argument("--module-name", default="RuntimePNFReceiptExport")
    args = parser.parse_args()

    payload = load_receipt_cases(args.run_db, run_id=args.run_id, canonical_thread_id=args.canonical_thread_id)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(_json_dumps(payload) + "\n", encoding="utf-8")
    else:
        print(_json_dumps(payload))
    if args.agda_out:
        args.agda_out.parent.mkdir(parents=True, exist_ok=True)
        args.agda_out.write_text(agda_module(payload, args.module_name), encoding="utf-8")
    return 0 if payload["diagnostic_count"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
