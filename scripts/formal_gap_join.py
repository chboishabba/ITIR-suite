#!/usr/bin/env python3
"""Deterministic, read-only formal gap join over existing itir.formal tools.

Consumes newline-delimited obligation requests, emits newline-delimited
candidate-only, source-bound inspect/route receipts. This is NOT an LLM agent,
theorem prover, database, indexer or source-translator.

Example:
  PYTHONPATH=itir-mcp/src python scripts/formal_gap_join.py \
      --input /tmp/obligations.jsonl --output /tmp/gap-candidates.jsonl

Default provider delegates to ITIR's existing DashiAgdaMcpTools. All outputs
are explicitly non-certifying. A separate kernel referee is needed to pay
any obligation. No external network or third-party publication is performed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Callable, Mapping, Any

MAX_INPUT = 500
MAX_LIMIT = 50


def _fingerprint(value: object) -> str:
    data = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def _nonempty(item: Mapping[str, object], name: str) -> str:
    value = item.get(name)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} required")
    return value.strip()


def normalize(item: Mapping[str, object]) -> dict[str, object]:
    identity = _nonempty(item, "obligation_ref")
    query = _nonempty(item, "query")
    target = _nonempty(item, "target_prover").lower()
    if target not in {"agda", "lean"}:
        raise ValueError("target_prover must be agda or lean")
    digest = _nonempty(item, "statement_digest")
    if not (len(digest) == 64 and all(x in "0123456789abcdefABCDEF" for x in digest)):
        raise ValueError("statement_digest must be a SHA256 hex digest")
    limit = item.get("limit", 10)
    if type(limit) is not int or not 1 <= limit <= MAX_LIMIT:
        raise ValueError("limit must be 1..50")
    return {"obligation_ref": identity, "query": query,
            "target_prover": target, "statement_digest": digest.lower(),
            "limit": limit, "demand_ref": str(item.get("demand_ref") or identity)}


def _safe_candidate(value: Any, label: str) -> dict[str, object]:
    """Never trust an external status bit, even from a caller-supplied fixture."""
    if not isinstance(value, dict):
        raise ValueError(f"{label} returned non-object")
    if value.get("candidate_only") is not True or value.get("establishes_proof") is not False:
        raise ValueError(f"{label} returned non-candidate or proof-promoting evidence")
    return {"authority_kind": str(value.get("authority_kind", "unknown")),
            "evidence_digest": _fingerprint(value),
            "candidate_only": True, "establishes_proof": False,
            "summary": value.get("summary")}


def join_one(obligation: Mapping[str, object],
             inspect: Callable[[Mapping[str, object]], dict],
             route: Callable[[Mapping[str, object]], dict]) -> dict:
    row = normalize(obligation)
    search = inspect({"action": "discover", "query": row["query"], "limit": row["limit"]})
    routed = route({"action": "proof_route_for_obligation",
                    "query": row["query"],
                    "external_obligation_ref": row["obligation_ref"],
                    "demand_ref": row["demand_ref"],
                    "statement_digest": row["statement_digest"],
                    "target_prover": row["target_prover"]})
    return {
        "schema": "itir.formal.gap-join.v1",
        "obligation_ref": row["obligation_ref"],
        "statement_digest": row["statement_digest"],
        "target_prover": row["target_prover"],
        "query_digest": _fingerprint(row["query"]),
        "discovery": _safe_candidate(search, "discover"),
        "route": _safe_candidate(routed, "proof_route_for_obligation"),
        "candidate_only": True,
        "establishes_proof": False,
        "discharges_obligation": False,
    }


def run(inputs: list[Mapping[str, object]],
        inspect: Callable[[Mapping[str, object]], dict],
        route: Callable[[Mapping[str, object]], dict]) -> list[dict]:
    if len(inputs) > MAX_INPUT:
        raise ValueError("Input exceeds bounded batch")
    references = set()
    rows = []
    for item in inputs:
        row = join_one(item, inspect, route)
        key = row["obligation_ref"]
        if key in references:
            raise ValueError("Duplicate obligation_ref")
        references.add(key)
        rows.append(row)
    return sorted(rows, key=lambda item: item["obligation_ref"])


def _tools():
    from itir_mcp.formal_tools import get_formal_tools
    operations = {spec.name: invoke for spec, invoke in get_formal_tools()}
    return operations["itir.formal.inspect"], operations["itir.formal.route"]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.input.resolve() == args.output.resolve():
        parser.error("input and output must differ")
    inputs = []
    for line, value in enumerate(args.input.read_text(encoding="utf-8").splitlines(), 1):
        if not value.strip():
            continue
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON at line {line}") from exc
        if not isinstance(parsed, dict):
            raise ValueError(f"Expected JSON object at line {line}")
        inputs.append(parsed)
    inspect, route = _tools()
    result = run(inputs, inspect, route)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("".join(json.dumps(item, sort_keys=True) + "\n"
                                   for item in result), encoding="utf-8")
    print(json.dumps({"schema": "itir.formal.gap-join.v1",
                      "obligations": len(result), "proved": 0,
                      "candidate_only": True, "output": str(args.output)},
                     sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
