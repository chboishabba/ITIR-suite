#!/usr/bin/env python3
"""Export receipt-backed PNF residual cases from a chat archive batch DB."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
ITIR_MCP_SRC = REPO_ROOT / "itir-mcp" / "src"
if str(ITIR_MCP_SRC) not in sys.path:
    sys.path.insert(0, str(ITIR_MCP_SRC))

from itir_mcp.pnf_residual_cases import load_receipt_cases  # noqa: E402


def _json_dumps(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=True, sort_keys=True, indent=2)


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
            "runtimePNFCaseCount : Nat",
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
