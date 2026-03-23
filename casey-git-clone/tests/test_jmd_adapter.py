from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from casey_git_clone.jmd_adapter import build_casey_import_preview  # noqa: E402


def test_build_casey_import_preview_from_runtime_graph_example() -> None:
    graph_payload = json.loads(
        Path(ROOT.parent / "examples" / "jmd_bridge" / "jmd_runtime_graph_minimal.json").read_text(encoding="utf-8")
    )
    preview = build_casey_import_preview(graph_payload)

    assert preview["casey_import_version"] == "casey.jmd.graph.v1"
    assert preview["source_graph_id"] == graph_payload["graph_id"]
    assert preview["paths"][0]["path"].startswith("jmd/")
    assert preview["dependencies"][0]["kind"] == "link"
