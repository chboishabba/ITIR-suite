from __future__ import annotations

from copy import deepcopy

from itir_mcp.formal_receipt_store import LocalRefereeReceiptStore
from itir_mcp.frontier_reference_validation import validate_typed_references

REPO = "example/proofs"
SHA = "a" * 40
PATH = "DASHI/Proof.agda"
THREAD = "thread-1"


def receipt():
    return {
        "status": "verified", "kernel_handoff_eligible": True,
        "authority_kind": "isolated_kernel_check",
        "candidate_only": False, "establishes_proof": True,
        "handoff": {
            "subject_commit": SHA, "authority_kind": "isolated_kernel_check",
            "candidate_only": False, "establishes_proof": True,
            "source_digest": "source", "artifact_digest": "artifact",
            "checker_digest": "checker", "dependency_digest": "deps",
        },
        "reference_binding": {
            "repo": REPO, "sha": SHA, "path": PATH,
            "canonical_thread_id": THREAD,
            "authenticated_local_referee": True,
        },
    }


def test_referee_receipt_persists_and_replay_is_idempotent(tmp_path):
    store = LocalRefereeReceiptStore(tmp_path / "receipts.sqlite3")
    verified = receipt()
    assert store.record_from_referee(REPO, SHA, PATH, THREAD, verified, referee_verified=True)
    assert store.record_from_referee(REPO, SHA, PATH, THREAD, verified, referee_verified=True)
    assert store.read(REPO, SHA, PATH, THREAD) == verified
    result = validate_typed_references(
        THREAD, [{"kind": "formal", "ref": f"{REPO}@{SHA}:{PATH}"}],
        formal_resolver=store.resolver(),
    )
    assert result["verified_count"] == 1


def test_actor_receipt_cannot_enter_store(tmp_path):
    store = LocalRefereeReceiptStore(tmp_path / "receipts.sqlite3")
    assert not store.record_from_referee(
        REPO, SHA, PATH, THREAD, receipt(), referee_verified=False
    )
    assert store.read(REPO, SHA, PATH, THREAD) is None


def test_stale_sha_and_thread_hold(tmp_path):
    store = LocalRefereeReceiptStore(tmp_path / "receipts.sqlite3")
    assert store.record_from_referee(
        REPO, SHA, PATH, THREAD, receipt(), referee_verified=True
    )
    assert not store.resolver()(REPO, "b" * 40, PATH, THREAD)
    assert not store.resolver()(REPO, SHA, PATH, "other-thread")
    altered = deepcopy(receipt())
    altered["handoff"]["subject_commit"] = "b" * 40
    assert not store.record_from_referee(
        REPO, SHA, PATH, "other-thread", altered, referee_verified=True
    )


def test_conflicting_replay_does_not_replace_receipt(tmp_path):
    store = LocalRefereeReceiptStore(tmp_path / "receipts.sqlite3")
    original = receipt()
    assert store.record_from_referee(REPO, SHA, PATH, THREAD, original, referee_verified=True)
    altered = deepcopy(original)
    altered["evidence_digest"] = "different"
    assert not store.record_from_referee(
        REPO, SHA, PATH, THREAD, altered, referee_verified=True
    )
    assert store.read(REPO, SHA, PATH, THREAD) == original
