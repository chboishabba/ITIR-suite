# Wiki Revision Monitor SQLite-Only Query

Date: 2026-03-31

## Change Class

Standard change.

## Problem

Even after removing DB blob fallback, the query layer still treated JSON
artifacts on disk as an operational fallback source. That kept the runtime
contract split across SQLite and filesystem sidecars.

## Requirement

- make the revision-monitor query lane SQLite-only
- stop reading JSON artifact files for run discovery, summary derivation, or
  selected graph hydration
- keep JSON sidecars, if any remain, as migration debt rather than a live query
  contract

## Promoted Slice

- remove artifact-run discovery from
  [revision_monitor_query.py](/home/c/Documents/code/ITIR-suite/SensibLaw/src/wiki_timeline/revision_monitor_query.py)
- remove artifact summary fallback from the query payload builder
- remove artifact selected-graph fallback from the query payload builder
- keep `summary_source` and `selected_graph_source`, but restrict them to:
  - `sqlite_read_model`
  - `none`

## Acceptance

- query payloads no longer depend on filesystem JSON artifacts
- `runs` and `latest_runs` are SQLite-only
- summary and selected graph are either SQLite-derived or `none`

## Quality Gate

Run from `SensibLaw/`:

- `../.venv/bin/python -m pytest -q tests/test_revision_monitor_query.py tests/test_revision_monitor_read_models.py tests/test_wiki_revision_pack_runner.py`

## C4 / PlantUML

```plantuml
@startuml
title Wiki Revision Monitor SQLite-Only Query

Component(query, "revision_monitor_query.py", "Query owner")
Database(sqlite, "Revision monitor SQLite", "Canonical operational store")
Component(artifacts, "JSON sidecars", "No longer queried operationally")

Rel(query, sqlite, "reads packs/runs/summary/graph")
Rel(query, artifacts, "not used operationally")

@enduml
```
