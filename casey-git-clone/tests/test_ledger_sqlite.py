from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from casey_git_clone.ledger_sqlite import (  # noqa: E402
    BuildLedgerRecord,
    OperationLedgerRecord,
    load_build,
    load_operation,
    upsert_build,
    upsert_operation,
)


def test_operation_ledger_roundtrip() -> None:
    rec = OperationLedgerRecord(
        operation_id="op-1",
        operation_kind="collapse",
        ws_id="ws-1",
        path="src/main.c",
        tree_id_before="tree-1",
        tree_id_after="tree-2",
        chosen_fv_id="fv-a",
        resolved_fv_id="fv-b",
        actor="alice",
        created_at="2026-03-09T00:00:00Z",
        receipt_hash="a" * 64,
    )

    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "casey_ledgers.sqlite"
        upsert_operation(db_path=db_path, record=rec)
        loaded = load_operation(db_path=db_path, operation_id="op-1")

    assert loaded is not None
    assert loaded["operation_id"] == "op-1"
    assert loaded["receipt_hash"] == "a" * 64


def test_build_ledger_roundtrip_with_selection_refs() -> None:
    rec = BuildLedgerRecord(
        build_id="build-1",
        tree_id="tree-2",
        selection_digest="b" * 64,
        created_at="2026-03-09T00:00:01Z",
        source_operation_id="op-1",
    )

    refs = [
        {"path": "README.md", "fv_id": "fv-readme"},
        {"path": "src/main.c", "fv_id": "fv-b"},
    ]

    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "casey_ledgers.sqlite"
        upsert_build(db_path=db_path, record=rec, selection_refs=refs)
        loaded = load_build(db_path=db_path, build_id="build-1")

    assert loaded is not None
    assert loaded["build_id"] == "build-1"
    assert {r["path"] for r in loaded["selection_refs"]} == {"README.md", "src/main.c"}
