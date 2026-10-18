"""Bounded, evidence-only fleet lifecycle via the existing stdio MCP registry."""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Mapping

from .contracts import JsonDict, ToolHandler, ToolInputError, ToolSpec

VERSION = "itir.fleet.evidence.v1"
BOUNDARY = ("Archive/PNF receipts are evidence only: no theorem, task, or promotion "
            "mutation. Refresh is operator-authorized exact async read/ingest only; "
            "no retries, sync fallback, browser/DOM, catalog, or ChatGPT messages.")

def _controller():
    from scripts import evidence_fleet_controller as controller
    return controller

def _check(payload: Mapping[str, Any], required: set[str], optional: set[str] = frozenset()) -> None:
    if not isinstance(payload, Mapping) or set(payload) - required - optional or required - set(payload):
        raise ToolInputError("invalid fleet tool fields")
    for key in required - {"authorized", "limit"}:
        if not isinstance(payload[key], str) or not payload[key].strip():
            raise ToolInputError("missing explicit fleet parameter")
    if "authorized" in required and payload["authorized"] is not True:
        raise ToolInputError("explicit authorized: true required")

def _path(path: str) -> str:
    if not Path(path).expanduser().is_file():
        raise ToolInputError("explicit existing file required")
    return path

def _response(result: Any) -> JsonDict:
    return {"version": VERSION, "authority": BOUNDARY, "authoritative": False,
            "promotion_state": "not_requested", "evidence": result}

def fleet_plan(payload: Mapping[str, Any]) -> JsonDict:
    _check(payload, {"control_db"}, {"limit"})
    limit = payload.get("limit", 3)
    if type(limit) is not int or limit not in (2, 3, 4):
        raise ToolInputError("limit must be 2, 3 or 4")
    try:
        with sqlite3.connect("file:" + str(Path(_path(payload["control_db"])).resolve()) + "?mode=ro",
                             uri=True) as db:
            return _response(_controller().plan(db, limit))
    except ToolInputError:
        raise
    except Exception:
        raise ToolInputError("fleet plan unavailable")

def fleet_refresh_evidence(payload: Mapping[str, Any]) -> JsonDict:
    # Authorization is checked before path resolution, import, DB or session.
    _check(payload, {"authorized","control_db","work_id","conversation_id",
                     "puller","archive_db"}, {"account","formal_file","slrw"})
    ctl = _controller()
    cid = payload["conversation_id"]
    if not ctl.UUID_PATTERN.fullmatch(cid):
        raise ToolInputError("invalid canonical conversation UUID")
    try:
        with sqlite3.connect(_path(payload["control_db"])) as db:
            ctl._validate_work(db, payload["work_id"], cid)
            provider = ctl.exact_async_archive_provider(
                _path(payload["puller"]), _path(payload["archive_db"]),
                payload.get("account","main"),
                formal_file=payload.get("formal_file"), slrw_path=payload.get("slrw"))
            result = ctl.refresh_work_evidence(db,payload["work_id"],cid,provider)
        return _response(result)
    except ToolInputError:
        raise
    except Exception:
        raise ToolInputError("fleet refresh unavailable")

def fleet_attach_gap(payload: Mapping[str, Any]) -> JsonDict:
    _check(payload, {"control_db","work_id","conversation_id","archive_receipt_digest",
                     "formal_file","slrw"})
    ctl = _controller()
    if not ctl.UUID_PATTERN.fullmatch(payload["conversation_id"]):
        raise ToolInputError("invalid canonical conversation UUID")
    try:
        with sqlite3.connect(_path(payload["control_db"])) as db:
            result=ctl.attach_gap_to_archive(
                db,payload["work_id"],payload["conversation_id"],
                payload["archive_receipt_digest"],_path(payload["formal_file"]),
                _path(payload["slrw"]))
        return _response(result)
    except ToolInputError:
        raise
    except Exception:
        raise ToolInputError("fleet offline gap unavailable")

def get_fleet_tools() -> list[tuple[ToolSpec, ToolHandler]]:
    def spec(name: str, title: str, properties: dict, required: list[str], read_only: bool):
        return ToolSpec(name="itir.fleet."+name,title=title,
            description=BOUNDARY,input_schema={"type":"object","properties":properties,
            "required":required,"additionalProperties":False},
            response_version=VERSION,read_only=read_only)
    string=lambda: {"type":"string","minLength":1}
    base={k:string() for k in ("control_db","work_id","conversation_id")}
    return [
        (spec("plan","Bounded fleet evidence proposals",
            {"control_db":string(),"limit":{"type":"integer","enum":[2,3,4]}},
            ["control_db"],True),fleet_plan),
        (spec("refresh_evidence","Authorized exact async archive evidence refresh",
            {**base,"authorized":{"type":"boolean","const":True},
             "puller":string(),"archive_db":string(),"account":string(),
             "formal_file":string(),"slrw":string()},
            ["authorized","control_db","work_id","conversation_id","puller","archive_db"],
            False),fleet_refresh_evidence),
        (spec("attach_gap","Offline exact gap attachment",
            {**base,"archive_receipt_digest":string(),"formal_file":string(),
             "slrw":string()},
            ["control_db","work_id","conversation_id","archive_receipt_digest",
             "formal_file","slrw"],False),fleet_attach_gap),
    ]
