# Wiki Revision Monitor Sidecar Contraction Slice 1

Date: 2026-03-31

## Change Class

Standard change.

## Problem

The revision-monitor query lane is already SQLite-only, but the runner still
emits redundant JSON sidecars that are no longer required for operational
reads. The safest first contraction slice is to remove the pure convenience
writes first, before redesigning any runner working-artifact interfaces.

## Requirement

- keep SQLite as the canonical operational store
- remove runner-side JSON writes that are now redundant convenience mirrors
- avoid touching working artifacts that still feed downstream runner steps

## Promoted Slice

- remove the run-summary JSON sidecar in `out_dir/runs/`
- remove the redundant `__latest.json` contested-graph alias
- keep the canonical contested-graph artifact path and the remaining working
  JSON artifacts unchanged for this slice

## Why This Slice

This is the lowest-risk contraction because:

- run summary is already persisted into SQLite read models
- the `__latest.json` graph alias is a duplicate of the canonical graph path
- neither removal changes the now-SQLite-only query contract

## Acceptance

- fresh runs no longer emit `runs/<run_id>.json`
- fresh runs no longer emit `contested_graphs/<article_id>__latest.json`
- the canonical contested-graph artifact still exists at its stable path
- SQLite summary and contested-graph read models remain intact

## Quality Gate

Run from `SensibLaw/`:

- `../.venv/bin/python -m pytest -q tests/test_revision_pack_storage.py tests/test_wiki_revision_pack_runner.py tests/test_revision_monitor_query.py tests/test_revision_monitor_read_models.py`

## C4 / PlantUML

```plantuml
@startuml
title Wiki Revision Monitor Sidecar Contraction Slice 1

Component(runner, "revision_pack_runner.py", "Runner owner")
Database(sqlite, "Revision monitor SQLite", "Canonical operational store")
Component(storage, "revision_pack_storage.py", "Canonical artifact paths")
Component(sidecars, "Redundant JSON sidecars", "Run summary + latest graph alias")

Rel(runner, sqlite, "writes canonical run/graph read models")
Rel(runner, storage, "writes canonical graph artifact")
Rel(runner, sidecars, "stops writing")

@enduml
```
