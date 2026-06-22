from __future__ import annotations

import json
import urllib.request
from pathlib import Path

import pytest

from itir_mcp import build_default_registry
from itir_mcp.zelph_pack_loader import (
    discover_zelph_pack_manifest_paths,
    load_zelph_pack_source_descriptor,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_discover_zelph_pack_manifest_paths_finds_repo_manifests_in_order() -> None:
    paths = discover_zelph_pack_manifest_paths(REPO_ROOT)
    assert [path.name for path in paths] == [
        "zelph_real_world_pack_v1.manifest.json",
        "zelph_real_world_pack_v1_5.manifest.json",
        "zelph_real_world_pack_v1_6.manifest.json",
    ]


def test_load_zelph_pack_source_descriptor_loads_existing_repo_entries() -> None:
    descriptor = load_zelph_pack_source_descriptor(REPO_ROOT)

    assert descriptor["version"] == "itir.zelph.pack_loader.v1"
    assert descriptor["descriptor_kind"] == "shared-shard-source"
    assert descriptor["domain"] == "zelph"
    assert descriptor["candidate_only"] is True
    assert descriptor["non_authoritative"] is True
    assert descriptor["network_fetch"] is False
    assert descriptor["manifest_count"] == 3
    assert descriptor["entry_count"] == 30
    assert descriptor["reference_count"] == 0

    manifest_names = [manifest["path"] for manifest in descriptor["manifests"]]
    assert manifest_names == [
        "docs/planning/zelph_real_world_pack_v1.manifest.json",
        "docs/planning/zelph_real_world_pack_v1_5.manifest.json",
        "docs/planning/zelph_real_world_pack_v1_6.manifest.json",
    ]
    assert all(entry["source_kind"] == "local_path" for entry in descriptor["entries"])
    assert all(entry["exists"] is True for entry in descriptor["entries"])
    assert all(entry["candidate_only"] is True for entry in descriptor["entries"])
    assert all(entry["non_authoritative"] is True for entry in descriptor["entries"])
    assert all(entry["network_fetch"] is False for entry in descriptor["entries"])

    first_entry = descriptor["entries"][0]
    assert first_entry["path"] == "SensibLaw/sl_zelph_demo/compile_db.py"
    assert first_entry["resolved_path"] == "SensibLaw/sl_zelph_demo/compile_db.py"


def test_load_zelph_pack_source_descriptor_fails_closed_on_missing_path(tmp_path: Path) -> None:
    manifest_path = tmp_path / "zelph_real_world_pack_v1.manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "version": "zelph.real_world_pack.v1",
                "entries": [
                    {
                        "path": "missing.txt",
                        "artifact_role": "bridge_proof",
                        "workflow_family": "demo",
                        "safety_tier": "safe_after_final_review",
                        "zelph_story": "technical_credibility",
                        "inclusion_status": "v1_pack",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(FileNotFoundError, match="missing Zelph pack entry path"):
        load_zelph_pack_source_descriptor(tmp_path, manifest_paths=[manifest_path])


def test_load_zelph_pack_source_descriptor_sanitizes_reference_only_urls_without_fetching(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo_root = tmp_path
    (repo_root / "demo.txt").write_text("ok", encoding="utf-8")
    manifest_path = repo_root / "docs" / "planning" / "zelph_real_world_pack_v1.manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(
            {
                "version": "zelph.real_world_pack.v1",
                "entries": [
                    {
                        "path": "demo.txt",
                        "artifact_role": "bridge_proof",
                        "workflow_family": "demo",
                        "safety_tier": "safe_after_final_review",
                        "zelph_story": "technical_credibility",
                        "inclusion_status": "v1_pack",
                        "source_url": "https://huggingface.co/datasets/example/demo/blob/main/pack.json?token=secret#frag",
                        "hf_url": "hf://datasets/example/demo/pack.json?download=1#frag",
                        "objectRefs": [
                            {
                                "sink": "hf",
                                "uri": "https://huggingface.co/datasets/example/demo/resolve/main/pack.json?download=1#frag",
                                "sizeBytes": 1,
                                "contentDigest": "abc",
                            }
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    def _fail_if_called(*args: object, **kwargs: object) -> None:
        raise AssertionError("network access should not occur")

    monkeypatch.setattr(urllib.request, "urlopen", _fail_if_called)

    descriptor = load_zelph_pack_source_descriptor(repo_root, manifest_paths=[manifest_path])

    assert descriptor["manifest_count"] == 1
    assert descriptor["entry_count"] == 1
    assert descriptor["reference_count"] == 3
    assert descriptor["network_fetch"] is False

    refs = descriptor["references"]
    assert {ref["field"] for ref in refs} == {"hf_url", "source_url", "uri"}
    assert all(ref["reference_only"] is True for ref in refs)
    assert all(ref["non_authoritative"] is True for ref in refs)
    assert all("?" not in ref["uri"] and "#" not in ref["uri"] for ref in refs)
    assert any(ref["uri"] == "hf://datasets/example/demo/pack.json" for ref in refs)
    assert any(ref["uri"] == "https://huggingface.co/datasets/example/demo/blob/main/pack.json" for ref in refs)
    assert any(ref["uri"] == "https://huggingface.co/datasets/example/demo/resolve/main/pack.json" for ref in refs)


def test_zelph_pack_sources_registry_tool_loads_repo_records_without_network_fetch() -> None:
    registry = build_default_registry()
    result = registry.invoke("itir.zelph.pack_sources", {"repo_root": str(REPO_ROOT)})

    assert result["ok"] is True
    descriptor = result["result"]
    assert descriptor["version"] == "itir.zelph.pack_loader.v1"
    assert descriptor["candidate_only"] is True
    assert descriptor["non_authoritative"] is True
    assert descriptor["network_fetch"] is False
    assert descriptor["manifest_count"] == 3
    assert descriptor["entry_count"] == 30


def test_zelph_pack_sources_safe_invoke_abstains_on_candidate_profile() -> None:
    registry = build_default_registry()
    result = registry.safe_invoke("itir.zelph.pack_sources", {"repo_root": str(REPO_ROOT)})

    assert result["ok"] is True
    payload = result["result"]
    assert payload["decision"] == "abstained"
    assert payload["authority_profile"]["tool_id"] == "itir.zelph.pack_sources"
    assert payload["authority_profile"]["candidate_only"] is True
    assert payload["authority_profile"]["non_authoritative"] is True
    assert "profile_candidate_only" in payload["receipt"]["reason_codes"]
