"""Exact referee-to-thread binding for typed formal references."""
from __future__ import annotations

from copy import deepcopy

from itir_mcp.frontier_reference_validation import (
    formal_receipt_resolver,
    validate_typed_references,
)

SHA = "a" * 40
REPO = "example/formal"
PATH = "DASHI/Interop/Proof.agda"
THREAD = "thread-1"
REF = f"{REPO}@{SHA}:{PATH}"


def certified():
    return {
        "status": "verified",
        "kernel_handoff_eligible": True,
        "authority_kind": "isolated_kernel_check",
        "candidate_only": False,
        "establishes_proof": True,
        "handoff": {
            "subject_commit": SHA,
            "authority_kind": "isolated_kernel_check",
            "candidate_only": False,
            "establishes_proof": True,
            "source_digest": "source",
            "artifact_digest": "artifact",
            "checker_digest": "checker",
            "dependency_digest": "dependencies",
        },
        "reference_binding": {
            "repo": REPO,
            "sha": SHA,
            "path": PATH,
            "canonical_thread_id": THREAD,
            "authenticated_local_referee": True,
        },
    }


def validate(provider, thread=THREAD):
    return validate_typed_references(
        thread, [{"kind": "formal", "ref": REF}],
        formal_resolver=formal_receipt_resolver(provider),
    )


def test_referee_bound_certification_resolves_exact_reference():
    result = validate(lambda *_: certified())
    assert result["verified_count"] == 1
    assert result["held_count"] == 0
    assert result["records"][0]["status"] == "resolved"


def test_candidate_and_unbound_receipts_never_resolve():
    baseline = certified()
    mutations = (
        ("status", "held"),
        ("kernel_handoff_eligible", False),
        ("authority_kind", "similarity"),
        ("authority_kind", "interactive_goal"),
        ("candidate_only", True),
        ("establishes_proof", False),
    )
    for key, value in mutations:
        candidate = deepcopy(baseline)
        candidate[key] = value
        assert validate(lambda *_: candidate)["held_count"] == 1, key
    for key, value in (
        ("repo", "other/formal"),
        ("sha", "b" * 40),
        ("path", "DASHI/Interop/Other.agda"),
        ("canonical_thread_id", "other-thread"),
        ("authenticated_local_referee", False),
    ):
        candidate = deepcopy(baseline)
        candidate["reference_binding"][key] = value
        assert validate(lambda *_: candidate)["held_count"] == 1, key


def test_stale_commit_and_missing_proof_digests_hold():
    candidate = certified()
    candidate["handoff"]["subject_commit"] = "b" * 40
    assert validate(lambda *_: candidate)["held_count"] == 1
    candidate["handoff"]["subject_commit"] = SHA
    candidate["handoff"]["checker_digest"] = ""
    assert validate(lambda *_: candidate)["held_count"] == 1


def test_provider_unavailable_and_missing_receipt_hold():
    assert validate(lambda *_: None)["held_count"] == 1

    def unavailable(*_):
        raise LookupError("receipt not found")

    assert validate(unavailable)["held_count"] == 1
    assert validate(lambda *_: certified(), thread="other-thread")["held_count"] == 1


def test_no_resolver_stays_fail_closed():
    result = validate_typed_references(THREAD, [{"kind": "formal", "ref": REF}])
    assert result["held_count"] == 1
