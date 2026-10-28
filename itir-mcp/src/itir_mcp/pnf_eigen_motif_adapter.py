from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from .pnf_eigen_motif_loader import VERSION as LOADER_VERSION


VERSION = "itir.pnf.eigen_motif_component_props.v1"


class EigenMotifAdapterError(ValueError):
    """Raised when normalized motif records cannot be projected safely."""


def build_component_props(loaded: Mapping[str, Any]) -> dict[str, Any]:
    """Project normalized motif records into presentation-ready component props.

    This adapter contains all motif-specific display shaping. UI components
    should consume the returned props directly and must not parse typed support,
    recompute macroscopic status, rank motifs, or infer authority.
    """

    source = _mapping(loaded, "loaded")
    if source.get("version") != LOADER_VERSION:
        raise EigenMotifAdapterError(f"expected loader version {LOADER_VERSION}")

    if source.get("candidate_only") is not True or source.get("non_authoritative") is not True:
        raise EigenMotifAdapterError("loader authority boundary must remain candidate-only")

    motifs = source.get("motifs")
    if not _is_sequence(motifs):
        raise EigenMotifAdapterError("motifs must be an array")

    items: list[dict[str, Any]] = []
    for index, raw in enumerate(motifs):
        motif = _mapping(raw, f"motifs[{index}]")
        motif_id = _required_text(motif.get("motif_id"), f"motifs[{index}].motif_id")
        eigenvalue = _number(motif.get("eigenvalue"), f"motifs[{index}].eigenvalue")
        rank = _nonnegative_int(motif.get("rank"), f"motifs[{index}].rank")
        if motif.get("macroscopic") is not True:
            raise EigenMotifAdapterError(f"motifs[{index}] must be macroscopic")

        support = _normalized_support(motif.get("typed_support"), f"motifs[{index}].typed_support")
        values = [entry["value"] for entry in support]
        shapes = [entry["dependency_shape"] for entry in support]
        tokens = [entry["token"] for entry in support]

        items.append(
            {
                "key": motif_id,
                "motif_id": motif_id,
                "rank": rank,
                "eigenvalue": eigenvalue,
                "eigenvalue_label": f"λ={eigenvalue:.6g}",
                "title": " · ".join(values),
                "support_label": " · ".join(tokens),
                "support_path": values,
                "dependency_shapes": shapes,
                "segments": [
                    {
                        "kind": entry["kind"],
                        "label": entry["value"],
                        "dependency_shape": entry["dependency_shape"],
                    }
                    for entry in support
                ],
                "source_ref": _optional_text(motif.get("source_ref")),
            }
        )

    return {
        "version": VERSION,
        "bulk_edge": _number(source.get("bulk_edge"), "bulk_edge"),
        "motif_count": len(items),
        "items": items,
        "source_ref": _optional_text(source.get("source_ref")),
        "parity_hash": _optional_text(source.get("parity_hash")),
        "empty": len(items) == 0,
        "candidate_only": True,
        "non_authoritative": True,
        "authority_boundary": {
            "read_only": True,
            "canonical_truth_mutated": False,
            "component_inference_required": False,
            "promotion": False,
            "routing": False,
            "support_authority": False,
        },
    }


def _normalized_support(value: Any, label: str) -> list[dict[str, str]]:
    if not _is_sequence(value) or not value:
        raise EigenMotifAdapterError(f"{label} must be a non-empty array")

    result: list[dict[str, str]] = []
    for index, raw in enumerate(value):
        entry = _mapping(raw, f"{label}[{index}]")
        required = ("kind", "value", "dependency_shape", "token")
        missing = [key for key in required if not isinstance(entry.get(key), str) or not entry[key].strip()]
        if missing:
            raise EigenMotifAdapterError(
                f"{label}[{index}] missing normalized fields: {', '.join(missing)}"
            )
        token = entry["token"].strip()
        expected = f"{entry['kind'].strip()}:{entry['value'].strip()}:{entry['dependency_shape'].strip()}"
        if token != expected:
            raise EigenMotifAdapterError(f"{label}[{index}].token does not match normalized fields")
        result.append(
            {
                "kind": entry["kind"].strip(),
                "value": entry["value"].strip(),
                "dependency_shape": entry["dependency_shape"].strip(),
                "token": token,
            }
        )
    return result


def _mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise EigenMotifAdapterError(f"{label} must be an object")
    return dict(value)


def _required_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise EigenMotifAdapterError(f"{label} must be a non-empty string")
    return value.strip()


def _optional_text(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise EigenMotifAdapterError("optional text fields must be strings")
    stripped = value.strip()
    return stripped or None


def _number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise EigenMotifAdapterError(f"{label} must be numeric")
    return float(value)


def _nonnegative_int(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise EigenMotifAdapterError(f"{label} must be a non-negative integer")
    return value


def _is_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray))
