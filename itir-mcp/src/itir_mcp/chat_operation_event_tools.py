"""TUI-independent read-only ChatGPT operation event replay."""
from __future__ import annotations
import importlib
from .contracts import ToolInputError, ToolExecutionError, ToolSpec

def replay(payload):
    cid=payload.get("conversation_id")
    cursor=payload.get("after",0)
    limit=payload.get("limit",100)
    if not isinstance(cid,str) or not cid or len(cid)>150:
        raise ToolInputError("conversation_id required")
    if type(cursor) is not int or cursor<0 or type(limit) is not int or not 1<=limit<=500:
        raise ToolInputError("invalid event window")
    try:
        journal=importlib.import_module("re_gpt.pg_operation_events")
        return journal.events_after(cid, after=cursor, limit=limit)
    except Exception as exc:
        raise ToolExecutionError("canonical operation event replay failed") from exc

def get_operation_event_tools():
    return [(ToolSpec(name="itir.chatgpt.operation_events",
                      title="Replay ChatGPT operation events",
                      description="PG source-scoped events after cursor; no TUI required.",
                      input_schema={"type":"object","properties":{
                          "conversation_id":{"type":"string"},
                          "after":{"type":"integer","minimum":0},
                          "limit":{"type":"integer","minimum":1,"maximum":500}},
                          "required":["conversation_id"],"additionalProperties":False},
                      read_only=True),replay)]
