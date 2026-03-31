# Wiki Revision Monitor Current State Temp Artifacts

Date: 2026-04-01

## Change Class

Standard change.

## Problem

`revision_pack_runner.py` still treats current timeline and current AOO JSON
paths as durable article-state continuity fields.

That is the wrong contract:

- SQLite row state should carry continuity
- path-based JSON files should be bounded tool artifacts only

## Requirement

- article-state continuity must not depend on current timeline or current AOO
  paths
- baseline initialization may still use path-based subprocess contracts, but
  only through bounded temp files
- current timeline/AOO paths should stop being persisted as durable authority

## Decision

For this slice:

- baseline current timeline and AOO builds use bounded temp files
- article state no longer carries forward or stores current timeline/AOO paths
- per-run article-result rows no longer persist current timeline/AOO paths
- snapshot fetch behavior stays unchanged in this slice

## Acceptance

- unchanged follow-on runs do not rely on prior current timeline/AOO paths
- baseline runs still succeed
- article-state continuity is driven by revid/timestamps/status, not timeline
  or AOO file paths
- focused revision-monitor tests stay green

## Quality Gate

Run from `SensibLaw/`:

- `../.venv/bin/python -m pytest -q tests/test_wiki_revision_pack_runner.py tests/test_revision_monitor_read_models.py tests/test_revision_monitor_query.py tests/test_revision_pack_summary.py`

## C4 / PlantUML

```plantuml
@startuml
title Wiki Revision Monitor Current State Temp Artifacts

Component(runner, "revision_pack_runner.py", "runner")
Database(sqlite, "Revision monitor SQLite", "continuity authority")
Component(tempfiles, "current timeline/AOO temp files", "subprocess-only")

Rel(runner, tempfiles, "uses on baseline initialization")
Rel(runner, sqlite, "stores revid, timestamps, status")

@enduml
```
