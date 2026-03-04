# Wiki Timeline Coalescing Contract v1 (2026-02-12)

## Origin
- `origin_online_id`: `698bdf6e-43f8-839c-9089-34ee3d3338dd`
- `origin_note`: User-provided architecture thread; documented as provenance only (no live fetch in this step).

## Purpose
Define deterministic coalescing behavior for wiki timeline AAO artifacts without introducing fuzzy merges, string-similarity merges, or view-layer side effects.

This contract applies to truth-lane coalescing only.

## Scope
- Entity coalescing
- Action coalescing
- Frame/step coalescing
- Evidence coalescing guards

Non-scope:
- View grouping (ranking, collapse, display-only clustering)
- Statistical salience scoring
- Causal inference

## Coalescing Principles
1. Coalescing is identity-first and anchor-aware.
2. Coalescing is deterministic and replayable.
3. Coalescing never crosses frame scope silently.
4. Coalescing never relies on semantic regex or fuzzy string distance.

## Entity Coalescing Rules
1. Primary key is resolved identity (stable external/canonical ID when available).
2. Surface variants (`the X` vs `X`) may coalesce only via deterministic canonical surface normalization.
3. Alias-only coalescing is allowed only when the alias map is explicit input and provenance-preserved.
4. Type conflicts (`PERSON` vs `ORG`) must not silently merge; keep distinct rows and emit a warning.

## Action Coalescing Rules
1. Canonical action key is lemma-first (`reported` -> `report`).
2. Inflection metadata (`tense`, `aspect`, `voice`, `surface`) is preserved in metadata, not key space.
3. Negation is metadata (`step.negation`) and must not create unbounded action variants (`not_*` proliferation).

## Step Coalescing Rules
Two steps are coalescible only when all are equal:
1. Canonical action lemma
2. Subject set (post-normalization)
3. Object set (post-normalization for entity lane; modifier lane compared separately)
4. Negation kind
5. Frame-local anchor context (same event/frame)

If any field differs, keep both steps.

## Inter-fact Linking and Duplicate Guards
1. Fact rows (`ev:NNNN:fMM`) are sentence-local projections of steps; `fMM`
   preserves step order inside the same event.
2. Sequence links (`prev_fact_ids` / `next_fact_ids`) are derived from
   `event.chains[]` and remain non-causal.
3. Clause-linked pairs must remain distinct facts when actions differ, even with
   identical sentence text:
   - governing + complement (`content_clause`)
   - governing + infinitive (`infinitive_clause`)
4. Fact rows are coalescible only when all are equal:
   - `event_id`
   - canonical action lemma
   - normalized subject set
   - normalized object set
   - anchor payload (`year/month/day/precision/kind`)
   - chain role metadata (`prev/next/kind`) where present
5. Never coalesce across different `event_id` values, even when sentence text is
   identical.

## Evidence Coalescing Rules
1. Evidence overlays must not mutate role lanes.
2. Evidence nodes/edges may coalesce only when their source anchors match (same citation/reference key and frame context).
3. Cross-frame evidence links must be explicit edge records; never inferred by global entity overlap alone.

## Forbidden Coalescing Inputs
- Embedding similarity
- Levenshtein/fuzzy distance
- Regex-only subject/action/object inference
- Global document union when projecting per-frame timeline rows

## Required Provenance
Each coalesced artifact must remain traceable to:
- source frame/event id
- normalized key fields used for merge
- profile id/hash when profile-driven rules apply

## Validation Invariants
1. No coalescing across different frame ids in frame-scoped views.
2. No object lane fan-out from global document-level unions.
3. For any timeline projection row, every entity must have participation in the row's frame set.
4. Coalescing must be idempotent across repeated runs on the same input.

## Implementation Notes (non-binding)
- Use resolver identity + canonical surface keys for entity rows.
- Use lemma-first keys for actions.
- Use explicit frame-scoped participation records for timeline projections.
