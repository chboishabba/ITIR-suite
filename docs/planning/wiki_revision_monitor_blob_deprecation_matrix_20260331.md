# Wiki Revision Monitor Blob Deprecation Matrix

Date: 2026-03-31

## Change Class

Standard change.

## Problem

The wiki revision monitor lane is now SQLite-first for its main query surfaces,
but the runner still writes several legacy blob columns as if they were part of
the operational contract. That keeps unnecessary duplicated payloads alive and
blurs which surfaces are canonical versus backcompat.

## Requirement

- Keep SQLite read-model tables as the canonical operational store.
- Keep only the minimum legacy blob fields needed for bounded backcompat and
  export behavior.
- Make deprecation status explicit before any schema drop.

## Consumer Audit

Repo-local audit result for the revision monitor lane:

- `summary_json`
  - still read in `revision_monitor_query.py` as a bounded DB fallback when
    SQLite run-summary / changed-article read models are absent
  - retain as backcompat for now
- `graph_json`
  - no longer used by the normal query path once contested graph read models
    exist
  - retain as bounded DB backcompat for now because the schema still exposes it
    and selected graph fallback remains policy-sensitive
- `packet_counts_json`
  - no repo-local readers remain
  - safe to downgrade to compact placeholder writes
- `result_json` on `wiki_revision_monitor_article_results`
  - no repo-local readers remain
  - safe to downgrade to compact placeholder writes
- `score_json`
  - no repo-local readers remain
  - safe to downgrade to compact placeholder writes
- `section_delta_json`
  - no repo-local readers remain
  - safe to downgrade to compact placeholder writes
- `result_json` on `wiki_revision_monitor_candidate_pairs`
  - no repo-local readers remain
  - safe to downgrade to compact placeholder writes

## Deprecation Matrix

Retain full write for bounded backcompat:

- `wiki_revision_monitor_runs.summary_json`
- `wiki_revision_monitor_contested_graphs.graph_json`

Retain column but downgrade writes to compact placeholders:

- `wiki_revision_monitor_article_results.packet_counts_json`
- `wiki_revision_monitor_article_results.result_json`
- `wiki_revision_monitor_candidate_pairs.score_json`
- `wiki_revision_monitor_candidate_pairs.section_delta_json`
- `wiki_revision_monitor_candidate_pairs.result_json`

Future schema-drop candidates after external consumer audit:

- all compact-placeholder blob columns above
- `graph_json` after graph DB fallback is no longer required
- `summary_json` after summary DB fallback is no longer required

## Promoted Slice

- document the blob deprecation matrix
- keep `summary_json` and `graph_json` as the only full backcompat writes
- switch unused operational blob writes to explicit compact placeholders
- add focused tests proving the retained-vs-placeholder split

## Acceptance

- docs identify which legacy blob columns are:
  - canonical no longer
  - retained for bounded backcompat
  - downgraded to compact placeholders
  - later schema-drop candidates
- focused runner tests prove:
  - `summary_json` is still populated
  - `graph_json` is still populated
  - deprecated operational blob columns are written as compact placeholders

## Quality Gate

Run from `SensibLaw/`:

- `../.venv/bin/python -m pytest -q tests/test_revision_monitor_query.py tests/test_revision_monitor_read_models.py tests/test_wiki_revision_pack_runner.py`

## C4 / PlantUML

```plantuml
@startuml
title Wiki Revision Monitor Blob Deprecation Matrix

Database(sqlite, "SQLite read models", "Canonical operational store")
Component(runner, "revision_pack_runner.py", "Producer")
Component(summaryBlob, "summary_json / graph_json", "Bounded backcompat")
Component(legacyBlob, "other legacy blob columns", "Placeholder-only until drop")
Component(query, "revision_monitor_query.py", "SQLite-first query owner")

Rel(runner, sqlite, "writes canonical operational rows")
Rel(runner, summaryBlob, "retains bounded full backcompat writes")
Rel(runner, legacyBlob, "writes compact placeholders only")
Rel(query, sqlite, "prefers canonical reads")
Rel(query, summaryBlob, "uses only as explicit fallback")

@enduml
```
