# Casey Git Clone x StatiBaker DB Interface Contract (2026-03-09)

## Purpose
Define the minimal safe DB-backed handoff between `casey-git-clone`
superposition/version-control artifacts and `StatiBaker` observer/state
surfaces.

## Resolved context
- Archived conceptual Casey threads:
  - title: `Git Coordination Debate`
  - online UUID: `697c4c95-e1cc-839e-ac27-c262a27574eb`
  - canonical thread id: `b8800296148a7c14e0b84a152e0c67a2ba32acb0`
  - source used: `db`
  - main topic: candidate-per-path superposition, explicit workspace
    selection, explicit collapse, immutable build views
  - title: `Casey's Git idea summary`
  - canonical thread id: `be7800224c818a1b8d029595c915727fffcdea04`
  - source used: `db`
  - main topic: keep ambiguity visible until explicit collapse
- Supporting orchestration thread:
  - title: `Codeex and Vibe Faster`
  - online UUID: `6986ccc6-a58c-83a1-9c72-76c671dd7af0`
  - canonical thread id: `a7f17c531c63b2e1c45906b2ed9c031e0984f8c8`
  - source used: `db`
  - main topic: threaded orchestration should remain above explicit commit and
    collapse boundaries

## Boundary statement
`casey-git-clone` may cross into `StatiBaker` only as observer-class execution
artifacts. SB records:
- what operation happened
- when it happened
- which explicit workspace/tree/build ids were involved

SB does not become:
- the Casey workspace authority
- the source of truth for candidate sets
- the owner of collapse semantics

## Path 1: Observer overlay on existing SB activity/state

### Intended role
Attach Casey-specific operation receipts to an existing SB `activity_event` or
state slice.

### SB-owned base tables
Reuse the existing DB-backed overlay seam:
- `sb_itir_overlays`
- `sb_itir_mission_refs`
- `sb_itir_evidence_refs`

### Proposed Casey extension tables

```sql
CREATE TABLE sb_casey_workspace_refs (
  annotation_id TEXT NOT NULL REFERENCES sb_itir_overlays(annotation_id) ON DELETE CASCADE,
  ref_order INTEGER NOT NULL,
  ws_id TEXT NOT NULL,
  head_tree_id TEXT,
  selected_path_count INTEGER,
  policy_tie_break TEXT,
  policy_prefer_author TEXT,
  PRIMARY KEY (annotation_id, ref_order)
);

CREATE TABLE sb_casey_operation_refs (
  annotation_id TEXT NOT NULL REFERENCES sb_itir_overlays(annotation_id) ON DELETE CASCADE,
  ref_order INTEGER NOT NULL,
  operation_kind TEXT NOT NULL,
  path TEXT,
  tree_id_before TEXT,
  tree_id_after TEXT,
  chosen_fv_id TEXT,
  resolved_fv_id TEXT,
  receipt_hash TEXT,
  created_at TEXT,
  PRIMARY KEY (annotation_id, ref_order)
);

CREATE TABLE sb_casey_build_refs (
  annotation_id TEXT NOT NULL REFERENCES sb_itir_overlays(annotation_id) ON DELETE CASCADE,
  ref_order INTEGER NOT NULL,
  build_id TEXT NOT NULL,
  tree_id TEXT NOT NULL,
  selection_digest TEXT NOT NULL,
  created_at TEXT,
  PRIMARY KEY (annotation_id, ref_order)
);
```

### Required `sb_itir_overlays` row constraints
- `observer_kind = 'casey_workspace_v1'`
- `activity_event_id` must point to an existing SB activity event
- `annotation_id` is the stable overlay id
- `sb_state_id` or `state_date` must be present

### Allowed semantics
- explicit publish/sync/collapse/build operation refs
- workspace id, tree id, build id
- selection digest, not raw mutable workspace content
- collapse receipts and chosen/resolved file-version ids

### Forbidden semantics
- treating SB as the canonical store for Casey candidate graphs
- raw blob bytes
- implicit collapse or selection decisions made by SB
- mutation commands emitted back into Casey

## Path 2: Separate read-only operation/build ledger

### Intended role
Persist richer Casey operation history and immutable build references in a
separate ledger that SB may reference but not own canonically.

### Proposed ledger tables

```sql
CREATE TABLE casey_operation_ledger (
  operation_id TEXT PRIMARY KEY,
  operation_kind TEXT NOT NULL,
  ws_id TEXT,
  path TEXT,
  tree_id_before TEXT,
  tree_id_after TEXT,
  chosen_fv_id TEXT,
  resolved_fv_id TEXT,
  actor TEXT,
  created_at TEXT NOT NULL,
  receipt_hash TEXT NOT NULL
);

CREATE TABLE casey_build_ledger (
  build_id TEXT PRIMARY KEY,
  tree_id TEXT NOT NULL,
  selection_digest TEXT NOT NULL,
  created_at TEXT NOT NULL,
  source_operation_id TEXT
);

CREATE TABLE casey_build_selection_refs (
  build_id TEXT NOT NULL REFERENCES casey_build_ledger(build_id) ON DELETE CASCADE,
  path TEXT NOT NULL,
  fv_id TEXT NOT NULL,
  PRIMARY KEY (build_id, path)
);
```

### SB-facing rule
SB may record references to:
- `operation_id`
- `build_id`
- `receipt_hash`
- `selection_digest`

SB must not materialize Casey’s mutable workspace/candidate graph as SB
canonical state.

## Current implementation reality
- `casey-git-clone` currently implements:
  - deterministic ids/hashes
  - non-blocking publish/sync/collapse/build operations
  - immutable `BuildView`
- `casey-git-clone` does not yet persist the ledgers defined here.
- `StatiBaker` does not yet implement the Casey-specific extension tables.

## Decision
The interface is confirmed at the documentation/schema level only.

What is confirmed:
- the seam is observer-only
- the seam is DB-backed
- Casey keeps workspace/build authority
- SB records receipts and references, not mutable superposition state

What remains to implement:
- Casey operation/build ledger persistence
- SB-owned `casey_workspace_v1` extension tables
- adapter code and end-to-end tests
