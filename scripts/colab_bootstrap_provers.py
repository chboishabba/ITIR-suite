#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Protocol

COLAB_CLI_COMMIT = "006ff96ac2d0e4dcfb702467a76493d687929be8"
COLAB_MCP_COMMIT = "b9ab3899e0f1fa493390b1fd6d54aa2e464ecdf1"
BASELINE_LEAN = "v4.35.0-rc3"


@dataclass(frozen=True)
class PlatformFacts:
    has_git: bool = False
    has_python: bool = True
    has_elan: bool = False
    lean_version: str | None = None
    has_agda: bool = False
    colab_cli_pinned: bool = False
    colab_mcp_pinned: bool = False


@dataclass(frozen=True)
class BootstrapStep:
    kind: str
    argv: tuple[str, ...]


@dataclass(frozen=True)
class BootstrapPlan:
    toolchain_policy: str
    baseline_lean: str
    steps: tuple[BootstrapStep, ...]


@dataclass(frozen=True)
class BootstrapReceipt:
    toolchain_policy: str
    baseline_lean: str
    colab_cli_commit: str
    colab_mcp_commit: str
    applied: tuple[dict, ...]

    def to_dict(self) -> dict:
        return asdict(self)


class CommandRunner(Protocol):
    def run(self, argv): ...


class SubprocessRunner:
    def run(self, argv):
        cp = subprocess.run(list(argv), capture_output=True, text=True, shell=False)
        return {"argv": list(argv), "returncode": cp.returncode, "stdout": cp.stdout, "stderr": cp.stderr}


def build_bootstrap_plan(platform: PlatformFacts) -> BootstrapPlan:
    steps: list[BootstrapStep] = []
    missing_apt = []
    if not platform.has_git:
        missing_apt.append("git")
    if not platform.has_elan:
        missing_apt.append("elan")
    if not platform.has_agda:
        missing_apt.extend(["agda", "agda-stdlib"])
    if missing_apt:
        steps.append(BootstrapStep("apt_update", ("apt-get", "update")))
        steps.append(BootstrapStep("apt_install", ("apt-get", "install", "-y", *missing_apt)))
    if platform.lean_version != BASELINE_LEAN:
        steps.append(BootstrapStep("install_lean", ("elan", "toolchain", "install", BASELINE_LEAN)))
        steps.append(BootstrapStep("set_baseline_lean", ("elan", "default", BASELINE_LEAN)))
    steps.append(BootstrapStep("install_runner", (sys.executable, "-m", "pip", "install", "-e", "tools/colab-runner")))
    if not platform.colab_cli_pinned:
        steps.append(BootstrapStep("install_colab_cli", (sys.executable, "-m", "pip", "install", f"git+https://github.com/googlecolab/google-colab-cli@{COLAB_CLI_COMMIT}")))
    if not platform.colab_mcp_pinned:
        steps.append(BootstrapStep("install_colab_mcp", (sys.executable, "-m", "pip", "install", f"git+https://github.com/googlecolab/colab-mcp@{COLAB_MCP_COMMIT}")))
    return BootstrapPlan("repo_pinned", BASELINE_LEAN, tuple(steps))


def apply_bootstrap_plan(plan: BootstrapPlan, runner: CommandRunner) -> BootstrapReceipt:
    applied = []
    for step in plan.steps:
        result = runner.run(step.argv)
        safe = {
            "kind": step.kind,
            "argv": list(step.argv),
            "returncode": int(result.get("returncode", 1)),
            "stdout": str(result.get("stdout", ""))[-4000:],
            "stderr": str(result.get("stderr", ""))[-4000:],
        }
        applied.append(safe)
        if safe["returncode"] != 0:
            raise RuntimeError(f"bootstrap step failed: {step.kind}")
    return BootstrapReceipt(
        toolchain_policy=plan.toolchain_policy,
        baseline_lean=plan.baseline_lean,
        colab_cli_commit=COLAB_CLI_COMMIT,
        colab_mcp_commit=COLAB_MCP_COMMIT,
        applied=tuple(applied),
    )


def _version(argv: list[str]) -> str | None:
    try:
        cp = subprocess.run(argv, capture_output=True, text=True, shell=False, timeout=20)
        return (cp.stdout or cp.stderr or "").strip().splitlines()[0]
    except (OSError, subprocess.SubprocessError, IndexError):
        return None


def detect_platform() -> PlatformFacts:
    lean = _version(["lean", "--version"])
    return PlatformFacts(
        has_git=shutil.which("git") is not None,
        has_python=True,
        has_elan=shutil.which("elan") is not None,
        lean_version=BASELINE_LEAN if lean and "4.35.0" in lean else lean,
        has_agda=shutil.which("agda") is not None,
        colab_cli_pinned=False,
        colab_mcp_pinned=False,
    )


def main() -> int:
    plan = build_bootstrap_plan(detect_platform())
    receipt = apply_bootstrap_plan(plan, SubprocessRunner())
    Path(".itir").mkdir(exist_ok=True)
    Path(".itir/colab-bootstrap-receipt.json").write_text(json.dumps(receipt.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(receipt.to_dict(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
