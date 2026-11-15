#!/usr/bin/env python3
"""Read-only A2 source-reachable finite-word frontier certificate.

Replay original finite-word logic from raw native audit receipts; reconstruct
node/direction dependencies independently of the evaluator's 'closed' flag.
This materializes an evidence-carrying frontier proof obligation, NOT an Agda
term or proof of physical HTTP206/native C++ semantics.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re

from audit_zelph_finite_query_family import _strict_json
from close_original_http206_lr_finite_words import original_http206_finite_words

_SHA = re.compile(r"[0-9a-f]{64}\Z")
_VERSION = "itir.zelph.source_reachable_lr_finite_word_certificate.v1"


def make_certificate(*, query_family: dict, audits: list[tuple[dict, str]],
                     finite_result: dict, query_family_raw_sha256: str,
                     finite_result_raw_sha256: str,
                     max_witness_nodes: int = 100000) -> dict:
    if (not isinstance(query_family, dict) or not isinstance(finite_result, dict)
            or not isinstance(audits, list) or not audits
            or any(type(h) is not str or not _SHA.fullmatch(h)
                   for h in (query_family_raw_sha256, finite_result_raw_sha256))
            or type(max_witness_nodes) is not int
            or not 0 < max_witness_nodes <= 1000000):
        raise ValueError("bounded original finite certificate requires SHA-bound inputs")
    fresh = original_http206_finite_words(
        query_family=query_family, audits=audits)
    if finite_result != fresh:
        raise ValueError("finite-word result differs from replayed original-source audits")
    by_label = {r["id"]: r for r in finite_result["query_results"]}
    if len(by_label) != len(query_family["queries"]):
        raise ValueError("duplicate or missing finite word results")
    if len(audits) != len(
            finite_result["source_equal_native_full_section_sweep_receipts"]):
        raise ValueError("missing raw original scan receipt dependency")

    # Only an exact scan accepted by the original-source evaluator may
    # contribute a full-direction equality. Partial native-positive rows
    # are NOT substituted for an unknown remainder of the source section.
    rows = {}
    row_sources = {}
    accepted = []
    for (audit, audit_sha), receipt in zip(
            audits, finite_result["source_equal_native_full_section_sweep_receipts"]):
        if receipt["sha256"] != audit_sha:
            raise ValueError("original audit digest mismatch")
        complete = receipt["accepted_exact_scan"] is True
        accepted.append({"sha256": audit_sha,
                         "used_for_direction_equality": complete})
        if not complete:
            continue
        for row in audit["native_original_selected_node_direction_rows"]:
            key = (row["node_id"], row["direction"])
            value = (row["native_original_neighbors_sorted_unique"],
                     row["native_original_values_seen"])
            if key in rows and rows[key] != value:
                raise ValueError("conflicting exact native multiplicity or neighbours")
            rows[key] = value
            row_sources.setdefault(key, set()).add(audit_sha)

    entries = []
    size = 0
    for query in query_family["queries"]:
        result = by_label[query["id"]]
        if (result["qid"] != query["qid"]
                or result["relation_word"] != query["word"]):
            raise ValueError("finite query QID or word drift")
        frontier = [query_family["qid_root_nodes"][query["qid"]]]
        steps = []
        missing = []
        for pos, direction in enumerate(query["word"]):
            gaps = [n for n in frontier if (n, direction) not in rows]
            if gaps:
                missing = [{"step": pos, "node_id": n, "direction": direction}
                           for n in gaps]
                break
            size += len(frontier)
            if size > max_witness_nodes:
                raise ValueError("source frontier witness over node budget")
            children = set()
            local = []
            contributing = set()
            for node in frontier:
                neighbors, multiplicity = rows[(node, direction)]
                sources = sorted(row_sources[(node, direction)])
                children.update(neighbors)
                contributing.update(sources)
                local.append({
                    "node_id": node, "direction": direction,
                    "native_original_neighbors_sorted_unique": neighbors,
                    "native_original_values_seen": multiplicity,
                    "exact_native_audit_shas": sources,
                })
            nxt = sorted(children)
            if pos >= len(result["trace"]):
                raise ValueError("missing source-reachable trace step")
            prior = result["trace"][pos]
            if (prior["step"] != pos or prior["direction"] != direction
                    or prior["input_nodes"] != frontier
                    or prior["result_nodes"] != nxt
                    or prior["source_equal_native_scan_receipt_shas"] !=
                        sorted(contributing)):
                raise ValueError("step frontier disagrees with original native evidence")
            steps.append({
                "step": pos, "direction": direction,
                "source_reachable_input_nodes": frontier,
                "original_and_selected_next_nodes": nxt,
                "per_node_direction_witnesses": local,
                "source_equal_native_scan_receipt_shas": sorted(contributing),
            })
            frontier = nxt
        closed = not missing
        if (len(result["trace"]) != len(steps)
                or result["missing_boundaries"] != missing
                or result["end_nodes"] != (frontier if closed else None)
                or ((result["status"] ==
                     "complete-for-declared-original-word") != closed)):
            raise ValueError("finite word completion or missing boundary mismatch")
        entries.append({
            "query_id": query["id"], "qid": query["qid"],
            "original_numeric_root": query_family["qid_root_nodes"][query["qid"]],
            "relation_word": query["word"],
            "source_reachable_steps": steps,
            "status": ("conditional-source-reachable-steps-complete" if closed
                       else "blocked-by-unknown-original-source-direction"),
            "missing_source_boundaries": missing,
            "end_nodes": frontier if closed else None,
        })
    all_closed = all(e["status"] ==
                     "conditional-source-reachable-steps-complete" for e in entries)
    if all_closed != finite_result["all_declared_original_lr_words_closed"]:
        raise ValueError("finite evaluator and source boundary conclusion differ")
    return {
        "version": _VERSION,
        "dataset_revision": finite_result["dataset_revision"],
        "manifest_sha256": finite_result["manifest_sha256"],
        "original_index_sha256": finite_result["original_index_sha256"],
        "native_positive_roots_receipt_sha256":
            finite_result["native_positive_roots_receipt_sha256"],
        "native_decoder_sha256": finite_result["native_decoder_sha256"],
        "query_family_raw_sha256": query_family_raw_sha256,
        "finite_result_raw_sha256": finite_result_raw_sha256,
        "accepted_audit_dependencies": accepted,
        "query_count": len(entries),
        "query_certificate_entries": entries,
        "all_declared_words_conditional_boundary_complete": all_closed,
        "all_twenty_distinct_words_conditional_boundary_complete": (
            all_closed and finite_result["all_twenty_original_lr_words_closed"]),
        "physical_http206_bytes_independently_replayed_here": False,
        "native_capnp_cpp_semantics_formally_refined_here": False,
        "agda_source_reachable_boundary_term_generated_here": False,
        "evidence_only": True, "s29_persistence_paid": False,
        "p854_source_support_paid": False, "nora_review_authority": False,
        "edit_authority": False,
    }


def verify_certificate(*, certificate: dict, query_family: dict,
                       audits: list[tuple[dict, str]], finite_result: dict,
                       query_family_raw_sha256: str,
                       finite_result_raw_sha256: str) -> None:
    expected = make_certificate(
        query_family=query_family, audits=audits, finite_result=finite_result,
        query_family_raw_sha256=query_family_raw_sha256,
        finite_result_raw_sha256=finite_result_raw_sha256,
        max_witness_nodes=1000000)
    if expected != certificate:
        raise ValueError("source-reachable certificate differs from replayed original evidence")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--query-family", type=Path, required=True)
    p.add_argument("--finite-result", type=Path, required=True)
    p.add_argument("--native-audit", type=Path, action="append", required=True)
    p.add_argument("--certificate", type=Path)
    p.add_argument("--max-witness-nodes", type=int, default=100000)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    try:
        family, family_sha = _strict_json(args.query_family)
        result, result_sha = _strict_json(args.finite_result)
        audits = [_strict_json(path) for path in args.native_audit]
        if args.certificate:
            supplied, _ = _strict_json(args.certificate)
            verify_certificate(
                certificate=supplied, query_family=family, audits=audits,
                finite_result=result, query_family_raw_sha256=family_sha,
                finite_result_raw_sha256=result_sha)
            output = {"status": "certificate-replayed",
                      "certificate_sha256": sha256(
                          json.dumps(supplied, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False).encode()).hexdigest(),
                      "edit_authority": False}
        else:
            output = make_certificate(
                query_family=family, audits=audits, finite_result=result,
                query_family_raw_sha256=family_sha,
                finite_result_raw_sha256=result_sha,
                max_witness_nodes=args.max_witness_nodes)
        wire = json.dumps(output, sort_keys=True, indent=2) + "\n"
        if args.output:
            with args.output.open("x", encoding="utf-8") as stream:
                stream.write(wire)
        else:
            print(wire, end="")
        return 0 if (args.certificate or
                     output["all_declared_words_conditional_boundary_complete"]) else 3
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        import sys
        print(json.dumps({"status": "blocked", "reason": str(exc),
                          "edit_authority": False}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
