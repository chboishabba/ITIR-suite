from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "notebooklm_pack_ingest.py"

spec = importlib.util.spec_from_file_location("notebooklm_pack_ingest", SCRIPT_PATH)
module = importlib.util.module_from_spec(spec)
assert spec is not None and spec.loader is not None
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def _write_pack_fixture(tmp_path: Path) -> Path:
    output_dir = tmp_path / "pack"
    output_dir.mkdir()
    (output_dir / "source_01.txt").write_text("alpha bravo\n", encoding="utf-8")
    (output_dir / "source_02.txt").write_text("charlie delta\n", encoding="utf-8")
    manifest = {
        "sources": 2,
        "manifest": [
            {"file": "source_01.txt", "repos": ["repo-a", "repo-b"], "words": 2, "bytes": 12},
            {"file": "source_02.txt", "repos": ["repo-c"], "words": 2, "bytes": 14},
        ],
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    return manifest_path


def test_normalize_manifest_adds_hashes_and_pack_run(tmp_path: Path) -> None:
    manifest_path = _write_pack_fixture(tmp_path)

    normalized = module.normalize_manifest(
        manifest_path,
        input_mode="repo_list",
        input_ref="/tmp/repos.txt",
        repo_scan_root="/tmp",
        max_sources=50,
        pack_run_id="notebooklm-pack-run:test",
        created_at="2026-03-29T00:00:00Z",
    )

    assert normalized["pack_run"]["pack_run_id"] == "notebooklm-pack-run:test"
    assert normalized["pack_run"]["source_count"] == 2
    assert normalized["packed_sources"][0]["source_file"] == "source_01.txt"
    assert normalized["packed_sources"][0]["source_file_hash"].startswith("sha256:")
    assert normalized["packed_sources"][1]["repos"] == ["repo-c"]


def test_build_command_plan_uses_placeholder_when_notebook_missing(tmp_path: Path) -> None:
    manifest_path = _write_pack_fixture(tmp_path)
    normalized = module.normalize_manifest(
        manifest_path,
        input_mode=None,
        input_ref=None,
        repo_scan_root=None,
        max_sources=5,
        pack_run_id="notebooklm-pack-run:test",
        created_at="2026-03-29T00:00:00Z",
    )

    plan = module.build_command_plan(
        normalized,
        notebook_context=module.NotebookContextPlan(
            notebook_id=None,
            notebook_title="Packed Research",
            create_if_missing=True,
        ),
        wait_timeout=120,
        wait_interval=3,
    )

    assert plan[0]["step"] == "create_notebook"
    assert plan[1]["command"][:4] == ["notebooklm", "source", "add", normalized["packed_sources"][0]["source_path"]]
    assert "__NOTEBOOK_ID__" in plan[1]["command"]
    assert any(step["step"] == "list_artifacts" for step in plan)


def test_cli_dry_run_writes_normalized_output(tmp_path: Path) -> None:
    manifest_path = _write_pack_fixture(tmp_path)
    output_path = tmp_path / "normalized.json"

    subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--manifest",
            str(manifest_path),
            "--input-mode",
            "repo_list",
            "--input-ref",
            "/tmp/repos.txt",
            "--repo-scan-root",
            "/tmp",
            "--max-sources",
            "7",
            "--notebook-title",
            "Packed Research",
            "--output",
            str(output_path),
        ],
        check=True,
        cwd=REPO_ROOT,
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["mode"] == "dry_run"
    assert payload["pack_run"]["input_mode"] == "repo_list"
    assert payload["pack_run"]["max_sources"] == 7
    assert len(payload["packed_sources"]) == 2
    assert payload["command_plan"][0]["step"] == "create_notebook"
    assert payload["command_plan"][-1]["step"] == "status"


def test_require_nested_id_reads_live_cli_shape() -> None:
    notebook_id, notebook = module.require_nested_id(
        {"notebook": {"id": "nb_123", "title": "Demo"}},
        "notebook",
    )
    source_id, source = module.require_nested_id(
        {"source": {"id": "src_456", "title": "source.txt"}},
        "source",
    )

    assert notebook_id == "nb_123"
    assert notebook["title"] == "Demo"
    assert source_id == "src_456"
    assert source["title"] == "source.txt"


def test_normalize_manifest_rejects_word_limit_overflow(tmp_path: Path) -> None:
    manifest_path = _write_pack_fixture(tmp_path)
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    payload["manifest"][0]["words"] = 500_001
    manifest_path.write_text(json.dumps(payload), encoding="utf-8")

    try:
        module.normalize_manifest(
            manifest_path,
            input_mode=None,
            input_ref=None,
            repo_scan_root=None,
            max_sources=2,
        )
    except ValueError as exc:
        assert "exceeds NotebookLM word limit" in str(exc)
    else:
        raise AssertionError("expected ValueError for word limit overflow")


def test_normalize_manifest_rejects_byte_limit_overflow(tmp_path: Path) -> None:
    manifest_path = _write_pack_fixture(tmp_path)
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    payload["manifest"][0]["bytes"] = (200 * 1024 * 1024) + 1
    manifest_path.write_text(json.dumps(payload), encoding="utf-8")

    try:
        module.normalize_manifest(
            manifest_path,
            input_mode=None,
            input_ref=None,
            repo_scan_root=None,
            max_sources=2,
        )
    except ValueError as exc:
        assert "exceeds NotebookLM byte limit" in str(exc)
    else:
        raise AssertionError("expected ValueError for byte limit overflow")
