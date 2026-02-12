# Frame Scope and Projection Validator Contract (2026-02-12)

## Purpose
Prevent projection leaks and circular fan-out artifacts in timeline/graph views.

Observed failure class:
- timeline rows that effectively become `date -> action -> (almost all entities in document)`

## Core rule
Every rendered node/edge in a frame-scoped projection must be traceable to the selected frame set.

## Scope model
- `frame_id` is the primary projection scope unit
- optional secondary scopes: `section_id`, `doc_id`, time bucket
- bucket summaries must be explicitly labeled as summaries

## Required index
Use frame-scoped participation records (conceptual shape):
- `(entity_id, frame_id, step_id, role)`

Do not derive per-frame objects by querying only global entity registries.

## Validator checks
1. **Entity leakage**
   - each projected entity must have participation in selected frame ids
2. **Step leakage**
   - each projected step must belong to selected frame ids
3. **Action leakage**
   - action nodes only from selected steps
4. **Cross-frame edges**
   - allowed only for explicitly typed evidence/context links with basis metadata

## Timeline synthesis rules
1. Prefer per-frame rows
2. If rendering bucket summary, label it as summary
3. Never silently union entity lists across all frames in the document

## Circularity handling notes
1. Circular-looking fan-out is usually a projection-scope bug, not a semantics bug.
2. Coalescing must remain frame-aware.
3. Year-only anchors should be de-prioritized when stronger same-year anchors exist.

## Dev-mode diagnostics
Expose for selected row:
- frame count
- step count
- entity count
- leakage warning count

## Test hooks
Add projection-invariant tests that fail if any entity/step/action appears without frame-local lineage.
