from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from chat_context_resolver_lib import live_provider


def test_extract_downloaded_json_paths_resolves_and_dedupes(tmp_path: Path) -> None:
    repo_root = tmp_path
    stdout = "\n".join(
        [
            "Downloaded conversation to exports/thread.json",
            "Downloaded conversation to exports/thread.json",
            f"Downloaded conversation to {tmp_path}/abs.json",
            "unrelated line",
        ]
    )

    paths = live_provider.extract_downloaded_json_paths(stdout, repo_root=repo_root)

    assert paths == [
        (repo_root / "exports/thread.json").resolve(),
        (tmp_path / "abs.json").resolve(),
    ]


def test_ingest_exports_to_structurer_reports_missing_ingest_script(tmp_path: Path) -> None:
    result = live_provider.ingest_exports_to_structurer(
        json_paths=[tmp_path / "export.json"],
        db_path=tmp_path / "archive.sqlite",
        venv_python=tmp_path / "venv/bin/python",
        repo_root=tmp_path,
        timeout=10,
    )

    assert result["ok"] is False
    assert "Missing ingest script" in result["error"]
    assert result["runs"] == []


def test_ingest_exports_to_structurer_runs_ingest_for_each_json(
    tmp_path: Path,
    monkeypatch,
) -> None:
    repo_root = tmp_path
    ingest_script = repo_root / "chat-export-structurer/src/ingest.py"
    ingest_script.parent.mkdir(parents=True)
    ingest_script.write_text("#!/usr/bin/env python3\n", encoding="utf-8")
    json_path = repo_root / "download.json"
    json_path.write_text("{}", encoding="utf-8")
    db_path = repo_root / "archive.sqlite"
    venv_python = repo_root / ".venv/bin/python"

    calls: list[list[str]] = []

    def _fake_run(cmd, **kwargs):
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, stdout="ok", stderr="")

    monkeypatch.setattr(live_provider.subprocess, "run", _fake_run)

    result = live_provider.ingest_exports_to_structurer(
        json_paths=[json_path],
        db_path=db_path,
        venv_python=venv_python,
        repo_root=repo_root,
        timeout=10,
    )

    assert result["ok"] is True
    assert result["ingested_count"] == 1
    assert len(result["runs"]) == 1
    assert result["runs"][0]["command"] == calls[0]
    assert calls[0][:2] == [str(venv_python), str(ingest_script)]
    assert "--source-id" in calls[0]


def test_persist_selector_to_structurer_wires_download_extract_and_ingest(
    tmp_path: Path,
    monkeypatch,
) -> None:
    repo_root = tmp_path
    downloaded = repo_root / "downloads" / "thread.json"
    downloaded.parent.mkdir(parents=True)
    downloaded.write_text("{}", encoding="utf-8")

    def _fake_download(selector, repo_root, venv_python, timeout):
        assert selector == "selector-value"
        return {"ok": True, "stdout": f"Downloaded conversation to {downloaded}"}

    captured: dict = {}

    def _fake_ingest(json_paths, db_path, venv_python, repo_root, timeout):
        captured["json_paths"] = json_paths
        return {"ok": True, "runs": [{"ok": True}], "ingested_count": 1}

    monkeypatch.setattr(live_provider, "run_web_download", _fake_download)
    monkeypatch.setattr(live_provider, "ingest_exports_to_structurer", _fake_ingest)

    result = live_provider.persist_selector_to_structurer(
        selector="selector-value",
        repo_root=repo_root,
        db_path=repo_root / "archive.sqlite",
        venv_python=repo_root / ".venv/bin/python",
        timeout=30,
    )

    assert result["ok"] is True
    assert result["download"]["ok"] is True
    assert result["downloaded_json_paths"] == [str(downloaded.resolve())]
    assert captured["json_paths"] == [downloaded.resolve()]
