# Wiki Fact Timeline Python Migration Brief

Date: 2026-03-30

## Current surface

The current fact timeline route still depends on TypeScript-owned domain logic:

- `itir-svelte/src/routes/graphs/wiki-fact-timeline/projection.ts`
- `itir-svelte/src/routes/graphs/wiki-fact-timeline/+page.server.ts`

That TS module currently owns:

- fact-row synthesis fallback
- fact-row coalescing
- anchor normalization and fallback policy
- proposition/proposition-link coercion
- diagnostics derivation

Under the new Python domain-ownership policy, that is migration debt.

## Reusable core to preserve or extract

- fact timeline projection over normalized wiki timeline AAO payloads
- native vs nested vs synthesized fact-row source selection
- coalescing and identity-key policy
- proposition and proposition-link projection
- diagnostics about projection source and output counts

These are domain semantics and should live in Python-owned runtime code.

## Specialized remainder that should stay explicit

- the route shell
- the graph presentation
- interaction state and selection
- panel composition

Those remain valid `itir-svelte` responsibilities.

## Proposed split

- new Python module:
  `SensibLaw/src/wiki_timeline/fact_timeline_projection.py`
- extend:
  `SensibLaw/scripts/query_wiki_timeline_aoo_db.py`
  with a projection mode that can emit a preprojected fact timeline payload
- update:
  `itir-svelte/src/routes/graphs/wiki-fact-timeline/+page.server.ts`
  to consume the Python projection instead of `projection.ts`

## Acceptance check

- the route payload shape is unchanged for the UI
- diagnostics stay stable
- TS no longer owns the canonical fact/proposition projection logic
- parity is covered by Python tests plus existing `itir-svelte` regressions
