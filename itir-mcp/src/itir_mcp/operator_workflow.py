"""AO-OP-1: bounded, read-only composition of existing canonical evidence producers."""
from __future__ import annotations

import hashlib
import json
from typing import Any, Callable, Mapping

from .frontier_evidence import build_frontier
from .governed_revival import governed_handoff, operation_review
from .pnf_work_packet_provider import build_work_packet

VERSION = "itir.ao.operator_workflow.v1"
MAX_ITEMS = 8
MAX_REF_CHARS = 256
MAX_TASK_CHARS = 512
MAX_OUTPUT_CHARS = 24000
RECEIPT_FIELDS = ("formal_gap_receipts", "repo_receipts", "pnf_receipts", "evidence_refs")
ALLOWED = {"archive_db", "candidates", "receipt_db", "operation_receipts", "max_items"}
CANDIDATE_FIELDS = {"canonical_thread_id", "task_atom", "kind", "typed_refs",
                    "formal_gap_receipts", "repo_receipts", "pnf_receipts", "evidence_refs",
                    "operation_status", "operation_id"}


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                   ensure_ascii=True).encode("utf-8")).hexdigest()


def _string(value: Any, limit: int = MAX_REF_CHARS) -> bool:
    return isinstance(value, str) and 0 < len(value.strip()) <= limit and not any(
        ord(c) < 32 for c in value
    )


def _validate(payload: Mapping[str, Any]) -> tuple[list[dict[str, Any]], int]:
    if not isinstance(payload, Mapping) or set(payload) - ALLOWED:
        raise ValueError("unknown operator workflow fields")
    if not _string(payload.get("archive_db"), 4096):
        raise ValueError("explicit canonical archive locator required")
    max_items = payload.get("max_items", MAX_ITEMS)
    if type(max_items) is not int or not 1 <= max_items <= MAX_ITEMS:
        raise ValueError("max_items must be 1..8")
    rows = payload.get("candidates")
    if not isinstance(rows, list) or not 1 <= len(rows) <= 64:
        raise ValueError("candidates must contain 1..64 explicit selectors")
    operations = payload.get("operation_receipts", False)
    if type(operations) is not bool:
        raise ValueError("operation_receipts must be boolean")
    if operations and not _string(payload.get("receipt_db"), 4096):
        raise ValueError("explicit receipt locator required")
    if "receipt_db" in payload and not _string(payload["receipt_db"], 4096):
        raise ValueError("invalid receipt locator")
    seen: set[str] = set()
    clean: list[dict[str, Any]] = []
    for item in rows:
        if not isinstance(item, dict) or set(item) - CANDIDATE_FIELDS:
            raise ValueError("unknown candidate fields")
        tid, task = item.get("canonical_thread_id"), item.get("task_atom")
        if not _string(tid) or tid in seen or not _string(task, MAX_TASK_CHARS):
            raise ValueError("unique canonical thread and bounded explicit task required")
        seen.add(tid)
        for key in RECEIPT_FIELDS:
            refs = item.get(key, [])
            if not isinstance(refs, list) or len(refs) > 16 or any(
                not _string(ref) for ref in refs
            ):
                raise ValueError("invalid bounded receipt references")
        typed = item.get("typed_refs", [])
        if not isinstance(typed, list) or len(typed) > 16 or any(
            not isinstance(ref, dict) or set(ref) != {"kind", "ref"}
            or not _string(ref["kind"], 32) or not _string(ref["ref"])
            for ref in typed
        ):
            raise ValueError("invalid typed references")
        for key in ("kind", "operation_status", "operation_id"):
            if key in item and not _string(item[key]):
                raise ValueError("invalid candidate metadata")
        clean.append(item)
    return sorted(clean, key=lambda x: x["canonical_thread_id"]), max_items


def build_operator_workflow(
    payload: Mapping[str, Any], *,
    verified_pnf_resolver: Callable[[str, tuple[str, ...]], bool] | None = None,
) -> dict[str, Any]:
    """Compose existing producer receipts; no roster writes, mutation or dispatch."""
    rows, max_items = _validate(payload)
    archive = payload["archive_db"]
    operations = payload.get("operation_receipts", False)
    # A bounded window is selected deterministically; omissions remain explicit.
    selected = rows[:max_items]
    frontier_input = [{
        "canonical_thread_id": r["canonical_thread_id"], "task_atom": r["task_atom"],
        "kind": r.get("kind", "implementation"),
        "typed_refs": r.get("typed_refs", []),
        **{k: r.get(k, []) for k in RECEIPT_FIELDS},
    } for r in selected]
    frontier = build_frontier(
        archive_db=archive, evidence=frontier_input, max_evaluated=max_items,
        max_proposals=4, completed_operations=operations,
        receipt_db=payload.get("receipt_db") if operations else None,
        operation_limit=24,
    )
    decisions = {r["canonical_thread_id"]: r for r in frontier["decisions"]}
    evidence = {r["canonical_thread_id"]: r for r in frontier["evidence_rows"]}
    mappings = {r["canonical_thread_id"]: r for r in frontier["source_mapping"]}
    abstentions = {}
    for item in frontier["abstentions"]:
        abstentions.setdefault(item["canonical_thread_id"], []).append(item["reason"])
    discovery = frontier.get("operation_discovery") or {}
    for item in discovery.get("holds", []):
        tid = item.get("canonical_thread_id")
        if tid:
            abstentions.setdefault(tid, []).append("operation_source_mapping_hold")
    result_rows = []
    for row in selected:
        tid = row["canonical_thread_id"]
        decision = decisions.get(tid)
        source = evidence.get(tid)
        reasons = list(abstentions.get(tid, []))
        mapping = mappings.get(tid, {})
        if decision is None:
            reasons.append("canonical_thread_missing_or_not_evaluated")
        if mapping.get("mapping_ambiguous"):
            reasons.append("ambiguous_source_mapping")
        typed = source.get("typed_reference_receipt", {}) if source else {}
        if typed.get("held_count", 0):
            reasons.append("unverified_typed_reference")
        status = row.get("operation_status", "not_requested")
        review = operation_review({"operation_status": status,
                                   "operation_id": row.get("operation_id")})
        if status in {"async_starting", "commit_unknown"}:
            reasons.append("operation_requires_reconciliation")
        if status != "not_requested" and not operations:
            reasons.append("operation_receipt_not_requested")
        if operations and not discovery.get("candidates"):
            reasons.append("operation_receipt_unavailable")
        # A caller-supplied receipt string is never verification. Only a trusted,
        # independently injected producer resolver can attest PNF semantics.
        verified_pnf = False
        if not reasons and row.get("pnf_receipts") and verified_pnf_resolver is not None:
            try:
                verified_pnf = verified_pnf_resolver(
                    tid, tuple(sorted(set(row["pnf_receipts"])))) is True
            except (ValueError, RuntimeError, OSError):
                reasons.append("pnf_verification_unavailable")
        packet_id = None
        packet_refs: list[dict[str, Any]] = []
        truncation: dict[str, Any] = {}
        if not reasons and decision and decision["decision"] == "admit":
            try:
                proposal = {"canonical_thread_id": tid, "task_atom": row["task_atom"],
                            **{k: sorted(set(row.get(k, []))) for k in RECEIPT_FIELDS}}
                packet = build_work_packet([proposal], archive_db=archive)["packets"][0]
                handoff = governed_handoff(proposal, archive_db=archive,
                                           max_selected=8, max_packet_chars=12000,
                                           operation_status=status)
                packet_id = packet["packet_id"]
                packet_refs = [{"message_id": ref["message_id"],
                                "body_sha256": ref["body_sha256"]}
                               for ref in packet["source_refs"][:8]]
                truncation = {"pnf": packet["truncation_receipt"],
                              "handoff": handoff["span_receipt"]}
                # PG materialisation is optional for read-only operator review.
                # Lexical work-packet absence is disclosed, not silently promoted.
                # Without producer verification, the operator may inspect a
                # candidate handoff, but cannot treat it as verified PNF.
                if verified_pnf:
                    truncation["pnf_verified_by_producer"] = True
                else:
                    truncation["pnf_verified_by_producer"] = False
            except (ValueError, RuntimeError, FileNotFoundError, KeyError):
                reasons.append("bounded_packet_or_handoff_unavailable")
        if decision and decision["decision"] != "admit":
            reasons.append("ledger_" + decision["decision"])
        reasons = sorted(set(reasons))
        result_rows.append({
            "canonical_thread_id": tid,
            "task_atom_digest": _digest(row["task_atom"]),
            "candidate_disposition": decision["decision"] if decision else "park",
            "authority": "producer_verified_pnf_review_only" if verified_pnf else "candidate_only_not_promoted",
            "pnf_verification": "verified" if verified_pnf else "unverified",
            "selected": bool(decision and decision["decision"] == "admit" and not reasons),
            "state": "held" if reasons else "candidate",
            "holds": reasons,
            "evidence_refs": sorted(set(source["evidence_refs"]))[:16] if source else [],
            "typed_reference_status": [
                {"kind": r["kind"], "status": r["status"]}
                for r in typed.get("records", [])[:16]
            ],
            "pnf_packet_id": packet_id,
            "source_refs": packet_refs,
            "operation_review": {"status": review["operation_status"],
                                 "decision": review["decision"],
                                 "automatic_resend_allowed": False},
            "next_action": "review_holds" if reasons else "inspect_candidate_handoff",
            "truncation": truncation,
        })
    result = {"version": VERSION, "authority": "candidate_only_not_promoted",
              "promotion": False, "dispatch_performed": False,
              "canonical_truth_mutated": False, "automatic_resend_allowed": False,
              "browser_dom_allowed": False, "rows": result_rows,
              "truncation": {"supplied": len(rows), "evaluated": len(selected),
                             "candidate_limit_hit": len(rows) > len(selected)},
              "absence_receipts": ["formal_kernel_refinement_unverified"]}
    result["workflow_id"] = _digest(result)
    if len(json.dumps(result, sort_keys=True)) > MAX_OUTPUT_CHARS:
        raise ValueError("operator workflow exceeds bounded output budget")
    return result
