from __future__ import annotations

from typing import Any, Mapping, Sequence

from .contracts import JsonDict, ToolInputError


WIKIDATA_REVIEW_PACKET_VERSION = "itir.wikidata.review_packet.v1"
ZELPH_PARTIAL_CLOSURE_VERSION = "itir.zelph.partial_closure.v1"

_AUTHORITY_BOUNDARY: JsonDict = {
    "read_only": True,
    "non_authoritative": True,
    "canonical_truth_mutated": False,
    "candidate_only": True,
    "promotion_authority": False,
}


def wikidata_review_packet(payload: Mapping[str, Any]) -> JsonDict:
    statements = _mapping_sequence(payload, "statements")
    constraints = _mapping_sequence(payload, "constraints")
    tooling_profile = _mapping(payload, "tooling_profile")
    payload_refs = _ref_list(payload.get("provenance_refs"), "provenance_refs")

    facts: list[JsonDict] = []
    citations: list[str] = []
    provenance_refs: list[str] = []
    for index, statement in enumerate(statements, start=1):
        fact = _normalize_statement(statement, index)
        facts.append(fact)
        for ref in fact["provenance_refs"]:
            if ref not in citations:
                citations.append(ref)
        for ref in fact["provenance_refs"]:
            if ref not in provenance_refs:
                provenance_refs.append(ref)

    constraint_diagnostics: list[JsonDict] = []
    for index, constraint in enumerate(constraints, start=1):
        diagnostic = _normalize_constraint(constraint, index)
        constraint_diagnostics.append(diagnostic)
        for ref in diagnostic["provenance_refs"]:
            if ref not in citations:
                citations.append(ref)
        for ref in diagnostic["provenance_refs"]:
            if ref not in provenance_refs:
                provenance_refs.append(ref)

    for ref in payload_refs:
        if ref not in citations:
            citations.append(ref)
        if ref not in provenance_refs:
            provenance_refs.append(ref)

    normalized_profile = _normalize_tooling_profile(tooling_profile)
    authority_boundary = dict(_AUTHORITY_BOUNDARY)
    authority_boundary["domain"] = "wikidata"

    return {
        "version": WIKIDATA_REVIEW_PACKET_VERSION,
        "domain": "wikidata",
        "packet_kind": "candidate_review_packet",
        "candidate_only": True,
        "non_authoritative": True,
        "promoted_claims": False,
        "truth_claims": False,
        "statement_count": len(facts),
        "constraint_count": len(constraint_diagnostics),
        "fact_count": len(facts),
        "facts": facts,
        "constraint_diagnostics": constraint_diagnostics,
        "citations": citations,
        "provenance_refs": provenance_refs,
        "tooling_profile": normalized_profile,
        "authority_boundary": authority_boundary,
        "summary": _summary_text(
            "Candidate-only Wikidata review packet",
            facts=len(facts),
            constraints=len(constraint_diagnostics),
            citations=len(citations),
        ),
    }


def zelph_partial_closure(payload: Mapping[str, Any]) -> JsonDict:
    partial_view = _mapping(payload, "partial_graph_view")
    candidate_refs = _ref_list(payload.get("candidate_refs"), "candidate_refs")

    completeness = _require_str(partial_view, "completeness")
    if completeness != "partial":
        raise ToolInputError("partial_graph_view.completeness must be partial")

    _require_true(partial_view, "subset_of_artifact")
    _require_true(partial_view, "candidate_only")
    _require_true(partial_view, "diagnostic_only")
    _reject_true(partial_view, "truth_authority")
    _reject_true(partial_view, "support_authority")
    _reject_true(partial_view, "admissibility_authority")
    _reject_true(partial_view, "promotion_authority")

    artifact_identity = _mapping(partial_view, "artifact_identity")
    selected_shards = _mapping_sequence(partial_view, "selected_shards")

    selected_candidates: list[JsonDict] = []
    inferred_refs: list[str] = []
    for index, shard in enumerate(selected_shards, start=1):
        candidate = _normalize_candidate_shard(shard, index)
        selected_candidates.append(candidate)
        candidate_ref = candidate["candidate_ref"]
        if candidate_ref not in inferred_refs:
            inferred_refs.append(candidate_ref)

    if candidate_refs:
        missing_refs = [ref for ref in candidate_refs if ref not in inferred_refs]
        if missing_refs:
            raise ToolInputError("candidate_refs must match the partial view candidate refs")
    else:
        candidate_refs = inferred_refs

    if not candidate_refs:
        raise ToolInputError("partial_graph_view must yield at least one candidate ref")

    authority_boundary = dict(_AUTHORITY_BOUNDARY)
    authority_boundary["domain"] = "zelph"

    selected_sections = _unique_strings(
        candidate["section"] for candidate in selected_candidates if candidate.get("section") is not None
    )

    return {
        "version": ZELPH_PARTIAL_CLOSURE_VERSION,
        "domain": "zelph",
        "closure_kind": "candidate_partial_closure",
        "incomplete_closure": True,
        "candidate_only": True,
        "non_authoritative": True,
        "promoted_claims": False,
        "truth_claims": False,
        "artifact_identity": _artifact_identity_summary(artifact_identity),
        "selected_candidate_count": len(selected_candidates),
        "selected_sections": selected_sections,
        "candidate_refs": inferred_refs,
        "selected_candidates": selected_candidates,
        "closure_summary": _summary_text(
            "Partial Zelph closure remains incomplete",
            candidates=len(selected_candidates),
            candidate_refs=len(inferred_refs),
        ),
        "diagnostics": [
            {
                "code": "incomplete_closure",
                "status": "asserted",
                "message": "The supplied shard view is partial and does not establish closure.",
            },
            {
                "code": "non_authoritative",
                "status": "asserted",
                "message": "This summary does not claim promotion, truth, or authority transfer.",
            },
            {
                "code": "candidate_refs_only",
                "status": "asserted",
                "message": "Only candidate refs from the partial view are retained.",
            },
        ],
        "authority_boundary": authority_boundary,
    }


def _normalize_statement(statement: Mapping[str, Any], index: int) -> JsonDict:
    statement_ref = _required_ref(statement, ("statement_ref", "statement_id", "id", "ref"), f"statements[{index}]")
    fact_text = _choose_text(statement, ("fact", "text", "claim", "summary"), f"statements[{index}]")
    provenance_refs = _ref_list(
        _choose_optional_value(statement, ("provenance_refs", "citation_refs", "source_refs")),
        f"statements[{index}].provenance_refs",
    )
    status = _optional_text(statement, ("status", "kind", "statement_kind")) or "candidate"
    confidence = _optional_number(statement.get("confidence"))
    fact: JsonDict = {
        "statement_ref": statement_ref,
        "candidate_ref": statement_ref,
        "status": status,
        "fact": _compact_text(fact_text),
        "provenance_refs": provenance_refs,
    }
    if confidence is not None:
        fact["confidence"] = confidence
    return fact


def _normalize_constraint(constraint: Mapping[str, Any], index: int) -> JsonDict:
    constraint_ref = _required_ref(constraint, ("constraint_ref", "constraint_id", "id", "ref"), f"constraints[{index}]")
    message = _choose_text(constraint, ("diagnostic", "message", "summary", "constraint"), f"constraints[{index}]")
    severity = _optional_text(constraint, ("severity", "level")) or "info"
    status = _optional_text(constraint, ("status",)) or "diagnostic"
    provenance_refs = _ref_list(
        _choose_optional_value(constraint, ("provenance_refs", "citation_refs", "source_refs")),
        f"constraints[{index}].provenance_refs",
    )
    related_refs = _ref_list(
        _choose_optional_value(constraint, ("candidate_refs", "statement_refs", "refs")),
        f"constraints[{index}].candidate_refs",
    )
    return {
        "constraint_ref": constraint_ref,
        "status": status,
        "severity": severity,
        "message": _compact_text(message),
        "candidate_refs": related_refs,
        "provenance_refs": provenance_refs,
    }


def _normalize_candidate_shard(shard: Mapping[str, Any], index: int) -> JsonDict:
    shard_ref = _required_ref(shard, ("candidate_ref", "shardId", "shard_id", "id", "ref"), f"selected_shards[{index}]")
    section = _optional_text(shard, ("section",))
    logical_kind = _optional_text(shard, ("logicalKind", "logical_kind"))
    encoding = _optional_text(shard, ("encoding",))
    content_digest = _optional_text(shard, ("contentDigest", "content_digest"))
    routing_keys = _ref_list(_choose_optional_value(shard, ("routingKeys", "routing_keys")), f"selected_shards[{index}].routingKeys")
    candidate: JsonDict = {
        "candidate_ref": shard_ref,
        "section": section,
        "logical_kind": logical_kind,
        "encoding": encoding,
        "content_digest": content_digest,
        "routing_key_count": len(routing_keys),
    }
    if routing_keys:
        candidate["routing_refs"] = routing_keys
    return candidate


def _normalize_tooling_profile(profile: Mapping[str, Any]) -> JsonDict:
    tool_id = _required_text(profile, "tool_id")
    result: JsonDict = {
        "tool_id": tool_id,
    }
    for key in ("kind", "max_authority", "validation_mode", "repair_mode"):
        value = profile.get(key)
        if value is not None:
            result[key] = _required_text({key: value}, key)
    for key in ("promotion_requires_gate", "candidate_only", "non_authoritative", "read_only"):
        if key in profile:
            result[key] = _require_bool(profile, key)
    authority_notes = profile.get("authority_notes")
    if authority_notes is not None:
        if not isinstance(authority_notes, Mapping):
            raise ToolInputError("tooling_profile.authority_notes must be an object")
        result["authority_notes"] = dict(authority_notes)
    authority_boundary = profile.get("authority_boundary")
    if authority_boundary is not None:
        if not isinstance(authority_boundary, Mapping):
            raise ToolInputError("tooling_profile.authority_boundary must be an object")
        normalized_boundary = dict(authority_boundary)
        result["authority_boundary"] = normalized_boundary
        for key in ("read_only", "non_authoritative", "candidate_only", "promotion_authority", "canonical_truth_mutated"):
            if key in normalized_boundary:
                value = normalized_boundary[key]
                if not isinstance(value, bool):
                    raise ToolInputError(f"tooling_profile.authority_boundary.{key} must be boolean")
    return result


def _artifact_identity_summary(artifact_identity: Mapping[str, Any]) -> JsonDict:
    return {
        key: _required_text(artifact_identity, key)
        for key in ("contractVersion", "artifactId", "artifactRevision", "artifactClass", "createdAtUtc")
    }


def _summary_text(headline: str, **parts: Any) -> str:
    details = ", ".join(f"{key}={value}" for key, value in parts.items())
    return f"{headline} ({details})" if details else headline


def _mapping(payload: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = payload.get(key)
    if not isinstance(value, Mapping):
        raise ToolInputError(f"Expected object field: {key}")
    return dict(value)


def _mapping_sequence(payload: Mapping[str, Any], key: str) -> list[Mapping[str, Any]]:
    value = payload.get(key)
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise ToolInputError(f"Expected array field: {key}")
    items: list[Mapping[str, Any]] = []
    for item in value:
        if not isinstance(item, Mapping):
            raise ToolInputError(f"Expected object entries in {key}")
        items.append(dict(item))
    if not items:
        raise ToolInputError(f"{key} must not be empty")
    return items


def _ref_list(value: Any, label: str) -> list[str]:
    if value is None:
        return []
    if isinstance(value, (str, bytes, bytearray)):
        refs = [value]
    elif isinstance(value, Sequence):
        refs = list(value)
    else:
        raise ToolInputError(f"Expected array field: {label}")
    normalized: list[str] = []
    for item in refs:
        normalized.append(_required_ref_item(item, label))
    return _unique_strings(normalized)


def _required_ref_item(item: Any, label: str) -> str:
    if isinstance(item, str) and item.strip():
        return item.strip()
    if isinstance(item, Mapping):
        for key in ("ref", "id", "uri", "value"):
            value = item.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    raise ToolInputError(f"Expected string refs in {label}")


def _required_ref(mapping: Mapping[str, Any], keys: Sequence[str], label: str) -> str:
    for key in keys:
        value = mapping.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    raise ToolInputError(f"{label} is missing a required ref")


def _choose_optional_value(mapping: Mapping[str, Any], keys: Sequence[str]) -> Any:
    for key in keys:
        if key in mapping:
            return mapping.get(key)
    return None


def _choose_text(mapping: Mapping[str, Any], keys: Sequence[str], label: str) -> str:
    for key in keys:
        value = mapping.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    raise ToolInputError(f"{label} is missing required text")


def _optional_text(mapping: Mapping[str, Any], keys: Sequence[str]) -> str | None:
    for key in keys:
        value = mapping.get(key)
        if isinstance(value, str):
            stripped = value.strip()
            if stripped:
                return stripped
    return None


def _required_text(mapping: Mapping[str, Any], key: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ToolInputError(f"Expected non-empty string field: {key}")
    return value.strip()


def _require_str(mapping: Mapping[str, Any], key: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ToolInputError(f"Expected non-empty string field: {key}")
    return value.strip()


def _require_bool(mapping: Mapping[str, Any], key: str) -> bool:
    value = mapping.get(key)
    if isinstance(value, bool):
        return value
    raise ToolInputError(f"Expected boolean field: {key}")


def _require_true(mapping: Mapping[str, Any], key: str) -> None:
    if key not in mapping:
        raise ToolInputError(f"Expected boolean field: {key}")
    if mapping.get(key) is not True:
        raise ToolInputError(f"{key} must be true")


def _reject_true(mapping: Mapping[str, Any], key: str) -> None:
    if mapping.get(key) is True:
        raise ToolInputError(f"{key} must be false")


def _optional_number(value: Any) -> int | float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return value


def _compact_text(value: str, limit: int = 240) -> str:
    text = " ".join(value.split())
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def _unique_strings(values: Sequence[str] | Sequence[Any]) -> list[str]:
    items: list[str] = []
    for value in values:
        text = str(value).strip()
        if text and text not in items:
            items.append(text)
    return items
