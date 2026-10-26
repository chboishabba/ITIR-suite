from __future__ import annotations

from itir_mcp.formal_receipt_store import default_receipt_store
from itir_mcp.formal_tools import _digest, get_formal_tools
from itir_mcp.frontier_reference_validation import validate_typed_references
from itir_mcp.registry import build_default_registry

SHA = "a" * 40
REPO = "example/proofs"
PATH = "Proof.agda"
THREAD = "thread-1"


def test_unconfigured_registry_cannot_write_or_resolve(tmp_path, monkeypatch):
    db = tmp_path / "formal.sqlite3"
    monkeypatch.setenv("ITIR_FORMAL_RECEIPT_DB", str(db))
    registry = build_default_registry()
    result = registry.invoke("itir.formal.certify", {
        "authenticated_local_referee": True,
        "repo": REPO, "path": PATH, "canonical_thread_id": THREAD,
    })
    assert result["ok"] is True
    assert not db.exists()
    validated = validate_typed_references(
        THREAD, [{"kind": "formal", "ref": f"{REPO}@{SHA}:{PATH}"}],
        formal_resolver=default_receipt_store().resolver(),
    )
    assert validated["held_count"] == 1


def test_referee_verified_certification_persists_and_resolves(tmp_path, monkeypatch):
    monkeypatch.setenv("ITIR_FORMAL_RECEIPT_DB", str(tmp_path / "formal.sqlite3"))
    artifact = {
        "schemaVersion": "artifact-resolution-receipt/v1",
        "contentDigest": "artifact", "verified": True,
        "authority": "transport-only", "establishesProof": False,
        "logicalArtifactRef": PATH,
    }
    kernel = {
        "schemaVersion": "kernel-certification-receipt/v1",
        "authority": "formal-checker-only", "certifiesFormalResult": True,
        "createsLegalAuthority": False, "applicabilityPromoted": False,
        "claimTruthPromoted": False, "certificationState": "kernel-certified",
        "sourceRevision": "git:" + SHA,
        "artifactRef": PATH, "artifactDigest": "artifact",
        "checker": "agda", "checkerRevision": "2.9", "dependencies": [],
    }
    trusted = {
        "authenticated_local_referee": True, "independent_kernel_success": True,
        "repo": REPO, "path": PATH, "canonical_thread_id": THREAD,
        "subject_commit": SHA, "source_digest": "artifact",
        "artifact_digest": "artifact",
        "checker_digest": _digest({"checker": "agda", "revision": "2.9"}),
        "dependency_digest": _digest([]),
    }
    def write(result, _trusted):
        binding = result["reference_binding"]
        return default_receipt_store().record_from_referee(
            binding["repo"], binding["sha"], binding["path"],
            binding["canonical_thread_id"], result, referee_verified=True,
        )

    tools = dict(get_formal_tools(
        certifier=lambda **_: kernel,
        handoff_validator=lambda *_: {"artifact_digest": "artifact"},
        referee_context=lambda: trusted, verified_receipt_writer=write,
    ))
    request = {
        "artifact_resolution_receipt": artifact,
        "demand_ref": "d", "obligation_ref": "o", "statement_digest": "s",
    }
    assert tools["itir.formal.certify"](request)["kernel_handoff_eligible"] is True
    assert tools["itir.formal.certify"](request)["kernel_handoff_eligible"] is True
    assert default_receipt_store().resolver()(REPO, SHA, PATH, THREAD)
    assert not default_receipt_store().resolver()(REPO, "b" * 40, PATH, THREAD)
    assert not default_receipt_store().resolver()(REPO, SHA, PATH, "other")
