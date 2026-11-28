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



def _view_evidence_request(payload: Mapping[str, Any]):
    """Validate native coordinates and inverse accounting only; Rust owns the
    signed reducer and authenticated formal readback. No caller proof payload."""
    family = _coordinate(payload, "family_ref")
    query = _coordinate(payload, "query_ref")
    requests = payload.get("pair_evidence", [])
    keys = ("left_selector_ref", "right_selector_ref", "evidence_ref",
            "repo", "sha", "path", "canonical_thread_id")
    if not isinstance(requests, list) or len(requests) > 45:
        raise ToolInputError("Expected at most 45 existing pair evidence coordinates")
    normalized = []
    requested = {}
    evidence_ids = set()
    for req in requests:
        if not isinstance(req, dict) or set(req) != set(keys):
            raise ToolInputError("Only existing pair evidence locator coordinates are accepted")
        row = {k: _coordinate(req, k) for k in keys}
        pair = tuple(sorted((row["left_selector_ref"], row["right_selector_ref"])))
        if pair[0] == pair[1] or pair in requested or row["evidence_ref"] in evidence_ids:
            raise ToolInputError("Duplicate or self pair evidence")
        requested[pair] = row
        evidence_ids.add(row["evidence_ref"])
        normalized.append(row)
    encoded = json.dumps(normalized, ensure_ascii=False, separators=(",", ":"))
    if len(encoded.encode("utf-8")) > 65536:
        raise ToolInputError("Pair evidence coordinate request too large")
    return family, query, encoded, requested


def _inspect_licensed_view_cohort(payload: Mapping[str, Any]) -> dict[str, Any]:
    family, query, encoded, requested = _view_evidence_request(payload)
    raw = _native(["relational-family", "inspect-licensed-view-cohort", family, query, encoded])
    if (raw.get("schema") != "slr.authenticated-view-cohort.v1"
            or raw.get("family_ref") != family or raw.get("query_ref") != query
            or raw.get("shared_transaction_snapshot") is not True
            or any(raw.get(k) is not False for k in (
                "derives_transitive_licences", "formal_consumer_equivalence_paid",
                "all_live_semantic_readings_covered", "creates_semantic_authority",
                "source_independence_paid", "world_truth_paid", "writes_database"))):
        raise ToolExecutionError("Invalid authenticated native cohort")
    selectors = raw.get("selector_refs")
    pairs = raw.get("pairs")
    if (not isinstance(selectors, list) or not 2 <= len(selectors) <= 10
            or any(not isinstance(s, str) or not s for s in selectors)
            or len(set(selectors)) != len(selectors)
            or not isinstance(pairs, list)):
        raise ToolExecutionError("Invalid cohort selector universe")
    universe = {(a, b) for a in selectors for b in selectors if a < b}
    seen = set()
    pair_refs = set()
    paid = available = equal = 0
    observed_answers = {}
    derived_inconsistent = set()
    for row in pairs:
        if not isinstance(row, dict):
            raise ToolExecutionError("Invalid native pair row")
        pair = (row.get("left_selector_ref"), row.get("right_selector_ref"))
        if (any(not isinstance(x, str) for x in pair) or pair not in universe or pair in seen
                or row.get("source_independence_paid") is not False
                or row.get("residual_paid") is not False
                or any(not isinstance(row.get(k), str) or not row[k] for k in
                       ("pair_ref", "forward_comparison_ref", "backward_comparison_ref"))
                or row["pair_ref"] in pair_refs):
            raise ToolExecutionError("Invalid native pair coordinate")
        seen.add(pair)
        pair_refs.add(row["pair_ref"])
        f, b = row.get("forward"), row.get("backward")
        if (not isinstance(f, dict) or not isinstance(b, dict)
                or not all(k in f and k in b for k in (
                    "status", "left_support", "right_support", "lost", "gained",
                    "opposed_signs", "bounded_signed_support_equal"))
                or f["left_support"] != b["right_support"]
                or f["right_support"] != b["left_support"]
                or f["lost"] != b["gained"] or f["gained"] != b["lost"]
                or f["status"] != b["status"]
                or f["opposed_signs"] != b["opposed_signs"]
                or f["bounded_signed_support_equal"] != b["bounded_signed_support_equal"]):
            raise ToolExecutionError("Native pair inverse mismatch")
        proof = row.get("authenticated_pair")
        req = requested.get(pair)
        if req is None:
            if (proof is not None or f["status"] != "missing_authenticated_pair"
                    or any(f[k] is not None for k in ("left_support", "right_support",
                        "lost", "gained", "opposed_signs", "bounded_signed_support_equal"))):
                raise ToolExecutionError("Unexpected proof for unrequested pair")
            continue
        if not isinstance(proof, dict):
            raise ToolExecutionError("Requested pair has no authenticated readback")
        binding, premise, answer = (proof.get(k) for k in
                                    ("binding", "authenticated_formal_premise", "answer"))
        if (proof.get("schema") != "slr.authenticated-bounded-reciprocal-query.v1"
                or proof.get("family_ref") != family or proof.get("query_ref") != query
                or any(proof.get(k) is not False for k in (
                    "creates_semantic_authority", "all_live_semantic_readings_covered",
                    "governed_identity_paid", "world_truth_paid", "writes_database"))
                or not all(isinstance(x, dict) for x in (binding, premise, answer))
                or any(binding.get(k) != v for k, v in {
                    "family_ref": family, "query_ref": query,
                    "consumer_ref": raw.get("consumer_ref"),
                    "left_selector_ref": req["left_selector_ref"],
                    "right_selector_ref": req["right_selector_ref"],
                    "evidence_ref": req["evidence_ref"]}.items())
                or premise.get("evidence_ref") != req["evidence_ref"]
                or premise.get("formal_premise_paid") is not True
                or premise.get("statement_digest") != binding.get("statement_digest")
                or any(premise.get(k) is not False for k in (
                    "creates_legal_authority", "applicability_promoted", "claim_truth_promoted"))
                or answer.get("schema") != "slr.signed-view-query-answer.v1"
                or answer.get("query_ref") != query
                or not all(k in answer for k in ("left_support", "right_support"))):
            raise ToolExecutionError("Foreign or promotion-bearing pair proof")
        left, right = answer["left_support"], answer["right_support"]
        if req["left_selector_ref"] != pair[0]:
            left, right = right, left
        if f["left_support"] != left or f["right_support"] != right:
            raise ToolExecutionError("Native signed answer differs from authenticated answer")
        if any(x is not None and (not isinstance(x, dict) or set(x) != {"positive", "negative"}
                   or any(type(v) is not bool for v in x.values())) for x in (left, right)):
            raise ToolExecutionError("Invalid signed support")
        if (binding.get("forward_comparison_ref") != row[
                "forward_comparison_ref" if req["left_selector_ref"] == pair[0] else "backward_comparison_ref"]
                or binding.get("backward_comparison_ref") != row[
                "backward_comparison_ref" if req["left_selector_ref"] == pair[0] else "forward_comparison_ref"]):
            raise ToolExecutionError("Native proof comparison binding mismatch")
        for selector, support in zip(pair, (left, right)):
            if selector in observed_answers and observed_answers[selector] != support:
                derived_inconsistent.add(selector)
            observed_answers[selector] = support
        paid += 1
        if left is None or right is None:
            if (f["status"] != "unavailable_answer"
                    or any(f[k] is not None for k in ("lost", "gained", "opposed_signs",
                                                     "bounded_signed_support_equal"))):
                raise ToolExecutionError("Unavailable answer promoted to parity")
        else:
            available += 1
            same = f["bounded_signed_support_equal"]
            if (type(same) is not bool or same != (left == right)
                    or f["status"] != ("preserved" if same else "different")
                    or f["lost"] != {k: left[k] and not right[k] for k in left}
                    or f["gained"] != {k: right[k] and not left[k] for k in left}
                    or f["opposed_signs"] is not ((left["positive"] and right["negative"])
                                                or (left["negative"] and right["positive"]))):
                raise ToolExecutionError("Invalid bounded support disposition")
            equal += int(same)
    inconsistent = raw.get("inconsistent_selector_refs")
    if (seen != universe or not set(requested).issubset(universe)
            or not isinstance(inconsistent, list)
            or any(not isinstance(s, str) or s not in selectors for s in inconsistent)
            or len(set(inconsistent)) != len(inconsistent)
            or set(inconsistent) != derived_inconsistent
            or any(type(raw.get(k)) is not int or raw[k] != v for k, v in {
                "pair_count": len(universe), "authenticated_pair_count": paid,
                "available_pair_count": available, "equal_support_pair_count": equal}.items())
            or raw.get("all_pairs_bounded_signed_support_equal") is not
                (equal == len(universe) and not inconsistent)):
        raise ToolExecutionError("Native cohort coverage accounting mismatch")
    return raw



def _inspect_query_context(payload: Mapping[str, Any], expand: bool) -> dict[str, Any]:
    family, query, encoded, requested = _view_evidence_request(payload)
    args = ["relational-family",
            "expand-query-context-capsule" if expand else "inspect-query-context-capsule",
            family, query, encoded]
    def digest(value):
        return (isinstance(value, str) and value.startswith("sha256:")
                and len(value) == 71 and all(c in "0123456789abcdef" for c in value[7:]))
    expected = None
    if expand:
        expected = _coordinate(payload, "capsule_digest")
        if not digest(expected):
            raise ToolInputError("Expected canonical capsule digest")
        args.append(expected)
    raw = _native(args)
    if expand:
        if (raw.get("schema") != "slr.query-context-expanded.v1"
                or raw.get("capsule_digest") != expected
                or raw.get("exact_current_replay") is not True
                or raw.get("creates_semantic_authority") is not False
                or raw.get("writes_database") is not False):
            raise ToolExecutionError("Stale or foreign native capsule expansion")
        envelope = raw.get("capsule_envelope")
        if not isinstance(envelope, dict) or envelope.get("capsule_digest") != expected:
            raise ToolExecutionError("Wrong expanded capsule digest")
    else:
        envelope = raw
    cap = envelope.get("capsule")
    if (envelope.get("schema") != "slr.query-context-capsule-envelope.v1"
            or not digest(envelope.get("capsule_digest"))
            or envelope.get("creates_semantic_authority") is not False
            or envelope.get("writes_database") is not False
            or not isinstance(cap, dict)
            or cap.get("schema") != "slr.query-context-capsule.v1"
            or cap.get("family_ref") != family or cap.get("query_ref") != query
            or not all(digest(cap.get(k)) for k in ("family_digest", "full_readback_digest"))
            or any(cap.get(k) is not True for k in ("noncanonical", "query_scoped",
                                                   "shared_transaction_snapshot"))
            or any(cap.get(k) is not False for k in ("creates_semantic_authority",
                                                    "world_truth_paid", "writes_database"))
            or not all(isinstance(cap.get(k), list) for k in (
                "sources", "pairs", "residuals", "reviews", "lifecycles", "queues", "pair_evidence"))):
        raise ToolExecutionError("Invalid native context capsule")
    full, compact = (envelope.get(k) for k in ("full_readback_json_bytes", "capsule_body_json_bytes"))
    loss = cap.get("loss_profile")
    if (type(full) is not int or type(compact) is not int or min(full, compact) <= 0
            or envelope.get("body_smaller_than_full_readback") is not (compact < full)
            or not isinstance(loss, dict) or not isinstance(loss.get("omitted_inline"), list)
            or not loss["omitted_inline"] or loss.get("canonical_owners_retained") is not True
            or loss.get("omission_implies_irrelevance") is not False
            or loss.get("expansion_requires_exact_current_replay") is not True):
        raise ToolExecutionError("Invalid context compression loss accounting")
    # Native authority remains in Rust. Check the compact coordinate inverse
    # and ensure no residual, review or pair disappears from the carrier.
    def unique_rows(name, key):
        rows = cap[name]
        if any(not isinstance(r, dict) or not isinstance(r.get(key), str) or not r[key] for r in rows):
            raise ToolExecutionError("Invalid capsule coordinate")
        refs = {r[key] for r in rows}
        if len(refs) != len(rows):
            raise ToolExecutionError("Duplicate capsule coordinate")
        return refs
    selectors = unique_rows("sources", "selector_ref")
    residuals = unique_rows("residuals", "residual_ref")
    reviews = unique_rows("reviews", "review_item_ref")
    obligations = unique_rows("queues", "obligation_ref")
    if (not 2 <= len(selectors) <= 10 or unique_rows("lifecycles", "obligation_ref") != obligations
            or {r.get("obligation_ref") for r in cap["reviews"]} != obligations
            or any(r.get("acquisition_obligation_ref") not in obligations for r in cap["residuals"])):
        raise ToolExecutionError("Capsule residual/review lifecycle inverse mismatch")
    if any(not digest(r.get("observation_digest")) or not isinstance(r.get("context"), dict)
           or not all(isinstance(r.get(k), str) and r[k] for k in (
               "source_revision_ref", "source_span_ref", "predicate_candidate_ref", "observation_ref"))
           for r in cap["sources"]):
        raise ToolExecutionError("Capsule source inverse missing")
    unique_rows("pairs", "pair_ref")
    universe = {(a, b) for a in selectors for b in selectors if a < b}
    actual = {(r.get("left_selector_ref"), r.get("right_selector_ref")) for r in cap["pairs"]}
    if actual != universe or len(actual) != len(cap["pairs"]):
        raise ToolExecutionError("Capsule pair universe mismatch")
    if sorted(cap["pair_evidence"], key=lambda r: (r["left_selector_ref"], r["right_selector_ref"])) != sorted(
            requested.values(), key=lambda r: (r["left_selector_ref"], r["right_selector_ref"])):
        raise ToolExecutionError("Capsule evidence locator mismatch")
    for r in cap["pairs"]:
        pair = (r["left_selector_ref"], r["right_selector_ref"])
        f, b = r.get("forward"), r.get("backward")
        if (not isinstance(f, dict) or not isinstance(b, dict)
                or f.get("lost") != b.get("gained") or f.get("gained") != b.get("lost")
                or f.get("left_support") != b.get("right_support")
                or f.get("right_support") != b.get("left_support")
                or r.get("residual_paid") is not False or r.get("source_independence_paid") is not False):
            raise ToolExecutionError("Capsule signed pair inverse mismatch")
        if pair not in requested:
            if (r.get("proof_binding") is not None or r.get("formal_premise") is not None
                    or r.get("proof_readback_digest") is not None
                    or f.get("status") != "missing_authenticated_pair"):
                raise ToolExecutionError("Unrequested capsule proof")
        else:
            binding, premise = r.get("proof_binding"), r.get("formal_premise")
            req = requested[pair]
            if (not digest(r.get("proof_readback_digest")) or not isinstance(binding, dict)
                    or not isinstance(premise, dict) or premise.get("formal_premise_paid") is not True
                    or premise.get("evidence_ref") != req["evidence_ref"]
                    or any(binding.get(k) != v for k, v in (
                        ("family_ref", family), ("query_ref", query),
                        ("left_selector_ref", req["left_selector_ref"]),
                        ("right_selector_ref", req["right_selector_ref"]),
                        ("evidence_ref", req["evidence_ref"])))):
                raise ToolExecutionError("Foreign capsule proof")
    if expand:
        full_family, cohort = raw.get("family"), raw.get("cohort")
        if (not isinstance(full_family, dict) or full_family.get("family_ref") != family
                or not isinstance(cohort, dict) or cohort.get("family_ref") != family
                or cohort.get("query_ref") != query or cohort.get("world_truth_paid") is not False):
            raise ToolExecutionError("Foreign expanded canonical readback")
    return raw


def _inspect_signed_query_frontier(payload: Mapping[str, Any]) -> dict[str, Any]:
    family, query, encoded, _ = _view_evidence_request(payload)
    digest = _coordinate(payload, "capsule_digest")
    if not (digest.startswith("sha256:") and len(digest)==71
            and all(c in "0123456789abcdef" for c in digest[7:])):
        raise ToolInputError("Exact current capsule digest required")
    raw = _native(["relational-family","inspect-signed-query-frontier",family,query,encoded,digest])
    if (raw.get("schema")!="slr.signed-query-frontier.v1"
            or raw.get("family_ref")!=family or raw.get("query_ref")!=query
            or raw.get("capsule_digest")!=digest or raw.get("exact_current_replay") is not True
            or raw.get("candidate_only") is not True
            or any(raw.get(k) is not False for k in ("formal_consumer_equivalence_paid",
                "world_truth_paid","writes_database","executes_acquisition"))
            or not all(isinstance(raw.get(k),list) for k in ("obligations","structural_residuals","existing_queues"))):
        raise ToolExecutionError("Invalid signed query frontier")
    ids=set()
    residuals=raw["structural_residuals"]
    if any(not isinstance(r,dict) or not isinstance(r.get("residual_ref"),str) for r in residuals):
        raise ToolExecutionError("Invalid structural residual inverse")
    residual_ids={r["residual_ref"] for r in residuals}
    for row in raw["obligations"]:
        if (not isinstance(row,dict) or row.get("candidate_only") is not True
                or row.get("paid") is not False or row.get("requires_reviewed_reentry") is not True
                or not isinstance(row.get("obligation_ref"),str) or row["obligation_ref"] in ids):
            raise ToolExecutionError("Invalid signed query obligation")
        ids.add(row["obligation_ref"])
        reason=row.get("reason")
        if reason=="inconsistent_selector_answer":
            if not isinstance(row.get("selector_ref"),str):
                raise ToolExecutionError("Missing selector inverse")
            continue
        f,b=row.get("forward"),row.get("backward")
        if (not isinstance(f,dict) or not isinstance(b,dict)
                or not all(k in f and k in b for k in ("status","left_support","right_support",
                    "lost","gained","bounded_signed_support_equal"))
                or f["status"]!=b["status"] or f["left_support"]!=b["right_support"]
                or f["right_support"]!=b["left_support"] or f["lost"]!=b["gained"]
                or f["gained"]!=b["lost"] or f["bounded_signed_support_equal"]!=b["bounded_signed_support_equal"]
                or not isinstance(row.get("existing_residual_refs"),list)
                or any(not isinstance(x,str) or x not in residual_ids for x in row["existing_residual_refs"])
                or any(not isinstance(row.get(k),str) or not row[k] for k in ("pair_ref","left_selector_ref",
                    "right_selector_ref","forward_comparison_ref","backward_comparison_ref"))):
            raise ToolExecutionError("Invalid directional obligation inverse")
        expected=("independent_pair_evidence_required" if f["status"]=="missing_authenticated_pair"
                  else "source_consumer_coverage_required" if f["status"]=="unavailable_answer"
                  else "signed_support_discriminator_required" if f["bounded_signed_support_equal"] is False
                  else None)
        if reason!=expected or expected is None:
            raise ToolExecutionError("Incorrect query debt classification")
    return raw


def inspect_relational_family(payload: Mapping[str, Any]) -> dict[str, Any]:
    action = payload.get("action", "family")
    if action == "signed_query_frontier":
        raw = _inspect_signed_query_frontier(payload)
    elif action in ("query_context_capsule", "expand_query_context_capsule"):
        raw = _inspect_query_context(payload, action == "expand_query_context_capsule")
    elif action == "licensed_view_cohort":
        raw = _inspect_licensed_view_cohort(payload)
    elif action == "family":
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
    elif action == "mabo_formal_demands":
        ref = _coordinate(payload, "obligation_ref")
        raw = _native(["relational-family", "inspect-mabo-formal-demands", ref])
        if (raw.get("schema") != "slr.mabo-formal-demand-readback.v1"
                or raw.get("obligation_ref") != ref
                or raw.get("candidate_only") is not True or raw.get("derived_only") is not True
                or any(raw.get(k) is not False for k in (
                    "shared_transaction_snapshot", "kernel_recertified", "establishes_proof",
                    "discharges_obligation", "creates_legal_authority", "claim_truth_promoted",
                    "search_executed", "writes_database"))
                or not all(isinstance(raw.get(k), list) for k in (
                    "demands", "source_review_nodes", "ancestry_edges"))):
            raise ToolExecutionError("Invalid native Mabo formal-demand receipt")
        ids = set()
        for row in raw["demands"]:
            if (not isinstance(row, dict) or row.get("obligation_ref") != ref
                    or row.get("residual_ref") != raw.get("residual_ref")
                    or row.get("candidate_only") is not True
                    or row.get("establishes_proof") is not False
                    or row.get("discharges_obligation") is not False
                    or not all(isinstance(row.get(k), str) and row[k] for k in (
                        "demand_ref", "statement_digest", "target_prover", "pnf_revision_ref",
                        "consumer_ref"))
                    or not isinstance(row.get("all_source_refs_reviewed_in_graph"), bool)
                    or not isinstance(row.get("formal_premise_evidence_refs"), list)
                    or row["demand_ref"] in ids):
                raise ToolExecutionError("Invalid exact Mabo demand coordinate")
            digest = row["statement_digest"]
            if (not digest.startswith("sha256:") or len(digest) != 71
                    or any(c not in "0123456789abcdef" for c in digest[7:])):
                raise ToolExecutionError("Invalid original Mabo statement digest")
            ids.add(row["demand_ref"])
    elif action == "investigation":
        ref = _coordinate(payload, "family_ref")
        raw = _native(["relational-family", "inspect-investigation", ref])
        if (raw.get("schema") != "slr.relational-investigation.v1" or raw.get("family_ref") != ref
                or any(raw.get(k) is not True for k in ("derived_only", "challengeable", "candidate_only"))
                or any(raw.get(k) is not False for k in (
                    "creates_graph_edges", "creates_actual_reopening", "formal_consumer_equivalence_paid",
                    "world_truth_paid", "creates_access_authority", "provider_acquisition_executed",
                    "writes_database"))
                or not all(isinstance(raw.get(k), list) for k in (
                    "gap_rows", "dependency_edges", "potential_reopening_cones"))):
            raise ToolExecutionError("Invalid native investigation receipt")
        gaps = raw["gap_rows"]
        lanes = {}
        ids = set()
        for row in gaps:
            if (not isinstance(row, dict) or row.get("candidate_only") is not True
                    or row.get("residual_paid") is not False
                    or row.get("formal_route_eligible") is not False
                    or not all(isinstance(row.get(k), str) and row[k] for k in (
                        "residual_ref", "comparison_ref", "obligation_ref", "diagnostic_lane", "route_state"))
                    or row["residual_ref"] in ids):
                raise ToolExecutionError("Invalid exact investigation gap")
            ids.add(row["residual_ref"])
            lane = row["diagnostic_lane"]
            lanes[lane] = lanes.get(lane, 0) + 1
        if raw.get("gap_counts") != lanes:
            raise ToolExecutionError("Investigation gap count mismatch")
        if any(not isinstance(c, dict) or c.get("creates_actual_reopening") is not False
               or c.get("creates_semantic_authority") is not False
               for c in raw["potential_reopening_cones"]):
            raise ToolExecutionError("Invalid potential reopening cone")
    elif action in ("recorded_parity", "local_research"):
        ref = _coordinate(payload, "family_ref")
        mode = "inspect-recorded-parity" if action == "recorded_parity" else "inspect-local-research"
        raw = _native(["relational-family", mode, ref])
        schema = ("slr.recorded-family-parity.v1" if action == "recorded_parity"
                  else "slr.relational-local-research.v1")
        if (raw.get("schema") != schema or raw.get("family_ref") != ref
                or raw.get("candidate_only") is not True
                or any(raw.get(k) is not False for k in (
                    "formal_consumer_equivalence_paid", "world_truth_paid", "writes_database"))):
            raise ToolExecutionError("Wrong or promotion-bearing native research receipt")
        if action == "recorded_parity":
            if (raw.get("reviewed_representation_parity_paid") is not False
                    or raw.get("source_independence_paid") is not False
                    or not isinstance(raw.get("pairs"), list)
                    or not isinstance(raw.get("recorded_consumer_adequacy"), list)
                    or not isinstance(raw.get("all_recorded_answers_equal"), bool)
                    or (not raw["all_recorded_answers_equal"] and raw["recorded_consumer_adequacy"])):
                raise ToolExecutionError("Invalid recorded-syntax parity receipt")
        else:
            if (raw.get("creates_access_authority") is not False
                    or raw.get("provider_acquisition_executed") is not False
                    or type(raw.get("network_requests")) is not int or raw["network_requests"] != 0
                    or raw.get("planned_moves") != [] or raw.get("pareto_move_refs") != []
                    or "selected_move_ref" not in raw or raw["selected_move_ref"] is not None
                    or not all(isinstance(raw.get(k), list) for k in
                               ("source_manifest", "lexical_seeds", "retrieval", "no_hit_hypothesis_refs"))):
                raise ToolExecutionError("Invalid read-only uncalibrated local research receipt")
            for row in raw["retrieval"]:
                if (not isinstance(row, dict) or row.get("candidate_only") is not True
                        or type(row.get("network_requests")) is not int or row["network_requests"] != 0
                        or not isinstance(row.get("passages"), list)
                        or any(not isinstance(p, dict) or p.get("candidate_only") is not True
                               for p in row["passages"])):
                    raise ToolExecutionError("Invalid candidate retrieval")
    elif action == "research_frontier":
        ref = _coordinate(payload, "family_ref")
        raw = _native(["relational-family", "inspect-research-frontier", ref])
        if (raw.get("schema") != "slr.relational-research-frontier.v1"
                or raw.get("family_ref") != ref
                or raw.get("candidate_only") is not True
                or any(raw.get(k) is not False for k in (
                    "formal_consumer_equivalence_paid", "world_truth_paid",
                    "creates_access_authority", "writes_database"))
                or raw.get("satisfied_payment_refs") != []
                or not all(isinstance(raw.get(k), list) for k in
                           ("residuals", "inverse", "hypotheses"))):
            raise ToolExecutionError("Wrong or promotion-bearing research frontier")
        residuals, inverse, hypotheses = (raw[k] for k in
                                          ("residuals", "inverse", "hypotheses"))
        if (not all(isinstance(x, dict) for x in residuals + inverse + hypotheses)
                or any(not isinstance(x.get("residual_ref"), str)
                       or not x["residual_ref"] for x in residuals + inverse + hypotheses)
                or any(x.get("status") not in ("open", "underidentified") for x in residuals)):
            raise ToolExecutionError("Invalid native research frontier coordinates")
        ids = {x["residual_ref"] for x in residuals}
        open_ids = {x["residual_ref"] for x in residuals if x["status"] == "open"}
        if (len(ids) != len(residuals) or len(inverse) != len(residuals)
                or {x["residual_ref"] for x in inverse} != ids
                or any(x["residual_ref"] not in open_ids
                       or x.get("candidate_only") is not True for x in hypotheses)):
            raise ToolExecutionError("Native research frontier inverse or hypothesis mismatch")
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
        description="Reopen native family, recorded syntax parity, local candidate research, source-exact investigation, Mabo formal demands, research frontier, revision or relation coordinates; read only.",
        input_schema={"type": "object", "properties": {
            "action": {"enum": ["family", "revision", "original_relations", "factor_consumer", "demand_fibre", "source_fibre", "research_frontier", "recorded_parity", "local_research", "investigation", "mabo_formal_demands", "licensed_view_cohort", "query_context_capsule", "expand_query_context_capsule", "signed_query_frontier"]},
            "demand_id": {"type": "integer", "minimum": 1},
            "pair_evidence": {"type": "array", "maxItems": 45, "items": {
                "type": "object", "additionalProperties": False,
                "properties": {k: {"type": "string"} for k in (
                    "left_selector_ref", "right_selector_ref", "evidence_ref",
                    "repo", "sha", "path", "canonical_thread_id")},
                "required": ["left_selector_ref", "right_selector_ref", "evidence_ref",
                             "repo", "sha", "path", "canonical_thread_id"]}},
            "batch_refs": {"type": "array", "items": {"type": "string"}, "maxItems": 4096},
            **{k: {"type": "string"} for k in ("family_ref", "query_ref", "capsule_digest", "transition_ref", "obligation_ref",
               "numeric_run_ref", "document_ref", "snapshot_ref", "packet_sha256", "relation_type",
               "source_sha256", "consumer_axis", "source_revision_ref")},
        }, "additionalProperties": False},
        read_only=True,
    ), inspect_relational_family)]
