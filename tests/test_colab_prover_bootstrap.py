from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "colab-runner" / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from colab_bootstrap_provers import (
    COLAB_CLI_COMMIT, COLAB_MCP_COMMIT, BASELINE_LEAN,
    PlatformFacts, build_bootstrap_plan, apply_bootstrap_plan,
)


class FakeRunner:
    def __init__(self):
        self.commands = []
    def run(self, argv):
        self.commands.append(list(argv))
        return {"argv": list(argv), "returncode": 0, "stdout": "ok", "stderr": ""}


def test_bootstrap_pins_google_colab_cli_commit():
    assert COLAB_CLI_COMMIT == "006ff96ac2d0e4dcfb702467a76493d687929be8"


def test_bootstrap_pins_colab_mcp_commit_as_optional_frontend():
    assert COLAB_MCP_COMMIT == "b9ab3899e0f1fa493390b1fd6d54aa2e464ecdf1"


def test_bootstrap_baseline_lean_is_v4_35_0_rc3():
    assert BASELINE_LEAN == "v4.35.0-rc3"


def test_repo_pinned_policy_does_not_override_checkout_lean_toolchain():
    plan = build_bootstrap_plan(PlatformFacts(has_git=True, has_python=True, has_elan=True, lean_version=BASELINE_LEAN, has_agda=True))
    assert plan.toolchain_policy == "repo_pinned"
    assert all("lean-toolchain" not in " ".join(step.argv) for step in plan.steps)


def test_bootstrap_is_idempotent_when_tools_already_match():
    plan = build_bootstrap_plan(PlatformFacts(has_git=True, has_python=True, has_elan=True, lean_version=BASELINE_LEAN, has_agda=True, colab_cli_pinned=True, colab_mcp_pinned=True))
    assert not any(step.kind == "install_lean" for step in plan.steps)


def test_bootstrap_receipt_records_actual_versions():
    runner = FakeRunner()
    receipt = apply_bootstrap_plan(build_bootstrap_plan(PlatformFacts()), runner)
    assert receipt.baseline_lean == BASELINE_LEAN
    assert receipt.colab_cli_commit == COLAB_CLI_COMMIT
    assert receipt.colab_mcp_commit == COLAB_MCP_COMMIT


def test_bootstrap_plan_never_serializes_github_token():
    plan = build_bootstrap_plan(PlatformFacts())
    assert "GITHUB_TOKEN" not in repr(plan)
    assert "ghp_" not in repr(plan)
