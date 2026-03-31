# Wiki Timeline View Python Migration Brief

Date: 2026-03-30

## Purpose

Continue the `P0` Python-domain-ownership migration by removing generic wiki
timeline view normalization from `itir-svelte` server code.

## Current problem

`itir-svelte/src/lib/server/wikiTimeline.ts` still owns:

- snapshot field normalization
- event filtering
- anchor coercion
- best-effort event ordering

That is generic wiki timeline semantics, not presentation-only route glue.

## Required boundary

Python must own the generic wiki timeline view projection. The `itir-svelte`
layer may:

- resolve source selection
- resolve repo / db paths
- invoke the Python query script
- consume the already-shaped payload

It must not:

- decide canonical event filtering rules
- re-own anchor normalization
- re-own canonical timeline ordering

## First bounded slice

- add a Python `timeline_view` projection to
  `SensibLaw/scripts/query_wiki_timeline_aoo_db.py`
- add a Python module that:
  - normalizes snapshot fields
  - normalizes anchor fields
  - filters invalid event rows
  - sorts events deterministically
- reduce `itir-svelte/src/lib/server/wikiTimeline.ts` to adapter-only loading
  over that projection

## Second bounded slice

- move source-key to suffix/rel-path resolution behind the same Python query
  path
- let `itir-svelte` pass a source key and consume returned source metadata
  instead of hardcoding local `SOURCE_PATHS` maps per route
- first adopters:
  - `itir-svelte/src/lib/server/wikiTimeline.ts`
  - `itir-svelte/src/routes/graphs/wiki-fact-timeline/+page.server.ts`
- next adopters:
  - `itir-svelte/src/routes/graphs/wiki-timeline-aoo/+page.server.ts`
  - `itir-svelte/src/routes/graphs/wiki-timeline-aoo-all/+page.server.ts`

## Acceptance check

- `wiki-timeline` route still loads the same payload shape
- event ordering/filtering is now owned by Python
- `wikiTimeline.ts` no longer contains inline event normalization/sort loops
- focused Python and `itir-svelte` regression tests pass
