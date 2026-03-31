# Wiki Revision Monitor v0.4 In-Place Migration

Date: 2026-03-31

## Change Class

Standard change.

## Problem

The v0.4 placeholder-only blob drop already applied to newly created revision
monitor DBs, but existing v0.3 DBs still carried the dead article-result and
candidate-pair blob columns. That left mixed schemas in operation.

## Requirement

- Apply the v0.4 placeholder-only column drop to existing revision-monitor DBs
  in place.
- Preserve row data for the surviving columns.
- Keep `summary_json` and `graph_json` untouched as the bounded backcompat blob
  fields.

## Promoted Slice

- detect legacy columns in:
  - `wiki_revision_monitor_article_results`
  - `wiki_revision_monitor_candidate_pairs`
- rebuild those tables in place with only the surviving v0.4 columns
- preserve existing row data for the retained columns
- prove migration behavior with a focused regression

## Acceptance

- opening an old v0.3 DB through
  [ensure_revision_pack_schema](/home/c/Documents/code/ITIR-suite/SensibLaw/src/wiki_timeline/revision_pack_runner.py)
  removes:
  - `packet_counts_json`
  - article-result `result_json`
  - `score_json`
  - `section_delta_json`
  - candidate-pair `result_json`
- retained row data survives the migration
- fresh-schema and query/read-model tests remain green

## Quality Gate

Run from `SensibLaw/`:

- `../.venv/bin/python -m pytest -q tests/test_revision_monitor_query.py tests/test_revision_monitor_read_models.py tests/test_wiki_revision_pack_runner.py`

## C4 / PlantUML

```plantuml
@startuml
title Wiki Revision Monitor v0.4 In-Place Migration

Component(schema, "ensure_revision_pack_schema()", "Schema/migration owner")
Database(v3db, "Existing v0.3 DB", "Legacy placeholder-only columns")
Database(v4db, "Migrated v0.4 DB", "Placeholder-only columns removed")
Component(query, "revision monitor query/read models", "Consumer")

Rel(schema, v3db, "detects legacy columns")
Rel(schema, v4db, "rebuilds tables in place")
Rel(query, v4db, "reads surviving canonical/backcompat surfaces")

@enduml
```
