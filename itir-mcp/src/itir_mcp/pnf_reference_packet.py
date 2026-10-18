"""Read-only bounded SLR producer-backed reference packet. No transcript materialisation."""
from __future__ import annotations

from typing import Any, Mapping

from .contracts import JsonDict, ToolInputError, ToolSpec

VERSION = "itir.pnf.reference_work_packet.v1"
MAX_ROWS = 24

def _connection(dsn: str):
    # SLR owns the PostgreSQL source schema. No new ITIR message persistence.
    try:
        import psycopg
    except ImportError as exc:
        raise ToolInputError("PostgreSQL read-only driver unavailable") from exc
    return psycopg.connect(dsn, autocommit=True, options="-c default_transaction_read_only=on")

def reference_work_packet(payload: Mapping[str, Any], *, connect=None) -> JsonDict:
    required={"pg_dsn","source_ref","work_ref","world_ref"}
    optional={"limit","drill_down","max_chars"}
    if (not isinstance(payload, Mapping) or required - set(payload)
        or set(payload) - required - optional):
        raise ToolInputError("explicit source/work/world selectors required")
    if not all(isinstance(payload[k],str) and payload[k].strip() for k in required):
        raise ToolInputError("selectors must be nonempty strings")
    limit=payload.get("limit",12)
    if type(limit) is not int or not 1 <= limit <= MAX_ROWS:
        raise ToolInputError("limit must be 1..24")
    drill=payload.get("drill_down",False)
    if type(drill) is not bool:
        raise ToolInputError("drill_down must be boolean")
    max_chars=payload.get("max_chars",0)
    if type(max_chars) is not int or not 0 <= max_chars <= 512:
        raise ToolInputError("max_chars must be 0..512")
    if drill and max_chars == 0:
        raise ToolInputError("explicit positive max_chars required for drill-down")
    # No raw source retrieval here: SLR producer must verify canonical SQLite digest.
    if drill:
        return {"version":VERSION,"candidate_only":True,"authority":"evidence_only",
                "source_ref":payload["source_ref"],"work_ref":payload["work_ref"],
                "world_ref":payload["world_ref"],"source_refs":[],"factor_signatures":[],
                "residual_signatures":[],"comparison_receipts":[],"related_work_refs":[],
                "missing_evidence":["canonical_archive_verified_drill_down_not_materialised"],
                "raw_text":None}
    opener=connect or _connection
    try:
        with opener(payload["pg_dsn"]) as conn:
            with conn.cursor() as cur:
                cur.execute("""SELECT message_ref,node_ref,parent_node_ref,branch_membership_ref,
                    role_ref,message_time_ref,source_thread_ref,archive_locator,body_sha256,
                    source_revision_ref,attachment_refs_json
                    FROM corpus.chat_archive_message
                    WHERE conversation_ref=%s AND archive_locator IS NOT NULL
                    AND candidate_only=TRUE AND creates_semantic_authority=FALSE
                    ORDER BY message_time_ref,message_ref LIMIT %s""",
                    (payload["source_ref"],limit))
                rows=cur.fetchall()
                refs=[dict(zip(("message_ref","node_ref","parent_node_ref",
                    "branch","role","time","source_thread_ref","archive_locator",
                    "body_sha256","source_revision_ref","attachment_refs_json"),row))
                    for row in rows]
                revisions=[r["source_revision_ref"] for r in refs]
                factors=[]
                comparisons=[]
                if revisions:
                    cur.execute("""SELECT s.source_revision_ref, f.role_ref, f.dependency_ref,
                        f.source_start_char, f.source_end_char, b.batch_ref
                        FROM corpus.source_statement s
                        JOIN pnf.statement_candidate_batch b ON b.statement_ref=s.statement_ref
                        JOIN pnf.statement_candidate_factor f ON f.batch_ref=b.batch_ref
                        WHERE s.source_revision_ref = ANY(%s)
                        AND b.candidate_only=TRUE AND b.semantic_admission_paid=FALSE
                        ORDER BY b.batch_ref,f.candidate_ref LIMIT %s""",
                        (revisions,limit))
                    factors=[dict(zip(("source_revision_ref","role_ref","dependency_ref",
                        "start_offset","end_offset","batch_ref"),row)) for row in cur.fetchall()]
                    cur.execute("""SELECT comparison_ref,left_source_revision_ref,
                        right_source_revision_ref,consumer_ref,packet_sha256
                        FROM semantic.itir_relational_comparison
                        WHERE (left_source_revision_ref = ANY(%s)
                           OR right_source_revision_ref = ANY(%s))
                        AND candidate_only=TRUE AND creates_semantic_authority=FALSE
                        ORDER BY comparison_ref LIMIT %s""",(revisions,revisions,limit))
                    comparisons=[dict(zip(("comparison_ref","left_source_revision_ref",
                        "right_source_revision_ref","consumer_ref","packet_sha256"),row))
                        for row in cur.fetchall()]
    except Exception:
        raise ToolInputError("producer reference packet unavailable")
    missing=[]
    if not refs: missing.append("source_reference_not_registered")
    if not factors: missing.append("selected_span_candidate_pnf_not_materialised")
    if not comparisons: missing.append("comparison_receipt_not_materialised")
    missing.extend(["world_store_binding_not_verified","related_work_join_not_verified"])
    return {"version":VERSION,"candidate_only":True,"authority":"evidence_only",
        "source_ref":payload["source_ref"],"work_ref":payload["work_ref"],
        "world_ref":payload["world_ref"],"source_refs":refs,
        "factor_signatures":factors,"residual_signatures":[],
        "comparison_receipts":comparisons,"related_work_refs":[],
        "missing_evidence":missing,"raw_text":None}

def get_reference_work_packet_tools():
    return [(ToolSpec(name="itir.pnf.reference_work_packet",
        title="Bounded producer-backed SLR PNF reference packet",
        description="Read-only candidate evidence; no promotion or raw transcript body.",
        input_schema={"type":"object","properties":{
            **{k:{"type":"string","minLength":1} for k in
               ("pg_dsn","source_ref","work_ref","world_ref")},
            "limit":{"type":"integer","minimum":1,"maximum":24},
            "drill_down":{"type":"boolean"},
            "max_chars":{"type":"integer","minimum":0,"maximum":512}},
            "required":["pg_dsn","source_ref","work_ref","world_ref"],
            "additionalProperties":False},
        response_version=VERSION,read_only=True),reference_work_packet)]
