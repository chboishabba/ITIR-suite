"""Read-only ITIR projection of the existing native SLR source owners.

No Python parser, comparison scoring, proof promotion, DB or file store here.
The executable is operator-configured and never selected by the MCP caller.
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any, Mapping

from .contracts import ToolInputError, ToolExecutionError, ToolSpec


def _coordinate(payload: Mapping[str, Any], name: str) -> str:
    value = payload.get(name)
    if not isinstance(value, str) or not value.strip() or len(value) > 2048 or "\x00" in value:
        raise ToolInputError(f"Expected bounded nonempty coordinate: {name}")
    return value


def _native(args: list[str]) -> dict[str, Any]:
    executable = os.environ.get("ITIR_SLR_NATIVE_EXECUTABLE")
    if not executable or not Path(executable).is_absolute() or not Path(executable).is_file():
        raise ToolExecutionError("Set ITIR_SLR_NATIVE_EXECUTABLE to the local SLR sensiblaw binary")
    try:
        result = subprocess.run([executable, *args], check=True, capture_output=True,
                                text=True, timeout=90)
        raw = json.loads(result.stdout)
    except (OSError, subprocess.SubprocessError, ValueError) as exc:
        # Do not return subprocess stderr (may contain connection information).
        raise ToolExecutionError("Native SLR readback failed") from exc
    if not isinstance(raw, dict):
        raise ToolExecutionError("Invalid native SLR response")
    return raw


def inspect_relational_family(payload: Mapping[str, Any]) -> dict[str, Any]:
    action = payload.get("action", "family")
    if action == "family":
        ref = _coordinate(payload, "family_ref")
        raw = _native(["relational-family", "inspect", ref])
        projection = raw.get("projection")
        if (raw.get("family_ref") != ref or not isinstance(projection, dict)
                or projection.get("schema") != "itir.relational-family.v2"
                or projection.get("candidate_only") is not True
                or raw.get("creates_access_authority") is not False
                or raw.get("applies_external_edit") is not False
                or projection.get("formal_consumer_equivalence_paid") is not False
                or projection.get("all_live_reading_coverage_paid") is not False):
            raise ToolExecutionError("Wrong or promotion-bearing native family receipt")
    elif action == "revision":
        ref = _coordinate(payload, "transition_ref")
        raw = _native(["relational-family", "inspect-revision", ref])
        if (raw.get("schema") != "itir.relational-family-revision.v1"
                or raw.get("transition_ref") != ref or raw.get("candidate_only") is not True
                or raw.get("creates_semantic_authority") is not False):
            raise ToolExecutionError("Wrong or promotion-bearing revision receipt")
    elif action == "original_relations":
        keys = ("numeric_run_ref", "document_ref", "snapshot_ref", "packet_sha256", "relation_type")
        values = [_coordinate(payload, k) for k in keys]
        raw = _native(["numeric-pnf-native", "relation-query", *values])
        expected = dict(zip(keys[:-1], values[:-1]))
        expected["query_relation_type"] = values[-1]
        if (raw.get("schema") != "slr.original-relation-query.v1"
                or any(raw.get(k) != v for k, v in expected.items())
                or raw.get("exact_persisted_packet_readback") is not True
                or raw.get("all_live_semantic_readings_covered") is not False
                or raw.get("governed_identity_paid") is not False
                or raw.get("level_three_paid") is not False
                or raw.get("world_truth_paid") is not False):
            raise ToolExecutionError("Wrong or promotion-bearing original relation receipt")
    elif action == "source_fibre":
        keys = ("source_revision_ref", "numeric_run_ref", "document_ref",
                "snapshot_ref", "packet_sha256")
        values = [_coordinate(payload, k) for k in keys]
        batches = payload.get("batch_refs")
        if (not isinstance(batches, list) or not 0 < len(batches) <= 4096
                or any(not isinstance(b, str) or not b.strip() or len(b) > 2048
                       or "\\x00" in b for b in batches)
                or len(set(batches)) != len(batches)):
            raise ToolInputError("Expected distinct bounded native batch references")
        encoded = json.dumps(batches, ensure_ascii=False, separators=(",", ":"))
        if len(encoded.encode("utf-8")) > 262144:
            raise ToolInputError("Batch reference request too large")
        raw = _native(["relational-family", "inspect-source-fibre", *values, encoded])
        transport = raw.get("original_transport")
        meet = transport.get("source_coordinate_meet") if isinstance(transport, dict) else None
        numeric = meet.get("numeric_original") if isinstance(meet, dict) else None
        checked = meet.get("checked_batches") if isinstance(meet, dict) else None
        if (raw.get("schema") != "slr.source-semantic-candidate-fragments.v1"
                or not isinstance(raw.get("rows"), list)
                or not isinstance(meet, dict) or not isinstance(numeric, dict)
                or not isinstance(checked, list)
                or any(not isinstance(b, dict) for b in checked)
                or [b.get("batch_ref") for b in checked] != batches
                or meet.get("source_revision_ref") != values[0]
                or any(numeric.get(k) != v for k, v in zip(keys[1:], values[1:]))
                or raw.get("semantic_coverage_paid") is not False
                or raw.get("world_truth_paid") is not False
                or meet.get("common_current_authority_snapshot") is not False
                or transport.get("outside_model_possible") is not True):
            raise ToolExecutionError("Wrong or promotion-bearing native source fibre")
    elif action in ("factor_consumer", "demand_fibre"):
        if action == "factor_consumer":
            keys = ("numeric_run_ref", "document_ref", "snapshot_ref", "packet_sha256", "consumer_axis")
            values = [_coordinate(payload, k) for k in keys]
            if values[-1] not in ("type_ref", "referential_type", "role", "value"):
                raise ToolInputError("Unknown recorded consumer axis")
            raw = _native(["numeric-pnf-native", "factor-consumer", *values])
            expected = dict(zip(keys, values))
            schema = "slr.recorded-factor-consumer.v1"
            exact_flag = "represented_product_projection_exact"
        else:
            keys = ("numeric_run_ref", "document_ref", "source_sha256")
            values = [_coordinate(payload, k) for k in keys]
            demand = payload.get("demand_id")
            if type(demand) is not int or not 0 < demand < (1 << 63):
                raise ToolInputError("Expected positive native demand ID")
            raw = _native(["numeric-pnf-native", "demand-fibre", *values, str(demand)])
            expected = dict(zip(keys, values))
            expected["demand_id"] = demand
            schema = "slr.native-demand-fibre.v1"
            exact_flag = "recorded_universe_exact"
        if (raw.get("schema") != schema or any(raw.get(k) != v for k, v in expected.items())
                or raw.get(exact_flag) is not True
                or any(raw.get(k) is not False for k in (
                    "semantic_coverage_paid", "source_meaning_correspondence_paid",
                    "governed_identity_paid", "level_three_paid", "world_truth_paid"))):
            raise ToolExecutionError("Wrong or promotion-bearing native fibre receipt")
    else:
        raise ToolInputError("Unknown read-only relational inspection action")
    return {"version": "itir.native_relational_inspection.v1", "action": action,
            "native_receipt": raw, "candidate_only": True,
            "creates_semantic_authority": False, "mutates": False}


def get_native_relational_tools():
    return [(ToolSpec(
        name="itir.relational.inspect",
        title="Inspect native SLR informational comparison",
        description="Reopen exact native family, revision or original relation coordinates; read only.",
        input_schema={"type": "object", "properties": {
            "action": {"enum": ["family", "revision", "original_relations", "factor_consumer", "demand_fibre", "source_fibre"]},
            "demand_id": {"type": "integer", "minimum": 1},
            "batch_refs": {"type": "array", "items": {"type": "string"}, "maxItems": 4096},
            **{k: {"type": "string"} for k in ("family_ref", "transition_ref",
               "numeric_run_ref", "document_ref", "snapshot_ref", "packet_sha256", "relation_type",
               "source_sha256", "consumer_axis", "source_revision_ref")},
        }, "additionalProperties": False},
        read_only=True,
    ), inspect_relational_family)]
