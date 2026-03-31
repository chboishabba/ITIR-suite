# Wiki Revision Monitor In-Process Extractors

Date: 2026-04-01

## Change Class

Standard change.

## Problem

The revision monitor runner had already stopped treating timeline and AOO JSON
files as durable authority, but the default path still depended on file-based
script interfaces:

- `SensibLaw/scripts/wiki_timeline_extract.py`
- `SensibLaw/scripts/wiki_timeline_aoo_extract.py`

That kept temporary JSON artifacts alive in the default runner path even after
the query lane became SQLite-canonical.

## Requirement

- lift importable Python entrypoints out of the extractor scripts
- call timeline extraction and AOO extraction in-process from
  `SensibLaw/src/wiki_timeline/revision_pack_runner.py`
- keep the scripts as thin CLI wrappers
- stop requiring timeline/AOO temp JSON files in the default revision-monitor
  path

## Implemented Boundary

- `SensibLaw/scripts/wiki_timeline_extract.py`
  - now exposes `build_timeline_payload_from_snapshot(...)`
- `SensibLaw/scripts/wiki_timeline_aoo_extract.py`
  - now exposes `build_aoo_payload_from_timeline(...)`
  - CLI `main(...)` is reduced to parse -> delegate -> write
- `SensibLaw/src/wiki_timeline/revision_pack_runner.py`
  - default timeline and AOO builders now load those script entrypoints
    in-process and pass payloads directly
  - compatibility wrappers preserve older override callables that still use the
    earlier file-path-only signature

## Result

- default runner path no longer shells out for timeline or AOO extraction
- default runner path no longer requires timeline/AOO temp JSON files
- pair and baseline flows still accept legacy override builders during the
  transition
- the remaining export decision is now narrower:
  - pair report JSON
  - contested graph JSON

## Acceptance

- timeline extraction is callable as a Python builder
- AOO extraction is callable as a Python builder
- revision-pack runner uses those builders in-process by default
- focused revision-monitor gate remains green

## Quality Gate

Run from `SensibLaw/`:

- `../.venv/bin/python -m pytest -q tests/test_wiki_revision_pack_runner.py tests/test_revision_monitor_read_models.py tests/test_revision_monitor_query.py tests/test_revision_pack_summary.py`

## C4 / PlantUML

```plantuml
@startuml
title Wiki Revision Monitor In-Process Extractors

Component(runner, "revision_pack_runner.py", "Runner owner")
Component(timeline, "wiki_timeline_extract.py", "Importable timeline builder")
Component(aoo, "wiki_timeline_aoo_extract.py", "Importable AAO builder")
Database(sqlite, "Revision monitor SQLite", "Canonical store")
Component(exports, "JSON exports", "Bounded export-only surfaces")

Rel(runner, timeline, "calls in-process")
Rel(runner, aoo, "calls in-process")
Rel(runner, sqlite, "writes canonical state")
Rel(runner, exports, "may emit explicit exports only")

@enduml
```
