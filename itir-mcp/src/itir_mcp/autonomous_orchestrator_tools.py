"""Autonomous Orchestrator MCP Tools for unified Antigravity & Codex execution.

Provides durable state inspection, lane claims, heartbeats, parent reports,
archive batch execution, and PNF gap checking over the shared
`.autonomous-orchestrator/` control plane.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .contracts import JsonDict, ToolHandler, ToolInputError, ToolSpec
from .fleet_round_runner import execute_pareto_conductor, spawn_parallel_lanes

SCHEMA_VERSION = "itir.ao_mcp_control.v1"
CONTROL_PLANE_DIRNAME = ".autonomous-orchestrator"
LANE_CLAIMS_DIRNAME = "lane_claims"
PARENT_REPORTS_DIRNAME = "parent_reports"


def _now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _resolve_repo(repo_root: str | None) -> Path:
    if repo_root:
        return Path(repo_root).expanduser().resolve()
    # Default to current working directory or Git repository root
    cwd = Path.cwd().resolve()
    for candidate in [cwd, *cwd.parents]:
        if (candidate / ".git").exists() or (candidate / CONTROL_PLANE_DIRNAME).exists():
            return candidate
    return cwd


def _ensure_dirs(repo: Path) -> tuple[Path, Path, Path]:
    cp_dir = repo / CONTROL_PLANE_DIRNAME
    lane_dir = cp_dir / LANE_CLAIMS_DIRNAME
    reports_dir = cp_dir / PARENT_REPORTS_DIRNAME
    for d in (cp_dir, lane_dir, reports_dir):
        d.mkdir(parents=True, exist_ok=True)
    return cp_dir, lane_dir, reports_dir


def _read_json_safe(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def _write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(f".tmp.{_now_utc().replace(':', '')}")
    tmp_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp_path.replace(path)


# --- Tool 1: itir.ao.status ---
def ao_status(payload: Mapping[str, Any]) -> JsonDict:
    repo = _resolve_repo(payload.get("repo_root"))
    cp_dir, lane_dir, reports_dir = _ensure_dirs(repo)
    filter_id = payload.get("orchestrator_id")

    registry = _read_json_safe(cp_dir / "registry.json") or {"runners": []}
    claims: dict[str, Any] = {}
    for claim_file in lane_dir.glob("*.json"):
        claim_data = _read_json_safe(claim_file)
        if claim_data:
            claims[claim_file.stem] = claim_data

    status_files: dict[str, Any] = {}
    for sf in cp_dir.glob("status*.json"):
        s_data = _read_json_safe(sf)
        if s_data:
            status_files[sf.name] = s_data

    heartbeats: dict[str, Any] = {}
    for hf in cp_dir.glob("heartbeat*.json"):
        h_data = _read_json_safe(hf)
        if h_data:
            heartbeats[hf.name] = h_data

    parent_reports: dict[str, Any] = {}
    for pr in reports_dir.glob("*.json"):
        pr_data = _read_json_safe(pr)
        if pr_data:
            parent_reports[pr.stem] = pr_data

    return {
        "version": SCHEMA_VERSION,
        "repo_root": str(repo),
        "control_plane_dir": str(cp_dir),
        "registry": registry,
        "lane_claims": claims,
        "status_files": status_files,
        "heartbeats": heartbeats,
        "parent_reports": parent_reports,
    }


# --- Tool 2: itir.ao.claim_lane ---
def ao_claim_lane(payload: Mapping[str, Any]) -> JsonDict:
    repo = _resolve_repo(payload.get("repo_root"))
    _, lane_dir, _ = _ensure_dirs(repo)

    orchestrator_id = str(payload.get("orchestrator_id") or "").strip()
    if not orchestrator_id:
        raise ToolInputError("orchestrator_id is required")

    lane = str(payload.get("lane") or "default").strip()
    lane_claim = payload.get("lane_claim")
    parent_id = payload.get("parent_orchestrator_id")

    claim_record = {
        "orchestrator_id": orchestrator_id,
        "lane": lane,
        "lane_claim": lane_claim,
        "parent_orchestrator_id": parent_id,
        "claimed_at": _now_utc(),
        "status_file": str(repo / CONTROL_PLANE_DIRNAME / f"status.{orchestrator_id}.json"),
        "heartbeat_file": str(repo / CONTROL_PLANE_DIRNAME / f"heartbeat.{orchestrator_id}.json"),
    }
    claim_path = lane_dir / f"{orchestrator_id}.json"
    _write_json_atomic(claim_path, claim_record)

    return {
        "version": SCHEMA_VERSION,
        "ok": True,
        "claim": claim_record,
    }


# --- Tool 3: itir.ao.heartbeat ---
def ao_heartbeat(payload: Mapping[str, Any]) -> JsonDict:
    repo = _resolve_repo(payload.get("repo_root"))
    cp_dir, _, _ = _ensure_dirs(repo)

    orchestrator_id = str(payload.get("orchestrator_id") or "").strip()
    if not orchestrator_id:
        raise ToolInputError("orchestrator_id is required")

    state = str(payload.get("state") or "busy").strip()
    heartbeat_record = {
        "orchestrator_id": orchestrator_id,
        "state": state,
        "last_heartbeat": _now_utc(),
        "phase": payload.get("phase", "running"),
        "current_step": payload.get("current_step", ""),
        "skill": payload.get("skill", ""),
        "blocker": payload.get("blocker"),
        "child_pid": payload.get("child_pid"),
    }
    hf_path = cp_dir / f"heartbeat.{orchestrator_id}.json"
    _write_json_atomic(hf_path, heartbeat_record)

    return {
        "version": SCHEMA_VERSION,
        "ok": True,
        "heartbeat": heartbeat_record,
    }


# --- Tool 4: itir.ao.report_result ---
def ao_report_result(payload: Mapping[str, Any]) -> JsonDict:
    repo = _resolve_repo(payload.get("repo_root"))
    _, _, reports_dir = _ensure_dirs(repo)

    parent_id = str(payload.get("parent_orchestrator_id") or "").strip()
    orchestrator_id = str(payload.get("orchestrator_id") or "").strip()
    if not parent_id or not orchestrator_id:
        raise ToolInputError("both parent_orchestrator_id and orchestrator_id are required")

    report_record = {
        "orchestrator_id": orchestrator_id,
        "parent_orchestrator_id": parent_id,
        "lane": payload.get("lane", "default"),
        "status": payload.get("status", "completed"),
        "summary": payload.get("summary", ""),
        "reported_at": _now_utc(),
        "zkp_frame": payload.get("zkp_frame", {}),
        "changed_files": payload.get("changed_files", []),
        "validation_commands": payload.get("validation_commands", []),
        "promotion_state": payload.get("promotion_state", "unspecified"),
        "remaining_gaps": payload.get("remaining_gaps", []),
    }

    report_file = reports_dir / f"{parent_id}.json"
    existing = _read_json_safe(report_file) or {"parent_orchestrator_id": parent_id, "reports": []}
    reports_list = existing.get("reports", [])
    reports_list.append(report_record)
    existing["reports"] = reports_list[-64:]  # rolling window of 64
    existing["last_report_at"] = _now_utc()
    _write_json_atomic(report_file, existing)

    return {
        "version": SCHEMA_VERSION,
        "ok": True,
        "report_count": len(existing["reports"]),
        "latest_report": report_record,
    }


# --- Tool 5: itir.ao.gap_check ---
def ao_gap_check(payload: Mapping[str, Any]) -> JsonDict:
    cid = str(payload.get("conversation_id") or "").strip()
    formal_file = str(payload.get("formal_file") or "").strip()
    if not cid or not formal_file:
        raise ToolInputError("conversation_id and formal_file are required")

    from re_gpt.gap_comparator import ExactGapComparator
    comparator = ExactGapComparator()
    report = comparator.compare(cid, formal_file)
    return {
        "version": SCHEMA_VERSION,
        "ok": True,
        "report": report.to_dict(),
        "markdown_summary": report.render_markdown(),
    }



def ao_spawn_parallel_lanes(payload: Mapping[str, Any]) -> JsonDict:
    lanes = payload.get("lanes")
    workers = payload.get("workers")
    if not isinstance(lanes, list) or not all(isinstance(item, Mapping) for item in lanes):
        raise ToolInputError("lanes must be an array of lane objects")
    if not isinstance(workers, list):
        raise ToolInputError("workers must be an array of conversation IDs or worker objects")
    if len(lanes) != len(workers):
        raise ToolInputError("lanes and workers must have equal length")
    db_path = payload.get("db_path")
    if db_path is not None and (not isinstance(db_path, str) or not db_path.strip()):
        raise ToolInputError("db_path must be a non-empty string when provided")
    try:
        result = spawn_parallel_lanes(
            lanes,
            workers,
            db_path=db_path.strip() if isinstance(db_path, str) else None,
        )
    except (TypeError, ValueError, FileNotFoundError) as exc:
        raise ToolInputError(str(exc)) from exc
    return {
        "version": SCHEMA_VERSION,
        "ok": True,
        "result": result,
    }



def ao_pareto_conductor(payload: Mapping[str, Any]) -> JsonDict:
    hierarchy = payload.get("hierarchy")
    candidate_lanes = payload.get("candidate_lanes")
    workers = payload.get("workers", [])
    worker_capacity = payload.get("worker_capacity")
    dispatch = bool(payload.get("dispatch", False))
    if not isinstance(hierarchy, Mapping):
        raise ToolInputError("hierarchy must be an object")
    if not isinstance(candidate_lanes, Mapping) or not all(
        isinstance(key, str) and isinstance(value, Mapping)
        for key, value in candidate_lanes.items()
    ):
        raise ToolInputError("candidate_lanes must map topic_id strings to lane objects")
    if isinstance(worker_capacity, bool) or not isinstance(worker_capacity, int):
        raise ToolInputError("worker_capacity must be an integer")
    if not 1 <= worker_capacity <= 20:
        raise ToolInputError("worker_capacity must be within [1, 20]")
    if not isinstance(workers, list):
        raise ToolInputError("workers must be an array")
    if dispatch and not workers:
        raise ToolInputError("workers are required when dispatch=true")
    db_path = payload.get("db_path")
    if db_path is not None and (not isinstance(db_path, str) or not db_path.strip()):
        raise ToolInputError("db_path must be a non-empty string when provided")
    try:
        result = execute_pareto_conductor(
            hierarchy,
            worker_capacity,
            candidate_lanes,
            workers,
            db_path=db_path.strip() if isinstance(db_path, str) else None,
            dispatch=dispatch,
        )
    except (TypeError, ValueError, FileNotFoundError) as exc:
        raise ToolInputError(str(exc)) from exc
    return {
        "version": SCHEMA_VERSION,
        "ok": True,
        "result": result,
    }


def get_autonomous_orchestrator_tools() -> list[tuple[ToolSpec, ToolHandler]]:
    return [

        (
            ToolSpec(
                name="itir.ao.pareto_conductor",
                title="AO hierarchical spectral Pareto conductor",
                description=(
                    "Plan or dispatch up to 20 AO workers from a dynamic PNF hierarchy. "
                    "W<=10 rolls subtopics into primary worker turns; W=20 branches high-alpha "
                    "subtopics only after pairwise noTypedMeet verification."
                ),
                input_schema={
                    "type": "object",
                    "required": ["hierarchy", "worker_capacity", "candidate_lanes"],
                    "properties": {
                        "hierarchy": {"type": "object"},
                        "worker_capacity": {"type": "integer", "minimum": 1, "maximum": 20},
                        "candidate_lanes": {
                            "type": "object",
                            "additionalProperties": {"type": "object"},
                        },
                        "workers": {
                            "type": "array",
                            "items": {
                                "oneOf": [
                                    {"type": "string"},
                                    {
                                        "type": "object",
                                        "required": ["conversation_id"],
                                        "properties": {"conversation_id": {"type": "string"}},
                                        "additionalProperties": True,
                                    },
                                ]
                            },
                        },
                        "dispatch": {"type": "boolean"},
                        "db_path": {"type": "string"},
                    },
                    "additionalProperties": False,
                },
                response_version=SCHEMA_VERSION,
                read_only=False,
            ),
            ao_pareto_conductor,
        ),
        (
            ToolSpec(
                name="itir.ao.spawn_parallel_lanes",
                title="Spawn independent AO Fleet lanes",
                description=(
                    "Dispatch one pairwise-independent AO lane per explicit Fleet worker using direct async "
                    "fast mode. Requires noTypedMeet-safe typed supports and never enables DOM fallback or automatic resend."
                ),
                input_schema={
                    "type": "object",
                    "required": ["lanes", "workers"],
                    "properties": {
                        "lanes": {
                            "type": "array",
                            "items": {"type": "object"},
                            "description": "Independent lane claim objects produced by compute_dynamic_lane_descent.",
                        },
                        "workers": {
                            "type": "array",
                            "items": {
                                "oneOf": [
                                    {"type": "string"},
                                    {
                                        "type": "object",
                                        "required": ["conversation_id"],
                                        "properties": {"conversation_id": {"type": "string"}},
                                        "additionalProperties": True,
                                    },
                                ]
                            },
                            "description": "One explicit ChatGPT conversation worker per lane.",
                        },
                        "db_path": {"type": "string"},
                    },
                    "additionalProperties": False,
                },
                response_version=SCHEMA_VERSION,
                read_only=False,
            ),
            ao_spawn_parallel_lanes,
        ),
        (
            ToolSpec(
                name="itir.ao.status",
                title="Autonomous Orchestrator Status",
                description="Query the shared .autonomous-orchestrator/ control plane (registry, status files, active heartbeats, and lane claims).",
                input_schema={
                    "type": "object",
                    "properties": {
                        "repo_root": {"type": "string", "description": "Optional path to repo root."},
                        "orchestrator_id": {"type": "string", "description": "Optional filter for runner ID."},
                    },
                    "required": [],
                    "additionalProperties": False,
                },
                response_version=SCHEMA_VERSION,
                read_only=True,
            ),
            ao_status,
        ),
        (
            ToolSpec(
                name="itir.ao.claim_lane",
                title="Autonomous Orchestrator Claim Lane",
                description="Register a lane claim for an autonomous runner in .autonomous-orchestrator/lane_claims/.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "repo_root": {"type": "string"},
                        "orchestrator_id": {"type": "string"},
                        "lane": {"type": "string"},
                        "lane_claim": {"type": "string"},
                        "parent_orchestrator_id": {"type": "string"},
                    },
                    "required": ["orchestrator_id", "lane"],
                    "additionalProperties": False,
                },
                response_version=SCHEMA_VERSION,
                read_only=False,
            ),
            ao_claim_lane,
        ),
        (
            ToolSpec(
                name="itir.ao.heartbeat",
                title="Autonomous Orchestrator Heartbeat",
                description="Emit or update a heartbeat for an active autonomous runner.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "repo_root": {"type": "string"},
                        "orchestrator_id": {"type": "string"},
                        "state": {"type": "string", "enum": ["busy", "done", "blocked", "degraded", "stalled"]},
                        "phase": {"type": "string"},
                        "current_step": {"type": "string"},
                        "skill": {"type": "string"},
                        "blocker": {"type": "string"},
                        "child_pid": {"type": "integer"},
                    },
                    "required": ["orchestrator_id"],
                    "additionalProperties": False,
                },
                response_version=SCHEMA_VERSION,
                read_only=False,
            ),
            ao_heartbeat,
        ),
        (
            ToolSpec(
                name="itir.ao.report_result",
                title="Autonomous Orchestrator Report Result",
                description="Record a child lane completion or escalation report in parent_reports/ with ZKP framing.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "repo_root": {"type": "string"},
                        "orchestrator_id": {"type": "string"},
                        "parent_orchestrator_id": {"type": "string"},
                        "lane": {"type": "string"},
                        "status": {"type": "string"},
                        "summary": {"type": "string"},
                        "zkp_frame": {"type": "object"},
                        "changed_files": {"type": "array", "items": {"type": "string"}},
                        "validation_commands": {"type": "array", "items": {"type": "string"}},
                        "promotion_state": {"type": "string"},
                        "remaining_gaps": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["orchestrator_id", "parent_orchestrator_id"],
                    "additionalProperties": False,
                },
                response_version=SCHEMA_VERSION,
                read_only=False,
            ),
            ao_report_result,
        ),
        (
            ToolSpec(
                name="itir.ao.gap_check",
                title="Autonomous Orchestrator Exact Gap Check",
                description="Calculate exact PNF provenance-backed multiset difference (Delta_Gap = M_informal \\ M_formal) between a ChatGPT research thread and a formal Agda/Lean file.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "conversation_id": {"type": "string"},
                        "formal_file": {"type": "string"},
                    },
                    "required": ["conversation_id", "formal_file"],
                    "additionalProperties": False,
                },
                response_version=SCHEMA_VERSION,
                read_only=True,
            ),
            ao_gap_check,
        ),
    ]
