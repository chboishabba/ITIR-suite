from __future__ import annotations

import pytest

from itir_mcp.formal_triangulation_evidence import candidate_evidence_from_triangulation
from itir_mcp.formal_receipt_store import default_receipt_store


def test_triangulation_never_claims_kernel_authority():
    rows = candidate_evidence_from_triangulation(
        {"shared_invariants": ["b", "a", "a"]},
        repo="chboishabba/dashi_agda", sha="a" * 40,
        source_paths=["DASHI/Physics/Closure/ClaySprintOne.agda"],
    )
    assert [r["invariant_id"] for r in rows] == ["a", "b"]
    assert all(r["candidate_only"] and not r["kernel_verified"] and not r["establishes_proof"] for r in rows)


def test_triangulation_rejects_unpinned_source():
    with pytest.raises(ValueError):
        candidate_evidence_from_triangulation({"shared_invariants": ["x"]}, repo="r/p", sha="floating", source_paths=["Proof.agda"])


def test_legacy_sqlite_receipt_env_is_rejected(monkeypatch):
    monkeypatch.setenv("ITIR_FORMAL_RECEIPT_DB", "/tmp/legacy.sqlite3")
    with pytest.raises(ValueError, match="retired"):
        default_receipt_store()
