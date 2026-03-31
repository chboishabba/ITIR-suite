# Wiki Revision Monitor Blob Backcompat Boundary

Date: 2026-03-31

## Change Class

Standard change.

## Problem

The revision monitor still retains legacy blob columns such as `summary_json`
and `graph_json`. Query behavior had become SQLite-first in practice, but the
lane did not make that precedence explicit or observable.

## Requirement

Keep blob columns as backcompat/export surfaces only, and expose the actual
summary/graph source in the query payload so operators can verify SQLite-first
behavior.

## Component Boundary

Shared owner:

- `SensibLaw/src/wiki_timeline/revision_monitor_query.py`

Adopters:

- `SensibLaw/scripts/query_wiki_revision_monitor.py`
- `itir-svelte/src/lib/server/wikiRevisionMonitor.ts`

Promoted slice:

- add explicit `summary_source` and `selected_graph_source` fields to the
  query payload
- prefer SQLite read models over DB blobs and artifacts when both exist
- pin that precedence in focused tests

## Acceptance

- query payload reports whether summary and graph came from:
  - `sqlite_read_model`
  - `db_blob`
  - `artifact`
  - or `none`
- focused tests prove SQLite read models win over blob columns when both are
  present

## Quality Gate

Run from `SensibLaw/`:

- `../.venv/bin/python -m pytest -q tests/test_revision_monitor_query.py tests/test_revision_monitor_read_models.py tests/test_wiki_revision_pack_runner.py`

## C4 / PlantUML

```plantuml
@startuml
title Wiki Revision Monitor Blob Backcompat Boundary

Component(query, "revision_monitor_query.py", "Query/read-model owner")
Database(sqlite, "wiki revision monitor sqlite", "Canonical operational store")
Component(blob, "legacy blob columns", "Backcompat/export only")
Component(artifact, "artifact files", "Fallback only")

Rel(query, sqlite, "prefers normalized SQLite read models")
Rel(query, blob, "uses only as backcompat fallback")
Rel(query, artifact, "uses only as last fallback")

@enduml
```
