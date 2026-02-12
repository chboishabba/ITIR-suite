# Importance DSL + Scope Validation (2026-02-12)

## Why
- Fix timeline projection leakage by enforcing frame-scoped participation.
- Keep importance as a view projection, never truth mutation.
- Add deterministic sizing/ordering that avoids chaos.

## Implemented
- `itir-svelte/src/lib/importanceProfiles.ts`
  - Added profile id lane: `none | entropy_role_section_v1`.
  - Added deterministic scorer for `entropy_role_section_v1` using:
    - role entropy focus
    - section-distinctiveness (KL-like term)
    - section TF-IDF-style lift
  - Added percentile-based bounded scaling:
    - `scale = min + (max-min) * sqrt(percentile)`

- `itir-svelte/src/routes/graphs/wiki-fact-timeline/+page.svelte`
  - Added `importanceProfile` selector.
  - Subject/object ranking now uses profile score first, count second.
  - Added node scale application (view-only).
  - Added scope validator that asserts node→fact mappings are frame-consistent:
    - `sub:*` nodes only map to facts containing that subject
    - `obj:*` nodes only map to facts containing that object
    - `pty:*` nodes only map to facts containing that party
    - `time:*` nodes only map to facts with matching anchor bucket
    - `fact:*` nodes only map to their exact fact id
  - Added diagnostic readout (`scope_validator`, `leaks`, sample).

- `itir-svelte/src/routes/graphs/wiki-timeline-aoo-all/+page.svelte`
  - Switched object counts/edges to step-scoped objects first.
  - Keeps event-global objects as fallback only when `steps[]` absent.
  - Reduces bucket-wide object union bleed.

- `itir-svelte/src/lib/ui/LayeredGraph.svelte`
  - Added optional `LayerNode.scale` with bounded width/height scaling.

## Notes
- This is not a full generic AST evaluator yet; profile logic is deterministic code with a stable profile id.
- Current metric scope is artifact-level JSON (single loaded dataset), not cross-database global stats.
- Truth artifacts remain unchanged; all scoring/sizing is computed at view time.
