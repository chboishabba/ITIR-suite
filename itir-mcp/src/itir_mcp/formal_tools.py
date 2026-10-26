"""Four governed formal operations over the existing dashi-agda preflight owner.

No actor-provided success flag can authenticate a local referee or pay a proof.
"""
from __future__ import annotations

import hashlib
import importlib
import json
import os
import sys
from pathlib import Path
from typing import Any, Callable, Mapping

from .contracts import ToolInputError, ToolSpec

MAX_ITEMS = 12
MAX_CHARS = 2400


def _digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()
    return hashlib.sha256(encoded).hexdigest()


def _condense(value: Any, *, depth: int = 0) -> Any:
    if depth >= 4:
        return "<nested-evidence>"
    if isinstance(value, dict):
        return {str(k): _condense(v, depth=depth + 1) for k, v in
                sorted(value.items(), key=lambda pair: str(pair[0]))[:MAX_ITEMS]}
    if isinstance(value, (tuple, list)):
        return [_condense(v, depth=depth + 1) for v in value[:MAX_ITEMS]]
    if isinstance(value, str):
        return value[:MAX_CHARS] + ("…" if len(value) > MAX_CHARS else "")
    return value


def _candidate(kind: str, raw: Any) -> dict[str, Any]:
    return {
        "authority_kind": kind, "candidate_only": True,
        "establishes_proof": False, "evidence_digest": _digest(raw),
        "summary": _condense(raw),
    }


def _default_tools() -> Any:
    root = Path(os.environ.get("DASHI_AGDA_ROOT", "/home/c/Documents/code/dashi_agda"))
    package = root / "tools" / "agda_preflight"
    if str(package) not in sys.path:
        sys.path.insert(0, str(package))
    service_module = importlib.import_module("agda_preflight.service")
    adapter_module = importlib.import_module("agda_preflight.mcp_adapter")
    extension = importlib.import_module("agda_preflight.mcp_semantic_extension")
    extension.install_mcp_adapter_semantic_extension(adapter_module.DashiAgdaMcpTools)
    index = Path(os.environ.get("DASHI_AGDA_INDEX", str(root / ".cache" / "agda_preflight" / "source-index.sqlite3")))
    return adapter_module.DashiAgdaMcpTools(service_module.DashiAgdaService(root, index))


def _required(data: Mapping[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ToolInputError(f"{key} must be a nonempty string")
    return value


def _bounded_limit(data: Mapping[str, Any]) -> int:
    limit = data.get("limit", 10)
    if type(limit) is not int or not 1 <= limit <= 50:
        raise ToolInputError("limit must be an integer between 1 and 50")
    return limit


def _receipt_hold(reason: str, evidence: Any) -> dict[str, Any]:
    return {
        "status": "held", "kernel_handoff_eligible": False,
        "candidate_only": True, "establishes_proof": False,
        "critique": {
            "protocol": "slr.referee-critique.v1",
            "failure_class": reason,
            "evidence_digest": _digest(evidence),
            "required_action": "repair-and-resubmit",
        },
    }


def _handoff_eligible(kernel: Mapping[str, Any], artifact: Mapping[str, Any],
                      handoff: Mapping[str, Any], trusted: Mapping[str, Any]) -> bool:
    # Authentication is not accepted from the actor's request. The trusted
    # referee context is injected by the local execution boundary.
    fields = ("subject_commit", "source_digest", "artifact_digest",
              "checker_digest", "dependency_digest")
    if not trusted.get("authenticated_local_referee") or not trusted.get("independent_kernel_success"):
        return False
    if handoff.get("authority_kind") != "isolated_kernel_check":
        return False
    if handoff.get("candidate_only") is not False or handoff.get("establishes_proof") is not True:
        return False
    if not all(isinstance(handoff.get(k), str) and handoff[k] and
               handoff[k] == trusted.get(k) for k in fields):
        return False
    if kernel.get("schemaVersion") != "kernel-certification-receipt/v1":
        return False
    if kernel.get("authority") != "formal-checker-only":
        return False
    if kernel.get("certifiesFormalResult") is not True:
        return False
    if any(kernel.get(key) is not False for key in
           ("createsLegalAuthority", "applicabilityPromoted", "claimTruthPromoted")):
        return False
    if kernel.get("certificationState") != "kernel-certified":
        return False
    if artifact.get("schemaVersion") != "artifact-resolution-receipt/v1":
        return False
    if artifact.get("verified") is not True:
        return False
    if artifact.get("authority") != "transport-only" or artifact.get("establishesProof") is not False:
        return False
    if kernel.get("artifactRef") != artifact.get("logicalArtifactRef"):
        return False
    if not kernel.get("artifactRef"):
        return False
    if kernel.get("checker") not in {"agda", "lean"}:
        return False
    if not kernel.get("checkerRevision"):
        return False
    if not isinstance(kernel.get("dependencies"), list):
        return False
    if not all(isinstance(item, str) and item for item in kernel["dependencies"]):
        return False
    if trusted["source_digest"] != artifact.get("contentDigest"):
        return False
    if trusted["checker_digest"] != _digest({
        "checker": kernel["checker"], "revision": kernel["checkerRevision"],
    }):
        return False
    if trusted["dependency_digest"] != _digest(kernel["dependencies"]):
        return False
    if kernel.get("sourceRevision") != "git:" + trusted["subject_commit"]:
        return False
    if kernel.get("artifactDigest") != trusted["artifact_digest"]:
        return False
    if artifact.get("contentDigest") != trusted["artifact_digest"]:
        return False
    return True


def get_formal_tools(
    *, tools_provider: Callable[[], Any] | None = None,
    certifier: Callable[..., dict[str, Any]] | None = None,
    handoff_validator: Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]] | None = None,
    interactive_backend: Callable[[Mapping[str, Any]], Any] | None = None,
    referee_context: Callable[[], Mapping[str, Any]] | None = None,
) -> list[tuple[ToolSpec, Callable[[Mapping[str, Any]], dict[str, Any]]]]:
    provider = tools_provider or _default_tools

    def inspect(data: Mapping[str, Any]) -> dict[str, Any]:
        action = str(data.get("action", "diagnose"))
        tools = provider()
        limit = _bounded_limit(data)
        if action == "diagnose":
            raw = tools.diagnose(_required(data, "target"),
                                 errors_only=data.get("errors_only") is True, limit=limit)
        elif action == "next_error":
            raw = tools.next_error(_required(data, "target"),
                                   require_fix=data.get("require_fix") is True)
        elif action == "affected":
            raw = tools.affected(_required(data, "target"), within=data.get("within"))
        elif action == "related_symbols":
            raw = tools.related_symbols(_required(data, "symbol"),
                                        include_history=False, limit=limit)
        elif action == "discover":
            raw = tools.discover(_required(data, "query"), limit=limit)
        elif action == "round_lineage":
            raw = tools.round_lineage(prefix=data.get("prefix"))
        else:
            raise ToolInputError("unknown inspect action")
        return _candidate("similarity" if action in {"related_symbols", "discover", "round_lineage"}
                          else "preflight", raw)

    def route(data: Mapping[str, Any]) -> dict[str, Any]:
        tools = provider()
        action = str(data.get("action", "proof_route_for_obligation"))
        if action == "proof_route_for_obligation":
            kwargs = {k: data[k] for k in ("demand_ref", "external_obligation_ref",
                      "statement_digest", "target_prover") if k in data}
            raw = tools.proof_route_for_obligation(_required(data, "query"), **kwargs)
        elif action == "da51_resolve":
            raw = tools.da51_resolve(_required(data, "address"))
        elif action == "formal_evidence_for_obligation":
            raw = tools.formal_evidence_for_obligation(
                demand_ref=_required(data, "demand_ref"),
                external_obligation_ref=_required(data, "external_obligation_ref"),
                statement_digest=_required(data, "statement_digest"),
            )
        else:
            raise ToolInputError("unknown route action")
        return _candidate("obligation_routing", raw)

    def refine(data: Mapping[str, Any]) -> dict[str, Any]:
        if interactive_backend is None:
            return {**_candidate("interactive_goal", {"status": "unavailable"}),
                    "status": "unavailable"}
        return _candidate("interactive_goal", interactive_backend(data))

    def certify(data: Mapping[str, Any]) -> dict[str, Any]:
        # Do not allow caller-provided "trusted" flags to act as authorization.
        if referee_context is None:
            return _receipt_hold("unauthenticated-referee", data)
        trusted = dict(referee_context())
        if not trusted.get("authenticated_local_referee"):
            return _receipt_hold("unauthenticated-referee", data)
        if data.get("authority_kind") in {"preflight", "similarity",
                                           "obligation_routing", "interactive_goal"}:
            return _receipt_hold("candidate-only-evidence", data)
        artifact = data.get("artifact_resolution_receipt")
        if not isinstance(artifact, dict):
            return _receipt_hold("missing-artifact-receipt", data)
        try:
            run = certifier
            validate = handoff_validator
            if run is None:
                run = importlib.import_module("agda_preflight.kernel_certification").certify_artifact
            if validate is None:
                validate = importlib.import_module(
                    "agda_preflight.kernel_evidence_handoff").validate_kernel_handoff
            kernel = run(
                artifact_resolution_receipt=artifact,
                demand_ref=_required(data, "demand_ref"),
                obligation_ref=_required(data, "obligation_ref"),
                statement_digest=_required(data, "statement_digest"),
                da51_address=data.get("da51_address"),
                checker=data.get("checker"),
            )
            normalized = validate(kernel, artifact)
            handoff = {
                "authority_kind": "isolated_kernel_check",
                "candidate_only": False,
                "establishes_proof": True,
                "subject_commit": trusted.get("subject_commit"),
                "source_digest": trusted.get("source_digest"),
                "artifact_digest": normalized.get("artifact_digest"),
                "checker_digest": trusted.get("checker_digest"),
                "dependency_digest": trusted.get("dependency_digest"),
            }
            if not _handoff_eligible(kernel, artifact, handoff, trusted):
                return _receipt_hold("stale-or-unverified-handoff",
                                     {"kernel": kernel, "artifact": artifact})
            return {
                "status": "verified", "kernel_handoff_eligible": True,
                "candidate_only": False, "establishes_proof": True,
                "authority_kind": "isolated_kernel_check",
                "evidence_digest": _digest({"kernel": kernel, "normalized": normalized}),
                "handoff": handoff, "evidence": _condense(normalized),
            }
        except (ValueError, RuntimeError, OSError, KeyError, TypeError) as error:
            return _receipt_hold("kernel-certification-failed",
                                 {"error": str(error), "artifact": artifact})

    def spec(name: str, description: str) -> ToolSpec:
        return ToolSpec(
            name=f"itir.formal.{name}", title=f"Formal {name}",
            description=description, response_version="formal-facade.v1",
            read_only=True,
            input_schema={"type": "object", "properties": {
                "action": {"type": "string"}, "target": {"type": "string"},
                "symbol": {"type": "string"}, "query": {"type": "string"},
                "limit": {"type": "integer"}, "artifact_resolution_receipt": {"type": "object"},
            }, "additionalProperties": True},
        )

    return [
        (spec("inspect", "Bounded preflight and similarity evidence; never proof."), inspect),
        (spec("route", "Candidate-only obligation and DA51 routing."), route),
        (spec("refine", "Optional interactive proof-state exploration; never proof."), refine),
        (spec("certify", "Referee-authenticated isolated kernel handoff; never merge authorization."), certify),
    ]
