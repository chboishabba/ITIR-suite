# Wiki Revision Monitor v0.5 Backcompat Blob Drop

Date: 2026-03-31

## Change Class

Standard change.

## Problem

The revision monitor still retained `summary_json` and `graph_json` as the last
bounded backcompat blob columns, even though the lane can now derive both
surfaces from SQLite read models and artifact fallback.

## Requirement

- remove `wiki_revision_monitor_runs.summary_json`
- remove `wiki_revision_monitor_contested_graphs.graph_json`
- preserve operational summary and selected-graph behavior through:
  - SQLite read models first
  - artifact fallback second
- migrate older DBs in place

## Promoted Slice

- bump the runner/state contract to `wiki_revision_pack_state_v0_5`
- remove `summary_json` and `graph_json` from fresh schema creation
- rebuild old `wiki_revision_monitor_runs` and
  `wiki_revision_monitor_contested_graphs` tables in place without those
  columns
- remove DB-blob fallback from
  [revision_monitor_query.py](/home/c/Documents/code/ITIR-suite/SensibLaw/src/wiki_timeline/revision_monitor_query.py)
- keep `summary_source` and `selected_graph_source`, but restrict them to:
  - `sqlite_read_model`
  - `artifact`
  - `none`

## Acceptance

- fresh DBs no longer create `summary_json` or `graph_json`
- old DBs migrate in place and preserve surviving row data
- query payload still returns summary and selected graph from SQLite read models
  when present
- focused tests prove:
  - v0.5 schema has no remaining blob backcompat columns
  - in-place migration removes the old columns
  - query stays SQLite-first

## Quality Gate

Run from `SensibLaw/`:

- `../.venv/bin/python -m pytest -q tests/test_revision_pack_summary.py tests/test_revision_monitor_query.py tests/test_revision_monitor_read_models.py tests/test_wiki_revision_pack_runner.py`

## C4 / PlantUML

```plantuml
@startuml
title Wiki Revision Monitor v0.5 Backcompat Blob Drop

Component(runner, "revision_pack_runner.py", "Schema + producer owner")
Component(query, "revision_monitor_query.py", "Read-model query owner")
Database(sqlite, "Revision monitor SQLite", "Canonical store, no blob columns")
Component(artifacts, "revision artifacts", "Fallback only")

Rel(runner, sqlite, "writes canonical rows only")
Rel(query, sqlite, "reads canonical rows first")
Rel(query, artifacts, "uses fallback only when SQLite summaries/graphs are absent")

@enduml
```
