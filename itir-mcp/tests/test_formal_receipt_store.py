from __future__ import annotations

from copy import deepcopy

from itir_mcp.formal_receipt_store import PostgresRefereeReceiptStore
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


class FakeCursor:
    def __init__(self, db):
        self.db = db
        self.row = None

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def execute(self, sql, params):
        key = tuple(params[:4])
        if sql.startswith("INSERT"):
            self.db.rows.setdefault(key, __import__("json").loads(params[4]))
        elif sql.startswith("SELECT"):
            value = self.db.rows.get(key)
            self.row = (value,) if value is not None else None
        else:
            raise AssertionError(sql)

    def fetchone(self):
        return self.row


class FakeConnection:
    def __init__(self):
        self.rows = {}

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def cursor(self):
        return FakeCursor(self)


def make_store():
    db = FakeConnection()
    return PostgresRefereeReceiptStore(connect=lambda _: db)


def test_referee_receipt_persists_and_replay_is_idempotent(tmp_path):
    store = make_store()
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
    store = make_store()
    assert not store.record_from_referee(
        REPO, SHA, PATH, THREAD, receipt(), referee_verified=False
    )
    assert store.read(REPO, SHA, PATH, THREAD) is None


def test_stale_sha_and_thread_hold(tmp_path):
    store = make_store()
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
    store = make_store()
    original = receipt()
    assert store.record_from_referee(REPO, SHA, PATH, THREAD, original, referee_verified=True)
    altered = deepcopy(original)
    altered["evidence_digest"] = "different"
    assert not store.record_from_referee(
        REPO, SHA, PATH, THREAD, altered, referee_verified=True
    )
    assert store.read(REPO, SHA, PATH, THREAD) == original
