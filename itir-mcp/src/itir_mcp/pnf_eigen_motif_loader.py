from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any


VERSION = "itir.pnf.eigen_motif_loader.v1"


class EigenMotifLoadError(ValueError):
    """Raised when a spectral motif payload violates the loader contract."""


def load_macroscopic_eigen_motifs(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Normalize macroscopic PNF eigen-motifs from a server-side spectral payload.

    The loader owns the Marchenko-Pastur/macroscopic selection rule. Consumers
    receive already-normalized records and must not reinterpret eigenvalues or
    typed-support strings.

    A motif is macroscopic iff eigenvalue > bulk_edge. Rows are processed
    independently and never merged, clustered, or promoted by shared support.
    """

    source = _mapping(payload, "payload")
    _reject_unknown_keys(source, {"bulk_edge", "motifs", "source_ref", "parity_hash"}, "payload")

    bulk_edge = _finite_number(source.get("bulk_edge"), "bulk_edge")
    if bulk_edge < 0:
        raise EigenMotifLoadError("bulk_edge must be non-negative")

    raw_motifs = source.get("motifs")
    if not _is_sequence(raw_motifs):
        raise EigenMotifLoadError("motifs must be an array")

    normalized: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for index, raw in enumerate(raw_motifs):
        motif = _mapping(raw, f"motifs[{index}]")
        _reject_unknown_keys(
            motif,
            {"motif_id", "eigenvalue", "typed_support", "macroscopic", "rank", "source_ref"},
            f"motifs[{index}]",
        )

        motif_id = _required_text(motif.get("motif_id"), f"motifs[{index}].motif_id")
        if motif_id in seen_ids:
            raise EigenMotifLoadError(f"duplicate motif_id: {motif_id}")
        seen_ids.add(motif_id)

        eigenvalue = _finite_number(motif.get("eigenvalue"), f"motifs[{index}].eigenvalue")
        is_macroscopic = eigenvalue > bulk_edge
        if "macroscopic" in motif:
            declared = motif["macroscopic"]
            if not isinstance(declared, bool):
                raise EigenMotifLoadError(f"motifs[{index}].macroscopic must be boolean")
            if declared is not is_macroscopic:
                raise EigenMotifLoadError(
                    f"motifs[{index}].macroscopic conflicts with eigenvalue > bulk_edge"
                )
        if not is_macroscopic:
            continue

        support = _typed_support(motif.get("typed_support"), f"motifs[{index}].typed_support")
        normalized.append(
            {
                "motif_id": motif_id,
                "eigenvalue": eigenvalue,
                "rank": _optional_nonnegative_int(motif.get("rank"), f"motifs[{index}].rank"),
                "typed_support": support,
                "support_count": len(support),
                "source_ref": _optional_text(motif.get("source_ref")),
                "macroscopic": True,
            }
        )

    normalized.sort(key=lambda row: (-row["eigenvalue"], row["motif_id"]))
    for derived_rank, motif in enumerate(normalized):
        if motif["rank"] is None:
            motif["rank"] = derived_rank

    return {
        "version": VERSION,
        "bulk_edge": bulk_edge,
        "motif_count": len(normalized),
        "motifs": normalized,
        "source_ref": _optional_text(source.get("source_ref")),
        "parity_hash": _optional_text(source.get("parity_hash")),
        "candidate_only": True,
        "non_authoritative": True,
        "authority_boundary": {
            "read_only": True,
            "canonical_truth_mutated": False,
            "promotion": False,
            "routing": False,
            "support_authority": False,
        },
    }


def _typed_support(value: Any, label: str) -> list[dict[str, str]]:
    if isinstance(value, str):
        raw_items = [part.strip() for part in value.split("·") if part.strip()]
    elif _is_sequence(value):
        raw_items = []
        for index, item in enumerate(value):
            if not isinstance(item, str) or not item.strip():
                raise EigenMotifLoadError(f"{label}[{index}] must be a non-empty string")
            raw_items.append(item.strip())
    else:
        raise EigenMotifLoadError(f"{label} must be a string or array of strings")

    if not raw_items:
        raise EigenMotifLoadError(f"{label} must not be empty")

    parsed: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for index, item in enumerate(raw_items):
        parts = [part.strip() for part in item.split(":", 2)]
        if len(parts) != 3 or not all(parts):
            raise EigenMotifLoadError(
                f"{label}[{index}] must have kind:value:dependency_shape form"
            )
        kind, support_value, dependency_shape = parts
        key = (kind, support_value, dependency_shape)
        if key in seen:
            continue
        seen.add(key)
        parsed.append(
            {
                "kind": kind,
                "value": support_value,
                "dependency_shape": dependency_shape,
                "token": f"{kind}:{support_value}:{dependency_shape}",
            }
        )
    return parsed


def _mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise EigenMotifLoadError(f"{label} must be an object")
    return dict(value)


def _finite_number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise EigenMotifLoadError(f"{label} must be numeric")
    result = float(value)
    if not math.isfinite(result):
        raise EigenMotifLoadError(f"{label} must be finite")
    return result


def _required_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise EigenMotifLoadError(f"{label} must be a non-empty string")
    return value.strip()


def _optional_text(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise EigenMotifLoadError("optional text fields must be strings")
    stripped = value.strip()
    return stripped or None


def _optional_nonnegative_int(value: Any, label: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise EigenMotifLoadError(f"{label} must be a non-negative integer")
    return value


def _is_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray))


def _reject_unknown_keys(mapping: Mapping[str, Any], allowed: set[str], label: str) -> None:
    unknown = sorted(set(mapping) - allowed)
    if unknown:
        raise EigenMotifLoadError(f"{label} contains unknown fields: {', '.join(unknown)}")
