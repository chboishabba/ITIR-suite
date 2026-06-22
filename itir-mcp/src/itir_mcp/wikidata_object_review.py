from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from .contracts import JsonDict, ToolInputError
from .domain_tools import climate_claim_review, gwb_follow_graph, wikidata_migration_candidate, wikidata_review_packet


VERSION = "itir.wikidata.object_review_bundle.v1"

_AUTHORITY_BOUNDARY: JsonDict = {
    "read_only": True,
    "non_authoritative": True,
    "canonical_truth_mutated": False,
    "candidate_only": True,
    "promotion_authority": False,
}

_CLIMATE_PROPERTIES = frozenset({"P5991", "P14143"})
_GWB_TERMS = ("gwb", "brexit", "withdrawal", "government white paper")


def normalize_wikidata_objects(value: Any) -> JsonDict:
    objects = _object_items(value)
    normalized_objects: list[JsonDict] = []
    statements: list[JsonDict] = []
    property_hints: list[str] = []
    class_hints: list[str] = []
    citations: list[str] = []

    for object_index, (object_key, raw_object) in enumerate(objects, start=1):
        qid = _entity_id(raw_object, object_key, object_index)
        label = _entity_label(raw_object)
        entity_ref = f"wikidata:{qid}"
        claim_rows = _claim_rows(raw_object, qid)
        normalized_objects.append(
            {
                "entity_id": qid,
                "entity_ref": entity_ref,
                "label": label,
                "claim_count": len(claim_rows),
                "property_ids": _unique([row["property_id"] for row in claim_rows]),
            }
        )
        for row in claim_rows:
            property_id = row["property_id"]
            value_ref = row["value_ref"]
            statement_ref = row["statement_ref"]
            if property_id not in property_hints:
                property_hints.append(property_id)
            if property_id in {"P31", "P279"} and value_ref and value_ref not in class_hints:
                class_hints.append(value_ref)
            provenance_refs = [statement_ref]
            for ref in row["reference_refs"]:
                if ref not in provenance_refs:
                    provenance_refs.append(ref)
            for ref in provenance_refs:
                if ref not in citations:
                    citations.append(ref)
            statements.append(
                {
                    "statement_id": statement_ref,
                    "fact": _fact_text(qid, label, property_id, value_ref, row["value_label"]),
                    "provenance_refs": provenance_refs,
                    "status": "candidate",
                }
            )

    return {
        "object_count": len(normalized_objects),
        "statement_count": len(statements),
        "objects": normalized_objects,
        "statements": statements,
        "property_hints": property_hints,
        "class_hints": class_hints,
        "citations": citations,
        "authority_boundary": dict(_AUTHORITY_BOUNDARY),
    }


def wikidata_object_review_bundle(payload: Mapping[str, Any]) -> JsonDict:
    objects_value = _objects_value(payload)
    normalized = normalize_wikidata_objects(objects_value)
    lanes = _resolve_lanes(payload, normalized)
    tooling_profile = _tooling_profile(payload)

    constraints = _constraints_for(normalized)
    review_packet = wikidata_review_packet(
        {
            "statements": normalized["statements"],
            "constraints": constraints,
            "tooling_profile": tooling_profile,
            "provenance_refs": normalized["citations"],
        }
    )

    outputs: JsonDict = {
        "wikidata_review_packet": review_packet,
    }
    if "migration" in lanes:
        outputs["migration_candidate"] = wikidata_migration_candidate(
            {
                "statement_refs": [statement["statement_id"] for statement in normalized["statements"]],
                "property_hints": normalized["property_hints"],
                "class_hints": normalized["class_hints"],
                "expected_fields": _expected_fields(normalized),
                "characteristic_fields": ["label", "description"],
                "constraint_refs": [constraint["constraint_id"] for constraint in constraints],
                "report_refs": ["itir.wikidata.object_review_bundle"],
                "citations": normalized["citations"],
                "provenance_refs": normalized["citations"],
                "authority_label": "candidate-only",
            }
        )
    if "climate" in lanes:
        outputs["climate_claim_review"] = climate_claim_review(
            {
                "authority_label": "candidate-only",
                "gate_requirements": {
                    "promotion_requires_gate": True,
                    "review_gate": "climate_nat_review",
                },
                "claims": _climate_claims(normalized),
                "citations": normalized["citations"],
                "provenance_refs": normalized["citations"],
            }
        )
    if "gwb" in lanes:
        outputs["gwb_follow_graph"] = gwb_follow_graph(_gwb_payload(normalized))

    return {
        "version": VERSION,
        "domain": "wikidata",
        "bundle_kind": "candidate_object_review_bundle",
        "candidate_only": True,
        "non_authoritative": True,
        "promoted_claims": False,
        "truth_claims": False,
        "input_shape": _input_shape(objects_value),
        "requested_lanes": lanes,
        "object_count": normalized["object_count"],
        "statement_count": normalized["statement_count"],
        "objects": normalized["objects"],
        "statement_refs": [statement["statement_id"] for statement in normalized["statements"]],
        "property_hints": normalized["property_hints"],
        "class_hints": normalized["class_hints"],
        "citations": normalized["citations"],
        "outputs": outputs,
        "authority_boundary": dict(_AUTHORITY_BOUNDARY),
        "summary": (
            "Candidate-only Wikidata object review bundle "
            f"(objects={normalized['object_count']}, statements={normalized['statement_count']}, lanes={','.join(lanes)})"
        ),
    }


def _objects_value(payload: Mapping[str, Any]) -> Any:
    for key in ("objects", "wikidata_objects", "wikidata_object", "object", "entities", "entity"):
        if key in payload:
            return payload[key]
    raise ToolInputError("Expected Wikidata object input in objects, object, entities, or entity")


def _object_items(value: Any) -> list[tuple[str | None, Mapping[str, Any]]]:
    if isinstance(value, Mapping):
        if _looks_like_entity(value):
            return [(None, dict(value))]
        items: list[tuple[str | None, Mapping[str, Any]]] = []
        for key, item in value.items():
            if not isinstance(item, Mapping):
                raise ToolInputError("Wikidata object dict values must be objects")
            items.append((str(key), dict(item)))
        if not items:
            raise ToolInputError("Wikidata object dict must not be empty")
        return items
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        items = []
        for item in value:
            if not isinstance(item, Mapping):
                raise ToolInputError("Wikidata object list entries must be objects")
            items.append((None, dict(item)))
        if not items:
            raise ToolInputError("Wikidata object list must not be empty")
        return items
    raise ToolInputError("Wikidata object input must be an object, list, or dict of objects")


def _looks_like_entity(value: Mapping[str, Any]) -> bool:
    return any(key in value for key in ("id", "entity_id", "qid", "claims", "statements", "sitelinks", "labels"))


def _entity_id(entity: Mapping[str, Any], object_key: str | None, index: int) -> str:
    for key in ("id", "entity_id", "qid"):
        value = entity.get(key)
        if isinstance(value, str) and value.strip():
            return _qid(value)
    if object_key:
        return _qid(object_key)
    raise ToolInputError(f"wikidata object {index} is missing id/entity_id/qid")


def _qid(value: str) -> str:
    text = value.strip()
    if text.startswith("wikidata:"):
        text = text.split(":", 1)[1]
    if not text:
        raise ToolInputError("empty Wikidata id")
    return text


def _entity_label(entity: Mapping[str, Any]) -> str | None:
    label = entity.get("label")
    if isinstance(label, str) and label.strip():
        return _compact(label)
    labels = entity.get("labels")
    if isinstance(labels, Mapping):
        en = labels.get("en")
        if isinstance(en, Mapping) and isinstance(en.get("value"), str):
            return _compact(en["value"])
        if isinstance(en, str):
            return _compact(en)
    return None


def _claim_rows(entity: Mapping[str, Any], qid: str) -> list[JsonDict]:
    claims = entity.get("claims") or entity.get("statements")
    if claims is None:
        return []
    if not isinstance(claims, Mapping):
        raise ToolInputError(f"{qid}.claims must be an object")
    rows: list[JsonDict] = []
    for property_id_raw, claim_value in claims.items():
        property_id = str(property_id_raw)
        claim_items = claim_value if isinstance(claim_value, list) else [claim_value]
        for index, item in enumerate(claim_items, start=1):
            rows.append(_claim_row(qid, property_id, item, index))
    return rows


def _claim_row(qid: str, property_id: str, item: Any, index: int) -> JsonDict:
    if isinstance(item, Mapping) and "mainsnak" in item:
        mainsnak = item.get("mainsnak")
        if not isinstance(mainsnak, Mapping):
            raise ToolInputError(f"{qid}.{property_id}[{index}].mainsnak must be an object")
        property_id = str(mainsnak.get("property") or property_id)
        value_ref, value_label = _snak_value(mainsnak)
        statement_id = str(item.get("id") or f"{qid}${property_id}-{index}")
        references = _reference_refs(item)
        return {
            "statement_ref": f"wikidata:{statement_id}",
            "property_id": property_id,
            "value_ref": value_ref,
            "value_label": value_label,
            "reference_refs": references,
        }
    value_ref, value_label = _simple_value(item)
    return {
        "statement_ref": f"wikidata:{qid}#{property_id}:{index}",
        "property_id": property_id,
        "value_ref": value_ref,
        "value_label": value_label,
        "reference_refs": [],
    }


def _snak_value(snak: Mapping[str, Any]) -> tuple[str, str | None]:
    datavalue = snak.get("datavalue")
    if not isinstance(datavalue, Mapping):
        return ("novalue", None)
    return _simple_value(datavalue.get("value"))


def _simple_value(value: Any) -> tuple[str, str | None]:
    if isinstance(value, Mapping):
        if isinstance(value.get("id"), str):
            return (value["id"], _label_from_mapping(value))
        if isinstance(value.get("numeric-id"), int):
            return (f"Q{value['numeric-id']}", _label_from_mapping(value))
        if isinstance(value.get("amount"), str):
            unit = value.get("unit")
            suffix = f" {unit}" if isinstance(unit, str) and unit not in {"1", ""} else ""
            return (value["amount"] + suffix, None)
        if isinstance(value.get("time"), str):
            return (value["time"], None)
        if isinstance(value.get("text"), str):
            return (_compact(value["text"]), None)
    if isinstance(value, str):
        return (_compact(value), None)
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return (str(value), None)
    return (_compact(repr(value)), None)


def _label_from_mapping(value: Mapping[str, Any]) -> str | None:
    for key in ("label", "text", "value"):
        item = value.get(key)
        if isinstance(item, str) and item.strip():
            return _compact(item)
    return None


def _reference_refs(item: Mapping[str, Any]) -> list[str]:
    refs = item.get("references")
    if not isinstance(refs, list):
        return []
    result: list[str] = []
    for index, ref in enumerate(refs, start=1):
        if isinstance(ref, Mapping):
            ref_hash = ref.get("hash")
            if isinstance(ref_hash, str) and ref_hash.strip():
                result.append(f"wikidata:ref:{ref_hash.strip()}")
            else:
                result.append(f"wikidata:ref:{index}")
    return _unique(result)


def _fact_text(qid: str, label: str | None, property_id: str, value_ref: str, value_label: str | None) -> str:
    subject = f"{qid} ({label})" if label else qid
    value = f"{value_ref} ({value_label})" if value_label else value_ref
    return _compact(f"{subject} has {property_id} {value}")


def _constraints_for(normalized: Mapping[str, Any]) -> list[JsonDict]:
    statement_refs = [statement["statement_id"] for statement in normalized["statements"]]
    return [
        {
            "constraint_id": "itir.wikidata.object_review.input_shape",
            "status": "diagnostic",
            "severity": "info",
            "message": "Input Wikidata objects were normalized into compact candidate statements.",
            "candidate_refs": statement_refs,
        },
        {
            "constraint_id": "itir.wikidata.object_review.non_authority",
            "status": "diagnostic",
            "severity": "info",
            "message": "Object review bundle is candidate-only and cannot promote Wikidata statements.",
            "candidate_refs": statement_refs,
        },
    ]


def _tooling_profile(payload: Mapping[str, Any]) -> JsonDict:
    profile = payload.get("tooling_profile")
    if isinstance(profile, Mapping):
        return dict(profile)
    return {
        "tool_id": "itir.wikidata.object_review_bundle",
        "kind": "validation",
        "max_authority": "receipt",
        "candidate_only": True,
        "non_authoritative": True,
        "read_only": True,
        "promotion_requires_gate": False,
    }


def _resolve_lanes(payload: Mapping[str, Any], normalized: Mapping[str, Any]) -> list[str]:
    requested = payload.get("lanes", "auto")
    if requested == "auto" or requested is None:
        lanes = ["wikidata", "migration"]
        if _has_climate_hint(payload, normalized):
            lanes.append("climate")
        if _has_gwb_hint(payload, normalized):
            lanes.append("gwb")
        return lanes
    if isinstance(requested, str):
        items = [requested]
    elif isinstance(requested, Sequence) and not isinstance(requested, (bytes, bytearray)):
        items = list(requested)
    else:
        raise ToolInputError("lanes must be auto, a string, or an array of strings")
    lanes = []
    aliases = {"nat": "climate", "climate_nat": "climate", "review": "wikidata"}
    for item in items:
        if not isinstance(item, str) or not item.strip():
            raise ToolInputError("lanes entries must be strings")
        lane = aliases.get(item.strip(), item.strip())
        if lane not in {"wikidata", "migration", "climate", "gwb"}:
            raise ToolInputError(f"unknown lane: {lane}")
        if lane not in lanes:
            lanes.append(lane)
    if "wikidata" not in lanes:
        lanes.insert(0, "wikidata")
    return lanes


def _has_climate_hint(payload: Mapping[str, Any], normalized: Mapping[str, Any]) -> bool:
    if payload.get("domain") in {"climate", "climate_nat", "nat"}:
        return True
    return any(prop in _CLIMATE_PROPERTIES for prop in normalized.get("property_hints", []))


def _has_gwb_hint(payload: Mapping[str, Any], normalized: Mapping[str, Any]) -> bool:
    if payload.get("domain") in {"gwb", "brexit"}:
        return True
    blob = " ".join(
        str(part).lower()
        for part in list(normalized.get("property_hints", []))
        + list(normalized.get("class_hints", []))
        + [obj.get("label") for obj in normalized.get("objects", []) if isinstance(obj, Mapping) and obj.get("label")]
    )
    return any(term in blob for term in _GWB_TERMS)


def _expected_fields(normalized: Mapping[str, Any]) -> list[str]:
    fields = ["entity_id", "property", "value"]
    if normalized.get("class_hints"):
        fields.append("class")
    return fields


def _climate_claims(normalized: Mapping[str, Any]) -> list[JsonDict]:
    statements = normalized.get("statements", [])
    claims: list[JsonDict] = []
    for index, statement in enumerate(statements, start=1):
        if not isinstance(statement, Mapping):
            continue
        text = str(statement.get("fact") or "")
        if any(prop in text for prop in _CLIMATE_PROPERTIES):
            claims.append(
                {
                    "claim_id": f"climate:{statement['statement_id']}",
                    "normal_form": f"wikidata_climate:{statement['statement_id']}",
                    "rendered_claim": text,
                    "candidate_status": "candidate",
                    "support_count": 0,
                    "contradiction_count": 0,
                    "citations": list(statement.get("provenance_refs") or []),
                    "provenance_refs": list(statement.get("provenance_refs") or []),
                    "authority_label": "candidate-only",
                }
            )
    if claims:
        return claims
    return [
        {
            "claim_id": "climate:wikidata-object-review",
            "normal_form": "wikidata_climate:object_review(candidate)",
            "rendered_claim": "Wikidata object review requested Climate NAT candidate assessment.",
            "candidate_status": "candidate",
            "support_count": 0,
            "contradiction_count": 0,
            "citations": list(normalized.get("citations", [])),
            "provenance_refs": list(normalized.get("citations", [])),
            "authority_label": "candidate-only",
        }
    ]


def _gwb_payload(normalized: Mapping[str, Any]) -> JsonDict:
    statement_refs = [str(statement["statement_id"]) for statement in normalized.get("statements", []) if isinstance(statement, Mapping)]
    if not statement_refs:
        statement_refs = ["wikidata:object-review"]
    authority_ref = "authority:gwb_external_review"
    return {
        "authority_label": "external authority follow graph",
        "source_refs": statement_refs,
        "authority_refs": [authority_ref],
        "follow_edges": [
            {
                "edge_ref": f"gwb-follow:{index}",
                "source_ref": ref,
                "authority_ref": authority_ref,
                "relation": "requires_external_authority_review",
                "citations": list(normalized.get("citations", [])),
                "provenance_refs": [ref],
            }
            for index, ref in enumerate(statement_refs, start=1)
        ],
        "unresolved_obligations": [
            {
                "obligation_id": "gwb:external-authority-review",
                "status": "open",
                "source_refs": statement_refs,
                "authority_refs": [authority_ref],
                "citations": list(normalized.get("citations", [])),
                "provenance_refs": statement_refs,
            }
        ],
        "citations": list(normalized.get("citations", [])),
        "provenance_refs": statement_refs,
    }


def _input_shape(value: Any) -> str:
    if isinstance(value, Mapping):
        return "single" if _looks_like_entity(value) else "dict"
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return "list"
    return "unknown"


def _compact(value: str, limit: int = 240) -> str:
    text = " ".join(value.strip().split())
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "..."


def _unique(items: Sequence[str]) -> list[str]:
    result: list[str] = []
    for item in items:
        if item not in result:
            result.append(item)
    return result
