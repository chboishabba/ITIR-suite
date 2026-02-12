# Wiki Timeline Layout -> Ribbon Alignment (2026-02-11)

## Why this note exists
The AAO timeline views need deterministic layout rules that are stable under
new extraction features. This note maps the existing ribbon contract to AAO
layout choices.

Reference:
- `SensibLaw/docs/timeline_ribbon.md`

## Mapped invariants
- Ordered domain first:
  AAO event view uses explicit step order (`S1`, `S2`, ...), not force layout.
- Anchors preserved:
  Time chain (`Year -> Month -> Day`) remains an anchor chain and connects to
  the first step action via `at`.
- Threads do not mutate mass:
  AAO `then` edges are continuation/linearization only and do not assert
  causality or authority.
- View transform is reversible:
  Layout mode switch (`roles|step-ribbon`) changes placement only, not truth.

## Current implementation
- Route: `itir-svelte/src/routes/graphs/wiki-timeline-aoo/+page.svelte`
- New mode: `step-ribbon` (default), URL-selectable via `?view=step-ribbon`
- Behavior:
  - per-step columns (`Subjects`, `Action`, `Objects`, optional `Purpose`)
  - explicit `then` edges from action step `i` to `i+1`
  - dynamic graph width based on step count
  - existing `roles` layout retained as fallback

## Guardrails
- No causal inference from `then`.
- No semantic pruning in layout code.
- No data mutation; only node/edge placement changes.
- Keep deterministic ordering from extracted `steps[]` index.

## Follow-ups
- Add a `show clause mechanics` toggle once modifier lanes are available
  (`modifier_objects` / `modifiers[]`).
- Add passive-voice normalization checks at extractor level so role lanes align
  with sentence semantics before layout.
