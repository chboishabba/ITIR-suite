# Wiki Revision Monitor Schema Contraction Plan

Date: 2026-03-31

## Change Class

Standard change.

## Problem

The wiki revision monitor lane is now operationally SQLite-first, but its DB
schema still contains legacy blob columns from the earlier artifact-centric
phase. Without a versioned contraction plan, those columns risk lingering
indefinitely or being removed unsafely.

## Requirement

- Define the schema transition from SQLite-first with backcompat blobs toward a
  stricter canonical SQLite store.
- Separate safe in-repo deprecation from still-unproven external-consumer
  compatibility.
- Make the next schema cut governable by version rather than by ad hoc cleanup.

## Current State

Version posture as of this note:

- current runner/report schema family:
  - `wiki_revision_pack_state_v0_3`
- current graph artifact schema family:
  - `wiki_contested_region_graph_v0_1`
- current pair report schema family:
  - `wiki_revision_pair_report_v0_1`

Operationally canonical:

- SQLite read-model tables in
  [revision_monitor_read_models.py](/home/c/Documents/code/ITIR-suite/SensibLaw/src/wiki_timeline/revision_monitor_read_models.py)

Bounded backcompat:

- `wiki_revision_monitor_runs.summary_json`
- `wiki_revision_monitor_contested_graphs.graph_json`

Placeholder-only legacy columns:

- `wiki_revision_monitor_article_results.packet_counts_json`
- `wiki_revision_monitor_article_results.result_json`
- `wiki_revision_monitor_candidate_pairs.score_json`
- `wiki_revision_monitor_candidate_pairs.section_delta_json`
- `wiki_revision_monitor_candidate_pairs.result_json`

## Repo-Local Consumer Audit

Repo-local audit result:

- no in-repo operational readers remain for the placeholder-only legacy blob
  columns above
- `summary_json` is still read by
  [revision_monitor_query.py](/home/c/Documents/code/ITIR-suite/SensibLaw/src/wiki_timeline/revision_monitor_query.py)
  as a bounded DB fallback
- `graph_json` remains in the contested graph table as bounded DB backcompat,
  even though the normal graph query path now hydrates from explicit SQLite
  graph rows

Known repo-local consumers to preserve during contraction:

- [query_wiki_revision_monitor.py](/home/c/Documents/code/ITIR-suite/SensibLaw/scripts/query_wiki_revision_monitor.py)
- [wikiRevisionMonitor.ts](/home/c/Documents/code/ITIR-suite/itir-svelte/src/lib/server/wikiRevisionMonitor.ts)
- light DB-count inspection in [check_recent_pages.py](/home/c/Documents/code/ITIR-suite/scripts/check_recent_pages.py)

## Versioned Plan

### v0.3 current

- SQLite-first operational reads
- `summary_json` and `graph_json` retained as bounded backcompat writes
- placeholder-only writes for the remaining legacy operational blobs

### v0.4 next schema cut

Precondition:

- complete explicit external-consumer audit for any tooling outside this repo
  that still inspects:
  - `wiki_revision_monitor_article_results.packet_counts_json`
  - `wiki_revision_monitor_article_results.result_json`
  - `wiki_revision_monitor_candidate_pairs.score_json`
  - `wiki_revision_monitor_candidate_pairs.section_delta_json`
  - `wiki_revision_monitor_candidate_pairs.result_json`

Promoted change:

- remove the placeholder-only legacy columns above from the schema
- keep `summary_json` and `graph_json` intact as bounded backcompat
- bump the runner/state contract to `wiki_revision_pack_state_v0_4`

### v0.5 later cut

Precondition:

- no remaining consumer depends on DB fallback for run summary
- no remaining consumer depends on DB fallback for selected graph payload
- query layer can rely on SQLite read models and artifact fallback only, or on
  SQLite read models alone if artifact fallback is also retired

Promoted change:

- remove `wiki_revision_monitor_runs.summary_json`
- remove `wiki_revision_monitor_contested_graphs.graph_json`
- bump the runner/state contract to `wiki_revision_pack_state_v0_5`

## Governance

- Do not drop any column before the corresponding consumer audit is complete.
- Keep tests proving SQLite-first precedence green at every stage.
- Treat file artifacts as exports, not as canonical operational state.
- Preserve the dedicated revision-monitor SQLite posture until a broader
  single-store migration is explicitly planned and governed.

## Acceptance

- the schema contraction path is versioned and explicit
- placeholder-only legacy blob columns are identified as the next drop set
- `summary_json` and `graph_json` have separate, stricter removal conditions

## Quality Gate

Run from `SensibLaw/`:

- `../.venv/bin/python -m pytest -q tests/test_revision_monitor_query.py tests/test_revision_monitor_read_models.py tests/test_wiki_revision_pack_runner.py`

## C4 / PlantUML

```plantuml
@startuml
title Wiki Revision Monitor Schema Contraction Plan

Database(sqlite, "Revision monitor SQLite", "Canonical operational store")
Component(readModels, "read-model tables", "Operational query contract")
Component(backcompat, "summary_json / graph_json", "Bounded fallback")
Component(legacy, "placeholder-only blob columns", "v0.4 drop set")
Component(consumers, "CLI + Svelte adapter", "Current consumers")

Rel(consumers, readModels, "preferred reads")
Rel(consumers, backcompat, "bounded fallback reads")
Rel(sqlite, legacy, "temporary compatibility residue")
Rel(sqlite, backcompat, "temporary bounded fallback")
Rel(sqlite, readModels, "canonical rows")

@enduml
```
