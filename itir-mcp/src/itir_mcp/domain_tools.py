from __future__ import annotations

from typing import Any, Mapping, Sequence

from .contracts import JsonDict, ToolInputError


WIKIDATA_REVIEW_PACKET_VERSION = "itir.wikidata.review_packet.v1"
WIKIDATA_MIGRATION_CANDIDATE_VERSION = "itir.wikidata.migration_candidate.v1"
ZELPH_PARTIAL_CLOSURE_VERSION = "itir.zelph.partial_closure.v1"
CLIMATE_CLAIM_REVIEW_VERSION = "itir.climate.claim_review.v1"
GWB_FOLLOW_GRAPH_VERSION = "itir.gwb.follow_graph.v1"

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


def wikidata_migration_candidate(payload: Mapping[str, Any]) -> JsonDict:
    statement_refs = _ref_list(payload.get("statement_refs"), "statement_refs")
    property_hints = _ref_list(payload.get("property_hints"), "property_hints")
    class_hints = _ref_list(payload.get("class_hints"), "class_hints")
    expected_fields = _field_list(payload.get("expected_fields"), "expected_fields")
    characteristic_fields = _field_list(payload.get("characteristic_fields"), "characteristic_fields")
    constraint_refs = _ref_list(payload.get("constraint_refs"), "constraint_refs")
    repair_refs = _ref_list(payload.get("repair_refs"), "repair_refs")
    report_refs = _ref_list(payload.get("report_refs"), "report_refs")
    citations = _ref_list(payload.get("citations"), "citations")
    provenance_refs = _ref_list(payload.get("provenance_refs"), "provenance_refs")
    authority_label = _required_text(payload, "authority_label")

    normalized_payload_parts = (
        statement_refs,
        property_hints,
        class_hints,
        expected_fields,
        characteristic_fields,
        constraint_refs,
        repair_refs,
        report_refs,
        citations,
        provenance_refs,
    )
    if not any(normalized_payload_parts):
        raise ToolInputError("migration candidate payload must include structural refs or hints")

    authority_boundary = dict(_AUTHORITY_BOUNDARY)
    authority_boundary["domain"] = "wikidata"

    return {
        "version": WIKIDATA_MIGRATION_CANDIDATE_VERSION,
        "domain": "wikidata",
        "packet_kind": "candidate_migration_packet",
        "candidate_only": True,
        "non_authoritative": True,
        "promoted_claims": False,
        "truth_claims": False,
        "authority_label": authority_label,
        "statement_refs": statement_refs,
        "property_hints": property_hints,
        "class_hints": class_hints,
        "expected_fields": expected_fields,
        "characteristic_fields": characteristic_fields,
        "constraint_refs": constraint_refs,
        "repair_refs": repair_refs,
        "report_refs": report_refs,
        "citations": citations,
        "provenance_refs": provenance_refs,
        "authority_boundary": authority_boundary,
        "summary": _summary_text(
            "Candidate-only Wikidata migration packet",
            statements=len(statement_refs),
            property_hints=len(property_hints),
            class_hints=len(class_hints),
            expected_fields=len(expected_fields),
            characteristic_fields=len(characteristic_fields),
            citations=len(citations),
        ),
    }


def climate_claim_review(payload: Mapping[str, Any]) -> JsonDict:
    claims = _mapping_sequence(payload, "claims")
    packet_gate_requirements = _normalize_gate_requirements(
        payload.get("gate_requirements"),
        "gate_requirements",
        default={"promotion_requires_gate": True, "review_gate": "climate_nat_review"},
    )
    authority_label = _normalize_candidate_authority_label(payload.get("authority_label"), "authority_label")
    payload_citations = _ref_list(payload.get("citations"), "citations")
    payload_provenance_refs = _ref_list(payload.get("provenance_refs"), "provenance_refs")

    review_claims: list[JsonDict] = []
    citations: list[str] = []
    provenance_refs: list[str] = []
    total_support_count = 0
    total_contradiction_count = 0

    for index, claim in enumerate(claims, start=1):
        normalized = _normalize_climate_claim(claim, index, packet_gate_requirements)
        review_claims.append(normalized)
        total_support_count += normalized["support_count"]
        total_contradiction_count += normalized["contradiction_count"]
        for ref in normalized["citations"]:
            if ref not in citations:
                citations.append(ref)
        for ref in normalized["provenance_refs"]:
            if ref not in provenance_refs:
                provenance_refs.append(ref)

    for ref in payload_citations:
        if ref not in citations:
            citations.append(ref)
    for ref in payload_provenance_refs:
        if ref not in provenance_refs:
            provenance_refs.append(ref)

    authority_boundary = dict(_AUTHORITY_BOUNDARY)
    authority_boundary["domain"] = "climate_nat"

    return {
        "version": CLIMATE_CLAIM_REVIEW_VERSION,
        "domain": "climate_nat",
        "packet_kind": "candidate_claim_review_packet",
        "candidate_only": True,
        "non_authoritative": True,
        "promoted_claims": False,
        "truth_claims": False,
        "authority_label": authority_label,
        "gate_requirements": packet_gate_requirements,
        "claim_count": len(review_claims),
        "support_count": total_support_count,
        "contradiction_count": total_contradiction_count,
        "claims": review_claims,
        "citations": citations,
        "provenance_refs": provenance_refs,
        "authority_boundary": authority_boundary,
        "summary": _summary_text(
            "Candidate-only Climate NAT claim review packet",
            claims=len(review_claims),
            support=total_support_count,
            contradictions=total_contradiction_count,
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


def gwb_follow_graph(payload: Mapping[str, Any]) -> JsonDict:
    authority_label = _required_text(payload, "authority_label")
    _reject_follow_graph_authority_creep(payload)

    source_refs = _ref_list(_choose_optional_value(payload, ("source_refs", "sources", "source_ref")), "source_refs")
    authority_refs = _ref_list(
        _choose_optional_value(payload, ("authority_refs", "authorities", "authority_ref")),
        "authority_refs",
    )
    follow_edges = _mapping_sequence(payload, "follow_edges")
    unresolved_obligations = _optional_mapping_sequence(payload, "unresolved_obligations")
    citation_refs = _ref_list(_choose_optional_value(payload, ("citations", "citation_refs")), "citations")
    provenance_refs = _ref_list(_choose_optional_value(payload, ("provenance_refs",)), "provenance_refs")

    normalized_edges: list[JsonDict] = []
    normalized_obligations: list[JsonDict] = []
    for index, edge in enumerate(follow_edges, start=1):
        normalized_edge = _normalize_follow_graph_edge(edge, index)
        normalized_edges.append(normalized_edge)
        if normalized_edge["source_ref"] not in source_refs:
            source_refs.append(normalized_edge["source_ref"])
        if normalized_edge["authority_ref"] not in authority_refs:
            authority_refs.append(normalized_edge["authority_ref"])
        for ref in normalized_edge["citation_refs"]:
            if ref not in citation_refs:
                citation_refs.append(ref)
        for ref in normalized_edge["provenance_refs"]:
            if ref not in provenance_refs:
                provenance_refs.append(ref)

    for index, obligation in enumerate(unresolved_obligations, start=1):
        normalized_obligation = _normalize_follow_graph_obligation(obligation, index)
        normalized_obligations.append(normalized_obligation)
        for ref in normalized_obligation["source_refs"]:
            if ref not in source_refs:
                source_refs.append(ref)
        for ref in normalized_obligation["authority_refs"]:
            if ref not in authority_refs:
                authority_refs.append(ref)
        for ref in normalized_obligation["citation_refs"]:
            if ref not in citation_refs:
                citation_refs.append(ref)
        for ref in normalized_obligation["provenance_refs"]:
            if ref not in provenance_refs:
                provenance_refs.append(ref)

    if not source_refs:
        raise ToolInputError("source_refs must not be empty")
    if not authority_refs:
        raise ToolInputError("authority_refs must not be empty")
    if not normalized_edges:
        raise ToolInputError("follow_edges must not be empty")

    authority_boundary = dict(_AUTHORITY_BOUNDARY)
    authority_boundary["domain"] = "gwb"

    return {
        "version": GWB_FOLLOW_GRAPH_VERSION,
        "domain": "gwb",
        "graph_kind": "candidate_follow_graph",
        "candidate_only": True,
        "non_authoritative": True,
        "promoted_claims": False,
        "truth_claims": False,
        "authority_label": authority_label,
        "source_refs": source_refs,
        "authority_refs": authority_refs,
        "follow_edges": normalized_edges,
        "unresolved_obligations": normalized_obligations,
        "citations": citation_refs,
        "provenance_refs": provenance_refs,
        "summary": _summary_text(
            "Candidate-only GWB follow graph",
            sources=len(source_refs),
            authorities=len(authority_refs),
            edges=len(normalized_edges),
            unresolved_obligations=len(normalized_obligations),
            citations=len(citation_refs),
        ),
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


def _normalize_follow_graph_edge(edge: Mapping[str, Any], index: int) -> JsonDict:
    edge_ref = _optional_text(edge, ("edge_ref", "follow_edge_ref", "id", "ref"))
    source_ref = _required_ref(
        edge,
        ("source_ref", "source_id", "source", "from_ref", "from_id"),
        f"follow_edges[{index}]",
    )
    authority_ref = _required_ref(
        edge,
        ("authority_ref", "authority_id", "target_ref", "target", "to_ref", "to_id"),
        f"follow_edges[{index}]",
    )
    relation = _optional_text(edge, ("relation", "kind", "edge_kind")) or "follows"
    citation_refs = _ref_list(
        _choose_optional_value(edge, ("citations", "citation_refs", "source_citations")),
        f"follow_edges[{index}].citations",
    )
    provenance_refs = _ref_list(
        _choose_optional_value(edge, ("provenance_refs", "provenance", "source_refs")),
        f"follow_edges[{index}].provenance_refs",
    )
    normalized: JsonDict = {
        "source_ref": source_ref,
        "authority_ref": authority_ref,
        "relation": relation,
        "citation_refs": citation_refs,
        "provenance_refs": provenance_refs,
    }
    if edge_ref is not None:
        normalized["edge_ref"] = edge_ref
    return normalized


def _normalize_follow_graph_obligation(obligation: Mapping[str, Any], index: int) -> JsonDict:
    obligation_ref = _required_ref(
        obligation,
        ("obligation_ref", "obligation_id", "id", "ref"),
        f"unresolved_obligations[{index}]",
    )
    status = _optional_text(obligation, ("status", "kind", "state")) or "unresolved"
    source_refs = _ref_list(
        _choose_optional_value(obligation, ("source_refs", "source_ref", "source_id")),
        f"unresolved_obligations[{index}].source_refs",
    )
    authority_refs = _ref_list(
        _choose_optional_value(obligation, ("authority_refs", "authority_ref", "authority_id")),
        f"unresolved_obligations[{index}].authority_refs",
    )
    citation_refs = _ref_list(
        _choose_optional_value(obligation, ("citations", "citation_refs")),
        f"unresolved_obligations[{index}].citations",
    )
    provenance_refs = _ref_list(
        _choose_optional_value(obligation, ("provenance_refs", "provenance")),
        f"unresolved_obligations[{index}].provenance_refs",
    )
    return {
        "obligation_ref": obligation_ref,
        "status": status,
        "source_refs": source_refs,
        "authority_refs": authority_refs,
        "citation_refs": citation_refs,
        "provenance_refs": provenance_refs,
    }


def _normalize_climate_claim(
    claim: Mapping[str, Any],
    index: int,
    inherited_gate_requirements: Mapping[str, Any],
) -> JsonDict:
    claim_id = _required_ref(claim, ("claim_id", "claimId", "id", "ref"), f"claims[{index}]")
    normal_form = _choose_text(claim, ("normal_form", "normalForm", "normal"), f"claims[{index}]")
    rendered_claim = _choose_text(claim, ("rendered_claim", "renderedClaim", "claim", "summary"), f"claims[{index}]")
    candidate_status_value = _choose_optional_value(claim, ("candidate_status", "status", "claim_status"))
    if candidate_status_value is None:
        candidate_status = "candidate"
    elif not isinstance(candidate_status_value, str) or not candidate_status_value.strip():
        raise ToolInputError(f"claims[{index}].candidate_status must be a non-empty string")
    else:
        candidate_status = candidate_status_value.strip()
    support_count = _non_negative_count(claim.get("support_count"), f"claims[{index}].support_count")
    contradiction_count = _non_negative_count(
        claim.get("contradiction_count"), f"claims[{index}].contradiction_count"
    )
    citations = _ref_list(
        _choose_optional_value(claim, ("citations", "citation_refs", "source_refs")),
        f"claims[{index}].citations",
    )
    provenance_refs = _ref_list(
        _choose_optional_value(claim, ("provenance_refs", "source_refs")),
        f"claims[{index}].provenance_refs",
    )
    authority_label = _normalize_candidate_authority_label(
        _choose_optional_value(claim, ("authority_label",)), f"claims[{index}].authority_label"
    )
    gate_requirements = _normalize_gate_requirements(
        _choose_optional_value(claim, ("gate_requirements",)),
        f"claims[{index}].gate_requirements",
        default=inherited_gate_requirements,
    )
    return {
        "claim_id": claim_id,
        "normal_form": _compact_text(normal_form),
        "rendered_claim": _compact_text(rendered_claim),
        "candidate_status": candidate_status,
        "support_count": support_count,
        "contradiction_count": contradiction_count,
        "citations": citations,
        "provenance_refs": provenance_refs,
        "authority_label": authority_label,
        "gate_requirements": gate_requirements,
    }


def _normalize_candidate_authority_label(value: Any, label: str) -> str:
    if value is None:
        return "candidate-only"
    text = _compact_text(_required_text({"value": value}, "value"), limit=64)
    if text != "candidate-only":
        raise ToolInputError(f"{label} must be candidate-only")
    return text


def _normalize_gate_requirements(
    value: Any,
    label: str,
    *,
    default: Mapping[str, Any] | None = None,
) -> JsonDict:
    normalized: JsonDict = dict(default or {})
    if value is None:
        return normalized
    if not isinstance(value, Mapping):
        raise ToolInputError(f"Expected object field: {label}")

    recognized = False
    for key in ("promotion_requires_gate", "requires_gate", "requires_human_review", "requires_external_review"):
        if key in value:
            normalized[key] = _require_bool(value, key)
            recognized = True
    for key in ("gate_id", "gate_kind", "gate_process", "review_gate", "reviewer_role", "authority_label"):
        if key in value:
            normalized[key] = _compact_text(_required_text(value, key), limit=96)
            recognized = True
    if "authority_label" in normalized and normalized["authority_label"] != "candidate-only":
        raise ToolInputError(f"{label}.authority_label must be candidate-only")
    if not recognized:
        raise ToolInputError(f"{label} must include recognized gate requirements")
    return normalized


def _non_negative_count(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ToolInputError(f"Expected non-negative integer field: {label}")
    if value < 0:
        raise ToolInputError(f"{label} must be non-negative")
    return value


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


def _optional_mapping_sequence(payload: Mapping[str, Any], key: str) -> list[Mapping[str, Any]]:
    value = payload.get(key)
    if value is None:
        return []
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise ToolInputError(f"Expected array field: {key}")
    items: list[Mapping[str, Any]] = []
    for item in value:
        if not isinstance(item, Mapping):
            raise ToolInputError(f"Expected object entries in {key}")
        items.append(dict(item))
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


def _field_list(value: Any, label: str) -> list[str]:
    if value is None:
        return []
    if isinstance(value, (str, bytes, bytearray)):
        items = [value]
    elif isinstance(value, Sequence):
        items = list(value)
    else:
        raise ToolInputError(f"Expected array field: {label}")
    normalized: list[str] = []
    for item in items:
        if isinstance(item, str) and item.strip():
            text = item.strip()
        elif isinstance(item, Mapping):
            text = _required_ref_item(item, label)
        else:
            raise ToolInputError(f"Expected string fields in {label}")
        if text not in normalized:
            normalized.append(text)
    return normalized


def _required_ref_item(item: Any, label: str) -> str:
    if isinstance(item, str) and item.strip():
        return item.strip()
    if isinstance(item, Mapping):
        for key in ("ref", "id", "uri", "value", "field", "field_name", "name"):
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


def _reject_follow_graph_authority_creep(value: Any, *, path: str = "payload") -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            key_text = str(key).strip().lower()
            if key_text in {
                "promoted_claims",
                "truth_claims",
                "promotion_authority",
                "self_authorizing",
                "self_authorising",
                "canonical_truth_mutated",
            } and item is True:
                raise ToolInputError(f"{path}.{key} must be false")
            if key_text == "authority_label" and isinstance(item, str):
                normalized = item.strip().lower().replace("-", "_").replace(" ", "_")
                if normalized in {"promoted", "self_authorizing", "self_authorising"}:
                    raise ToolInputError("authority_label must not claim promotion or self-authorizing status")
            if key_text in {"status", "authority_status", "kind", "mode"} and isinstance(item, str):
                normalized = item.strip().lower().replace("-", "_").replace(" ", "_")
                if normalized in {"promoted", "self_authorizing", "self_authorising"}:
                    raise ToolInputError(f"{path}.{key} must not claim promotion or self-authorizing status")
            _reject_follow_graph_authority_creep(item, path=f"{path}.{key}")
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, item in enumerate(value):
            _reject_follow_graph_authority_creep(item, path=f"{path}[{index}]")
