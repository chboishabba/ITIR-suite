from __future__ import annotations

from dataclasses import replace
from hashlib import sha256
import json

import pytest

from itir_mcp.zelph_query_closure import (
    DeclaredNameObject,
    audit_declared_name_partition,
    evaluate_query_closure,
    lookup_audited_name,
)


def _encode(rows):
    return json.dumps(rows, separators=(",", ":")).encode()


def _decode(raw):
    for row in json.loads(raw):
        yield tuple(row)


def _inputs():
    first = _encode([["wikidata", "Q10403939", 24721153],
                     ["wikidata", "Q10422059", 63706277]])
    second = _encode([["wikidata", "Q10403939", 24721153],
                      ["wikidata", "Q10651551", 2475334]])
    declared = [
        DeclaredNameObject("name-1", 1, "wikidata", len(first), sha256(first).hexdigest()),
        DeclaredNameObject("name-4", 4, "wikidata", len(second), sha256(second).hexdigest()),
    ]
    return declared, {"name-1": first, "name-4": second}


def _audit():
    declared, raw = _inputs()
    return audit_declared_name_partition(
        artifact_id="full-graph", graph_revision="sha:pinned",
        declared=declared, raw_objects=raw, decode=_decode,
    )


def test_same_revision_raw_bytes_are_checked_and_collision_fibre_is_retained():
    audit = _audit()
    assert audit["physical_objects_checked"] == 2
    assert audit["declared_object_set_exhausted"]
    assert not audit["source_graph_name_domain_exhausted"]
    result = lookup_audited_name(audit, "Q10403939")
    assert result["collision"]
    assert len(result["candidate_nodes"]) == 2
    assert result["status"] == "found-in-inspected-objects"
    assert not result["negative_query_authority"]


def test_not_found_in_decoded_cover_is_not_global_absence():
    result = lookup_audited_name(_audit(), "Q99999")
    assert result["status"] == "unresolved-in-original-graph"
    assert result["candidate_nodes"] == []
    assert not result["complete_for_source_graph"]


@pytest.mark.parametrize("bad", ["Q0", "Q01", "Q-2", "Q２", "P123", ""])
def test_canonical_qid_required(bad):
    with pytest.raises(ValueError, match="canonical Wikidata QID"):
        lookup_audited_name(_audit(), bad)


def test_missing_or_extra_physical_objects_refused():
    declared, raw = _inputs()
    with pytest.raises(ValueError, match="coverage mismatch"):
        audit_declared_name_partition(
            artifact_id="full", graph_revision="r", declared=declared,
            raw_objects={"name-1": raw["name-1"]}, decode=_decode,
        )
    with pytest.raises(ValueError, match="coverage mismatch"):
        audit_declared_name_partition(
            artifact_id="full", graph_revision="r", declared=declared,
            raw_objects={**raw, "fake": b""}, decode=_decode,
        )


def test_byte_mutation_and_wrong_digest_refused():
    declared, raw = _inputs()
    with pytest.raises(ValueError, match="byte length/digest mismatch"):
        audit_declared_name_partition(
            artifact_id="full", graph_revision="r", declared=declared,
            raw_objects={**raw, "name-1": raw["name-1"] + b" "}, decode=_decode,
        )
    with pytest.raises(ValueError, match="byte length/digest mismatch"):
        audit_declared_name_partition(
            artifact_id="full", graph_revision="r",
            declared=[replace(declared[0], sha256_hex="0" * 64), declared[1]],
            raw_objects=raw, decode=_decode,
        )


def test_duplicate_chunk_identity_refused():
    declared, raw = _inputs()
    with pytest.raises(ValueError, match="duplicate section/global"):
        audit_declared_name_partition(
            artifact_id="full", graph_revision="r",
            declared=[replace(declared[0], chunk_index=4), declared[1]],
            raw_objects=raw, decode=_decode,
        )


def test_decoder_cannot_switch_language_or_supply_negative_node():
    declared, raw = _inputs()
    with pytest.raises(ValueError, match="outside declared"):
        audit_declared_name_partition(
            artifact_id="full", graph_revision="r", declared=declared,
            raw_objects=raw, decode=lambda _: [("en", "Q5", 1)],
        )
    with pytest.raises(ValueError, match="outside declared"):
        audit_declared_name_partition(
            artifact_id="full", graph_revision="r", declared=declared,
            raw_objects=raw, decode=lambda _: [("wikidata", "Q5", -1)],
        )


def test_query_closure_refuses_mixed_revisions_and_unproved_negatives():
    audit = _audit()
    with pytest.raises(ValueError, match="mixed physical graph revisions"):
        evaluate_query_closure(
            name_audit=audit, required={}, inspected={},
            observation_revision="sha:other",
        )
    partial = evaluate_query_closure(
        name_audit=audit,
        required={"P31": ["left", "right"], "P14143": ["native-guid"]},
        inspected={"P31": ["left"]},
        observation_revision="sha:pinned",
    )
    assert partial["missing_dependencies"] == {
        "P31": ["right"], "P14143": ["native-guid"]
    }
    assert partial["coverage_status"] == "incomplete"
    covered = evaluate_query_closure(
        name_audit=audit, required={"P31": ["left", "right"]},
        inspected={"P31": ["left", "right"]},
        observation_revision="sha:pinned",
    )
    assert covered["family_dependencies_inspected"]
    assert covered["coverage_status"] == "unverified-source-closure"
    assert not covered["scoped_negative_answer_permitted"]
