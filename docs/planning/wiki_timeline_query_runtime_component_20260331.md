# Wiki Timeline Query Runtime Component

Date: 2026-03-31

## Change Class

Standard change.

## Problem

Most generic wiki/timeline semantics have already moved to Python, but
`itir-svelte/src/lib/server/wikiTimeline.ts` still owns runtime loader policy:

- DB path fallback resolution
- source-key normalization and fallback
- source-envelope loading for timeline-view queries

That is still canonical runtime behavior, not presentation-only shell glue.

## Requirement

- move generic timeline-view loader and resolver policy behind one Python owner
- keep `itir-svelte` as a thin adapter that invokes Python and consumes the
  returned envelope
- do not mix this first slice with AAO overlay or AAO fallback behavior

## Promoted Slice

New Python owner:

- `SensibLaw/src/wiki_timeline/query_runtime.py`

First bounded responsibilities:

- canonical DB path resolution for wiki/timeline queries
- source-key normalization with explicit fallback
- source-meta envelope loading for `timeline_view`

Adopters:

- `SensibLaw/scripts/query_wiki_timeline_aoo_db.py`
- `itir-svelte/src/lib/server/wikiTimeline.ts`

## Acceptance

- `wikiTimeline.ts` no longer owns DB path fallback policy for timeline-view
  loading
- `wikiTimeline.ts` no longer owns source-key normalization for timeline-view
  loading
- `query_wiki_timeline_aoo_db.py` delegates that runtime policy to the shared
  Python owner
- timeline-view callers still receive `{ source, rel_path, timeline_suffix, payload }`

## Quality Gate

Run from repo root:

- `/home/c/Documents/code/ITIR-suite/.venv/bin/python -m pytest -q SensibLaw/tests/test_timeline_view_projection.py`
- `cd itir-svelte && node --test tests/wiki_timeline_refactor_regressions.test.js tests/graph_ui_regressions.test.js && npm run check`

## C4 / PlantUML

```plantuml
@startuml
title Wiki Timeline Query Runtime Component

Component(ts, "wikiTimeline.ts", "Svelte server adapter")
Component(cli, "query_wiki_timeline_aoo_db.py", "CLI wrapper")
Component(runtime, "query_runtime.py", "Python loader/runtime owner")
Database(sqlite, "itir.sqlite", "Canonical wiki timeline store")

Rel(ts, cli, "invokes")
Rel(cli, runtime, "delegates db-path/source/runtime loading")
Rel(runtime, sqlite, "loads projection payload and source envelope")

@enduml
```
