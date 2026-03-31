# Wiki Revision Monitor Read Models Component

Date: 2026-03-31

## Change Class

Standard change.

## Problem

The revision monitor still relied too heavily on stored `summary_json` and
`result_json` blobs for query surfaces. That left the lane queryable, but not
through explicit SQLite-first read models for latest runs and changed articles.

## Requirement

Add producer-owned SQLite read models for run summaries and changed-article
rows, and wire both the runner and query layer to use them.

## Component Boundary

Shared owner:

- `SensibLaw/src/wiki_timeline/revision_monitor_read_models.py`

Adopters:

- `SensibLaw/src/wiki_timeline/revision_pack_runner.py`
- `SensibLaw/src/wiki_timeline/revision_monitor_query.py`

Promoted slice:

- SQLite schema for run-summary read models
- SQLite schema for changed-article read models
- runner-side upsert of both read-model tables
- query-side latest-run and changed-article reads

## Acceptance

- runner populates explicit read-model tables in SQLite
- query layer can return latest runs and changed articles from SQLite
- focused tests pin both write and read paths

## Quality Gate

Run from `SensibLaw/`:

- `../.venv/bin/python -m pytest -q tests/test_revision_monitor_read_models.py tests/test_revision_monitor_query.py tests/test_wiki_revision_pack_runner.py`

## C4 / PlantUML

```plantuml
@startuml
title Wiki Revision Monitor Read Models Component

Component(runner, "revision_pack_runner.py", "Producer")
Component(query, "revision_monitor_query.py", "Query/read-model consumer")
Component(readmodels, "revision_monitor_read_models.py", "SQLite read-model owner")
Database(sqlite, "wiki revision monitor sqlite", "Canonical operational store")

Rel(runner, readmodels, "writes run and article read models")
Rel(query, readmodels, "reads latest runs and changed articles")
Rel(readmodels, sqlite, "stores normalized query rows")

@enduml
```
