# Wiki Timeline UI Priority Demotion (2026-04-01)

## Context

The meaningful wiki timeline runtime moves are already in:

- `SensibLaw/src/wiki_timeline/query_runtime.py`
- `SensibLaw/scripts/query_wiki_timeline_aoo_db.py`
- `itir-svelte/src/lib/server/wikiTimeline.ts`
- `itir-svelte/src/lib/server/wiki_timeline/aoo_adapter.ts`

The remaining `itir-svelte` AAO work is now mostly presentation-only shell
residue in:

- `itir-svelte/src/routes/graphs/wiki-timeline-aoo/+page.svelte`
- `itir-svelte/src/routes/graphs/wiki-timeline-aoo-all/+page.svelte`

## Decision

Demote further AAO route-shell extraction from active priority to opportunistic
cleanup.

Promote Python/runtime/store consolidation ahead of it.

## Why

The remaining AAO route-shell work is:

- presentation-only
- route-local
- low-risk
- low architectural leverage
- deferrable without reintroducing TS business logic

The higher-value open work is still in:

- SQLite/store contract consolidation
- Python-owned runtime and read-model followthrough
- cross-lane producer/query normalization

## Governance

- ITIL:
  treat future AAO route-shell extraction as low-risk maintenance, not as a
  lead migration lane
- ISO 9000:
  keep the rule explicit that TS must not regain business logic while these
  residual cleanups remain optional
- Six Sigma:
  prioritize the highest-variance producer/store duplication, not local
  presentation rearrangement
- C4:
  the AAO route shell is a presentation component; canonical runtime behavior
  now lives in Python/runtime and SQLite-backed query/read-model components

## Promotion Rule

Only promote more AAO route-shell extraction ahead of Python/store work if:

- it unblocks a concrete operator workflow, or
- it reveals a hidden runtime rule still living in TS

Otherwise, treat it as `P3` cleanup.
