from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from .pnf_spectral_numeric_abi import spectral_parity_hash, validate_spectral_numeric_abi


VERSION = "itir.pnf.spectral_candidate_packet.v0_1"

_FORBIDDEN_AUTHORITY_KEYS = {
    "truth",
    "support",
    "admissibility",
    "runtime",
    "promoted",
    "routing",
    "vector",
    "truth_authority",
    "support_authority",
    "admissibility_authority",
    "promotion_authority",
    "promotion",
    "promotion_enabled",
}


def build_candidate_spectral_packet(
    partial_view: Mapping[str, Any],
    spectral_payload_summary_or_payload: Mapping[str, Any],
) -> dict[str, Any]:
    partial = _mapping(partial_view, "partial_view")
    _reject_authority_creep(partial, "partial_view")

    graph_refs = _graph_refs(partial)
    spectral_input = _mapping(spectral_payload_summary_or_payload, "spectral_payload_summary_or_payload")
    _reject_authority_creep(spectral_input, "spectral_payload_summary_or_payload")

    if _looks_like_full_spectral_payload(spectral_input):
        validated_summary = validate_spectral_numeric_abi(dict(spectral_input))
        candidate_refs = _candidate_refs_from_full_payload(spectral_input)
        validation = {"status": "validated", "summary": validated_summary}
        parity_hash = validated_summary.get("parity_hash")
        summary_for_projection: Mapping[str, Any] = validated_summary
    else:
        summary_for_projection = _summary_payload(spectral_input)
        candidate_refs = _candidate_refs_from_summary(spectral_input)
        parity_hash = _parity_hash_from_summary(spectral_input)
        validation = {"status": "not_performed", "summary": _summary_projection(summary_for_projection)}

    phi_psi_ref_summary = _phi_psi_ref_summary(candidate_refs, summary_for_projection, graph_refs)
    packet: dict[str, Any] = {
        "version": VERSION,
        "candidate_only": True,
        "non_authoritative": True,
        "graph_refs": graph_refs,
        "candidate_refs": candidate_refs,
        "phi_psi_ref_summary": phi_psi_ref_summary,
        "validation": validation,
        "authority_boundary": {
            "read_only": True,
            "non_authoritative": True,
            "candidate_only": True,
            "canonical_truth_mutated": False,
            "truth": False,
            "support": False,
            "admissibility": False,
            "runtime": False,
            "promoted": False,
            "routing": False,
            "vector": False,
        },
    }
    if parity_hash is not None:
        packet["parity_hash"] = parity_hash
    return packet


def _looks_like_full_spectral_payload(payload: Mapping[str, Any]) -> bool:
    required_keys = {
        "schema",
        "graph_version",
        "operator_profile",
        "object_registry",
        "row_map",
        "residual_edge_table",
        "adjacency",
        "degree",
        "laplacian",
        "spectral_coordinates",
        "gemv",
        "receipts",
        "rebuild_witness",
        "authority",
        "parity_hash",
    }
    return required_keys.issubset(payload.keys())


def _graph_refs(partial_view: Mapping[str, Any]) -> dict[str, Any]:
    graph_refs: dict[str, Any] = {
        "artifact_identity": _artifact_identity(partial_view),
        "selectors": _string_list(partial_view.get("selectors")),
        "selected_shard_ids": _string_list(partial_view.get("selected_shard_ids")),
        "selected_sections": _string_list(partial_view.get("selected_sections")),
        "selected_shard_count": len(_string_list(partial_view.get("selected_shard_ids"))),
    }
    for key in ("completeness", "subset_of_artifact"):
        if key in partial_view:
            graph_refs[key] = partial_view[key]
    return graph_refs


def _artifact_identity(partial_view: Mapping[str, Any]) -> dict[str, Any]:
    identity = partial_view.get("artifact_identity")
    if not isinstance(identity, Mapping):
        return {}
    allowed = ("contractVersion", "artifactId", "artifactRevision", "artifactClass", "createdAtUtc")
    return {key: identity[key] for key in allowed if key in identity}


def _summary_payload(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    if "summary" in payload and isinstance(payload.get("summary"), Mapping):
        return payload["summary"]  # type: ignore[return-value]
    return payload


def _summary_projection(summary_payload: Mapping[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key in ("schema", "graph_version", "operator_profile", "objects", "rows", "spectral_dimensions", "probe_rows", "edge_kinds", "gemv_rows", "parity_hash", "candidate_only", "diagnostic_only"):
        if key in summary_payload:
            result[key] = summary_payload[key]
    if "validation" in summary_payload:
        result["validation"] = summary_payload["validation"]
    return result


def _candidate_refs_from_full_payload(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    spectral_coordinates = _mapping(payload.get("spectral_coordinates"), "spectral_coordinates")
    psi = _mapping(spectral_coordinates.get("psi"), "spectral_coordinates.psi")
    probes = psi.get("probes")
    if not isinstance(probes, list):
        return []
    refs: list[dict[str, Any]] = []
    for probe_index, probe_item in enumerate(probes):
        probe = _mapping(probe_item, f"spectral_coordinates.psi.probes[{probe_index}]")
        probe_id = _text(probe.get("probe_id"))
        for index, ref_item in enumerate(probe.get("candidate_refs") or []):
            ref = _mapping(ref_item, f"spectral_coordinates.psi.probes[{probe_index}].candidate_refs[{index}]")
            refs.append(
                {
                    "probe_id": probe_id,
                    "candidate_ref": _text(ref.get("candidate_ref")),
                    "row": _int(ref.get("row"), "row"),
                    "object_id": _text(ref.get("object_id")),
                    "rank": _int(ref.get("rank", index), "rank"),
                }
            )
    return refs


def _candidate_refs_from_summary(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    if isinstance(payload.get("candidate_refs"), list):
        return [_compact_candidate_ref(ref, index) for index, ref in enumerate(payload["candidate_refs"]) if isinstance(ref, Mapping)]

    spectral_coordinates = payload.get("spectral_coordinates")
    if isinstance(spectral_coordinates, Mapping):
        psi = spectral_coordinates.get("psi")
        if isinstance(psi, Mapping):
            probes = psi.get("probes")
            if isinstance(probes, list):
                refs: list[dict[str, Any]] = []
                for probe_index, probe_item in enumerate(probes):
                    if not isinstance(probe_item, Mapping):
                        continue
                    probe_id = _text(probe_item.get("probe_id"))
                    candidate_refs = probe_item.get("candidate_refs")
                    if not isinstance(candidate_refs, list):
                        continue
                    for index, ref_item in enumerate(candidate_refs):
                        if not isinstance(ref_item, Mapping):
                            continue
                        refs.append(
                            {
                                "probe_id": probe_id,
                                "candidate_ref": _text(ref_item.get("candidate_ref")),
                                "row": _int(ref_item.get("row"), "row"),
                                "object_id": _text(ref_item.get("object_id")),
                                "rank": _int(ref_item.get("rank", index), "rank"),
                            }
                        )
                return refs

    return []


def _compact_candidate_ref(ref: Mapping[str, Any], index: int) -> dict[str, Any]:
    result = {
        "candidate_ref": _text(ref.get("candidate_ref")),
        "row": _int(ref.get("row"), "row"),
        "object_id": _text(ref.get("object_id")),
        "rank": _int(ref.get("rank", index), "rank"),
    }
    probe_id = _text(ref.get("probe_id"))
    if probe_id:
        result["probe_id"] = probe_id
    return result


def _phi_psi_ref_summary(
    candidate_refs: Sequence[Mapping[str, Any]],
    summary_payload: Mapping[str, Any],
    graph_refs: Mapping[str, Any],
) -> dict[str, Any]:
    candidate_probe_ids = []
    candidate_rows = []
    for ref in candidate_refs:
        probe_id = _text(ref.get("probe_id"))
        if probe_id and probe_id not in candidate_probe_ids:
            candidate_probe_ids.append(probe_id)
        row = ref.get("row")
        if isinstance(row, int) and row not in candidate_rows:
            candidate_rows.append(row)

    rows = _int(summary_payload.get("rows", len(candidate_rows)), "rows")
    probe_rows = _int(summary_payload.get("probe_rows", len(candidate_probe_ids)), "probe_rows")
    return {
        "phi": {
            "rows": rows,
            "objects": _int(summary_payload.get("objects", 0), "objects") if "objects" in summary_payload else None,
            "spectral_dimensions": _int(summary_payload.get("spectral_dimensions", 0), "spectral_dimensions")
            if "spectral_dimensions" in summary_payload
            else None,
        },
        "psi": {
            "probe_rows": probe_rows,
            "probe_ids": candidate_probe_ids,
            "candidate_ref_count": len(candidate_refs),
        },
        "refs": {
            "graph_ref_count": len(_string_list(graph_refs.get("selected_shard_ids"))),
            "candidate_ref_count": len(candidate_refs),
            "candidate_rows": candidate_rows,
            "parity_hash_present": "parity_hash" in summary_payload and bool(summary_payload.get("parity_hash")),
        },
    }


def _parity_hash_from_summary(payload: Mapping[str, Any]) -> str | None:
    parity_hash = payload.get("parity_hash")
    if isinstance(parity_hash, str) and parity_hash.strip():
        return parity_hash.strip()
    summary = payload.get("summary")
    if isinstance(summary, Mapping):
        parity_hash = summary.get("parity_hash")
        if isinstance(parity_hash, str) and parity_hash.strip():
            return parity_hash.strip()
    return None


def _reject_authority_creep(payload: Mapping[str, Any], label: str) -> None:
    _scan_forbidden_authority_creep(payload, label)


def _scan_forbidden_authority_creep(value: Any, path: str) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            next_path = f"{path}.{key}"
            if key in _FORBIDDEN_AUTHORITY_KEYS and item is True:
                raise ValueError(f"{next_path} must not be true")
            _scan_forbidden_authority_creep(item, next_path)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _scan_forbidden_authority_creep(item, f"{path}[{index}]")


def _mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} must be an object")
    return dict(value)


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _text(value: Any) -> str:
    if not isinstance(value, str):
        return "" if value is None else str(value).strip()
    return value.strip()


def _int(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        try:
            return int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{label} must be an integer") from exc
    return value
