"""Read-only GO-CAM/SBML/assay candidate projection onto the canonical ITIR world-model boundary.

Does not modify PostgreSQL, use SQLite, manufacture PNF factors, or bypass
the generic source-span/parser/reviewer/promotion architecture.  Identifiers
and provenance are external/source-bound, not semantic identity proofs.
"""
from __future__ import annotations

import hashlib
import json
from decimal import Decimal, InvalidOperation
from collections.abc import Mapping
from typing import Any

VERSION = "itir.biological.source-candidate.v1"


def _digest(value: Any) -> str:
    canonical = json.dumps(value, sort_keys=True, ensure_ascii=False,
                           separators=(",", ":"), default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _nonempty(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"missing {name}")
    return value.strip()


def _sha(value: object) -> str:
    s = _nonempty(value, "source sha256")
    if len(s) != 64 or any(x not in "0123456789abcdef" for x in s.lower()):
        raise ValueError("source sha256 must contain 64 hexadecimal characters")
    return s.lower()


def _candidate_evidence(value: object) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ValueError("candidate causal relation must retain original evidence")
    refs = []
    for item in value:
        if not isinstance(item, Mapping):
            raise ValueError("candidate evidence must be structured")
        reference = item.get("reference")
        if isinstance(reference, Mapping):
            reference = reference.get("id")
        refs.append(_nonempty(reference, "original evidence reference"))
    return sorted(set(refs))


_TRANSPORT_MODES = {
    "local_diffusion", "vascular_perfusion", "plasma_membrane",
    "interstitial", "gap_junction", "blood_brain_barrier",
}


def _nonnegative_decimal(value: object, label: str) -> str:
    try:
        result = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValueError(f"invalid {label}") from exc
    if not result.is_finite() or result < 0:
        raise ValueError(f"invalid {label}")
    return str(result)


def _project_spatial_assay(report: Mapping[str, Any]) -> dict[str, Any]:
    if report.get("status") != "source-matched-spatial-observation-not-kinetic-mechanism":
        raise ValueError("spatial assay has not passed selected source qualification")
    if report.get("pnf_mutation_performed") is not False:
        raise ValueError("spatial assay cannot claim canonical mutation")
    if report.get("original_source_digest_verified_by_independent_fetch") is not False:
        raise ValueError("unreviewed source digest cannot self-claim external authentication")
    if report.get("transport_mode_claim_independently_validated") is not False:
        raise ValueError("transport mechanism must not self-promote from a candidate")
    digest = _sha(report.get("source_sha256"))
    if digest != _sha(report.get("original_csv_sha256")):
        raise ValueError("spatial source assay digest discrepancy")
    original_digest = _sha(report.get("original_source_sha256_declared"))
    original_id = _nonempty(report.get("original_source"), "original spatial source ID")
    if original_id != _nonempty(report.get("source_id"), "spatial source ID"):
        raise ValueError("spatial original-source ID mismatch")
    raw = report.get("context_measurements")
    if not isinstance(raw, list) or not raw:
        raise ValueError("spatial candidate requires measured context rows")
    count = report.get("original_measurement_rows")
    if type(count) is not int or count != len(raw):
        raise ValueError("spatial report measured row count mismatch")
    if not raw:
        raise ValueError("spatial report cannot be empty")
    seen = set()
    contexts = []
    for entry in raw:
        if not isinstance(entry, Mapping):
            raise ValueError("malformed spatial measurement row")
        ident = tuple(_nonempty(entry.get(key), key) for key in
            ("specimen", "region", "compartment"))
        time = _nonnegative_decimal(entry.get("time_s"), "spatial time")
        context_key = (ident[0], time, ident[1], ident[2])
        if context_key in seen:
            raise ValueError("duplicate same specimen/time/location spatial observation")
        seen.add(context_key)
        mode = _nonempty(entry.get("transport_mode"), "transport mode")
        if mode not in _TRANSPORT_MODES:
            raise ValueError("unsupported physical transport mode")
        context = {
            "specimen_id": ident[0],
            "time_s": time,
            "region": ident[1],
            "compartment": ident[2],
            "bh4_amount_mol": _nonnegative_decimal(
                entry.get("bh4_amount_mol"), "BH4 molar amount"
            ),
            "bh2_amount_mol": _nonnegative_decimal(
                entry.get("bh2_amount_mol"), "BH2 molar amount"
            ),
            "delivery_connection_id": _nonempty(
                entry.get("connection_id"), "spatial transport connection"
            ),
            "transport_mode": mode,
            "transport_original_reference": _nonempty(
                entry.get("transport_source_reference"), "original transport reference"
            ),
            "experiment_id": _nonempty(entry.get("experiment"), "original experiment"),
            "split": _nonempty(entry.get("split"), "original evaluation split"),
            "candidate_only": True,
            "same_physical_model_established": False,
            "transport_law_validated": False,
            "pnf_promoted": False,
        }
        contexts.append(context)
    return {
        "source_id": original_id,
        "original_source_digest_declared": original_digest,
        "measured_csv_sha256": digest,
        "candidate_only": True,
        "same_specimen_context_rows": contexts,
        "same_physical_model_established": False,
        "transport_law_validated": False,
        "clinical_or_causal_mechanism_established": False,
        "pnf_mutation_performed": False,
    }


def project_biological_sources(
    receipt: Mapping[str, Any],
    *,
    kinetic_calibration: Mapping[str, Any] | None = None,
    genotype_holdout: Mapping[str, Any] | None = None,
    spatial_measurement: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Pure candidate-only projection. Never read or write PNF automatically."""
    if receipt.get("status") != "unpromoted-source-intake":
        raise ValueError("not an unpromoted source-intake receipt")
    if receipt.get("pnf_mutation_performed") is not False:
        raise ValueError("source receipt cannot claim PNF mutation")
    if receipt.get("biological_calibration_proven") is not False:
        raise ValueError("input inappropriately promotes biological calibration")
    gocam, sbml = receipt.get("gocam"), receipt.get("sbml")
    if not isinstance(gocam, Mapping) or not isinstance(sbml, Mapping):
        raise ValueError("GO-CAM and SBML source blocks required")
    go_id = _nonempty(gocam.get("model_id"), "GO-CAM model id")
    sbml_id = _nonempty(sbml.get("model_id"), "SBML model id")
    go_sha, sbml_sha = _sha(gocam.get("sha256")), _sha(sbml.get("sha256"))
    sources = [
        {"source_kind": "GO-CAM", "source_id": go_id, "sha256": go_sha,
         "schema_validated": gocam.get("schema_validated") is True},
        {"source_kind": "SBML", "source_id": sbml_id, "sha256": sbml_sha,
         "schema_validated": sbml.get("schema_validated") is True},
    ]
    activities = gocam.get("activities")
    reactions = sbml.get("reactions")
    if not isinstance(activities, list) or not isinstance(reactions, list):
        raise ValueError("activities and reactions must be arrays")
    aids = set()
    statements = []
    source_evidence_by_activity: dict[str, set[str]] = {}
    for activity in activities:
        if not isinstance(activity, Mapping):
            raise ValueError("malformed activity")
        subject = _nonempty(activity.get("id"), "activity id")
        if subject in aids:
            raise ValueError("duplicate activity identifier")
        aids.add(subject)
    for activity in activities:
        subject = activity["id"]
        activity_evidence: set[str] = set()
        original_molecular_evidence = activity.get("molecular_function_evidence") or []
        if original_molecular_evidence:
            activity_evidence.update(_candidate_evidence(original_molecular_evidence))
        for edge in activity.get("causal_associations") or ():
            if not isinstance(edge, Mapping):
                raise ValueError("malformed causal relation")
            predicate = _nonempty(edge.get("predicate"), "RO predicate")
            object_id = _nonempty(
                edge.get("downstream_activity"), "downstream activity"
            )
            if object_id not in aids:
                raise ValueError("out-of-model causal reference")
            evidence_refs = _candidate_evidence(edge.get("evidence"))
            activity_evidence.update(evidence_refs)
            candidate = {
                "source_id": go_id, "source_sha256": go_sha,
                "subject": subject, "predicate": predicate,
                "object": object_id, "evidence_refs": evidence_refs,
                "candidate_only": True, "rejected": False,
                "reviewed": False, "promoted": False,
            }
            candidate["candidate_ref"] = "biology:candidate:" + _digest(candidate)
            statements.append(candidate)
        source_evidence_by_activity[subject] = activity_evidence
    rids = set()
    for reaction in reactions:
        if not isinstance(reaction, Mapping):
            raise ValueError("malformed SBML reaction")
        ident = _nonempty(reaction.get("id"), "reaction id")
        if ident in rids:
            raise ValueError("duplicate SBML reaction id")
        rids.add(ident)
    joins = []
    for edge in receipt.get("candidate_joins") or ():
        if not isinstance(edge, Mapping) or edge.get("trusted") is not False:
            raise ValueError("only untrusted candidate joins can be imported")
        aid = _nonempty(edge.get("gocam_activity"), "join activity")
        rid = _nonempty(edge.get("sbml_reaction"), "join reaction")
        ev = _nonempty(edge.get("evidence_reference"), "join original reference")
        if aid not in aids or rid not in rids:
            raise ValueError("join endpoint not present in source")
        if ev not in source_evidence_by_activity[aid]:
            raise ValueError(
                "join evidence not attached to original selected GO-CAM activity"
            )
        joins.append({
            "left": {"kind":"GO-CAM activity","id":aid,"source_sha256":go_sha},
            "right": {"kind":"SBML reaction","id":rid,"source_sha256":sbml_sha},
            "original_evidence_reference": ev,
            "candidate_only": True, "identity_established": False,
            "mechanism_validated": False, "promotion_permitted": False,
        })
    if len({(j["left"]["id"],j["right"]["id"]) for j in joins}) != len(joins):
        raise ValueError("duplicate source candidate joins")
    studies = []
    for kind, report in (
        ("kinetics", kinetic_calibration),
        ("genotype_holdout", genotype_holdout),
    ):
        if report is None:
            continue
        if not isinstance(report, Mapping):
            raise ValueError("assay report must be a mapping")
        if report.get("pnf_mutation_performed") is not False:
            raise ValueError("assay report claims canonical-world mutation")
        study_sha = _sha(report.get("source_sha256"))
        study = {
            "kind": kind,
            "original_source_id": _nonempty(
                report.get("source_id")
                if kind=="kinetics"
                else (report.get("metadata") or {}).get("source"),
                "assay source id"
            ),
            "sha256": study_sha,
            "status": _nonempty(report.get("status"), "report status"),
            "candidate_only":True,
            "bio_model_identity_established":False,
            "biological_mechanism_validated":False,
        }
        studies.append(study)
    spatial_candidates = (
        _project_spatial_assay(spatial_measurement)
        if spatial_measurement is not None else None
    )
    bundle = {
        "spatial_observation_candidates": spatial_candidates,
        "schema":VERSION,
        "authority":"source-evidence-candidate-only",
        "source_artifacts":sources,
        "candidate_statements":statements,
        "candidate_joins":joins,
        "assay_evidence":studies,
        "original_receipt_digest":_digest(receipt),
        "pnf_promotion":False, "postgres_mutation":False,
        "source_statement_parser_invoked":False,
        "required_next_authority":[
            "original model schema validation",
            "producer-supplied source spans",
            "canonical SLR/PNF parser",
            "typed evidence review",
            "separate PostgreSQL promotion receipt",
        ],
    }
    bundle["bundle_id"] = "biology:bundle:" + _digest(bundle)
    return bundle
