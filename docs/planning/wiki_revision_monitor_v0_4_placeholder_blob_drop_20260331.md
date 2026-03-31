# Wiki Revision Monitor v0.4 Placeholder Blob Drop

Date: 2026-03-31

## Change Class

Standard change.

## Problem

The repo-local and local-workspace audit found no surviving consumers for the
placeholder-only legacy blob columns in the revision monitor lane, but the v0.3
schema still carried them for newly created DBs.

## Requirement

- Remove the placeholder-only legacy columns from the v0.4 schema for newly
  created revision monitor DBs.
- Keep existing v0.3 DBs readable without requiring an immediate destructive
  migration.
- Preserve `summary_json` and `graph_json` as the remaining bounded backcompat
  blob fields.

## Workspace Audit Result

Audited under `/home/c/Documents/code`:

- no local sibling-repo consumer was found for:
  - `wiki_revision_monitor_article_results.packet_counts_json`
  - `wiki_revision_monitor_article_results.result_json`
  - `wiki_revision_monitor_candidate_pairs.score_json`
  - `wiki_revision_monitor_candidate_pairs.section_delta_json`
  - `wiki_revision_monitor_candidate_pairs.result_json`

## Promoted Slice

- bump the runner/state contract from `wiki_revision_pack_state_v0_3` to
  `wiki_revision_pack_state_v0_4`
- remove the placeholder-only columns from new-table creation in
  [revision_pack_runner.py](/home/c/Documents/code/ITIR-suite/SensibLaw/src/wiki_timeline/revision_pack_runner.py)
- keep insert statements column-scoped so older DBs with the extra columns
  remain writable and readable
- update focused tests to prove the v0.4 schema no longer creates those
  columns

## Acceptance

- new revision monitor DBs do not contain the dropped placeholder-only columns
- focused runner tests prove:
  - `summary_json` still exists and is populated
  - `graph_json` still exists and is populated
  - article-result and candidate-pair placeholder-only columns are absent in a
    fresh v0.4 DB
- query/read-model tests remain green

## Quality Gate

Run from `SensibLaw/`:

- `../.venv/bin/python -m pytest -q tests/test_revision_monitor_query.py tests/test_revision_monitor_read_models.py tests/test_wiki_revision_pack_runner.py`

## C4 / PlantUML

```plantuml
@startuml
title Wiki Revision Monitor v0.4 Placeholder Blob Drop

Component(runner, "revision_pack_runner.py", "Schema owner")
Database(v4db, "v0.4 SQLite schema", "No placeholder-only legacy blobs")
Database(v3db, "v0.3 SQLite schema", "Readable legacy DB with extra columns")
Component(query, "revision_monitor_query.py", "SQLite-first consumer")

Rel(runner, v4db, "creates/writes v0.4 schema")
Rel(runner, v3db, "still writes by named columns")
Rel(query, v4db, "reads canonical rows")
Rel(query, v3db, "reads compatible retained surfaces")

@enduml
```
