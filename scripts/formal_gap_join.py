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
    # SLR stores sha256:<hex>; the external proof router uses the exact
    # statement_digest as part of its primary key. Do not strip the prefix
    # or case-normalize a persisted digest into a different demand.
    hex_part = digest.removeprefix("sha256:")
    if not (len(hex_part) == 64 and all(x in "0123456789abcdefABCDEF" for x in hex_part)):
        raise ValueError("statement_digest must be SHA256 hex, optionally prefixed sha256:")
    limit = item.get("limit", 10)
    if type(limit) is not int or not 1 <= limit <= MAX_LIMIT:
        raise ValueError("limit must be 1..50")
    return {"obligation_ref": identity, "query": query,
            "target_prover": target, "statement_digest": digest,
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
             route: Callable[[Mapping[str, object]], dict], *,
             require_binding: bool = False) -> dict:
    row = normalize(obligation)
    search = inspect({"action": "discover", "query": row["query"], "limit": row["limit"]})
    discovery = _safe_candidate(search, "discover")
    routed = route({"action": "proof_route_for_obligation",
                    "query": row["query"],
                    "external_obligation_ref": row["obligation_ref"],
                    "demand_ref": row["demand_ref"],
                    "statement_digest": row["statement_digest"],
                    "target_prover": row["target_prover"], "limit": row["limit"]})
    route_receipt = _safe_candidate(routed, "proof_route_for_obligation")
    expected_binding = {"demand_ref": row["demand_ref"],
                        "external_obligation_ref": row["obligation_ref"],
                        "statement_digest": row["statement_digest"]}
    binding = routed.get("demand_binding")
    if (require_binding or binding is not None) and binding != expected_binding:
        raise ValueError("Formal route returned a foreign or unbound demand")
    return {
        "schema": "itir.formal.gap-join.v1",
        "obligation_ref": row["obligation_ref"],
        "demand_ref": row["demand_ref"],
        "statement_digest": row["statement_digest"],
        "target_prover": row["target_prover"],
        "query_digest": _fingerprint(row["query"]),
        "discovery": discovery,
        "route": route_receipt, "demand_binding": binding,
        "candidate_only": True,
        "establishes_proof": False,
        "discharges_obligation": False,
    }


def run(inputs: list[Mapping[str, object]],
        inspect: Callable[[Mapping[str, object]], dict],
        route: Callable[[Mapping[str, object]], dict], *,
        require_binding: bool = False) -> list[dict]:
    if len(inputs) > MAX_INPUT:
        raise ValueError("Input exceeds bounded batch")
    # Validate the entire batch before any routing side effect in the existing
    # preflight index. Multiple distinct demands may belong to one obligation.
    normalized = [normalize(item) for item in inputs]
    references = [row["demand_ref"] for row in normalized]
    if len(set(references)) != len(references):
        raise ValueError("Duplicate demand_ref")
    return [join_one(row, inspect, route, require_binding=require_binding)
            for row in sorted(normalized, key=lambda x: (x["obligation_ref"], x["demand_ref"]))]


def bind_mabo_queries(queries: list[Mapping[str, object]], receipt: Mapping[str, Any],
                      obligation_ref: str) -> tuple[list[dict], dict[str, dict]]:
    """Select actual native demands; a search hint cannot alter their identity.

    The caller supplies only query text and limit. Paid or ancestry-incomplete
    demands stay held. This is a routing preparation, never formal payment.
    """
    if (receipt.get("schema") != "slr.mabo-formal-demand-readback.v1"
            or receipt.get("obligation_ref") != obligation_ref
            or receipt.get("candidate_only") is not True
            or receipt.get("establishes_proof") is not False
            or receipt.get("discharges_obligation") is not False
            or receipt.get("writes_database") is not False
            or not isinstance(receipt.get("demands"), list)):
        raise ValueError("Invalid native Mabo demand receipt")
    rows = receipt["demands"]
    if any(not isinstance(r, dict) or not isinstance(r.get("demand_ref"), str)
           or not r["demand_ref"] for r in rows):
        raise ValueError("Invalid native demand coordinate")
    by_ref = {r["demand_ref"]: r for r in rows}
    if len(by_ref) != len(rows) or len(queries) > MAX_INPUT:
        raise ValueError("Duplicate demand or bounded batch exceeded")
    bound, provenance = [], {}
    for request in queries:
        if set(request) - {"demand_ref", "query", "limit"}:
            raise ValueError("Mabo queries cannot override native demand coordinates")
        ref = _nonempty(request, "demand_ref")
        if ref in provenance or ref not in by_ref:
            raise ValueError("Duplicate or unknown native demand")
        row = by_ref[ref]
        if (row.get("obligation_ref") != obligation_ref
                or row.get("residual_ref") != receipt.get("residual_ref")
                or row.get("candidate_only") is not True
                or row.get("establishes_proof") is not False
                or row.get("discharges_obligation") is not False
                or row.get("all_source_refs_reviewed_in_graph") is not True
                or row.get("formal_premise_evidence_refs") != []):
            raise ValueError("Native demand is held, already paid, or foreign")
        bound.append(normalize({
            "obligation_ref": obligation_ref, "demand_ref": ref,
            "statement_digest": row.get("statement_digest"),
            "target_prover": row.get("target_prover"),
            "query": _nonempty(request, "query"), "limit": request.get("limit", 10)}))
        provenance[ref] = {
            "native_readback_digest": _fingerprint(receipt),
            "native_demand": row,
            "query_is_operator_search_hint": True,
            "independent_recertification_performed": False,
        }
    return bound, provenance


def _tools():
    from itir_mcp.formal_tools import get_formal_tools
    operations = {spec.name: invoke for spec, invoke in get_formal_tools()}
    return operations["itir.formal.inspect"], operations["itir.formal.route"]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--mabo-obligation", help="Reopen native Mabo demands; input rows contain demand_ref, query, limit only")
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
    provenance = {}
    if args.mabo_obligation:
        from itir_mcp.native_relational_tools import inspect_relational_family
        native = inspect_relational_family({"action": "mabo_formal_demands",
                                            "obligation_ref": args.mabo_obligation})
        inputs, provenance = bind_mabo_queries(inputs, native["native_receipt"], args.mabo_obligation)
    inspect, route = _tools()
    result = run(inputs, inspect, route, require_binding=bool(args.mabo_obligation))
    for row in result:
        if args.mabo_obligation:
            row["native_mabo_provenance"] = provenance[row["demand_ref"]]
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
