# Wiki Revision Monitor Writer Contraction Roadmap

Date: 2026-04-01

## Change Class

Standard change roadmap.

## Problem

The wiki revision monitor query lane is now SQLite-canonical, but the runner in
`SensibLaw/src/wiki_timeline/revision_pack_runner.py` still writes and reuses
JSON working artifacts during normal operation.

That means the lane is not yet complete end to end:

- SQLite is canonical on the read side
- JSON sidecars still participate in the write side

## Requirement

- keep SQLite as the canonical operational store
- stop treating runner-written JSON artifacts as working state
- preserve bounded compatibility only where an explicit export surface is still
  justified

## Completion Roadmap

1. Remove runner-side dependence on pair-report JSON after write
   - keep pair report export path temporarily
   - stop rereading `pair_report_path` to derive:
     - issue packets
     - graph extract / contested-graph inputs
   - use in-memory pair payloads instead

2. Freeze the canonical replacement contract for remaining working artifacts
   - classify:
     - pair reports
     - snapshots
     - timeline files
     - AOO files
   - each surface must become one of:
     - SQLite-owned operational state
     - temporary tool-input artifact
     - explicit export-only artifact
     - dead duplication to remove

3. Remove persistent pair-report dependence from operational state
   - stop exposing pair report as the primary operational detail carrier
   - keep only SQLite-selected pair and packet read models for runtime/query
   - retain pair report only if an explicit operator export contract survives

4. Collapse current-article snapshot/timeline/AOO persistence to in-process
   builder calls or SQLite-owned equivalents
   - article state should not require JSON files as durable authority
   - timeline/AOO extraction should not require temp JSON handoff in the
     default path

5. Remove pair-snapshot / pair-timeline / pair-AOO sidecar reliance from pair
   comparison flow
   - default pair comparison should call timeline/AOO builders in-process
   - do not persist pair-side timeline/AOO artifacts as lane state

6. Decide final export posture
   - either:
     - no JSON exports
     - or explicitly versioned export-only artifacts
   - export must no longer be mistaken for storage

## Promoted Slice

Promote step 1 first:

- stop the runner from rereading pair-report JSON it just wrote
- preserve the existing pair-report export artifact for now
- use in-memory pair payloads for issue packets and contested-graph shaping

## Acceptance

- runner no longer depends on `pair_report_path` reads for immediate internal
  follow-on logic
- issue packet rows come from in-memory pair payloads
- contested graph shaping comes from in-memory pair payloads
- default timeline and AOO extraction are in-process, not subprocess file hops
- existing pair-report export path remains stable until final export posture is
  decided
- focused revision-monitor tests stay green

## Quality Gate

Run from `SensibLaw/`:

- `../.venv/bin/python -m pytest -q tests/test_wiki_revision_pack_runner.py tests/test_revision_monitor_read_models.py tests/test_revision_monitor_query.py tests/test_revision_pack_summary.py`

## C4 / PlantUML

```plantuml
@startuml
title Wiki Revision Monitor Writer Contraction Roadmap

Component(runner, "revision_pack_runner.py", "Runner owner")
Database(sqlite, "Revision monitor SQLite", "Canonical operational store")
Component(export, "pair report JSON", "Temporary export-only artifact")
Component(readmodels, "revision_monitor_read_models.py", "Operational query surfaces")

Rel(runner, sqlite, "writes canonical operational state")
Rel(runner, readmodels, "materializes selected pairs and issue packets")
Rel(runner, export, "may emit export-only artifact")
Rel(readmodels, sqlite, "reads")

@enduml
```
