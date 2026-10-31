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

def queue_turn(payload):
    cid=payload.get("conversation_id")
    prompt=payload.get("prompt")
    actor=payload.get("actor","agent")
    key=payload.get("job_id")
    provider=payload.get("provider","chatgpt")
    if provider not in {"chatgpt","local"}:
        raise ToolInputError("unsupported provider")
    if not isinstance(cid,str) or not cid or len(cid)>150:
        raise ToolInputError("invalid conversation ID")
    if not isinstance(prompt,str) or not prompt.strip() or len(prompt)>200000:
        raise ToolInputError("invalid prompt")
    if not isinstance(actor,str) or not actor or len(actor)>80:
        raise ToolInputError("invalid actor")
    if key is not None and (not isinstance(key,str) or not key or len(key)>150):
        raise ToolInputError("invalid job ID")
    try:
        from re_gpt.pg_turn_worker import queue_turn as submit
        return submit(cid,prompt,actor=actor,job_id=key,provider=provider)
    except Exception as exc:
        raise ToolExecutionError("PG conversation queue submission failed") from exc

def status(payload):
    job_id=payload.get("job_id")
    if not isinstance(job_id,str) or not job_id or len(job_id)>150:
        raise ToolInputError("job_id required")
    from re_gpt.pg_turn_worker import job_status
    return job_status(job_id)

def cancel(payload):
    job_id=payload.get("job_id")
    if not isinstance(job_id,str) or not job_id or len(job_id)>150:
        raise ToolInputError("job_id required")
    from re_gpt.pg_turn_worker import cancel_queued
    return cancel_queued(job_id)

def get_operation_event_tools():
    return [(ToolSpec(name="itir.chatgpt.job_status",
                      title="Read server-owned turn job status",
                      description="Inspect PG job and linked operation status without transcript leakage.",
                      input_schema={"type":"object","properties":{"job_id":{"type":"string"}},
                          "required":["job_id"],"additionalProperties":False},
                      read_only=True),status),
            (ToolSpec(name="itir.chatgpt.cancel_queued",
                      title="Cancel an unstarted queued turn",
                      description="Never cancels running or commit-unknown operations.",
                      input_schema={"type":"object","properties":{"job_id":{"type":"string"}},
                          "required":["job_id"],"additionalProperties":False},
                      read_only=False),cancel),
            (ToolSpec(name="itir.chatgpt.queue_turn",
                      title="Enqueue a server-owned ChatGPT turn",
                      description="Create a durable PG work item; processing requires separate worker.",
                      input_schema={"type":"object","properties":{
                          "conversation_id":{"type":"string"},
                          "prompt":{"type":"string"},
                          "actor":{"type":"string"},
                          "provider":{"type":"string","enum":["chatgpt","local"]},
                          "job_id":{"type":"string"}},
                          "required":["conversation_id","prompt"],"additionalProperties":False},
                      read_only=False),queue_turn),
            (ToolSpec(name="itir.chatgpt.operation_events",
                      title="Replay ChatGPT operation events",
                      description="PG source-scoped events after cursor; no TUI required.",
                      input_schema={"type":"object","properties":{
                          "conversation_id":{"type":"string"},
                          "after":{"type":"integer","minimum":0},
                          "limit":{"type":"integer","minimum":1,"maximum":500}},
                          "required":["conversation_id"],"additionalProperties":False},
                      read_only=True),replay)]
