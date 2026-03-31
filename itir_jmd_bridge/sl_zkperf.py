from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
import sys
from typing import Any


def load_sl_payload(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("SL payload must be a JSON object")
    return payload


def load_contested_affidavit_review_payload(
    db_path: str | Path,
    *,
    review_run_id: str | None = None,
) -> dict[str, Any]:
    build_summary, list_runs = _load_sensiblaw_contested_review_helpers()
    db = Path(db_path).resolve()
    with sqlite3.connect(str(db)) as conn:
        selected_review_run_id = review_run_id
        if not selected_review_run_id:
            runs = list_runs(conn, limit=1)
            if not runs:
                raise ValueError(f"no contested affidavit review runs found in {db}")
            selected_review_run_id = str(runs[0]["review_run_id"])
        payload = build_summary(conn, review_run_id=str(selected_review_run_id))
    if not isinstance(payload, dict):
        raise ValueError("contested affidavit review summary must be a JSON object")
    payload.setdefault("run", {})
    if isinstance(payload["run"], dict):
        payload["run"].setdefault("review_run_id", str(selected_review_run_id))
        payload["run"].setdefault("db_path", str(db))
    return payload


def build_zkperf_observation_from_sl_payload(
    payload: dict[str, Any],
    *,
    source_path: str | Path,
    run_id: str | None = None,
    trace_id: str | None = None,
    asserted_at: str | None = None,
    runtime_metrics: list[dict[str, Any]] | None = None,
    extra_trace_refs: list[dict[str, str]] | None = None,
    extra_proof_refs: list[dict[str, str]] | None = None,
    theory_evidence_path: str | Path | None = None,
    theory_family: str | None = None,
) -> dict[str, Any]:
    source = Path(source_path).resolve()
    source_ref = str(source)
    payload_bytes = _canonical_json_bytes(payload)
    payload_sha256 = hashlib.sha256(payload_bytes).hexdigest()
    inferred_run_id = run_id or _derive_run_id(payload, payload_sha256)
    inferred_trace_id = trace_id or _derive_trace_id(payload, payload_sha256)
    asserted_at_utc = asserted_at or _derive_asserted_at(payload, source)

    metrics = _build_metrics(payload, payload_bytes)
    if runtime_metrics:
        metrics.extend(runtime_metrics)
    theory_evidence = _load_theory_evidence(theory_evidence_path, family=theory_family)
    if theory_evidence is not None:
        metrics.extend(theory_evidence["metrics"])
    trace_refs = [
        {
            "kind": "sl_payload_path",
            "ref": source_ref,
        },
        {
            "kind": "sl_payload_sha256",
            "ref": f"sha256:{payload_sha256}",
        },
    ]
    if extra_trace_refs:
        trace_refs.extend(extra_trace_refs)
    if theory_evidence is not None:
        trace_refs.extend(theory_evidence["trace_refs"])
    proof_refs = _build_proof_refs(payload)
    if extra_proof_refs:
        proof_refs.extend(extra_proof_refs)
    if theory_evidence is not None:
        proof_refs.extend(theory_evidence["proof_refs"])
    related_artifact_refs = _build_related_artifact_refs(payload)
    projection = _build_sl_state_projection(payload)

    observation = {
        "zkperf_observation_id": "",
        "trace_id": inferred_trace_id,
        "run_id": inferred_run_id,
        "asserted_at": asserted_at_utc,
        "source_ref": source_ref,
        "status": "observed",
        "metrics": metrics,
        "trace_refs": trace_refs,
        "proof_refs": proof_refs,
        "related_artifact_refs": related_artifact_refs,
        "hash": "",
        **projection,
    }
    return _finalize_observation(observation)


def build_zkperf_observation_from_sl_file(
    path: str | Path,
    *,
    run_id: str | None = None,
    trace_id: str | None = None,
    asserted_at: str | None = None,
    runtime_metrics: list[dict[str, Any]] | None = None,
    extra_trace_refs: list[dict[str, str]] | None = None,
    extra_proof_refs: list[dict[str, str]] | None = None,
    theory_evidence_path: str | Path | None = None,
    theory_family: str | None = None,
) -> dict[str, Any]:
    return build_zkperf_observation_from_sl_payload(
        load_sl_payload(path),
        source_path=path,
        run_id=run_id,
        trace_id=trace_id,
        asserted_at=asserted_at,
        runtime_metrics=runtime_metrics,
        extra_trace_refs=extra_trace_refs,
        extra_proof_refs=extra_proof_refs,
        theory_evidence_path=theory_evidence_path,
        theory_family=theory_family,
    )


def build_zkperf_observation_from_contested_review_db(
    db_path: str | Path,
    *,
    review_run_id: str | None = None,
    run_id: str | None = None,
    trace_id: str | None = None,
    asserted_at: str | None = None,
    runtime_metrics: list[dict[str, Any]] | None = None,
    extra_trace_refs: list[dict[str, str]] | None = None,
    extra_proof_refs: list[dict[str, str]] | None = None,
    theory_evidence_path: str | Path | None = None,
    theory_family: str | None = None,
) -> dict[str, Any]:
    db = Path(db_path).resolve()
    payload = load_contested_affidavit_review_payload(db, review_run_id=review_run_id)
    resolved_review_run_id = _lookup(payload, "run", "review_run_id")
    trace_refs = [
        {"kind": "sl_db_path", "ref": str(db)},
    ]
    if resolved_review_run_id:
        trace_refs.append({"kind": "sl_review_run_id", "ref": str(resolved_review_run_id)})
    if extra_trace_refs:
        trace_refs.extend(extra_trace_refs)
    return build_zkperf_observation_from_sl_payload(
        payload,
        source_path=db,
        run_id=run_id,
        trace_id=trace_id,
        asserted_at=asserted_at,
        runtime_metrics=runtime_metrics,
        extra_trace_refs=trace_refs,
        extra_proof_refs=extra_proof_refs,
        theory_evidence_path=theory_evidence_path,
        theory_family=theory_family,
    )


def build_zkperf_trace_observations_from_progress_log(
    progress_log_path: str | Path,
    *,
    run_id: str,
    trace_id: str,
    started_at: str,
    finished_at: str,
    sl_output_path: str | Path | None = None,
    sl_db_path: str | Path | None = None,
    command: list[str] | None = None,
) -> list[dict[str, Any]]:
    progress_log = Path(progress_log_path).resolve()
    events = parse_cli_progress_log(progress_log)
    observations: list[dict[str, Any]] = []
    previous_stage_slug: str | None = None
    previous_progress_ratio: float | None = None
    previous_completed: float | None = None
    previous_total: float | None = None
    previous_message_length: float | None = None
    for index, event in enumerate(events, start=1):
        stage_name = str(event.get("stage") or "unknown")
        stage_slug = _slugify(stage_name)
        stage_family = _derive_stage_family(stage_name)
        domain_roles = _derive_domain_roles(stage_name, event.get("section"), event.get("message"))
        domain_signals = _derive_domain_signals(stage_name, event.get("section"), event.get("status"), event.get("message"))
        completed_value = float(event["completed"]) if isinstance(event.get("completed"), (int, float)) else None
        total_value = float(event["total"]) if isinstance(event.get("total"), (int, float)) else None
        metrics: list[dict[str, Any]] = [
            {"metric": "trace.step_index", "value": index, "unit": "count"},
            {"metric": "trace.progress_event", "value": 1, "unit": "count"},
            {"metric": f"trace.stage.{stage_slug}", "value": 1, "unit": "count"},
            {"metric": f"trace.stage_family.{stage_family}", "value": 1, "unit": "count"},
        ]
        for role in domain_roles:
            metrics.append({"metric": f"trace.domain_role.{role}", "value": 1, "unit": "count"})
        for signal in domain_signals:
            metrics.append({"metric": f"trace.domain_signal.{signal}", "value": 1, "unit": "count"})
        section = event.get("section")
        if section:
            metrics.append({"metric": f"trace.section.{_slugify(str(section))}", "value": 1, "unit": "count"})
        status = event.get("status")
        if status:
            metrics.append({"metric": f"trace.status.{_slugify(str(status))}", "value": 1, "unit": "count"})
        for key, value in sorted(event.items()):
            if key in {"stage", "section", "status", "message"}:
                continue
            if isinstance(value, (int, float)):
                metrics.append(
                    {
                        "metric": f"trace.detail.{_slugify(str(key))}",
                        "value": value,
                        "unit": _trace_metric_unit(str(key)),
                    }
                )
        completed = event.get("completed")
        total = event.get("total")
        if isinstance(completed, (int, float)) and isinstance(total, (int, float)) and float(total) > 0:
            progress_ratio = round(float(completed) / float(total), 6)
            metrics.append(
                {
                    "metric": "trace.progress_ratio",
                    "value": progress_ratio,
                    "unit": "ratio",
                }
            )
            metrics.append(
                {
                    "metric": "trace.progress_remaining_ratio",
                    "value": round(max(1.0 - progress_ratio, 0.0), 6),
                    "unit": "ratio",
                }
            )
            metrics.append(
                {
                    "metric": "trace.progress_completed_clamped",
                    "value": round(min(max(progress_ratio, 0.0), 1.0), 6),
                    "unit": "ratio",
                }
            )
            if previous_progress_ratio is not None:
                metrics.append(
                    {
                        "metric": "trace.progress_delta_ratio",
                        "value": round(progress_ratio - previous_progress_ratio, 6),
                        "unit": "ratio",
                    }
                )
            previous_progress_ratio = progress_ratio
        message_text = str(event.get("message") or "")
        message_length = float(len(message_text))
        metrics.append({"metric": "trace.message_present", "value": 1 if message_text else 0, "unit": "flag"})
        if message_text:
            metrics.append({"metric": "trace.message_length_chars", "value": len(message_text), "unit": "chars"})
        if previous_stage_slug is not None:
            transition_key = f"{previous_stage_slug}__to__{stage_slug}"
            metrics.append({"metric": f"trace.transition.{transition_key}", "value": 1, "unit": "count"})
        trace_refs: list[dict[str, str]] = [
            {"kind": "sl_progress_log_path", "ref": str(progress_log)},
            {"kind": "sl_observation_role", "ref": "trace_step"},
            {"kind": "progress_stage", "ref": stage_name},
            {"kind": "progress_stage_family", "ref": stage_family},
        ]
        if domain_roles:
            for role in domain_roles:
                trace_refs.append({"kind": "trace_domain_role", "ref": role})
        if domain_signals:
            for signal in domain_signals:
                trace_refs.append({"kind": "trace_domain_signal", "ref": signal})
        if section:
            trace_refs.append({"kind": "progress_section", "ref": str(section)})
        if status:
            trace_refs.append({"kind": "progress_status", "ref": str(status)})
        if event.get("message"):
            trace_refs.append({"kind": "progress_message", "ref": str(event["message"])})
        if sl_output_path is not None:
            trace_refs.append({"kind": "sl_payload_path", "ref": str(Path(sl_output_path).resolve())})
        if sl_db_path is not None:
            trace_refs.append({"kind": "sl_db_path", "ref": str(Path(sl_db_path).resolve())})
        if command:
            trace_refs.append({"kind": "sl_command", "ref": json.dumps(command, ensure_ascii=True)})
        if previous_stage_slug is not None:
            trace_refs.append({"kind": "progress_prev_stage", "ref": previous_stage_slug})

        related_artifact_refs: list[dict[str, str]] = []
        if sl_output_path is not None:
            related_artifact_refs.append({"kind": "sl_payload_path", "ref": str(Path(sl_output_path).resolve())})
        if sl_db_path is not None:
            related_artifact_refs.append({"kind": "sl_db_path", "ref": str(Path(sl_db_path).resolve())})

        region = _derive_trace_region(stage_slug, stage_family, event.get("section"), domain_roles, domain_signals)
        flow_tags = _build_trace_flow_tags(stage_family, event.get("section"), status, domain_roles, domain_signals)
        register_changes = _build_trace_register_changes(
            index=index,
            completed=completed_value,
            total=total_value,
            message_length=message_length,
            role_count=float(len(domain_roles)),
            signal_count=float(len(domain_signals)),
            previous_completed=previous_completed,
            previous_total=previous_total,
            previous_message_length=previous_message_length,
        )
        registers = {
            "AX": hex(index),
            "DX": hex(int(message_length)),
            "SI": hex(len(domain_roles)),
            "DI": hex(len(domain_signals)),
        }
        if completed_value is not None:
            registers["BX"] = hex(int(completed_value))
        if total_value is not None:
            registers["CX"] = hex(int(total_value))
        register_fingerprints = {
            name: _register_fingerprint_for_value(int(value, 16))
            for name, value in registers.items()
        }

        observation = {
            "zkperf_observation_id": "",
            "trace_id": trace_id,
            "run_id": run_id,
            "asserted_at": _derive_progress_asserted_at(started_at, finished_at, event),
            "source_ref": str(progress_log),
            "status": "observed",
            "metrics": metrics,
            "trace_refs": trace_refs,
            "proof_refs": [],
            "related_artifact_refs": related_artifact_refs,
            "hash": "",
            "registers": registers,
            "registerFingerprints": register_fingerprints,
            "registerChanges": register_changes,
            "flowTags": flow_tags,
            "region": region,
            "transition": stage_slug.upper(),
            "fromRegion": previous_stage_slug.upper() if previous_stage_slug is not None else "TRACE_START",
            "toRegion": region,
        }
        observations.append(_finalize_observation(observation))
        previous_stage_slug = stage_slug
        previous_completed = completed_value
        previous_total = total_value
        previous_message_length = message_length
    return observations


def parse_cli_progress_log(path: str | Path) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for raw_line in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        parsed = _parse_progress_line(line)
        if parsed is not None:
            events.append(parsed)
    return events


def _load_theory_evidence(path: str | Path | None, *, family: str | None = None) -> dict[str, Any] | None:
    if path is None:
        return None
    evidence_path = Path(path).resolve()
    payload = json.loads(evidence_path.read_text(encoding="utf-8"))
    if isinstance(payload, dict) and payload.get("schema_version") == "mdl-evidence-v1":
        return _theory_evidence_from_mdl_evidence_v1(evidence_path, payload)
    if isinstance(payload, dict) and isinstance(payload.get("family_context"), dict):
        return _theory_evidence_from_family_report(evidence_path, payload)
    if isinstance(payload, list):
        return _theory_evidence_from_family_classification_list(evidence_path, payload, family=family)
    if isinstance(payload, dict) and isinstance(payload.get("batches"), list):
        return _theory_evidence_from_batch_summary(evidence_path, payload, family=family)
    raise ValueError(f"unsupported theory evidence shape: {evidence_path}")


def _theory_evidence_from_mdl_evidence_v1(path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    mdl = payload.get("mdl")
    if not isinstance(mdl, dict):
        raise ValueError(f"mdl-evidence-v1 missing mdl object: {path}")

    metrics: list[dict[str, Any]] = [
        {"metric": "theory.mdl.available", "value": 1, "unit": "flag"},
        {"metric": "theory.mdl.total_length", "value": float(mdl.get("total_length", 0.0) or 0.0), "unit": "code_length"},
        {"metric": "theory.mdl.descent_monotone", "value": 1 if bool(mdl.get("descent_monotone")) else 0, "unit": "flag"},
        {"metric": "theory.mdl.violation_count", "value": int(mdl.get("violation_count", 0) or 0), "unit": "count"},
        {"metric": "theory.mdl.worst_increase", "value": float(mdl.get("worst_increase", 0.0) or 0.0), "unit": "cost_delta"},
    ]
    if mdl.get("worst_step") is not None:
        metrics.append({"metric": "theory.mdl.worst_step", "value": int(mdl.get("worst_step", 0) or 0), "unit": "count"})

    trajectory = payload.get("trajectory")
    if isinstance(trajectory, list):
        metrics.append({"metric": "theory.mdl.trajectory_step_count", "value": len(trajectory), "unit": "count"})

    trace_refs = [{"kind": "theory_evidence_path", "ref": str(path)}]
    for key, kind in (
        ("program_id", "theory_program_id"),
        ("run_id", "theory_run_id"),
        ("input_id", "theory_input_id"),
        ("family", "theory_family"),
        ("model_class", "theory_model_class"),
        ("coding_scheme", "theory_coding_scheme"),
        ("measured_at", "theory_measured_at"),
    ):
        value = payload.get(key)
        if value:
            trace_refs.append({"kind": kind, "ref": str(value)})

    proof_refs = [{"kind": "theory_evidence_kind", "ref": "mdl_evidence_v1"}]
    witness = payload.get("witness")
    if isinstance(witness, dict):
        artifact_path = witness.get("artifact_path")
        commit = witness.get("commit")
        if artifact_path:
            proof_refs.append({"kind": "theory_witness_artifact_path", "ref": str(artifact_path)})
        if commit:
            proof_refs.append({"kind": "theory_witness_commit", "ref": str(commit)})

    return {"metrics": metrics, "trace_refs": trace_refs, "proof_refs": proof_refs}


def _theory_evidence_from_family_report(path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    family_context = payload.get("family_context")
    report_summary = family_context.get("report_summary") if isinstance(family_context, dict) else None
    if not isinstance(report_summary, dict):
        raise ValueError(f"family report missing report_summary: {path}")
    mdl_rows = report_summary.get("mdl_descent")
    if not isinstance(mdl_rows, list) or not mdl_rows:
        raise ValueError(f"family report missing mdl_descent rows: {path}")
    mdl_row = mdl_rows[0]
    if not isinstance(mdl_row, dict):
        raise ValueError(f"family report mdl_descent row must be an object: {path}")
    closest_row = _first_dict(report_summary.get("closestpoint"))
    fejer_row = _first_dict(report_summary.get("fejer_set"))
    family_name = family_context.get("family") if isinstance(family_context, dict) else None

    metrics: list[dict[str, Any]] = [
        {"metric": "theory.mdl.available", "value": 1, "unit": "flag"},
        {"metric": "theory.mdl.descent_monotone", "value": 1 if bool(mdl_row.get("MDL_monotone")) else 0, "unit": "flag"},
        {"metric": "theory.mdl.violation_count", "value": int(mdl_row.get("MDL_violations", 0) or 0), "unit": "count"},
        {"metric": "theory.mdl.worst_increase", "value": float(mdl_row.get("MDL_worst_increase", 0.0) or 0.0), "unit": "cost_delta"},
        {"metric": "theory.mdl.worst_iter", "value": int(mdl_row.get("MDL_worst_iter", 0) or 0), "unit": "count"},
    ]
    if closest_row is not None:
        metrics.extend(
            [
                {"metric": "theory.dynamics.closestpoint.available", "value": 1, "unit": "flag"},
                {"metric": "theory.dynamics.closestpoint.frac", "value": float(closest_row.get("closest_frac", 0.0) or 0.0), "unit": "ratio"},
                {"metric": "theory.dynamics.closestpoint.max_violation", "value": float(closest_row.get("closest_max_violation", 0.0) or 0.0), "unit": "violation"},
            ]
        )
    if fejer_row is not None:
        metrics.extend(
            [
                {"metric": "theory.dynamics.fejer.available", "value": 1, "unit": "flag"},
                {"metric": "theory.dynamics.fejer.frac", "value": float(fejer_row.get("fejer_set_frac", 0.0) or 0.0), "unit": "ratio"},
                {"metric": "theory.dynamics.fejer.max_violation", "value": float(fejer_row.get("fejer_set_max_violation", 0.0) or 0.0), "unit": "violation"},
            ]
        )

    trace_refs = [{"kind": "theory_evidence_path", "ref": str(path)}]
    if family_name:
        trace_refs.append({"kind": "theory_family", "ref": str(family_name)})
    proof_refs = [{"kind": "theory_evidence_kind", "ref": "dashi_family_report"}]
    return {"metrics": metrics, "trace_refs": trace_refs, "proof_refs": proof_refs}


def _theory_evidence_from_family_classification_list(
    path: Path,
    rows: list[Any],
    *,
    family: str | None = None,
) -> dict[str, Any]:
    match = _select_family_row(rows, family=family)
    metrics: list[dict[str, Any]] = [
        {"metric": "theory.mdl.available", "value": 1, "unit": "flag"},
        {"metric": "theory.mdl.exact_ok", "value": 1 if bool(match.get("mdl_exact_ok")) else 0, "unit": "flag"},
        {"metric": "theory.dynamics.cone_ok", "value": 1 if bool(match.get("cone_ok")) else 0, "unit": "flag"},
        {"metric": "theory.dynamics.fejer_ok", "value": 1 if bool(match.get("fejer_ok")) else 0, "unit": "flag"},
        {"metric": "theory.dynamics.closest_ok", "value": 1 if bool(match.get("closest_ok")) else 0, "unit": "flag"},
        {"metric": "theory.dynamics.boundary_steps", "value": int(match.get("boundary_steps", 0) or 0), "unit": "count"},
        {"metric": "theory.dynamics.tail_localized", "value": 1 if bool(match.get("tail_localized")) else 0, "unit": "flag"},
        {"metric": "theory.dynamics.terminal_boundary", "value": 1 if bool(match.get("terminal_boundary")) else 0, "unit": "flag"},
    ]
    trace_refs = [
        {"kind": "theory_evidence_path", "ref": str(path)},
        {"kind": "theory_family", "ref": str(match.get("family"))},
    ]
    if match.get("family_class"):
        trace_refs.append({"kind": "theory_family_class", "ref": str(match["family_class"])})
    proof_refs = [{"kind": "theory_evidence_kind", "ref": "dashi_family_classification"}]
    return {"metrics": metrics, "trace_refs": trace_refs, "proof_refs": proof_refs}


def _theory_evidence_from_batch_summary(
    path: Path,
    payload: dict[str, Any],
    *,
    family: str | None = None,
) -> dict[str, Any]:
    if family:
        for batch in payload.get("batches", []):
            if not isinstance(batch, dict):
                continue
            families = batch.get("families")
            if not isinstance(families, list):
                continue
            for row in families:
                if isinstance(row, dict) and str(row.get("family")) == family:
                    return _theory_evidence_from_family_classification_list(path, families, family=family)
    metrics: list[dict[str, Any]] = [
        {"metric": "theory.mdl.available", "value": 1, "unit": "flag"},
        {
            "metric": "theory.mdl.tail_boundary_instance_count",
            "value": int(payload.get("mdl_tail_boundary_instance_count", 0) or 0),
            "unit": "count",
        },
        {
            "metric": "theory.mdl.tail_boundary_unique_family_count",
            "value": int(payload.get("mdl_tail_boundary_unique_family_count", 0) or 0),
            "unit": "count",
        },
        {"metric": "theory.dynamics.cone_ok", "value": 1 if bool(payload.get("mdl_tail_boundary_all_cone_ok")) else 0, "unit": "flag"},
        {"metric": "theory.dynamics.fejer_ok", "value": 1 if bool(payload.get("mdl_tail_boundary_all_fejer_ok")) else 0, "unit": "flag"},
        {"metric": "theory.dynamics.closest_ok", "value": 1 if bool(payload.get("mdl_tail_boundary_all_closest_ok")) else 0, "unit": "flag"},
        {"metric": "theory.mdl.exact_ok", "value": 0 if bool(payload.get("mdl_tail_boundary_all_mdl_exact_fail")) else 1, "unit": "flag"},
    ]
    trace_refs = [{"kind": "theory_evidence_path", "ref": str(path)}]
    proof_refs = [{"kind": "theory_evidence_kind", "ref": "dashi_tail_boundary_batch"}]
    return {"metrics": metrics, "trace_refs": trace_refs, "proof_refs": proof_refs}


def _select_family_row(rows: list[Any], *, family: str | None = None) -> dict[str, Any]:
    candidates = [row for row in rows if isinstance(row, dict)]
    if not candidates:
        raise ValueError("family classification evidence contained no rows")
    if family is not None:
        for row in candidates:
            if str(row.get("family")) == family:
                return row
        raise ValueError(f"family {family!r} not found in theory evidence")
    return candidates[0]


def _first_dict(value: Any) -> dict[str, Any] | None:
    if isinstance(value, list) and value and isinstance(value[0], dict):
        return value[0]
    return None


def _canonical_json_bytes(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def _finalize_observation(observation: dict[str, Any]) -> dict[str, Any]:
    basis = dict(observation)
    basis["zkperf_observation_id"] = (
        "zkperf-obsv:" + hashlib.sha256(_canonical_json_bytes({"kind": "id", **basis})).hexdigest()[:24]
    )
    digest = hashlib.sha256(_canonical_json_bytes(basis)).hexdigest()
    basis["hash"] = f"sha256:{digest}"
    return basis


def _derive_run_id(payload: dict[str, Any], payload_sha256: str) -> str:
    candidates = [
        _lookup(payload, "run", "review_run_id"),
        _lookup(payload, "run", "semantic_run_id"),
        _lookup(payload, "acceptance", "run", "workflow_link", "workflow_run_id"),
        _lookup(payload, "acceptance", "run", "run_id"),
        _lookup(payload, "run", "workflow_run_id"),
        _lookup(payload, "run", "run_id"),
        _lookup(payload, "semantic_context", "workflow", "workflow_run_id"),
    ]
    for candidate in candidates:
        if candidate:
            return str(candidate)
    return f"sl-run:{payload_sha256[:24]}"


def _derive_trace_id(payload: dict[str, Any], payload_sha256: str) -> str:
    candidates = [
        _lookup(payload, "run", "review_run_id"),
        _lookup(payload, "run", "semantic_run_id"),
        _lookup(payload, "acceptance", "run", "workflow_link", "workflow_run_id"),
        _lookup(payload, "run", "run_id"),
    ]
    for candidate in candidates:
        if candidate:
            return f"sl-trace:{_slugify(str(candidate))}"
    return f"sl-trace:{payload_sha256[:24]}"


def _derive_asserted_at(payload: dict[str, Any], source: Path) -> str:
    candidates = [
        _lookup(payload, "run", "created_at"),
        _lookup(payload, "acceptance", "run", "workflow_link", "created_at"),
        _lookup(payload, "run", "created_at"),
        _lookup(payload, "created_at"),
    ]
    for candidate in candidates:
        if candidate:
            return _normalize_utc(str(candidate))
    stat = source.stat()
    return datetime.fromtimestamp(stat.st_mtime, tz=UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _normalize_utc(value: str) -> str:
    text = value.strip().replace(" ", "T")
    if text.endswith("Z"):
        return text
    if "+" in text[10:] or text.endswith("00:00"):
        parsed = datetime.fromisoformat(text)
    else:
        parsed = datetime.fromisoformat(f"{text}+00:00")
    return parsed.astimezone(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _derive_progress_asserted_at(started_at: str, finished_at: str, event: dict[str, Any]) -> str:
    elapsed_seconds = event.get("elapsed_seconds")
    if not isinstance(elapsed_seconds, (int, float)):
        return finished_at
    started = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
    stamped = started.astimezone(UTC).timestamp() + float(elapsed_seconds)
    return datetime.fromtimestamp(stamped, tz=UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _lookup(payload: dict[str, Any], *keys: str) -> Any:
    current: Any = payload
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    return current


def _parse_progress_line(line: str) -> dict[str, Any] | None:
    if line.startswith("{"):
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            return None
        if isinstance(payload, dict) and payload.get("stage"):
            return payload
        return None
    if not line.startswith("[progress] "):
        return None
    body = line[len("[progress] ") :].strip()
    if not body:
        return None
    if " - " in body:
        prefix, message = body.split(" - ", 1)
    else:
        prefix, message = body, ""
    parts = prefix.split()
    if not parts:
        return None
    event: dict[str, Any] = {"stage": parts[0]}
    for token in parts[1:]:
        if re.fullmatch(r"\d+/\d+", token):
            completed_text, total_text = token.split("/", 1)
            event["completed"] = int(completed_text)
            event["total"] = int(total_text)
            continue
        if "=" not in token:
            continue
        key, raw_value = token.split("=", 1)
        normalized_key = {
            "elapsed": "elapsed_seconds",
            "rate": "items_per_second",
            "eta": "eta_seconds_remaining",
            "eta_band": "eta_confidence_interval_seconds",
        }.get(key, key)
        event[normalized_key] = _parse_progress_value(normalized_key, raw_value)
    if message:
        event["message"] = message.strip()
    return event


def _parse_progress_value(key: str, raw_value: str) -> Any:
    text = raw_value.strip()
    if key.endswith("_seconds") and text.endswith("s"):
        text = text[:-1]
    elif key == "items_per_second" and text.endswith("/s"):
        text = text[:-2]
    try:
        if "." in text:
            return float(text)
        return int(text)
    except ValueError:
        return text


def _trace_metric_unit(key: str) -> str:
    if key.endswith("_seconds"):
        return "seconds"
    if key.endswith("_per_second"):
        return "rate"
    if key in {"completed", "total"} or key.endswith("_count"):
        return "count"
    return "value"


def _derive_stage_family(stage_name: str) -> str:
    stage = _slugify(stage_name)
    if stage.endswith("-started") or stage.endswith("-start"):
        return "start"
    if stage.endswith("-finished") or stage.endswith("-finish") or stage.endswith("-done"):
        return "finish"
    if stage.endswith("-failed") or stage.endswith("-error"):
        return "error"
    if stage.endswith("-running") or stage.endswith("-progress") or stage.endswith("-update"):
        return "progress"
    return "other"


def _derive_domain_roles(stage_name: str, section: Any, message: Any) -> list[str]:
    """Lightweight domain buckets for affidavit/coverage lanes.

    We stay additive and coarse so progress logs from other lanes still pass
    through unchanged. Roles are derived from stage/section/message tokens.
    """

    def tokens(value: Any) -> set[str]:
        if value is None:
            return set()
        slug = _slugify(str(value))
        parts = set(slug.replace("-", " ").split())
        parts.add(slug)
        return {p for p in parts if p}

    vocab = {
        "affidavit": "affidavit",
        "affidavit_review": "affidavit",
        "coverage": "coverage",
        "match": "matching",
        "matching": "matching",
        "align": "matching",
        "link": "matching",
        "review": "review",
        "source": "source",
        "google_docs": "source",
        "response": "source",
        "doc": "source",
        "chronology": "chronology",
        "normalize": "normalization",
        "normalization": "normalization",
        "persist": "persistence",
        "save": "persistence",
        "write": "persistence",
        "publish": "publish",
        "upload": "publish",
        "stream": "publish",
        "index": "index",
        "fact": "fact_state",
        "claim": "fact_state",
        "zelph": "fact_state",
    }

    seen: list[str] = []
    for token in tokens(stage_name) | tokens(section) | tokens(message):
        role = vocab.get(token)
        if role and role not in seen:
            seen.append(role)
    return seen


def _derive_domain_signals(stage_name: str, section: Any, status: Any, message: Any) -> list[str]:
    def token_set(value: Any) -> set[str]:
        if value is None:
            return set()
        slug = _slugify(str(value))
        parts = set(slug.replace("-", " ").split())
        parts.add(slug)
        return {part for part in parts if part}

    tokens = token_set(stage_name) | token_set(section) | token_set(status) | token_set(message)
    mapping = {
        "covered": "coverage_recovered",
        "coverage": "coverage_activity",
        "missing": "review_gap",
        "review_required": "review_gap",
        "gap": "review_gap",
        "conflict": "conflict_pressure",
        "contested": "conflict_pressure",
        "unresolved": "conflict_pressure",
        "supported": "support_signal",
        "unsupported": "support_signal",
        "persist": "persistence_boundary",
        "saved": "persistence_boundary",
        "write": "persistence_boundary",
        "publish": "publish_boundary",
        "upload": "publish_boundary",
        "stream": "publish_boundary",
        "index": "index_boundary",
        "anchor": "anchor_activity",
        "candidate": "candidate_activity",
        "normalize": "normalization_activity",
        "normalization": "normalization_activity",
        "chronology": "chronology_activity",
        "timeline": "chronology_activity",
        "google_docs": "source_ingest",
        "response": "source_ingest",
        "affidavit": "affidavit_focus",
        "fact": "fact_state_activity",
        "claim": "fact_state_activity",
        "zelph": "fact_state_activity",
    }
    seen: list[str] = []
    for token in tokens:
        signal = mapping.get(token)
        if signal and signal not in seen:
            seen.append(signal)
    return seen


def _build_metrics(payload: dict[str, Any], payload_bytes: bytes) -> list[dict[str, Any]]:
    walk = _walk_counts(payload)
    metrics: list[dict[str, Any]] = [
        {"metric": "payload_bytes", "value": len(payload_bytes), "unit": "bytes"},
        {"metric": "top_level_keys", "value": len(payload), "unit": "count"},
        {"metric": "dict_nodes", "value": walk["dict_nodes"], "unit": "count"},
        {"metric": "list_nodes", "value": walk["list_nodes"], "unit": "count"},
        {"metric": "scalar_nodes", "value": walk["scalar_nodes"], "unit": "count"},
        {"metric": "max_depth", "value": walk["max_depth"], "unit": "levels"},
    ]
    summary = _lookup(payload, "summary")
    if isinstance(summary, dict):
        for key in (
            "source_document_count",
            "event_count",
            "fact_count",
            "observation_count",
            "statement_count",
            "relation_candidate_count",
        ):
            value = summary.get(key)
            if isinstance(value, int):
                metrics.append({"metric": key, "value": value, "unit": "count"})
    review_queue = payload.get("review_queue")
    if isinstance(review_queue, list):
        metrics.append({"metric": "review_queue_count", "value": len(review_queue), "unit": "count"})
    chronology = payload.get("chronology")
    if isinstance(chronology, list):
        metrics.append({"metric": "chronology_row_count", "value": len(chronology), "unit": "count"})
    stories = _lookup(payload, "acceptance", "stories")
    if isinstance(stories, list):
        metrics.append({"metric": "acceptance_story_count", "value": len(stories), "unit": "count"})
        metrics.append(
            {
                "metric": "acceptance_pass_count",
                "value": sum(1 for row in stories if isinstance(row, dict) and row.get("status") == "pass"),
                "unit": "count",
            }
        )
    hypotheses = payload.get("hypotheses")
    if isinstance(hypotheses, list):
        metrics.append({"metric": "hypothesis_count", "value": len(hypotheses), "unit": "count"})

    # Affidavit / contested-review style enrichments (additive and safe)
    metrics.extend(_build_affidavit_metrics(payload))
    return metrics


def _build_affidavit_metrics(payload: dict[str, Any]) -> list[dict[str, Any]]:
    metrics: list[dict[str, Any]] = []

    def append_int(name: str, value: Any, unit: str = "count") -> None:
        if isinstance(value, (int, float)):
            metrics.append({"metric": name, "value": value, "unit": unit})

    def append_counts(prefix: str, mapping: Any) -> None:
        if isinstance(mapping, dict):
            for key, value in mapping.items():
                append_int(f"{prefix}.{key}", value)

    # Summary-derived metrics (if present)
    summary = payload.get("summary")
    if isinstance(summary, dict):
        for key in (
            "abstained_affidavit_count",
            "abstained_source_count",
            "affidavit_proposition_count",
            "contested_affidavit_count",
            "contested_source_count",
            "covered_count",
            "missing_review_count",
            "partial_count",
            "provisional_anchor_bundle_count",
            "provisional_structured_anchor_count",
            "related_review_cluster_count",
            "related_source_count",
            "review_queue_only_count",
            "substantive_response_count",
            "unsupported_affidavit_count",
            "candidate_anchor_count",
            "chronology_gap_count",
            "event_extraction_gap_count",
            "evidence_gap_count",
            "normalization_gap_count",
            "procedural_event_cue_count",
            "calendar_reference_hint_count",
            "transcript_timestamp_hint_count",
        ):
            append_int(f"summary.{key}", summary.get(key))
        for ratio_key in ("affidavit_supported_ratio", "substantive_response_ratio"):
            append_int(f"summary.{ratio_key}", summary.get(ratio_key), unit="ratio")

        append_counts("summary.conflict_state", summary.get("conflict_state_counts"))
        append_counts("summary.evidentiary_state", summary.get("evidentiary_state_counts"))
        append_counts("summary.operational_status", summary.get("operational_status_counts"))
        append_counts("summary.semantic_basis", summary.get("semantic_basis_counts"))
        append_counts("summary.support_direction", summary.get("support_direction_counts"))
        append_counts("summary.support_status", summary.get("support_status_counts"))
        append_counts("summary.best_response_role", summary.get("best_response_role_counts"))

    # Normalized metrics v1 (if present)
    norm = payload.get("normalized_metrics_v1")
    if isinstance(norm, dict):
        for key in (
            "candidate_signal_count",
            "candidate_signal_density",
            "provisional_bundle_count",
            "provisional_bundle_density",
            "provisional_queue_row_count",
            "provisional_row_density",
            "review_required_source_ratio",
        ):
            unit = "ratio" if "density" in key or "ratio" in key else "count"
            append_int(f"norm.{key}", norm.get(key), unit=unit)
        append_counts("norm.review_item_status", norm.get("review_item_status_counts"))
        append_counts("norm.source_status", norm.get("source_status_counts"))
        append_counts("norm.primary_workload", norm.get("primary_workload_counts"))
        append_counts("norm.workload_presence", norm.get("workload_presence_counts"))

    # Row-level rollups if present
    affidavit_rows = payload.get("affidavit_rows")
    if isinstance(affidavit_rows, list):
        append_int("affidavit_rows.count", len(affidavit_rows))
        append_counts("affidavit_rows.coverage_status", _count_field(affidavit_rows, "coverage_status"))
        append_counts("affidavit_rows.support_status", _count_field(affidavit_rows, "support_status"))
        append_counts("affidavit_rows.relation_type", _count_field(affidavit_rows, "relation_type"))
        append_counts("affidavit_rows.conflict_state", _count_field(affidavit_rows, "conflict_state"))
        append_counts(
            "affidavit_rows.primary_target_component",
            _count_field(affidavit_rows, "primary_target_component"),
        )

    source_rows = payload.get("source_review_rows")
    if isinstance(source_rows, list):
        append_int("source_review_rows.count", len(source_rows))
        append_counts("source_review_rows.review_status", _count_field(source_rows, "review_status"))
        append_counts("source_review_rows.candidate_status", _count_field(source_rows, "candidate_status"))

    facts = payload.get("zelph_claim_state_facts")
    if isinstance(facts, list):
        append_int("zelph_claim_state_facts.count", len(facts))
        append_counts("zelph_claim_state_facts.support_status", _count_field(facts, "support_status"))
        append_counts("zelph_claim_state_facts.coverage_status", _count_field(facts, "coverage_status"))
        append_counts("zelph_claim_state_facts.conflict_state", _count_field(facts, "conflict_state"))
        append_counts("zelph_claim_state_facts.operational_status", _count_field(facts, "operational_status"))

    gap_metrics = _build_affidavit_semantic_gap_metrics(payload)
    metrics.extend(gap_metrics)

    return metrics


def _build_sl_state_projection(payload: dict[str, Any]) -> dict[str, Any]:
    counters = _collect_sl_state_counters(payload)
    register_order = ["AX", "BX", "CX", "DX", "SI", "DI", "R8", "R9", "R10", "R11"]
    register_map = {
        "AX": counters.get("pass_count", 0),
        "BX": counters.get("review_gap_count", 0),
        "CX": counters.get("contested_count", 0),
        "DX": counters.get("fact_count", 0),
        "SI": counters.get("review_queue_count", 0),
        "DI": counters.get("event_count", 0),
        "R8": counters.get("observation_count", 0),
        "R9": counters.get("statement_count", 0),
        "R10": counters.get("source_count", 0),
        "R11": counters.get("excerpt_count", 0),
    }
    registers = {name: hex(int(max(value, 0))) for name, value in register_map.items()}
    register_fingerprints = {
        name: _register_fingerprint_for_value(int(max(value, 0)))
        for name, value in register_map.items()
    }
    register_changes = [
        {"register": name, "old": "0x0", "new": registers[name]}
        for name in register_order
        if int(registers[name], 16) > 0
    ]

    return {
        "registerOrder": register_order,
        "registers": registers,
        "registerFingerprints": register_fingerprints,
        "registerChanges": register_changes,
        "flowTags": _build_sl_flow_tags(payload, counters),
        "region": "SL_WORKBENCH" if isinstance(payload.get("workbench"), dict) else "SL_ACCEPTANCE",
        "fromRegion": "SL_ACCEPTANCE" if isinstance(payload.get("acceptance"), dict) else "SL_SOURCE",
        "toRegion": "SL_WORKBENCH" if isinstance(payload.get("workbench"), dict) else "SL_ACCEPTANCE",
        "transition": _derive_sl_transition(payload),
    }


def _collect_sl_state_counters(payload: dict[str, Any]) -> dict[str, int]:
    acceptance_summary = _lookup(payload, "acceptance", "summary")
    workbench_summary = _lookup(payload, "workbench", "summary")

    def count(mapping: Any, key: str) -> int:
        if isinstance(mapping, dict):
            value = mapping.get(key)
            if isinstance(value, (int, float)):
                return int(value)
        return 0

    review_gap_count = (
        count(acceptance_summary, "fail_count")
        + count(acceptance_summary, "partial_count")
        + count(workbench_summary, "review_queue_count")
        + count(workbench_summary, "policy_review_required_count")
        + count(workbench_summary, "needs_followup_count")
    )
    contested_count = (
        count(workbench_summary, "contested_fact_count")
        + count(workbench_summary, "contested_item_count")
        + count(workbench_summary, "contested_chronology_item_count")
    )
    return {
        "pass_count": max(count(acceptance_summary, "pass_count"), count(workbench_summary, "reviewed_fact_count")),
        "review_gap_count": review_gap_count,
        "contested_count": contested_count,
        "fact_count": count(workbench_summary, "fact_count"),
        "review_queue_count": count(workbench_summary, "review_queue_count"),
        "event_count": count(workbench_summary, "event_count") + count(workbench_summary, "approximate_event_count"),
        "observation_count": count(workbench_summary, "observation_count"),
        "statement_count": count(workbench_summary, "statement_count"),
        "source_count": count(workbench_summary, "source_count"),
        "excerpt_count": count(workbench_summary, "excerpt_count"),
    }


def _build_sl_flow_tags(payload: dict[str, Any], counters: dict[str, int]) -> list[str]:
    tags: list[str] = []

    def append(value: Any) -> None:
        token = _feature_tag(value)
        if token and token not in tags:
            tags.append(token)

    selector = payload.get("selector")
    acceptance = payload.get("acceptance")
    workbench = payload.get("workbench")
    append("SL")
    if isinstance(selector, dict):
        append(selector.get("workflow_kind"))
        append(selector.get("wave"))
        append(selector.get("source_label"))
    if isinstance(acceptance, dict):
        append("ACCEPTANCE")
        append(acceptance.get("fixture_kind"))
    if isinstance(workbench, dict):
        append("WORKBENCH")
    if counters.get("pass_count", 0) > 0:
        append("ACCEPTANCE_PASS")
    if counters.get("review_gap_count", 0) > 0:
        append("REVIEW_QUEUE")
        append("REVIEW_GAP")
    if counters.get("contested_count", 0) > 0:
        append("CONTESTED")
    if counters.get("event_count", 0) > 0:
        append("CHRONOLOGY")
    if counters.get("fact_count", 0) > 0:
        append("FACT_STATE")
    if isinstance(workbench, dict) and isinstance(workbench.get("zelph"), dict):
        append("ZELPH")
    if _counter_from_summary(payload, "legal_procedural_review_queue_count") > 0:
        append("LEGAL_PROCEDURAL")
    return tags


def _derive_sl_transition(payload: dict[str, Any]) -> str:
    selector = payload.get("selector")
    workflow_kind = selector.get("workflow_kind") if isinstance(selector, dict) else None
    if workflow_kind:
        return _feature_tag(workflow_kind) or "SL_FLOW"
    return "SL_FLOW"


def _counter_from_summary(payload: dict[str, Any], key: str) -> int:
    summary = _lookup(payload, "workbench", "summary")
    if isinstance(summary, dict):
        value = summary.get(key)
        if isinstance(value, (int, float)):
            return int(value)
    return 0


def _build_trace_flow_tags(
    stage_family: str,
    section: Any,
    status: Any,
    domain_roles: list[str],
    domain_signals: list[str],
) -> list[str]:
    tags: list[str] = ["TRACE", _feature_tag(stage_family) or "OTHER"]
    section_tag = _feature_tag(section)
    status_tag = _feature_tag(status)
    if section_tag and section_tag not in tags:
        tags.append(section_tag)
    if status_tag and status_tag not in tags:
        tags.append(status_tag)
    for item in domain_roles:
        token = _feature_tag(item)
        if token and token not in tags:
            tags.append(token)
    for item in domain_signals:
        token = _feature_tag(item)
        if token and token not in tags:
            tags.append(token)
    return tags


def _derive_trace_region(
    stage_slug: str,
    stage_family: str,
    section: Any,
    domain_roles: list[str],
    domain_signals: list[str],
) -> str:
    for value in (section, domain_roles[0] if domain_roles else None, domain_signals[0] if domain_signals else None):
        token = _feature_tag(value)
        if token:
            return token
    return _feature_tag(stage_family) or _feature_tag(stage_slug) or "TRACE"


def _build_trace_register_changes(
    *,
    index: int,
    completed: float | None,
    total: float | None,
    message_length: float,
    role_count: float,
    signal_count: float,
    previous_completed: float | None,
    previous_total: float | None,
    previous_message_length: float | None,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = [{"register": "AX", "old": max(index - 1, 0), "new": index}]
    if completed is not None:
        rows.append({"register": "BX", "old": previous_completed or 0, "new": completed})
    if total is not None:
        rows.append({"register": "CX", "old": previous_total or 0, "new": total})
    rows.append({"register": "DX", "old": previous_message_length or 0, "new": message_length})
    rows.append({"register": "SI", "old": 0, "new": role_count})
    rows.append({"register": "DI", "old": 0, "new": signal_count})
    return rows


def _register_fingerprint_for_value(value: int) -> str:
    if value <= 0:
        return "C"
    if value <= 2:
        return "L"
    if value <= 5:
        return "M"
    return "H"


def _feature_tag(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    token = re.sub(r"[^A-Za-z0-9]+", "_", text).strip("_").upper()
    return token or None


def _build_affidavit_semantic_gap_metrics(payload: dict[str, Any]) -> list[dict[str, Any]]:
    summary = payload.get("summary")
    if not isinstance(summary, dict):
        return []

    def as_number(value: Any) -> float:
        return float(value) if isinstance(value, (int, float)) else 0.0

    conflict_counts = summary.get("conflict_state_counts")
    unresolved_conflicts = 0.0
    if isinstance(conflict_counts, dict):
        unresolved_conflicts = as_number(conflict_counts.get("unresolved"))

    missing_review_count = as_number(summary.get("missing_review_count"))
    contested_affidavit_count = as_number(summary.get("contested_affidavit_count"))
    covered_count = as_number(summary.get("covered_count"))

    weights = {
        "missing_review": 1.0,
        "unresolved_conflict": 3.0,
        "contested_affidavit": 2.0,
        "covered_credit": 1.0,
    }
    semantic_gap_score = max(
        weights["missing_review"] * missing_review_count
        + weights["unresolved_conflict"] * unresolved_conflicts
        + weights["contested_affidavit"] * contested_affidavit_count
        - weights["covered_credit"] * covered_count,
        0.0,
    )

    return [
        {"metric": "semantic_gap_score", "value": semantic_gap_score, "unit": "semantic_cost"},
        {
            "metric": "semantic_gap_model_version",
            "value": 1,
            "unit": "version",
        },
        {
            "metric": "semantic_gap_terms.missing_review_count",
            "value": missing_review_count,
            "unit": "count",
        },
        {
            "metric": "semantic_gap_terms.unresolved_conflict_count",
            "value": unresolved_conflicts,
            "unit": "count",
        },
        {
            "metric": "semantic_gap_terms.contested_affidavit_count",
            "value": contested_affidavit_count,
            "unit": "count",
        },
        {
            "metric": "semantic_gap_terms.covered_count",
            "value": covered_count,
            "unit": "count",
        },
        {
            "metric": "semantic_gap_weights.missing_review",
            "value": weights["missing_review"],
            "unit": "weight",
        },
        {
            "metric": "semantic_gap_weights.unresolved_conflict",
            "value": weights["unresolved_conflict"],
            "unit": "weight",
        },
        {
            "metric": "semantic_gap_weights.contested_affidavit",
            "value": weights["contested_affidavit"],
            "unit": "weight",
        },
        {
            "metric": "semantic_gap_weights.covered_credit",
            "value": weights["covered_credit"],
            "unit": "weight",
        },
    ]


def _walk_counts(value: Any, *, depth: int = 1) -> dict[str, int]:
    counts = {
        "dict_nodes": 0,
        "list_nodes": 0,
        "scalar_nodes": 0,
        "max_depth": depth,
    }
    if isinstance(value, dict):
        counts["dict_nodes"] += 1
        for child in value.values():
            child_counts = _walk_counts(child, depth=depth + 1)
            counts = _merge_counts(counts, child_counts)
        return counts
    if isinstance(value, list):
        counts["list_nodes"] += 1
        for child in value:
            child_counts = _walk_counts(child, depth=depth + 1)
            counts = _merge_counts(counts, child_counts)
        return counts
    counts["scalar_nodes"] += 1
    return counts


def _merge_counts(left: dict[str, int], right: dict[str, int]) -> dict[str, int]:
    left["dict_nodes"] += right["dict_nodes"]
    left["list_nodes"] += right["list_nodes"]
    left["scalar_nodes"] += right["scalar_nodes"]
    left["max_depth"] = max(left["max_depth"], right["max_depth"])
    return left


def _count_field(rows: list[Any], field: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        if isinstance(row, dict):
            value = row.get(field)
            if value is None:
                continue
            key = str(value)
            counts[key] = counts.get(key, 0) + 1
    return counts


def _build_proof_refs(payload: dict[str, Any]) -> list[dict[str, str]]:
    refs: list[dict[str, str]] = []
    workflow_link = _lookup(payload, "acceptance", "run", "workflow_link")
    if isinstance(workflow_link, dict):
        workflow_kind = workflow_link.get("workflow_kind")
        workflow_run_id = workflow_link.get("workflow_run_id")
        if workflow_kind and workflow_run_id:
            refs.append(
                {
                    "kind": str(workflow_kind),
                    "ref": str(workflow_run_id),
                }
            )
    semantic_run_id = _lookup(payload, "run", "semantic_run_id")
    if semantic_run_id:
        refs.append({"kind": "semantic_run", "ref": str(semantic_run_id)})
    return refs


def _build_related_artifact_refs(payload: dict[str, Any]) -> list[dict[str, str]]:
    refs: list[dict[str, str]] = []
    for key_path, kind in (
        (("run", "semantic_run_id"), "semantic_run"),
        (("acceptance", "run", "run_id"), "fact_run"),
        (("acceptance", "run", "workflow_link", "workflow_run_id"), "workflow_run"),
    ):
        value = _lookup(payload, *key_path)
        if value:
            refs.append({"kind": kind, "ref": str(value)})
    return refs


def _load_sensiblaw_contested_review_helpers():
    sensiblaw_root = Path(__file__).resolve().parents[1] / "SensibLaw"
    sensiblaw_src = sensiblaw_root / "src"
    for path in (sensiblaw_root, sensiblaw_src):
        if path.exists() and str(path) not in sys.path:
            sys.path.insert(0, str(path))
    try:
        from fact_intake import (  # type: ignore
            build_contested_affidavit_review_summary,
            list_contested_affidavit_review_runs,
        )
    except Exception as exc:  # pragma: no cover - import error path
        raise RuntimeError(
            "Unable to import SensibLaw contested-review helpers; expected SensibLaw/src on sys.path"
        ) from exc
    return build_contested_affidavit_review_summary, list_contested_affidavit_review_runs


def _slugify(value: str) -> str:
    chars = []
    for char in value.lower():
        chars.append(char if char.isalnum() else "-")
    slug = "".join(chars).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug or "trace"
