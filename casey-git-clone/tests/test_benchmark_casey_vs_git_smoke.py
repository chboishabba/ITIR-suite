from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.benchmark_casey_vs_git import main  # noqa: E402


def test_benchmark_casey_vs_git_smoke(capsys, tmp_path) -> None:
    markdown_out = tmp_path / "summary.md"
    exit_code = main(
        [
            "--tiers",
            "small",
            "--lanes",
            "baseline_linear",
            "divergence_native",
            "build_freeze",
            "traceability_cost",
            "--surfaces",
            "cli",
            "library",
            "--samples",
            "1",
            "--markdown-out",
            str(markdown_out),
        ]
    )
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    assert payload["benchmark_version"] == "casey_vs_git.v1"
    assert payload["tiers"] == ["small"]
    assert len(payload["results"]) == 8
    assert "| tier | lane | surface |" in payload["markdown_summary"]
    assert markdown_out.exists()
    first = payload["results"][0]
    assert "casey" in first
    assert "git" in first
    assert "elapsed_ms" in first["casey"]
    assert "persisted_bytes_delta" in first["git"]
