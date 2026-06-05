from __future__ import annotations

import shutil
from typing import Any


def probe_vulkan_path() -> dict[str, Any]:
    probes: dict[str, Any] = {
        "glslc": bool(shutil.which("glslc")),
        "python_vulkan_import": False,
        "device_enumeration": False,
        "shader_spv_available": False,
        "tiny_parity": False,
    }
    try:
        import vulkan  # noqa: F401

        probes["python_vulkan_import"] = True
    except Exception:
        probes["python_vulkan_import"] = False
    ready = all(probes.values())
    missing = [key for key, value in probes.items() if not value]
    return {
        "suite": "dashi_vulkan_adapter",
        "intent_gpu": True,
        "active_backend": "vulkan" if ready else "cpu",
        "fallback_reason": None if ready else "probe_failed:" + ",".join(missing),
        "status": "ok" if ready else "skipped",
        "probes": probes,
        "parity_hash": None,
    }
