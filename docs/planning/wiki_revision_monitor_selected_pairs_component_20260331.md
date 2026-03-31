# Wiki Revision Monitor Selected Pair Read Models

Date: 2026-03-31

## Change Class

Standard change.

## Problem

The revision monitor still relied on pair-report artifacts for selected pair
detail such as pair kind, severity, score, and section-touch summaries.

## Requirement

Add producer-owned SQLite read models for selected pairs and wire the runner
and query layer to use them.

## Component Boundary

Shared owner:

- `SensibLaw/src/wiki_timeline/revision_monitor_read_models.py`

Adopters:

- `SensibLaw/src/wiki_timeline/revision_pack_runner.py`
- `SensibLaw/src/wiki_timeline/revision_monitor_query.py`

Promoted slice:

- SQLite schema for selected pair rows
- runner-side replace/upsert of selected pairs per article/run
- query-side selected pair reads for the selected article

## Acceptance

- runner populates explicit selected-pair rows in SQLite
- query layer can return selected pair detail from SQLite
- focused tests pin both write and read paths

## Quality Gate

Run from `SensibLaw/`:

- `../.venv/bin/python -m pytest -q tests/test_revision_monitor_read_models.py tests/test_revision_monitor_query.py tests/test_wiki_revision_pack_runner.py`

## C4 / PlantUML

```plantuml
@startuml
title Wiki Revision Monitor Selected Pair Read Models

Component(runner, "revision_pack_runner.py", "Producer")
Component(query, "revision_monitor_query.py", "Query/read-model consumer")
Component(readmodels, "revision_monitor_read_models.py", "SQLite read-model owner")
Database(sqlite, "wiki revision monitor sqlite", "Canonical operational store")

Rel(runner, readmodels, "writes selected pair rows")
Rel(query, readmodels, "reads selected pair rows")
Rel(readmodels, sqlite, "stores normalized selected-pair detail")

@enduml
```
