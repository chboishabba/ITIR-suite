"""Typed, source-bound reference inspection; no transcript access or proof promotion."""
from __future__ import annotations

import os
import re
import sqlite3
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from .pnf_work_packet_provider import canonical_archive_path

VERSION = "itir.ao.typed_references.v1"
SHA = re.compile(r"^[0-9a-f]{40}$")
REPO = re.compile(r"^(?P<owner>[A-Za-z0-9_.-]+)/(?P<repo>[A-Za-z0-9_.-]+)#(?P<pr>[1-9][0-9]*)@(?P<sha>[0-9a-f]{40})$")
FORMAL = re.compile(r"^(?P<repo>[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)@(?P<sha>[0-9a-f]{40}):(?P<path>[A-Za-z0-9_./-]+\.(?:agda|lean))$")
COMPLETE = frozenset({"complete"})
MAX_OPERATIONS = 200


def _archive_map(path: str | None, source_ids: Sequence[str]) -> dict[str, list[str]]:
    """Bounded mapping for selected transport IDs, never reads canonical message bodies."""
    if not source_ids:
        return {}
    archive = canonical_archive_path(path)
    if not archive.is_file():
        raise FileNotFoundError("canonical archive missing")
    with sqlite3.connect(archive.resolve().as_uri() + "?mode=ro", uri=True) as db:
        cols = {x[1] for x in db.execute("PRAGMA table_info(messages)")}
        if not {"canonical_thread_id", "source_thread_id", "account_id", "platform"} <= cols:
            raise ValueError("canonical mapping schema mismatch")
        marks = ",".join("?" for _ in source_ids)
        rows = db.execute(
            "SELECT source_thread_id, canonical_thread_id FROM messages "
            "WHERE account_id='main' AND platform='chatgpt' "
            "AND source_thread_id IN (" + marks + ") "
            "AND canonical_thread_id IS NOT NULL "
            "GROUP BY source_thread_id, canonical_thread_id",
            tuple(source_ids),
        )
        result: dict[str, list[str]] = {}
        for source, canonical in rows:
            result.setdefault(str(source), []).append(str(canonical))
        return result


def completed_operation_candidates(
    *, archive_db: str | None = None, db_path: str | None = None,
    limit: int = 24,
) -> dict[str, Any]:
    """Recent completed transport operations; exact canonical identity only."""
    if type(limit) is not int or not 1 <= limit <= MAX_OPERATIONS:
        raise ValueError("limit must be 1..200")
    raw = db_path or os.environ.get("ITIR_REGPT_RECEIPT_DB") or "~/.chatgpt_history.sqlite3"
    if not isinstance(raw, str) or not raw.strip():
        raise ValueError("invalid transport receipt DB")
    path = Path(raw).expanduser()
    if not path.is_file():
        raise FileNotFoundError("transport receipt cache missing")
    with sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True) as db:
        db.row_factory = sqlite3.Row
        columns = {x[1] for x in db.execute("PRAGMA table_info(mutation_attempts)")}
        required = {"operation_id", "conversation_id", "operation", "state",
                    "started_at", "completed_at", "user_node_id", "assistant_node_id"}
        if not required <= columns:
            raise ValueError("mutation receipt schema mismatch")
        rows = db.execute(
            "SELECT operation_id,conversation_id,operation,state,started_at,"
            "completed_at,user_node_id,assistant_node_id FROM mutation_attempts "
            "WHERE state='complete' AND completed_at IS NOT NULL "
            "AND conversation_id IS NOT NULL "
            "ORDER BY completed_at DESC,operation_id DESC LIMIT ?",
            (limit + 1,),
        ).fetchall()
    chosen = rows[:limit]
    mapping = _archive_map(archive_db, sorted({str(r["conversation_id"]) for r in chosen}))
    candidates = []
    holds = []
    for row in chosen:
        source = str(row["conversation_id"])
        ids = mapping.get(source, [])
        record = {"operation_id": str(row["operation_id"]),
                  "source_thread_id": source, "state": str(row["state"]),
                  "operation": str(row["operation"]), "completed_at": row["completed_at"],
                  "transport_authority": "re_gpt_receipt_cache"}
        if len(ids) != 1:
            holds.append({**record, "status": "hold", "reason":
                          "unmapped_source" if not ids else "ambiguous_source_mapping"})
        else:
            candidates.append({**record, "canonical_thread_id": ids[0],
                               "status": "source_bound_complete",
                               "evidence_ref": "op:" + str(row["operation_id"])})
    return {"version": "itir.ao.completed_operation_candidates.v1",
            "candidates": candidates, "holds": holds,
            "truncation": {"limit": limit, "more_available": len(rows) > limit},
            "policy": {"canonical_read_only": True, "transport_read_only": True,
                       "dispatch": False, "resend": False, "raw_bodies": False}}



def formal_receipt_resolver(
    receipt_provider: Callable[[str, str, str, str], Mapping[str, Any] | None],
) -> Callable[[str, str, str, str], bool]:
    """Accept only referee-supplied, source-bound formal certification receipts.

    The provider must obtain receipts from the independent local referee.
    Actor-provided MCP arguments and candidate inspection outputs are not trusted.
    """
    def resolve(repo: str, sha: str, path: str, thread: str) -> bool:
        if not isinstance(repo, str) or not isinstance(sha, str):
            return False
        if not isinstance(path, str) or not isinstance(thread, str) or not thread:
            return False
        if SHA.fullmatch(sha) is None or FORMAL.fullmatch(f"{repo}@{sha}:{path}") is None:
            return False
        if ".." in path.split("/"):
            return False
        try:
            receipt = receipt_provider(repo, sha, path, thread)
        except (KeyError, LookupError, OSError, ValueError):
            return False
        if not isinstance(receipt, Mapping):
            return False
        if receipt.get("status") != "verified":
            return False
        if receipt.get("kernel_handoff_eligible") is not True:
            return False
        if receipt.get("authority_kind") != "isolated_kernel_check":
            return False
        if receipt.get("candidate_only") is not False:
            return False
        if receipt.get("establishes_proof") is not True:
            return False
        handoff = receipt.get("handoff")
        if not isinstance(handoff, Mapping):
            return False
        if handoff.get("subject_commit") != sha:
            return False
        if handoff.get("authority_kind") != "isolated_kernel_check":
            return False
        if handoff.get("candidate_only") is not False:
            return False
        if handoff.get("establishes_proof") is not True:
            return False
        if not all(isinstance(handoff.get(key), str) and handoff[key] for key in
                   ("source_digest", "artifact_digest", "checker_digest", "dependency_digest")):
            return False
        binding = receipt.get("reference_binding")
        if not isinstance(binding, Mapping):
            return False
        return (binding.get("repo") == repo
                and binding.get("sha") == sha
                and binding.get("path") == path
                and binding.get("canonical_thread_id") == thread
                and binding.get("authenticated_local_referee") is True)

    return resolve


def validate_typed_references(
    canonical_thread_id: str, references: Sequence[Mapping[str, Any]], *,
    operation_candidates: Mapping[str, Any] | None = None,
    repository_resolver: Callable[[str, int, str], bool] | None = None,
    formal_resolver: Callable[[str, str, str, str], bool] | None = None,
) -> dict[str, Any]:
    """Resolution requires an independent provider; path/label alone never verifies."""
    if not isinstance(canonical_thread_id, str) or not canonical_thread_id:
        raise ValueError("canonical_thread_id required")
    if not isinstance(references, (list, tuple)) or len(references) > 32:
        raise ValueError("references must be bounded")
    ops = {str(x["operation_id"]): x for x in (operation_candidates or {}).get("candidates", [])}
    records = []
    for ref in references:
        if not isinstance(ref, Mapping) or set(ref) != {"kind", "ref"}:
            raise ValueError("reference must have exactly kind/ref")
        kind, value = ref["kind"], ref["ref"]
        if kind not in {"operation", "repository", "formal"} or not isinstance(value, str) or len(value) > 512:
            raise ValueError("invalid typed reference")
        status, reason = "hold", "unverified"
        normalized = value
        if kind == "operation":
            if not re.fullmatch(r"op:[A-Za-z0-9_.:-]{1,128}", value):
                raise ValueError("invalid operation reference")
            op = ops.get(value[3:])
            if op and op["canonical_thread_id"] == canonical_thread_id and op["state"] in COMPLETE:
                status, reason = "source_bound", "complete_operation_exact_mapping"
            else:
                reason = "operation_missing_unmapped_or_incomplete"
        elif kind == "repository":
            match = REPO.fullmatch(value)
            if not match:
                raise ValueError("expected owner/repo#PR@40hexsha")
            owner_repo = match["owner"] + "/" + match["repo"]
            if repository_resolver is not None and repository_resolver(owner_repo, int(match["pr"]), match["sha"]):
                status, reason = "resolved", "repository_pr_head_verified"
            else:
                reason = "repository_connector_verification_unavailable_or_failed"
        else:
            match = FORMAL.fullmatch(value)
            if not match or ".." in match["path"].split("/"):
                raise ValueError("expected owner/repo@40hexsha:path.agda|lean")
            if formal_resolver is not None and formal_resolver(
                match["repo"], match["sha"], match["path"], canonical_thread_id
            ):
                status, reason = "resolved", "formal_receipt_source_bound"
            else:
                reason = "formal_kernel_receipt_unavailable_or_unbound"
        records.append({"kind": kind, "ref": normalized, "status": status, "reason": reason,
                        "canonical_thread_id": canonical_thread_id})
    return {"version": VERSION, "records": records,
            "verified_count": sum(x["status"] != "hold" for x in records),
            "held_count": sum(x["status"] == "hold" for x in records),
            "authority": "candidate_reference_validation_not_claim_promotion"}
