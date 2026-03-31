# Wiki Timeline AAO Query Runtime Component

Date: 2026-03-31

## Change Class

Standard change.

## Problem

After the generic timeline-view runtime slice, the AAO adapter still owned
runtime loader policy in `itir-svelte/src/lib/server/wiki_timeline/aoo_adapter.ts`:

- timeline suffix candidate generation from `relPath`
- direct DB candidate loading policy
- AAO source-envelope loader path wiring

That is still canonical runtime behavior and should live beside the existing
Python query runtime owner, not in TS.

## Requirement

- move AAO raw/source-envelope runtime loading into the Python
  `wiki_timeline` runtime family
- keep TS responsible only for adapter work:
  - invoke Python
  - normalize payload object
  - apply HCA overlay when needed
- keep HCA overlay behavior out of the Python move for this slice

## Promoted Slice

- extend `SensibLaw/src/wiki_timeline/query_runtime.py` with:
  - rel-path to suffix-candidate resolution
  - raw AAO payload loading by rel-path
  - raw AAO source-envelope loading by source key and variant
- rewire `SensibLaw/scripts/query_wiki_timeline_aoo_db.py`
- thin `itir-svelte/src/lib/server/wiki_timeline/aoo_adapter.ts`

## Acceptance

- `aoo_adapter.ts` no longer owns suffix-candidate generation or DB candidate
  selection
- `loadWikiTimelineAooSource(...)` and `loadWikiTimelineAoo(...)` both invoke
  the Python query path
- HCA overlay behavior remains unchanged and still TS-local

## Quality Gate

Run from repo root:

- `/home/c/Documents/code/ITIR-suite/.venv/bin/python -m pytest -q SensibLaw/tests/test_timeline_view_projection.py SensibLaw/tests/test_wiki_timeline_numeric_projection.py SensibLaw/tests/test_fact_timeline_projection.py`
- `cd itir-svelte && node --test tests/wiki_timeline_refactor_regressions.test.js tests/graph_ui_regressions.test.js && npm run check`

## C4 / PlantUML

```plantuml
@startuml
title Wiki Timeline AAO Query Runtime Component

Component(ts, "aoo_adapter.ts", "Svelte AAO adapter")
Component(cli, "query_wiki_timeline_aoo_db.py", "CLI wrapper")
Component(runtime, "query_runtime.py", "Python runtime owner")
Component(overlay, "hca_overlay.ts", "TS HCA overlay")
Database(sqlite, "itir.sqlite", "Canonical wiki timeline store")

Rel(ts, cli, "invokes raw/source-envelope load")
Rel(cli, runtime, "delegates AAO loading policy")
Rel(runtime, sqlite, "loads raw AAO payload")
Rel(ts, overlay, "applies HCA overlay only")

@enduml
```
