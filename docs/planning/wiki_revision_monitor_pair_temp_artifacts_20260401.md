# Wiki Revision Monitor Pair Temp Artifacts

Date: 2026-04-01

## Change Class

Standard change.

## Problem

The query lane is already SQLite-canonical, but pair comparison in
`SensibLaw/src/wiki_timeline/revision_pack_runner.py` still persists pair-side
snapshot, timeline, and AOO JSON files under the durable run output tree.

Those files are still needed as path-based subprocess inputs, but they are not
canonical operational state and should not survive as durable lane storage.

## Requirement

- keep SQLite as the canonical operational store
- preserve path-based subprocess contracts for pair comparison
- demote pair snapshot, pair timeline, and pair AOO artifacts to bounded
  temporary files
- keep pair report export unchanged for this slice

## Decision

Promote roadmap step 5 before broader export posture changes:

- `pair_snapshots`, pair `timeline`, and pair `aoo` files become bounded temp
  artifacts inside `_build_pair_report(...)`
- pair report export remains the only durable pair-side JSON artifact in this
  slice
- selected pair, issue packet, and contested graph operational state remains
  SQLite-owned

## Acceptance

- `_build_pair_report(...)` no longer writes durable pair-side snapshot,
  timeline, or AOO artifacts under the revision-monitor out dir
- pair comparison still succeeds through path-based subprocess inputs
- pair report export still exists for the selected pair path contract
- focused revision-monitor tests stay green

## Quality Gate

Run from `SensibLaw/`:

- `../.venv/bin/python -m pytest -q tests/test_wiki_revision_pack_runner.py tests/test_revision_monitor_read_models.py tests/test_revision_monitor_query.py tests/test_revision_pack_summary.py`

## C4 / PlantUML

```plantuml
@startuml
title Wiki Revision Monitor Pair Temp Artifacts

Component(runner, "revision_pack_runner.py", "Pair comparison orchestrator")
Component(tempfiles, "bounded temp artifacts", "subprocess-only file inputs")
Database(sqlite, "Revision monitor SQLite", "canonical operational store")
Component(export, "pair report JSON", "temporary export surface")

Rel(runner, tempfiles, "writes pair snapshot/timeline/AOO temp files")
Rel(runner, sqlite, "writes selected pairs, issue packets, graph rows")
Rel(runner, export, "writes selected pair export")

@enduml
```
