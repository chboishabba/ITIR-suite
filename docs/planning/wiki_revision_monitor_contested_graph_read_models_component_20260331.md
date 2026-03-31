# Wiki Revision Monitor Contested Graph Read Models

Date: 2026-03-31

## Change Class

Standard change.

## Problem

The revision monitor still hydrated `selected_graph` from `graph_json` or
artifact files even though most contested graph structure was already stored in
SQLite. That left the contested-graph route dependent on stored graph blobs.

## Requirement

Add explicit SQLite read models for contested-graph event and epistemic rows,
and assemble `selected_graph` from SQLite-first graph read models.

## Component Boundary

Shared owner:

- `SensibLaw/src/wiki_timeline/revision_monitor_read_models.py`

Adopters:

- `SensibLaw/src/wiki_timeline/revision_pack_runner.py`
- `SensibLaw/src/wiki_timeline/revision_monitor_query.py`

Promoted slice:

- SQLite schema for contested-graph event rows
- SQLite schema for contested-graph epistemic rows
- runner-side persist of those rows during graph insertion
- query-side graph assembly from graph, region, cycle, edge, pair, event, and
  epistemic rows

## Acceptance

- runner populates explicit contested-graph event and epistemic rows
- query layer can assemble `selected_graph` from SQLite-first graph read models
- focused tests pin both write and read paths

## Quality Gate

Run from `SensibLaw/`:

- `../.venv/bin/python -m pytest -q tests/test_revision_monitor_read_models.py tests/test_revision_monitor_query.py tests/test_wiki_revision_pack_runner.py`

## C4 / PlantUML

```plantuml
@startuml
title Wiki Revision Monitor Contested Graph Read Models

Component(runner, "revision_pack_runner.py", "Producer")
Component(query, "revision_monitor_query.py", "Query/read-model consumer")
Component(readmodels, "revision_monitor_read_models.py", "SQLite read-model owner")
Database(sqlite, "wiki revision monitor sqlite", "Canonical operational store")

Rel(runner, readmodels, "writes contested-graph rows")
Rel(query, readmodels, "reads contested-graph rows")
Rel(readmodels, sqlite, "stores normalized graph detail")

@enduml
```
