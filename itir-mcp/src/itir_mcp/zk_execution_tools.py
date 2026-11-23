"""Local, non-authoritative adapters to existing zkSEC and zkperf owners."""
from __future__ import annotations

import json
import math
import re
from hashlib import sha256
from typing import Any, Mapping

from .contracts import JsonDict, ToolInputError, ToolExecutionError, ToolSpec

SEC = "itir.zksec.policy_preview"
PERF = "itir.zkperf.window_plan"
INDEX = "itir.zkperf.evidence_index_check"
BUSHIDO = "itir.zkperf.bushido_ab_candidate"
ACTIONS = ("read", "collect", "review", "plan", "deploy", "remediate", "patch")
RISKS = ("low", "medium", "high")
LAYERS = ("binary_closure", "source_debug", "traces", "models", "build_events")
MAX_BYTES = 65536
REF = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,159}", re.ASCII)
HASH = re.compile(r"[0-9a-f]{64}", re.ASCII)


def _invalid():
    raise ToolInputError("Malformed or out-of-scope observation input")


def _bounded(payload, keys):
    if not isinstance(payload, Mapping) or set(payload) != set(keys):
        _invalid()
    try:
        raw = json.dumps(dict(payload), allow_nan=False, separators=(",", ":"))
    except (ValueError, TypeError, RecursionError):
        _invalid()
    if len(raw.encode("utf-8")) > MAX_BYTES:
        _invalid()


def _ref(value):
    if not isinstance(value, str) or not REF.fullmatch(value):
        _invalid()
    return value


def _hash(value):
    if not isinstance(value, str) or not HASH.fullmatch(value):
        _invalid()
    return value


def _result(name, **fields):
    return {
        "version": name + ".v1",
        "state": "proposal_only",
        "candidate_only": True,
        "non_authoritative": True,
        "execution_authorized": False,
        "publication_authorized": False,
        **fields,
    }


def authority_profile(name):
    return {
        "tool_id": name, "kind": "validation", "inputs": ["observed"],
        "outputs": ["observed"], "mutates": False, "validation_mode": "strict",
        "repair_mode": "none", "max_authority": "observed",
        "promotion_requires_gate": True,
        "authority_notes": {
            "gate": "external trusted actor and exact grounded execution review",
            "candidate_only": True, "non_authoritative": True,
        },
    }


def policy_preview(payload):
    _bounded(payload, ("action", "risk_level"))
    action, risk = payload["action"], payload["risk_level"]
    if action not in ACTIONS or risk not in RISKS:
        _invalid()
    try:
        from zksec.security import assess_action
    except ImportError:
        raise ToolExecutionError("zkSEC provider unavailable; configure trusted local installation") from None
    # Never accept claimed managed actor, scope, confirmation or plan receipt.
    decision = assess_action(action=action, actor_role="anonymous",
                             source="public", risk_level=risk, confirmed=False)
    return _result(SEC, provider="zkSEC.security.assess_action",
                   assumed_source="public", hypothetical_decision=decision.decision,
                   reason_code=decision.reason_code)


def window_plan(payload):
    _bounded(payload, ("observations", "max_observations_per_window"))
    rows, limit = payload["observations"], payload["max_observations_per_window"]
    if not isinstance(rows, list) or not 1 <= len(rows) <= 128 or type(limit) is not int or not 1 <= limit <= 128:
        _invalid()
    # Narrow projection of existing zkperf-on-SL observation contract.
    # No raw payloads, file paths, URLs, identity claims or extra authority fields.
    required = {"zkperf_observation_id", "trace_id", "run_id", "asserted_at",
                "source_ref", "status", "metrics", "trace_refs", "proof_refs", "hash"}
    seen, clean = set(), []
    for row in rows:
        if not isinstance(row, dict) or set(row) != required or row["status"] != "observed":
            _invalid()
        for key in ("zkperf_observation_id", "trace_id", "run_id", "source_ref"):
            _ref(row[key])
        identity = row["zkperf_observation_id"]
        if identity in seen:
            _invalid()
        seen.add(identity)
        if not isinstance(row["asserted_at"], str) or not re.fullmatch(
            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?Z",row["asserted_at"]):
            _invalid()
        if not isinstance(row["hash"], str) or not row["hash"].startswith("sha256:"):
            _invalid()
        _hash(row["hash"][7:])
        for key in ("trace_refs", "proof_refs"):
            if not isinstance(row[key], list) or len(row[key]) > 32:
                _invalid()
            for val in row[key]:
                _ref(val)
        if not row["trace_refs"]:  # proof refs alone are not observations
            _invalid()
        if not isinstance(row["metrics"], list) or len(row["metrics"]) > 32:
            _invalid()
        names = set()
        for metric in row["metrics"]:
            if not isinstance(metric, dict) or set(metric) != {"name", "kind", "value"}:
                _invalid()
            name, kind, val = _ref(metric["name"]), metric["kind"], metric["value"]
            if name in names or kind not in ("integer", "float", "number"):
                _invalid()
            names.add(name)
            if type(val) not in (int, float) or abs(val) > 2**53 or not math.isfinite(val):
                _invalid()
            if kind == "integer" and type(val) is not int:
                _invalid()
        clean.append(dict(row))
    try:
        from itir_jmd_bridge.zkperf_stream_core import build_zkperf_stream_fixture_from_observations
    except ImportError:
        raise ToolExecutionError("ITIR zkperf stream provider unavailable; configure trusted suite installation") from None
    try:
        manifest = build_zkperf_stream_fixture_from_observations(clean, max_observations_per_window=limit)
    except (ValueError, OverflowError, TypeError):
        _invalid()
    # Keep existing grouping and identity, but never include raw observation payload or publish.
    windows = [{k: w[k] for k in ("windowId", "sequence", "runId", "traceId", "observationIds",
                                    "startedAtUtc", "endedAtUtc")} for w in manifest["windows"]]
    return _result(PERF, provider="itir_jmd_bridge.zkperf_stream_core",
                   stream_contract=manifest["contractVersion"], stream_id=manifest["streamId"],
                   stream_revision=manifest["streamRevision"], windows=windows,
                   supplied_hashes_verified=False, proof_verified=False)


def evidence_index_check(payload):
    _bounded(payload, ("index",))
    index = payload["index"]
    required = {"schema", "commit_claim", "layers", "missing_layers", "state", "grounding",
                "native_acceptance", "publication_authorized", "index_sha256"}
    if not isinstance(index, dict) or set(index) != required or type(index["schema"]) is not int or index["schema"] != 1:
        _invalid()
    if (index["state"], index["grounding"], index["native_acceptance"]) != ("proposal_only", "OPEN", "OPEN") or index["publication_authorized"] is not False:
        _invalid()
    if not isinstance(index["commit_claim"], str) or not re.fullmatch("[0-9a-f]{40}", index["commit_claim"]):
        _invalid()
    _hash(index["index_sha256"])
    layers = index["layers"]
    if not isinstance(layers, dict) or set(layers) != set(LAYERS):
        _invalid()
    counts = {}
    for k in LAYERS:
        rows = layers[k]
        if not isinstance(rows, list) or len(rows) > 128:
            _invalid()
        paths = set()
        for row in rows:
            if not isinstance(row, dict) or set(row) != {"path", "sha256", "bytes"}:
                _invalid()
            path = row["path"]
            if not isinstance(path, str) or not 1 <= len(path) <= 512 or "\\" in path or any(ord(c)<32 for c in path) or any(p in ("", ".", "..") for p in path.split("/")) or path in paths:
                _invalid()
            paths.add(path)
            _hash(row["sha256"])
            if type(row["bytes"]) is not int or not 0 <= row["bytes"] <= 2**63-1:
                _invalid()
        counts[k] = len(rows)
    missing = [k for k in LAYERS if not counts[k]]
    if index["missing_layers"] != missing:
        _invalid()
    canonical = json.dumps({k: v for k, v in index.items() if k != "index_sha256"},
                           sort_keys=True, separators=(",", ":")).encode()
    if sha256(canonical).hexdigest() != index["index_sha256"]:
        raise ToolInputError("Evidence index self-commitment mismatch")
    return _result(INDEX, commit_claim=index["commit_claim"], index_sha256=index["index_sha256"],
                   layer_counts=counts, missing_layers=missing, self_commitment_matches=True,
                   files_verified=False, binary_linkage_verified=False, proof_verified=False)


def bushido_ab_candidate(payload):
    """Normalize an already reconciled *candidate*, without validating native execution.

    No filesystem access or claimed same-request linkage. Reuse the exact
    zkperf window_plan producer for the one canonical candidate observation.
    """
    _bounded(payload, ("reconciliation", "asserted_at"))
    r = payload["reconciliation"]
    timestamp = payload["asserted_at"]
    if not isinstance(timestamp, str) or not re.fullmatch(
        r"\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(?:\\.\\d{1,6})?Z", timestamp
    ):
        _invalid()
    keys = {"version", "state", "non_authoritative", "candidate_only",
            "native_acceptance", "decision", "missing_controls", "contradictions",
            "baseline_origin", "enabled_origin", "native_reported_counts",
            "fixture_run_ids", "execution_authorized", "publication_authorized",
            "same_run_linkage_verified", "request_identity_verified",
            "runtime_binary_linkage_verified", "physical_enforcement_verified",
            "input_sha256"}
    if not isinstance(r, dict) or set(r) != keys:
        _invalid()
    if (r["version"] != "bushido.extension_ab_reconciliation.v1"
            or r["state"] != "proposal_only" or r["native_acceptance"] != "OPEN"):
        _invalid()
    if any(r[k] is not True for k in ("non_authoritative", "candidate_only")):
        _invalid()
    if any(r[k] is not False for k in (
        "execution_authorized", "publication_authorized", "same_run_linkage_verified",
        "request_identity_verified", "runtime_binary_linkage_verified",
        "physical_enforcement_verified")):
        _invalid()
    decision = r["decision"]
    if decision not in ("consistent_controls_observed", "contradiction_observed", "inconclusive"):
        _invalid()
    if (not isinstance(r["missing_controls"], list)
            or not isinstance(r["contradictions"], list)
            or len(r["missing_controls"]) > 32 or len(r["contradictions"]) > 32
            or any(not isinstance(v, str) or not REF.fullmatch(v) for v in
                   r["missing_controls"] + r["contradictions"])):
        _invalid()
    if (decision == "consistent_controls_observed"
            and (r["missing_controls"] or r["contradictions"])):
        _invalid()
    if decision == "contradiction_observed" and not r["contradictions"]:
        _invalid()
    if decision == "inconclusive" and (not r["missing_controls"] or r["contradictions"]):
        _invalid()
    runs = r["fixture_run_ids"]
    if not isinstance(runs, list) or len(runs) != 2 or any(
        not isinstance(v, str) or not re.fullmatch("[0-9a-f]{32}", v) for v in runs
    ) or runs[0] == runs[1]:
        _invalid()
    source_hashes = r["input_sha256"]
    names = ("baseline_origin", "enabled_origin", "baseline_preview", "enabled_preview")
    if not isinstance(source_hashes, dict) or set(source_hashes) != set(names):
        _invalid()
    for digest in source_hashes.values():
        _hash(digest)
    allowed_routes = {"extension_allow_route", "extension_deny_route",
                      "extension_redirect_route", "extension_redirect_target_route"}
    counts = {}
    for name in ("baseline_origin", "enabled_origin", "native_reported_counts"):
        values = r[name]
        if not isinstance(values, dict) or set(values) != allowed_routes:
            # Native prefix may omit routes, but omitted is a missing control,
            # not evidence of zero physical requests.
            if name != "native_reported_counts" or not isinstance(values, dict) or not set(values) <= allowed_routes:
                _invalid()
        for value in values.values():
            if type(value) is not int or value < 0 or value > 2**53:
                _invalid()
        counts[name] = sum(values.values())
    if decision == "consistent_controls_observed":
        a, b = r["baseline_origin"], r["enabled_origin"]
        n = r["native_reported_counts"]
        if (any(a[k] < 1 for k in allowed_routes)
                or b["extension_allow_route"] < 1 or b["extension_redirect_route"] < 1
                or b["extension_deny_route"] != 0 or b["extension_redirect_target_route"] != 0
                or any(n.get(k, 0) < 1 for k in allowed_routes)):
            _invalid()
    if decision == "contradiction_observed" and not (
        r["enabled_origin"]["extension_deny_route"]
        or r["enabled_origin"]["extension_redirect_target_route"]
    ):
        _invalid()
    # Hash is an exact commitment to supplied canonical metadata, not a check
    # against file bytes, process identity, nor independently captured evidence.
    canonical = json.dumps(r, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    digest = sha256(canonical).hexdigest()
    row = {
        "zkperf_observation_id": "bushido-ab-" + digest[:32],
        "trace_id": "bushido-ab-trace-" + digest[:24],
        "run_id": "bushido-ab-" + runs[1],
        "asserted_at": timestamp,
        "source_ref": "receipt:sha256:" + digest,
        "status": "observed",
        "metrics": [
            {"name": "baseline_origin_events", "kind": "integer",
             "value": counts["baseline_origin"]},
            {"name": "enabled_origin_events", "kind": "integer",
             "value": counts["enabled_origin"]},
            {"name": "native_reported_events", "kind": "integer",
             "value": counts["native_reported_counts"]},
        ],
        "trace_refs": ["trace:sha256:" + digest],
        "proof_refs": [],
        "hash": "sha256:" + digest,
    }
    plan = window_plan({"observations": [row], "max_observations_per_window": 1})
    return _result(
        BUSHIDO, provider="itir.zkperf.window_plan", observation=row,
        reconciliation_decision=decision, reconciliation_sha256=digest,
        supplied_input_hashes_verified=False, files_verified=False,
        same_run_linkage_verified=False, request_identity_verified=False,
        binary_linkage_verified=False, physical_enforcement_verified=False,
        native_acceptance="OPEN", stream_contract=plan["stream_contract"],
        stream_id=plan["stream_id"], stream_revision=plan["stream_revision"],
        windows=plan["windows"], proof_verified=False,
    )


def get_zk_execution_tools():
    def spec(name, title, description, properties):
        return ToolSpec(name=name, title=title, description=description, response_version=name+".v1",
                        input_schema={"type":"object", "properties":properties,
                                      "required":list(properties), "additionalProperties":False})
    return [
        (spec(SEC, "zkSEC policy preview", "Hypothetical public-source policy only; grants no authority.",
              {"action":{"type":"string","enum":list(ACTIONS)}, "risk_level":{"type":"string","enum":list(RISKS)}}), policy_preview),
        (spec(PERF, "zkperf window plan", "Group supplied redacted observation metadata with existing ITIR zkperf stream owner; no capture or publish.",
              {"observations":{"type":"array","minItems":1,"maxItems":128,"items":{"type":"object"}},
               "max_observations_per_window":{"type":"integer","minimum":1,"maximum":128}}), window_plan),
        (spec(INDEX, "zkperf evidence index check", "Check supplied Bushido five-layer index self-commitment, not files or proof.",
              {"index":{"type":"object"}}), evidence_index_check),
        (spec(BUSHIDO, "Bushido A/B candidate observation", "Project a supplied reconciliation into the existing zkperf window owner; no native acceptance.",
              {"reconciliation":{"type":"object"}, "asserted_at":{"type":"string"}}), bushido_ab_candidate),
    ]
