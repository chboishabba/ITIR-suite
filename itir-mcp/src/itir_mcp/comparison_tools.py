from __future__ import annotations

from datetime import datetime
from typing import Any, Mapping, Sequence

from .contracts import JsonDict, ToolInputError, ToolSpec


def _require_mapping(payload: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = payload.get(key)
    if not isinstance(value, Mapping):
        raise ToolInputError(f"Expected object field: {key}")
    return value


def _optional_mapping(payload: Mapping[str, Any], key: str) -> Mapping[str, Any] | None:
    value = payload.get(key)
    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise ToolInputError(f"Expected object field: {key}")
    return value


def _require_sequence(payload: Mapping[str, Any], key: str) -> Sequence[Mapping[str, Any]]:
    value = payload.get(key)
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise ToolInputError(f"Expected array field: {key}")
    rows: list[Mapping[str, Any]] = []
    for item in value:
        if not isinstance(item, Mapping):
            raise ToolInputError(f"Expected object entries in array field: {key}")
        rows.append(item)
    return rows


def _observation_payload(raw: Mapping[str, Any]) -> JsonDict:
    text = str(raw.get("text") or "").strip()
    observed_time = str(raw.get("observed_time") or "").strip() or None
    source_system = str(raw.get("source_system") or "").strip() or None
    source_scope = str(raw.get("source_scope") or "").strip() or None
    anchor_refs = raw.get("anchor_refs") if isinstance(raw.get("anchor_refs"), Mapping) else {}
    provenance = raw.get("provenance") if isinstance(raw.get("provenance"), Mapping) else {}
    geometry = raw.get("geometry") if isinstance(raw.get("geometry"), Mapping) else {}
    latitude = _coerce_float(geometry.get("lat"))
    longitude = _coerce_float(geometry.get("lon"))
    return {
        "obs_id": str(raw.get("obs_id") or "").strip() or None,
        "source_family": str(raw.get("source_family") or "").strip() or None,
        "source_system": source_system,
        "source_scope": source_scope,
        "capture_mode": str(raw.get("capture_mode") or "").strip() or None,
        "observed_time": observed_time,
        "text": text,
        "geometry": {"lat": latitude, "lon": longitude} if latitude is not None and longitude is not None else None,
        "anchor_refs": dict(anchor_refs),
        "provenance": dict(provenance),
    }


def _token_terms(text: str) -> set[str]:
    return {token.lower() for token in text.split() if token.strip()}


def _round_metric(value: float) -> float:
    return round(float(value), 3)


def _token_overlap(left: str, right: str) -> float:
    left_terms = _token_terms(left)
    right_terms = _token_terms(right)
    if not left_terms and not right_terms:
        return 1.0
    union = left_terms | right_terms
    if not union:
        return 0.0
    return len(left_terms & right_terms) / len(union)


def _time_proximity(left: str | None, right: str | None) -> float | None:
    if not left or not right:
        return None
    left_dt = _parse_datetime(left)
    right_dt = _parse_datetime(right)
    if left_dt is None or right_dt is None:
        return None
    delta_seconds = abs((right_dt - left_dt).total_seconds())
    return max(0.0, 1.0 - min(delta_seconds / 21600.0, 1.0))


def _geo_proximity(
    left: Mapping[str, Any] | None,
    right: Mapping[str, Any] | None,
) -> float | None:
    if not left or not right:
        return None
    left_lat = _coerce_float(left.get("lat"))
    left_lon = _coerce_float(left.get("lon"))
    right_lat = _coerce_float(right.get("lat"))
    right_lon = _coerce_float(right.get("lon"))
    if None in {left_lat, left_lon, right_lat, right_lon}:
        return None
    distance = abs(left_lat - right_lat) + abs(left_lon - right_lon)
    return max(0.0, 1.0 - min(distance / 10.0, 1.0))


def _confidence_band(value: float) -> str:
    if value >= 0.75:
        return "high"
    if value >= 0.4:
        return "medium"
    return "low"


def compare_observations(payload: Mapping[str, Any]) -> JsonDict:
    left = _observation_payload(_require_mapping(payload, "left"))
    right = _observation_payload(_require_mapping(payload, "right"))

    text_overlap = _round_metric(_token_overlap(str(left.get("text") or ""), str(right.get("text") or "")))
    time_proximity = _time_proximity(left.get("observed_time"), right.get("observed_time"))
    geo_proximity = _geo_proximity(
        left.get("geometry") if isinstance(left.get("geometry"), Mapping) else None,
        right.get("geometry") if isinstance(right.get("geometry"), Mapping) else None,
    )
    score_parts = [text_overlap]
    if time_proximity is not None:
        score_parts.append(time_proximity)
    if geo_proximity is not None:
        score_parts.append(geo_proximity)
    similarity = _round_metric(sum(score_parts) / len(score_parts))

    left_terms = _token_terms(str(left.get("text") or ""))
    right_terms = _token_terms(str(right.get("text") or ""))
    shared_features = sorted(left_terms & right_terms)[:8]
    distinct_features = sorted((left_terms ^ right_terms))[:8]
    return {
        "version": "itir.compare_observations.v1",
        "left": left,
        "right": right,
        "similarity": similarity,
        "confidence": _confidence_band(similarity),
        "signals": {
            "text_overlap": text_overlap,
            "time_proximity": None if time_proximity is None else _round_metric(time_proximity),
            "geo_proximity": None if geo_proximity is None else _round_metric(geo_proximity),
        },
        "shared_features": shared_features,
        "distinct_features": distinct_features,
    }


def score_coherence(payload: Mapping[str, Any]) -> JsonDict:
    observations = [_observation_payload(item) for item in _require_sequence(payload, "observations")]
    if len(observations) < 2:
        return {
            "version": "itir.score_coherence.v1",
            "observation_count": len(observations),
            "coherence": 1.0 if observations else 0.0,
            "confidence": "high" if observations else "low",
            "comparison_count": 0,
            "weakest_pair": None,
        }

    pair_results: list[JsonDict] = []
    for left_index in range(len(observations)):
        for right_index in range(left_index + 1, len(observations)):
            pair_results.append(
                compare_observations(
                    {
                        "left": observations[left_index],
                        "right": observations[right_index],
                    }
                )
            )
    coherence = _round_metric(
        sum(float(item["similarity"]) for item in pair_results) / len(pair_results)
    )
    weakest_pair = min(pair_results, key=lambda item: float(item["similarity"]))
    return {
        "version": "itir.score_coherence.v1",
        "observation_count": len(observations),
        "comparison_count": len(pair_results),
        "coherence": coherence,
        "confidence": _confidence_band(coherence),
        "weakest_pair": weakest_pair,
    }


def build_envelope(payload: Mapping[str, Any]) -> JsonDict:
    left = _observation_payload(_require_mapping(payload, "left"))
    right = _observation_payload(_require_mapping(payload, "right"))
    comparison = _optional_mapping(payload, "comparison")
    if comparison is None:
        comparison = compare_observations({"left": left, "right": right})
    return {
        "version": "itir.build_envelope.v1",
        "envelope_type": "itir.observation_comparison.v1",
        "left_observation": left,
        "right_observation": right,
        "comparison": dict(comparison),
        "meta": {
            "generated_by": "itir.compare_observations",
            "transport_safe": True,
        },
    }


def get_comparison_tools():
    return [
        (
            ToolSpec(
                name="itir.compare_observations",
                title="ITIR compare observations",
                description="Compare two bounded observations with deterministic text/time/geo signals.",
                input_schema={
                    "type": "object",
                    "required": ["left", "right"],
                    "properties": {
                        "left": {"type": "object"},
                        "right": {"type": "object"},
                    },
                },
            ),
            compare_observations,
        ),
        (
            ToolSpec(
                name="itir.score_coherence",
                title="ITIR score coherence",
                description="Score coherence over a bounded observation window using pairwise observation comparisons.",
                input_schema={
                    "type": "object",
                    "required": ["observations"],
                    "properties": {
                        "observations": {"type": "array"},
                    },
                },
            ),
            score_coherence,
        ),
        (
            ToolSpec(
                name="itir.build_envelope",
                title="ITIR build envelope",
                description="Wrap two bounded observations and an optional comparison in a transport-safe ITIR envelope.",
                input_schema={
                    "type": "object",
                    "required": ["left", "right"],
                    "properties": {
                        "left": {"type": "object"},
                        "right": {"type": "object"},
                        "comparison": {"type": "object"},
                    },
                },
            ),
            build_envelope,
        ),
    ]


def _coerce_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_datetime(value: str) -> datetime | None:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
