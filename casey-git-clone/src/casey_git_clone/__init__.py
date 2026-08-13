"""Casey Git Clone core package."""

from __future__ import annotations

from importlib import import_module

__all__ = [
    "Blob",
    "BuildLedgerRecord",
    "BuildView",
    "CaseyOverlayRefs",
    "Commit",
    "FileVersion",
    "OperationLedgerRecord",
    "PathState",
    "TreeState",
    "WorkspacePolicy",
    "WorkspaceView",
    "build_snapshot",
    "casey_to_sb_overlay_record",
    "cli_main",
    "collapse_conflict",
    "create_workspace",
    "emit_casey_observer_artifacts",
    "emit_runtime_observer_artifacts",
    "emit_runtime_receipts",
    "export_casey_facts",
    "initialize_runtime",
    "load_current_tree",
    "load_workspace",
    "publish_edits",
    "sync_workspace",
]

_EXPORTS = {
    "Blob": ("casey_git_clone.models", "Blob"),
    "BuildLedgerRecord": ("casey_git_clone.ledger_sqlite", "BuildLedgerRecord"),
    "BuildView": ("casey_git_clone.models", "BuildView"),
    "CaseyOverlayRefs": ("casey_git_clone.exchange", "CaseyOverlayRefs"),
    "Commit": ("casey_git_clone.models", "Commit"),
    "FileVersion": ("casey_git_clone.models", "FileVersion"),
    "OperationLedgerRecord": ("casey_git_clone.ledger_sqlite", "OperationLedgerRecord"),
    "PathState": ("casey_git_clone.models", "PathState"),
    "TreeState": ("casey_git_clone.models", "TreeState"),
    "WorkspacePolicy": ("casey_git_clone.models", "WorkspacePolicy"),
    "WorkspaceView": ("casey_git_clone.models", "WorkspaceView"),
    "build_snapshot": ("casey_git_clone.operations", "build_snapshot"),
    "casey_to_sb_overlay_record": ("casey_git_clone.exchange", "casey_to_sb_overlay_record"),
    "cli_main": ("casey_git_clone.cli", "main"),
    "collapse_conflict": ("casey_git_clone.operations", "collapse_conflict"),
    "create_workspace": ("casey_git_clone.runtime_sqlite", "create_workspace"),
    "emit_casey_observer_artifacts": ("casey_git_clone.adapters", "emit_casey_observer_artifacts"),
    "emit_runtime_observer_artifacts": ("casey_git_clone.receipts", "emit_runtime_observer_artifacts"),
    "emit_runtime_receipts": ("casey_git_clone.receipts", "emit_runtime_receipts"),
    "export_casey_facts": ("casey_git_clone.export", "export_casey_facts"),
    "initialize_runtime": ("casey_git_clone.runtime_sqlite", "initialize_runtime"),
    "load_current_tree": ("casey_git_clone.runtime_sqlite", "load_current_tree"),
    "load_workspace": ("casey_git_clone.runtime_sqlite", "load_workspace"),
    "publish_edits": ("casey_git_clone.operations", "publish_edits"),
    "sync_workspace": ("casey_git_clone.operations", "sync_workspace"),
}


def __getattr__(name: str):
    if name not in _EXPORTS:
        raise AttributeError(name)
    module_name, attr_name = _EXPORTS[name]
    module = import_module(module_name)
    value = getattr(module, attr_name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(__all__))
