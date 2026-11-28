"""Independent referee domain extension; no actor authority.

The trusted local adapter must independently establish theorem-to-answer
correspondence and reopen the exact native binding. This module validates
the returned extension and binds it to the already certified kernel result.
It does not create that correspondence from candidate JSON.
"""
import hashlib
import json
import re

DIGEST=re.compile(r"sha256:[0-9a-f]{64}\Z")

def require(ok, reason):
    if not ok:
        raise ValueError(reason)

def validated_extension(extension, kernel, request):
    require(isinstance(extension,dict) and set(extension)=={
        "slr_premise_binding","slr_reciprocal_query_binding","slr_reciprocal_query_answer"},
        "unexpected independently checked domain extension")
    p=extension["slr_premise_binding"]
    b=extension["slr_reciprocal_query_binding"]
    a=extension["slr_reciprocal_query_answer"]
    require(isinstance(p,dict) and set(p)=={
        "demand_ref","obligation_ref","consumer_ref","pnf_revision_ref","statement_digest",
        "result_kind","source_revisions","artifact_digest","checker_revision","dependencies",
        "residual_ref","proposition_ref","da51_address","artifact_ref","source_revision",
        "evidence_ref","producer","checker","statement_language","target_prover","dependent_refs"},
        "wrong premise binding fields")
    require(isinstance(b,dict) and set(b)=={
        "schema","proof_scope","family_ref","consumer_ref","query_ref","left_selector_ref",
        "right_selector_ref","left_source_revision_ref","right_source_revision_ref",
        "left_observation_ref","right_observation_ref","left_observation_sha256",
        "right_observation_sha256","forward_comparison_ref","backward_comparison_ref",
        "statement_digest","evidence_ref","answer_sha256"}, "wrong reciprocal binding fields")
    require(isinstance(a,dict) and set(a)=={"schema","query_ref","left_support","right_support"},
            "wrong answer fields")
    require(all(isinstance(b[k],str) and b[k] for k in b),"empty reciprocal coordinate")
    require(b["schema"]=="slr-reciprocal-source-query-binding-v1" and
            b["proof_scope"]=="bounded-source-proposition" and
            a["schema"]=="slr.signed-view-query-answer.v1" and a["query_ref"]==b["query_ref"],
            "wrong query scope")
    for side in ("left_support","right_support"):
        s=a[side]
        require(s is None or (isinstance(s,dict) and set(s)=={"positive","negative"}
                and all(type(v) is bool for v in s.values())),"invalid signed support")
    require(b["left_selector_ref"]!=b["right_selector_ref"] and
            b["left_source_revision_ref"]!=b["right_source_revision_ref"],"non-distinct pair")
    require(all(DIGEST.fullmatch(b[k]) for k in ("statement_digest","answer_sha256",
            "left_observation_sha256","right_observation_sha256")),"invalid digest")
    # Native serde_json uses canonical map ordering for these scalar fields;
    # the independent callback must also reopen native binding exactly.
    digest="sha256:"+hashlib.sha256(json.dumps(a,sort_keys=True,separators=(",",":"),
                                             ensure_ascii=False).encode()).hexdigest()
    require(b["answer_sha256"]==digest,"signed answer digest mismatch")
    require(p["demand_ref"]==request["demand_ref"] and p["obligation_ref"]==request["obligation_ref"]
            and p["statement_digest"]==request["statement_digest"]==b["statement_digest"]
            and p["consumer_ref"]==b["consumer_ref"] and p["evidence_ref"]==b["evidence_ref"]
            and p["da51_address"]==request.get("da51_address"),"foreign premise")
    require(isinstance(p["source_revisions"],list) and
            all(isinstance(x,str) and x for x in p["source_revisions"]) and
            all(b[k] in p["source_revisions"] for k in ("left_source_revision_ref","right_source_revision_ref")),
            "source revision mismatch")
    for pk,kk in (("artifact_digest","artifactDigest"),("artifact_ref","artifactRef"),
                  ("source_revision","sourceRevision"),("checker","checker"),
                  ("checker_revision","checkerRevision"),("dependencies","dependencies")):
        require(p[pk]==kernel[kk],"kernel premise mismatch: "+pk)
    return json.loads(json.dumps(extension))
