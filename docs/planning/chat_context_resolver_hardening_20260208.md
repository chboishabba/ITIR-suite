# Chat Context Resolver Hardening (SQLite temp_store) (2026-02-08)

## Why this exists
While querying `chat-export-structurer/my_archive.sqlite` (large DB, FTS enabled),
we observed intermittent SQLite failures like:

- `Error: stepping, unable to open database file (14)`

This can happen when SQLite chooses to materialize intermediate results using
temporary files during query execution (sorting/grouping/FTS joins) and the
chosen temp-store path is not usable in the current runtime environment.

The resolver should be resilient to this because it is a *core context hygiene*
entrypoint used by `$robust-context-fetch`.

## Change (intended behavior)
All resolver DB connections should:

- be read-only (`mode=ro&immutable=1`)
- avoid temp-file dependence by preferring in-memory temp storage:
  - `PRAGMA temp_store=MEMORY`
- refuse writes defensively:
  - `PRAGMA query_only=ON`

This is not a semantic change to how matching works; it is a robustness change
to reduce “mysterious” failures during FTS candidate lookups and other queries.

## Scope / non-goals
- No schema changes.
- No changes to match priority (canonical_thread_id exact -> title exact ->
  title contains -> FTS candidates).
- No web fallback policy changes.

