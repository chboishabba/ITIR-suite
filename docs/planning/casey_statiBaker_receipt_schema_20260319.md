# Casey Git Clone x StatiBaker Receipt Schema (2026-03-19)

## Purpose
Sharpen the Casey -> StatiBaker observer seam from a high-level interface note
into an explicit receipt/reference schema that can be implemented without
transferring Casey authority into SB.

## Relationship to the earlier seam note
This document refines:
- `docs/planning/casey_git_clone_statiBaker_interface_20260309.md`

That earlier note froze the observer-only posture and DB-backed direction.
This document narrows the exact receipt/reference fields to carry forward.

## Boundary statement
Casey exports observer-class receipts.

SB may record:
- operation refs
- workspace refs
- build refs
- receipt hashes and digests

SB must not record as canonical state:
- mutable Casey candidate graphs
- raw blob bytes
- hidden collapse authority
- synthetic Casey decisions made inside SB

## Receipt families

### 1. Workspace reference payload
Attach bounded workspace context to an SB overlay when needed.

```json
{
  "ws_id": "alice",
  "head_tree_id": "tree-...",
  "selected_path_count": 1,
  "policy_tie_break": "stable_hash",
  "policy_prefer_author": "alice"
}
```

Required meaning:
- identify the explicit Casey workspace involved
- expose only small summary fields, not the full mutable selection graph

### 2. Operation receipt payload
Capture a single publish/sync/collapse/build-adjacent operation by reference.

```json
{
  "operation_id": "op-...",
  "operation_kind": "collapse",
  "ws_id": "alice",
  "path": "src/main.c",
  "tree_id_before": "tree-old",
  "tree_id_after": "tree-new",
  "chosen_fv_id": "fv-a",
  "resolved_fv_id": "fv-a",
  "actor": "alice",
  "created_at": "2026-03-19T10:03:00+00:00",
  "receipt_hash": "0123..."
}
```

Required meaning:
- make explicit what Casey action happened
- preserve before/after tree ids
- preserve chosen/resolved candidate ids where relevant
- preserve actor/time/receipt hash

### 3. Build reference payload
Attach frozen build context by digest, not by mutable state transfer.

```json
{
  "build_id": "build-...",
  "tree_id": "tree-new",
  "selection_digest": "abcd...",
  "created_at": "2026-03-19T10:04:00+00:00",
  "selection_refs": [
    {
      "path": "src/main.c",
      "fv_id": "fv-a"
    }
  ]
}
```

Required meaning:
- represent the frozen Casey build world
- expose build selection refs only as immutable build content
- keep build refs separate from live workspace state

## SB overlay expectations

### `observer_kind`
- Casey overlays must use:
  - `observer_kind = 'casey_workspace_v1'`

### Minimum overlay payload shape
At the overlay row level, the annotation should carry:
- stable `annotation_id`
- `activity_event_id`
- `state_date` or `sb_state_id`
- `provenance`
- zero or more workspace refs
- zero or more operation refs
- zero or more build refs

### Overlay constraints
- overlays cannot rewrite SB history
- overlays cannot back-fill Casey candidate contents as SB canonical truth
- overlays cannot imply SB-originated collapse authority

## SQL table posture
The SQL direction remains the same as the 2026-03-09 seam note:
- SB-owned extension tables for:
  - workspace refs
  - operation refs
  - build refs
- separate Casey operation/build ledgers remain valid and desirable

This document does not replace that SQL note; it narrows the wire-level receipt
semantics those tables should carry.

## Current implementation reality
- `casey-git-clone` currently implements:
  - observer-ledger helper models/tables for operations and builds
  - overlay helper `casey_workspace_v1`
  - local Casey runtime/CLI testbed
- `casey-git-clone` does not yet emit the full receipt families above as a
  first-class end-to-end seam.
- `StatiBaker` does not yet implement the Casey-specific extension tables.

## Decision
The Casey -> SB seam is now specified in two layers:
- 2026-03-09: observer-only DB posture
- 2026-03-19: exact receipt/reference semantics

What remains to implement:
- Casey operation/build receipt emission mapped to these payloads
- SB extension-table ingestion aligned to these receipt families
- end-to-end tests proving SB stores refs/digests only and never owns mutable
  Casey candidate graphs
