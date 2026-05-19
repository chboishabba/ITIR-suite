from __future__ import annotations

import csv
import os
from pathlib import Path

from scripts import run_m5_beta_openai_adapter as adapter
from scripts import run_m5_eval_protocol as protocol


def test_env_loader_returns_keys_without_values(tmp_path: Path, monkeypatch) -> None:
    env_file = tmp_path / ".env_poc"
    env_file.write_text(
        "OPENAI_API_KEY=sk-test-secret\n# ignored\nPOSTGRES_HOST=localhost\n",
        encoding="utf-8",
    )
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("POSTGRES_HOST", raising=False)

    loaded = adapter.load_env_file(env_file)

    assert loaded == ["OPENAI_API_KEY", "POSTGRES_HOST"]
    assert os.environ["OPENAI_API_KEY"] == "sk-test-secret"
    assert "sk-test-secret" not in loaded


def test_treatment_context_preserves_governance_boundary() -> None:
    suite = protocol.load_suite(protocol.DEFAULT_SUITE)
    query = suite["queries"][0]

    context = adapter.build_treatment_context(query, suite)

    assert context["context_mode"] == "treatment_structured_candidate_axis_context"
    assert context["retrieval_is_live_m4"] is False
    assert context["typed_residual_profile"]["authority"] == "unresolved"
    assert context["governance_invariants"]["promotion_authority"] is False
    assert "M6_alone_can_prove_promotion_authority" in context["hard_limits"]
    assert context["support_packets"]


def test_live_score_sheet_contains_codex_judge_refs(tmp_path: Path) -> None:
    row = {
        "query_id": "q1",
        "category": "exact_support",
        "query": "What is proven?",
        "codex_judge_packet_ref": "packet.md",
        "promotion_authority": "false",
    }

    adapter.write_live_score_sheet(tmp_path / "score.csv", [row])
    rows = list(csv.DictReader((tmp_path / "score.csv").open(encoding="utf-8")))

    assert rows[0]["codex_judge_packet_ref"] == "packet.md"
    assert rows[0]["codex_prelim_judgment_ref"] == ""
    assert rows[0]["promotion_authority"] == "false"
