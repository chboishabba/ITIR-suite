from __future__ import annotations

import json
from pathlib import Path

from itir_jmd_bridge.formal_proof_artifact import package_formal_proof_artifact


def test_package_formal_proof_artifact_binds_exact_demand_and_transport(tmp_path: Path) -> None:
    source = tmp_path / "MaboProof.agda"
    source.write_text("module MaboProof where\n", encoding="utf-8")
    out = tmp_path / "out"

    result = package_formal_proof_artifact(
        source_path=source,
        output_dir=out,
        demand_ref="formal-demand:mabo:sha256:abc",
        obligation_ref="legal-obligation:mabo:1",
        statement_digest="sha256:" + "11" * 32,
        da51_address="0xDA51831100800000",
    )

    receipt = result["receipt"]
    artifact = result["artifact"]
    resolved = result["resolved"]

    assert artifact["contractVersion"] == "shared-shard-artifact/v1"
    assert artifact["formalProof"]["demandRef"] == "formal-demand:mabo:sha256:abc"
    assert artifact["formalProof"]["obligationRef"] == "legal-obligation:mabo:1"
    assert artifact["formalProof"]["statementDigest"] == "sha256:" + "11" * 32
    assert artifact["formalProof"]["da51Address"] == "0xDA51831100800000"
    assert len(artifact["shards"]) == 1
    assert artifact["shards"][0]["contentDigest"] == receipt["contentDigest"]
    assert resolved["selectedObjectRef"]["sink"] == "file"
    assert resolved["fetch"]["sink"] == "file"
    assert receipt["verified"] is True
    assert receipt["authority"] == "transport-only"
    assert receipt["establishesProof"] is False
    assert receipt["logicalArtifactRef"] == result["logical_artifact_ref"]

    for name in ("shared-shard-artifact.json", "resolved-artifact.json", "artifact-resolution-receipt.json"):
        assert (out / name).exists()
        json.loads((out / name).read_text(encoding="utf-8"))


def test_statement_digest_must_be_sha256(tmp_path: Path) -> None:
    source = tmp_path / "proof.agda"
    source.write_text("module proof where\n", encoding="utf-8")
    try:
        package_formal_proof_artifact(
            source_path=source,
            output_dir=tmp_path / "out",
            demand_ref="demand:1",
            obligation_ref="obligation:1",
            statement_digest="not-a-digest",
            da51_address=None,
        )
    except ValueError as error:
        assert "statement_digest" in str(error)
    else:
        raise AssertionError("invalid statement digest must fail closed")
