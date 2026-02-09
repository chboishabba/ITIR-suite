# Schema Chat Thread Map (for docs updates) (2026-02-08)

This file records which archived ChatGPT threads contain *schema-relevant* decisions
so we can cite them when updating repo docs (without guessing from memory).

Resolver entrypoint (DB-first):
`scripts/chat_context_resolver.py`

Note: the archive is message-centric (`messages` + `messages_fts`) rather than a
separate `threads` table. When doing ad-hoc SQL, set:
`PRAGMA temp_store=MEMORY;` to avoid temp-file `SQLITE_CANTOPEN` failures.

## High-signal threads (confirmed)

### 1) Ontology DB: table/column inventory as CSV
- Title: `Data management ontology topology`
- canonical_thread_id: `331a7d1304f329259315649e7a9d729a83b51daf`
- Why it matters:
  - Contains an explicit table/column inventory as CSV plus sample rows (useful
    for cross-checking migrations/docs, and for onboarding).
- Docs it should support:
  - `SensibLaw/docs/sqlite_migrations.md`
  - `SensibLaw/docs/ontology.md`
  - `SensibLaw/docs/ontology_er.md`

### 2) SL ingest DB schema optimization guidance (rule atoms/elements/lints)
- Title: `Schema optimisation advice`
- canonical_thread_id: `fab9d17befe44bba3931944d5af9d1d458d27e76`
- Why it matters:
  - Contains concrete DB normalization advice (dedupe text, hash-keyed tables,
    reference tables, composite key consistency).
- Docs it should support:
  - `SensibLaw/DATABASE.md` (ingest DB)
  - `SensibLaw/docs/schema.md` (Document model) only if we explicitly connect
    storage layout vs serialized schema (avoid mixing concerns).

### 3) Structural vs interpretive layer separation (SL vs ITIR vs TiRC)
- Title: `Branch · Cross-comparison of SL ITIR TIRC`
- canonical_thread_id: `0baa733624372fdcdf4c7e624a5b0401a38a3fe7`
- Why it matters:
  - Enumerates the separation guarantees and which docs are “frozen” (structural
    logic vs interpretive overlay).
- Docs it should support:
  - `SensibLaw/docs/itir_vs_sl.md`
  - `docs/planning/project_interfaces.md` (suite boundaries)

### 4) Actor-related schema design context (DB + governance)
- Title: `Actor table design`
- canonical_thread_id: `21f55daa80206517e38f8c0fa56ee9bb2db8a9a0`
- Why it matters:
  - Not strictly “actors table DDL” in the latest message, but it is the best
    thread-id anchor we’ve seen for actor schema discussion and boundaries.
- Docs it should support:
  - `SensibLaw/docs/external_ontologies.md` (external actor refs)
  - `SensibLaw/docs/ONTOLOGY_EXTERNAL_REFS.md`

## Notes / pitfalls observed

- Keyword queries like `"schema"` work well when the thread has a titled anchor.
  Queries like `"sqlite migrations"` often return FTS candidates dominated by
  untitled tool-heavy threads; prefer:
  1) a known titled anchor (e.g., “ontology topology”), or
  2) a follow-up SQL query to locate threads by title/text patterns, then fetch
     by canonical_thread_id.

