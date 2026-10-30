from __future__ import annotations

from itir_mcp.formal_receipt_store import default_receipt_store
from itir_mcp.formal_tools import _digest, get_formal_tools
from itir_mcp.frontier_reference_validation import validate_typed_references
from itir_mcp.registry import build_default_registry

from itir_mcp.formal_receipt_store import PostgresRefereeReceiptStore
import itir_mcp.formal_receipt_store as receipt_module
import itir_mcp.registry as registry_module


class _Cursor:
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
            import json
            self.db.rows.setdefault(key, json.loads(params[4]))
        elif sql.startswith("SELECT"):
            v = self.db.rows.get(key)
            self.row = (v,) if v is not None else None
        else:
            raise AssertionError(sql)
    def fetchone(self):
        return self.row


class _DB:
    def __init__(self):
        self.rows = {}
    def __enter__(self):
        return self
    def __exit__(self, *_):
        return False
    def cursor(self):
        return _Cursor(self)


def _setup_receipts(monkeypatch):
    db = _DB()
    store = PostgresRefereeReceiptStore(connect=lambda _: db)
    monkeypatch.setattr(receipt_module, "default_receipt_store", lambda: store)
    monkeypatch.setattr(registry_module, "default_receipt_store", lambda: store)
    globals()["default_receipt_store"] = lambda: store
    return store


SHA = "a" * 40
REPO = "example/proofs"
PATH = "Proof.agda"
THREAD = "thread-1"


def test_unconfigured_registry_cannot_write_or_resolve(tmp_path, monkeypatch):
    db = tmp_path / "formal.sqlite3"
    _setup_receipts(monkeypatch)
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
    _setup_receipts(monkeypatch)
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

    tools = {spec.name: handler for spec, handler in get_formal_tools(
        certifier=lambda **_: kernel,
        handoff_validator=lambda *_: {"artifact_digest": "artifact"},
        referee_context=lambda: trusted, verified_receipt_writer=write,
    )}
    request = {
        "artifact_resolution_receipt": artifact,
        "demand_ref": "d", "obligation_ref": "o", "statement_digest": "s",
    }
    assert tools["itir.formal.certify"](request)["kernel_handoff_eligible"] is True
    assert tools["itir.formal.certify"](request)["kernel_handoff_eligible"] is True
    assert default_receipt_store().resolver()(REPO, SHA, PATH, THREAD)
    assert not default_receipt_store().resolver()(REPO, "b" * 40, PATH, THREAD)
    assert not default_receipt_store().resolver()(REPO, SHA, PATH, "other")


def test_configured_registry_writes_only_verified_results(tmp_path, monkeypatch):
    import itir_mcp.registry as registry_module

    _setup_receipts(monkeypatch)
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
    original = registry_module.get_formal_tools

    def with_checker(**kwargs):
        return original(
            certifier=lambda **_: kernel,
            handoff_validator=lambda *_: {"artifact_digest": "artifact"},
            **kwargs,
        )

    monkeypatch.setattr(registry_module, "get_formal_tools", with_checker)
    registry = build_default_registry(local_referee_context=lambda: trusted)
    payload = {
        "artifact_resolution_receipt": artifact,
        "demand_ref": "d", "obligation_ref": "o", "statement_digest": "s",
    }
    response = registry.invoke("itir.formal.certify", payload)
    assert response["ok"] is True
    assert default_receipt_store().resolver()(REPO, SHA, PATH, THREAD)
    trusted["authenticated_local_referee"] = False
    assert registry.invoke("itir.formal.certify", payload)["ok"] is True
    assert not default_receipt_store().resolver()(REPO, "b" * 40, PATH, THREAD)
