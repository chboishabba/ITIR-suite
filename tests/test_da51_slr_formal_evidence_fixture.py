from __future__ import annotations

import json
from pathlib import Path


FIXTURE = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "planning"
    / "jmd_fixtures"
    / "da51_slr_formal_evidence_v1.example.json"
)


def load_fixture() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_positive_chain_preserves_exact_formal_identity_and_nonpromotion():
    data = load_fixture()
    positive = data["positive"]
    demand = positive["demand"]
    evidence = positive["formalEvidence"]
    payment = positive["slrPayment"]
    artifact = positive["artifact"]

    assert demand["demandRef"] == evidence["demandRef"] == payment["demandRef"]
    assert (
        demand["externalObligationRef"]
        == evidence["externalObligationRef"]
        == payment["obligationRef"]
    )
    assert (
        demand["statementDigest"]
        == evidence["statementDigest"]
        == payment["statementDigest"]
        == artifact["statementDigest"]
    )
    assert demand["da51Address"] == evidence["da51Address"] == artifact["da51Address"]
    assert evidence["certificationState"] == "kernel-certified"
    assert payment["formalPremisePaid"] is True
    assert payment["createsLegalAuthority"] is False
    assert payment["applicabilityPromoted"] is False
    assert payment["claimTruthPromoted"] is False


def test_one_logical_shard_may_have_hf_and_ipfs_refs_with_same_digest():
    shard = load_fixture()["positive"]["artifact"]["shards"][0]
    refs = shard["objectRefs"]
    assert {item["sink"] for item in refs} == {"hf", "ipfs"}
    assert {item["contentDigest"] for item in refs} == {shard["contentDigest"]}
    assert all(item["uri"] != shard["shardId"] for item in refs)


def test_runtime_evidence_remains_observational():
    runtime = load_fixture()["positive"]["runtimeEvidence"]
    assert {item["producer"] for item in runtime} == {"zkperf", "ebpf-mcp"}
    assert all(item["establishesProof"] is False for item in runtime)


def test_negative_vectors_cover_required_authority_and_identity_failures():
    ids = {item["id"] for item in load_fixture()["negativeVectors"]}
    assert ids == {
        "wrong-statement-digest",
        "wrong-obligation-ref",
        "route-as-proof",
        "agda2lean-capability-as-proof",
        "da51-status-as-proof",
        "cid-as-semantic-identity",
        "runtime-observation-as-theorem",
        "stale-source-revision",
        "similar-symbol-as-equivalent",
    }
