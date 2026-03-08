# Fuzzymodo x StatiBaker DB Interface Contract (2026-03-09)

## Purpose
Define the minimal safe DB-backed handoff between `fuzzymodo` selector
decisions and `StatiBaker` state/history surfaces.

This contract is intentionally narrow:
- `fuzzymodo` remains the selector / norm-constraint / replay authority
- `StatiBaker` remains the append-only observer/state authority
- no normative authority is transferred into `StatiBaker`

## Resolved context
- Archived source thread:
  - title: `OSS-Fuzz Bug Detection`
  - online UUID: `698686e2-6e48-839e-ad0f-91e6fa4697f8`
  - canonical thread id: `f007250c85c623e16ea46238451cdbb00c745743`
  - source used: `db`
- Supporting SB boundary thread already reflected in suite planning:
  - `Conductor vs SB/ITIR`
  - online UUID: `6986c9f5-3988-839d-ad80-9338ea8a04eb`
  - source used: prior synced planning/doc state

## Boundary statement
`fuzzymodo` may cross into `StatiBaker` only through SB-owned SQLite tables, in
one of two ways:
1. an observer overlay attached to an existing SB `activity_event`
2. a separate read-only decision ledger that SB may reference, but does not
   treat as canonical memory state

`StatiBaker` must not ingest as canonical SB state:
- raw selector DSL payloads
- norm constraints as SB policy
- speculative branch trees as SB truth
- summary text that replaces provenance

## Path 1: Observer overlay on existing SB activity/state

### Intended role
Attach a `fuzzymodo` decision or evaluation outcome to an already-existing SB
timeline/state record for operator review.

### SB-owned base tables
Reuse the existing overlay seam already implemented in
`StatiBaker/sb/dashboard_store_sqlite.py`:
- `sb_itir_overlays`
- `sb_itir_mission_refs`
- `sb_itir_evidence_refs`

### Proposed `fuzzymodo` extension tables
These remain SB-owned tables in the same SQLite DB:

```sql
CREATE TABLE sb_fuzzymodo_selector_refs (
  annotation_id TEXT NOT NULL REFERENCES sb_itir_overlays(annotation_id) ON DELETE CASCADE,
  ref_order INTEGER NOT NULL,
  selector_hash TEXT NOT NULL,
  decision_state TEXT,
  matched INTEGER,
  policy_hash TEXT,
  replay_key TEXT,
  created_at TEXT,
  PRIMARY KEY (annotation_id, ref_order)
);

CREATE TABLE sb_fuzzymodo_reason_codes (
  annotation_id TEXT NOT NULL REFERENCES sb_itir_overlays(annotation_id) ON DELETE CASCADE,
  ref_order INTEGER NOT NULL,
  reason_code TEXT NOT NULL,
  detail TEXT,
  PRIMARY KEY (annotation_id, ref_order)
);

CREATE TABLE sb_fuzzymodo_artifact_refs (
  annotation_id TEXT NOT NULL REFERENCES sb_itir_overlays(annotation_id) ON DELETE CASCADE,
  ref_order INTEGER NOT NULL,
  artifact_kind TEXT NOT NULL,
  artifact_locator TEXT NOT NULL,
  artifact_hash TEXT,
  PRIMARY KEY (annotation_id, ref_order)
);
```

### Required `sb_itir_overlays` row constraints
- `observer_kind = 'fuzzymodo_selector_v1'`
- `activity_event_id` must point to an existing SB activity event
- `annotation_id` is the stable overlay id
- `sb_state_id` or `state_date` must be present
- `provenance_json` remains provenance metadata only, not the primary payload

### Allowed semantics
- selector hash reference
- terminal or buffered decision state
- matched/not-matched outcome
- reason codes
- refs to replay artifacts or external decision-ledger rows

### Forbidden semantics
- raw selector clause trees copied into SB canonical tables
- norm constraints treated as SB policy
- mutation instructions
- full branch exploration dumps

## Path 2: Separate read-only decision ledger

### Intended role
Persist `fuzzymodo` decision/replay facts in a dedicated ledger that SB can
join against or reference, while keeping that ledger outside SB canonical state.

This is the better fit for richer selector history and replayability.

### Proposed ledger tables
These may live in a separate SQLite DB or a clearly isolated table family in a
shared DB, but they are not SB canonical state tables.

```sql
CREATE TABLE fuzzymodo_decision_ledger (
  decision_id TEXT PRIMARY KEY,
  selector_hash TEXT NOT NULL,
  decision_state TEXT NOT NULL,
  matched INTEGER,
  policy_hash TEXT,
  replay_key TEXT,
  fact_digest TEXT,
  created_at TEXT NOT NULL,
  decided_by TEXT,
  source_tool TEXT NOT NULL DEFAULT 'fuzzymodo'
);

CREATE TABLE fuzzymodo_decision_ledger_reason_codes (
  decision_id TEXT NOT NULL REFERENCES fuzzymodo_decision_ledger(decision_id) ON DELETE CASCADE,
  ref_order INTEGER NOT NULL,
  reason_code TEXT NOT NULL,
  detail TEXT,
  PRIMARY KEY (decision_id, ref_order)
);

CREATE TABLE fuzzymodo_decision_ledger_artifacts (
  decision_id TEXT NOT NULL REFERENCES fuzzymodo_decision_ledger(decision_id) ON DELETE CASCADE,
  ref_order INTEGER NOT NULL,
  artifact_kind TEXT NOT NULL,
  artifact_locator TEXT NOT NULL,
  artifact_hash TEXT,
  PRIMARY KEY (decision_id, ref_order)
);
```

### SB-facing rule
SB may only ingest references to this ledger, for example:
- `decision_id`
- `selector_hash`
- `artifact_locator`
- `policy_hash`

SB must not copy the ledger wholesale into canonical timeline/state tables.

## Current implementation reality
- `fuzzymodo` currently implements:
  - canonical selector hashing
  - boolean selector evaluation
  - speculation branch / retirement primitives
- `fuzzymodo` does not yet implement the richer decision-ledger or overlay
  adapter described here.
- `StatiBaker` currently implements the generic DB-backed overlay seam, but not
  the `fuzzymodo_selector_v1` extension tables.

## Decision
The interface is confirmed at the documentation/schema level only.

What is confirmed:
- the seam is observer-only
- the seam is DB-backed
- the seam is append-only / reference-heavy
- selector and norm authority stay outside SB

What remains to implement:
- SB-owned `fuzzymodo_selector_v1` extension tables
- `fuzzymodo` decision-ledger persistence
- adapter code and end-to-end tests for both paths
