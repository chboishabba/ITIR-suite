# Wiki Revision Monitor Query Component

Date: 2026-03-31

## Change Class

Standard change.

## Problem

The revision monitor already had a query CLI, but the pack/run/article read
model logic still lived inline in:

- `SensibLaw/scripts/query_wiki_revision_monitor.py`

That kept the lane queryable, but not through a reusable producer-owned Python
component.

## Requirement

Create one shared Python owner for revision monitor query/read-model assembly
so consumers can reuse pack/run/summary/graph queries without scraping the CLI
script.

## Component Boundary

Shared owner:

- `SensibLaw/src/wiki_timeline/revision_monitor_query.py`

Adopter:

- `SensibLaw/scripts/query_wiki_revision_monitor.py`

Promoted slice:

- repo-root resolution from the state DB
- pack registry normalization
- artifact-backed run discovery
- graph-summary fallback assembly
- selected run/article graph loading
- final query payload assembly

## Acceptance

- the CLI script imports the shared query owner
- focused query tests cover DB-backed and artifact-fallback paths
- the CLI stays a thin argparse/print wrapper

## Quality Gate

Run from `SensibLaw/`:

- `../.venv/bin/python -m pytest -q tests/test_revision_monitor_query.py`

## C4 / PlantUML

```plantuml
@startuml
title Wiki Revision Monitor Query Component

Component(cli, "query_wiki_revision_monitor.py", "CLI wrapper")
Component(query, "revision_monitor_query.py", "Query/read-model owner")
Component(db, "wiki_revision_harness.sqlite", "Revision monitor state store")
Component(artifacts, "demo/ingest/wiki_revision_monitor", "Artifact fallback store")

Rel(cli, query, "delegates query assembly")
Rel(query, db, "reads packs/runs/graphs")
Rel(query, artifacts, "reads fallback graph artifacts")

@enduml
```
