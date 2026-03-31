# Wiki Revision Monitor Pair Report State Demotion

Date: 2026-04-01

## Change Class

Standard change.

## Problem

`pair_report_path` still leaks into revision-monitor operational semantics even
after the SQLite-first query conversion:

- run-level `reported` counts depend on path presence
- article-state continuity can carry forward `report_path` from previous state

That makes a legacy export link look like a required runtime state carrier.

## Requirement

- selected-pair state must drive operational counts
- article-state continuity must not depend on prior pair-report paths
- pair report path may remain as a legacy link for one transition slice

## Decision

For this slice:

- `candidate_pair_counts.reported` is derived from selected pair state, not
  `pair_report_path` presence
- article state no longer carries forward `report_path` from previous runs
- pair report path remains available in selected pair and article payloads as a
  legacy link only

## Acceptance

- no run-level count depends on `pair_report_path` existence
- article-state continuity does not reuse prior `report_path`
- pair report export path remains present where currently emitted
- focused revision-monitor tests stay green

## Quality Gate

Run from `SensibLaw/`:

- `../.venv/bin/python -m pytest -q tests/test_wiki_revision_pack_runner.py tests/test_revision_monitor_read_models.py tests/test_revision_monitor_query.py tests/test_revision_pack_summary.py`

## C4 / PlantUML

```plantuml
@startuml
title Wiki Revision Monitor Pair Report State Demotion

Component(runner, "revision_pack_runner.py", "run writer")
Database(sqlite, "Revision monitor SQLite", "canonical state")
Component(link, "pair_report_path", "legacy link only")

Rel(runner, sqlite, "derives counts from selected pair state")
Rel(runner, link, "may expose optional link")

@enduml
```
