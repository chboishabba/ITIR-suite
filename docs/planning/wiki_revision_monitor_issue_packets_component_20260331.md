# Wiki Revision Monitor Issue Packet Read Models

Date: 2026-03-31

## Change Class

Standard change.

## Problem

The revision monitor still relied on pair-report artifacts for selected
article packet detail. The lane had SQLite-first run and changed-article
surfaces, but selected issue packets were still only available indirectly via
report/result blobs.

## Requirement

Add producer-owned SQLite read models for selected issue packets and wire the
runner and query layer to use them.

## Component Boundary

Shared owner:

- `SensibLaw/src/wiki_timeline/revision_monitor_read_models.py`

Adopters:

- `SensibLaw/src/wiki_timeline/revision_pack_runner.py`
- `SensibLaw/src/wiki_timeline/revision_monitor_query.py`

Promoted slice:

- SQLite schema for selected issue-packet rows
- runner-side replace/upsert of selected packet rows per article/run
- query-side selected-article packet reads

## Acceptance

- runner populates explicit selected-packet rows in SQLite
- query layer can return selected issue packets from SQLite for the selected
  article
- focused tests pin both write and read paths

## Quality Gate

Run from `SensibLaw/`:

- `../.venv/bin/python -m pytest -q tests/test_revision_monitor_read_models.py tests/test_revision_monitor_query.py tests/test_wiki_revision_pack_runner.py`

## C4 / PlantUML

```plantuml
@startuml
title Wiki Revision Monitor Issue Packet Read Models

Component(runner, "revision_pack_runner.py", "Producer")
Component(query, "revision_monitor_query.py", "Query/read-model consumer")
Component(readmodels, "revision_monitor_read_models.py", "SQLite read-model owner")
Database(sqlite, "wiki revision monitor sqlite", "Canonical operational store")

Rel(runner, readmodels, "writes selected issue-packet rows")
Rel(query, readmodels, "reads selected issue-packet rows")
Rel(readmodels, sqlite, "stores normalized packet detail")

@enduml
```
