# SQLite Runtime Substrate

## Purpose

Normalize shared SQLite path resolution and connection plumbing so query and
read-only runtime callers stop re-implementing the same defaults.

## Scope

- `SensibLaw/src/storage/sqlite_runtime.py`
- first adopters:
  - `SensibLaw/src/wiki_timeline/query_runtime.py`
  - `SensibLaw/scripts/query_wiki_timeline_aoo_db.py`
  - `SensibLaw/scripts/query_fact_review.py`

## Boundary

- in scope:
  - repo-relative SQLite path resolution
  - environment fallback resolution
  - read-only and normal SQLite connect helpers
  - row factory setup
- out of scope:
  - schema creation
  - migrations
  - write-path semantics
  - lane-specific query selection policy

## Acceptance

- the first adopters preserve their current query results
- read-only callers keep the same resolved DB behavior
- write-capable callers remain writable by default
- tests cover both explicit path resolution and connection behavior

