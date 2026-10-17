from __future__ import annotations

from dataclasses import asdict, dataclass
import os
from pathlib import Path
import platform
import subprocess
import sys
from typing import Any, Callable


@dataclass(frozen=True)
class RuntimeReceipt:
    python_version: str
    os_kernel: str
    cpu_count: int | None
    memory_total_kib: int | None
    memory_available_kib: int | None
    versions: dict[str, str | None]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _memory() -> tuple[int | None, int | None]:
    try:
        values: dict[str, int] = {}
        for line in Path("/proc/meminfo").read_text(encoding="utf-8").splitlines():
            key, rest = line.split(":", 1)
            if key in {"MemTotal", "MemAvailable"}:
                values[key] = int(rest.strip().split()[0])
        return values.get("MemTotal"), values.get("MemAvailable")
    except (OSError, ValueError):
        return None, None


def _version(argv: list[str], cwd: Path, runner: Callable[..., subprocess.CompletedProcess[str]]) -> str | None:
    try:
        cp = runner(argv, cwd=cwd, capture_output=True, text=True, shell=False, timeout=20)
        text = (cp.stdout or cp.stderr or "").strip()
        return text.splitlines()[0] if text else None
    except (OSError, subprocess.SubprocessError):
        return None


def collect_runtime_receipt(operation: str, checkout: Path, runner=subprocess.run) -> RuntimeReceipt:
    total, available = _memory()
    versions: dict[str, str | None] = {}
    if operation in {"lake_build", "lake_env_lean"}:
        versions["lake"] = _version(["lake", "--version"], checkout, runner)
        versions["lean"] = _version(["lake", "env", "lean", "--version"], checkout, runner)
    elif operation == "agda_module":
        versions["agda"] = _version(["agda", "--version"], checkout, runner)
    return RuntimeReceipt(
        python_version=sys.version.split()[0],
        os_kernel=f"{platform.system()} {platform.release()}",
        cpu_count=os.cpu_count(),
        memory_total_kib=total,
        memory_available_kib=available,
        versions=versions,
    )
