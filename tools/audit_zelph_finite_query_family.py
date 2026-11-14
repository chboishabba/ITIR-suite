#!/usr/bin/env python3
"""Finite left/right relation-word closure from prior *physical root audits*.

Composes same-revision selected-root one-hop equalities, demands a checked
observation at EVERY intermediate node/direction, and refuses unsupported
query words or global negatives. The finite equality is conditional on
authenticity of the referenced prior native audit evidence. No property
semantics, Wikidata statement support or edit authority is inferred.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Any, Mapping, Sequence

_SHA = re.compile(r"[0-9a-f]{64}\Z")
_QID = re.compile(r"Q[1-9][0-9]*\Z")
_DIRECTIONS = frozenset(("left", "right"))
_NATIVE_VERSION = "itir.zelph.native_physical_selected_original_query_cut.v1"


def _strict_json(path: Path, max_bytes: int = 64 * 1024 * 1024) -> tuple[dict, str]:
    if not path.is_file() or not 0 < path.stat().st_size <= max_bytes:
        raise ValueError(f"invalid bounded input JSON file: {path}")
    raw = path.read_bytes()

    def no_dupes(items: list[tuple[str, Any]]) -> dict:
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError(f"duplicate input JSON key: {key}")
            result[key] = value
        return result

    result = json.loads(
        raw.decode("utf-8"), object_pairs_hook=no_dupes,
        parse_constant=lambda x: (_ for _ in ()).throw(ValueError("nonfinite JSON")),
    )
    if not isinstance(result, dict):
        raise ValueError("JSON top-level must be object")
    return result, sha256(raw).hexdigest()


def _node(value: Any) -> int:
    if type(value) is not int or not 0 <= value <= (2**64 - 1):
        raise ValueError("physical nodes must be uint64 integers")
    return value


def _strict_neighbours(raw: Any) -> tuple[int, ...]:
    if not isinstance(raw, list) or len(raw) > 1_000_000:
        raise ValueError("bounded neighbour array required")
    values = tuple(_node(x) for x in raw)
    if list(values) != sorted(set(values)):
        raise ValueError("neighbours must be sorted and distinct")
    return values


def finite_relation_word_closure(
    *, query_family: Mapping[str, Any],
    audits: Sequence[tuple[Mapping[str, Any], str]],
    max_frontier: int = 200_000, max_steps: int = 16,
) -> dict[str, Any]:
    """Construct exact finite word traces or explicit boundary non-coverage.

    Grammar: numeric graph left/right steps rooted at (QID, node ID) pairs.
    NOT property-labelled P31/P279, native qualifiers, SPARQL joins or all paths.
    """
    if not audits:
        raise ValueError("at least one independently obtained native root audit required")
    if type(max_frontier) is not int or not 1 <= max_frontier <= 1_000_000:
        raise ValueError("positive bounded frontier size required")
    if type(max_steps) is not int or not 1 <= max_steps <= 64:
        raise ValueError("positive bounded relation-word depth required")
    if query_family.get("version") != "itir.zelph.finite_lr_query_family.v1":
        raise ValueError("explicit finite left/right query family contract required")
    revision, manifest_sha, artifact = None, None, None
    rows: dict[tuple[int, str], tuple[int, ...]] = {}
    counts: dict[tuple[int, str], int] = {}
    sources: dict[tuple[int, str], set[str]] = {}
    all_roots: dict[str, int] = {}
    any_unreplayed = False

    for audit, raw_digest in audits:
        if not _SHA.fullmatch(raw_digest):
            raise ValueError("audit file raw SHA256 missing")
        if audit.get("version") != _NATIVE_VERSION:
            raise ValueError("native per-root physical audit schema required")
        if (
            audit.get("native_schema_decoder_executed") is not True
            or audit.get("selected_root_one_hop_bidirectional_adjacency_equal_original_bin") is not True
            or audit.get("selected_name_routes_and_inverse_checked") is not True
            or audit.get("edit_authority") is not False
        ):
            raise ValueError("audit not accepted as same-original root comparison")
        if audit.get("source_bin_route_oracle_recomputed_in_this_run") is not False:
            raise ValueError("unexpected source-oracle recomputation claim")
        if audit.get("original_bin_upstream_authenticity_proved") is not False:
            raise ValueError("upstream authenticity must be verified independently")
        if audit.get("source_bin_range_equality_reverified_in_this_run") is not True:
            any_unreplayed = True
        rev = audit.get("dataset_revision")
        digest = audit.get("manifest_sha256")
        art = audit.get("artifact_id", "wikidata-20260309-all")
        if not isinstance(rev, str) or not re.fullmatch(r"[0-9a-f]{40}", rev):
            raise ValueError("immutable dataset SHA missing")
        if not isinstance(digest, str) or not _SHA.fullmatch(digest):
            raise ValueError("raw manifest digest missing")
        if revision is None:
            revision, manifest_sha, artifact = rev, digest, art
        elif (rev, digest, art) != (revision, manifest_sha, artifact):
            raise ValueError("mixed dataset/artifact/manifest identity across audits")
        declared = audit.get("qid_root_nodes")
        if not isinstance(declared, dict) or not declared:
            raise ValueError("native audit lacks explicit QID root identities")
        for qid, value in declared.items():
            if not isinstance(qid, str) or not _QID.fullmatch(qid):
                raise ValueError("noncanonical QID in physical root mapping")
            nid = _node(value)
            if qid in all_roots and all_roots[qid] != nid:
                raise ValueError("conflicting physical node IDs for same QID")
            all_roots[qid] = nid
        adjacency = audit.get("root_adjacency")
        if not isinstance(adjacency, list) or len(adjacency) > 100_000:
            raise ValueError("native audit missing bounded source-equal root rows")
        local_keys = set()
        for row in adjacency:
            if not isinstance(row, dict):
                raise ValueError("root adjacency must be an object")
            node_id = _node(row.get("node_id"))
            direction = row.get("direction")
            if direction not in _DIRECTIONS:
                raise ValueError("direction outside admitted query grammar")
            neighbours = _strict_neighbours(row.get("neighbors"))
            raw_count = row.get("source_values_seen")
            if (
                type(raw_count) is not int or raw_count < len(neighbours)
                or row.get("source_truncated") is not False
                or row.get("physical_truncated") is not False
            ):
                raise ValueError("truncated/malformed source or selected adjacency")
            key = (node_id, direction)
            if key in local_keys:
                raise ValueError("duplicate same-root direction inside audit")
            local_keys.add(key)
            if key in rows and (rows[key] != neighbours or counts[key] != raw_count):
                raise ValueError("conflicting source/selected same-node rows across audits")
            rows[key] = neighbours
            counts[key] = raw_count
            sources.setdefault(key, set()).add(raw_digest)
        extra_numeric = audit.get("additional_numeric_root_nodes", [])
        if (
            not isinstance(extra_numeric, list)
            or len(extra_numeric) > 100000
            or any(type(node) is not int or not 0 <= node <= (2**64 - 1)
                   for node in extra_numeric)
            or extra_numeric != sorted(set(extra_numeric))
        ):
            raise ValueError("numeric frontier roots must be sorted distinct uint64 IDs")
        declared_nodes = set(declared.values()) | set(extra_numeric)
        if local_keys != {
            (node, direction) for node in declared_nodes for direction in _DIRECTIONS
        }:
            raise ValueError("each native audit must expose both directions for every declared root")

    declared_queries = query_family.get("queries")
    if (
        not isinstance(declared_queries, list) or not declared_queries
        or len(declared_queries) > 10_000
    ):
        raise ValueError("bounded nonempty explicit query family required")
    qids = query_family.get("qid_root_nodes")
    if not isinstance(qids, dict) or not qids:
        raise ValueError("query family must explicitly bind canonical QIDs to nodes")
    if set(qids) - set(all_roots):
        raise ValueError("query family QID absent from native selected root audits")
    for qid, node in qids.items():
        if not isinstance(qid, str) or not _QID.fullmatch(qid) or _node(node) != all_roots[qid]:
            raise ValueError("query family root QID/node conflicts with physical audit")
    result_queries = []
    missing: dict[tuple[int, str], set[str]] = {}
    labels = set()
    for query in declared_queries:
        if not isinstance(query, dict):
            raise ValueError("query entry not object")
        label, qid, word = query.get("id"), query.get("qid"), query.get("word")
        if not isinstance(label, str) or not label or label in labels:
            raise ValueError("each finite query requires a unique nonempty identifier")
        labels.add(label)
        if not isinstance(qid, str) or qid not in qids:
            raise ValueError("query root outside declared QID domain")
        if (
            not isinstance(word, list) or len(word) > max_steps
            or any(not isinstance(step, str) or step not in _DIRECTIONS for step in word)
        ):
            raise ValueError("query word exceeds grammar/depth budget")
        frontier = {qids[qid]}
        trace = []
        query_missing = []
        for index, direction in enumerate(word):
            if len(frontier) > max_frontier:
                raise ValueError("intermediate frontier exceeds explicit resource bound")
            absent = sorted(node for node in frontier if (node, direction) not in rows)
            if absent:
                for node in absent:
                    missing.setdefault((node, direction), set()).add(label)
                    query_missing.append({
                        "step": index, "node_id": node, "direction": direction,
                    })
                break
            next_frontier: set[int] = set()
            for node in frontier:
                next_frontier.update(rows[(node, direction)])
            if len(next_frontier) > max_frontier:
                raise ValueError("expanded frontier exceeds explicit resource bound")
            trace.append({
                "step": index, "direction": direction,
                "input_nodes": sorted(frontier),
                "result_nodes": sorted(next_frontier),
                "source_row_audit_shas": sorted({
                    digest for node in frontier for digest in sources[(node, direction)]
                }),
            })
            frontier = next_frontier
        result_queries.append({
            "id": label, "qid": qid, "relation_word": word,
            "status": (
                "complete-for-declared-finite-word" if not query_missing
                else "incomplete-missing-boundary"
            ),
            "trace": trace,
            "end_nodes": sorted(frontier) if not query_missing else None,
            "missing_boundaries": query_missing,
        })
    return {
        "version": "itir.zelph.finite_lr_query_closure.v1",
        "dataset_revision": revision,
        "manifest_sha256": manifest_sha,
        "graph_artifact_id": artifact,
        "finite_family_query_count": len(result_queries),
        "observed_root_direction_rows": len(rows),
        "all_declared_words_closed": not missing,
        "coverage_status": (
            "complete-for-explicit-finite-lr-words" if not missing
            else "incomplete-missing-root-directions"
        ),
        "query_results": result_queries,
        "missing_boundaries": [
            {
                "node_id": node, "direction": direction,
                "required_for_queries": sorted(query_ids),
            }
            for (node, direction), query_ids in sorted(missing.items())
        ],
        "upstream_audit_raw_shas": sorted({digest for _, digest in audits}),
        "every_audit_reverified_source_bin_ranges_in_its_run": not any_unreplayed,
        "real_original_bin_authenticity_independently_verified": False,
        "proves_all_Wikidata_queries": False,
        "proves_property_filtered_P31_P279_or_P14143": False,
        "proves_native_GUID_P854": False,
        "allows_scoped_negative_answer": False,
        "candidate_only": True,
        "source_support_paid": False,
        "edit_authority": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query-family", type=Path, required=True)
    parser.add_argument("--native-audit", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--max-frontier", type=int, default=200_000)
    parser.add_argument("--max-steps", type=int, default=16)
    args = parser.parse_args()
    try:
        family, _ = _strict_json(args.query_family)
        audits = [_strict_json(path) for path in args.native_audit]
        result = finite_relation_word_closure(
            query_family=family, audits=audits,
            max_frontier=args.max_frontier, max_steps=args.max_steps,
        )
        output = json.dumps(result, sort_keys=True, indent=2) + "\n"
        if args.output:
            args.output.write_text(output, encoding="utf-8")
        else:
            print(output, end="")
        return 0 if result["all_declared_words_closed"] else 3
    except (ValueError, OSError, TypeError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        import sys
        print(json.dumps({"status": "blocked", "reason": str(exc), "edit_authority": False}),
              file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
