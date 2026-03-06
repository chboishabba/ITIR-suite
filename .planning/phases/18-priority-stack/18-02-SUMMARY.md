# Phase 18 Plan 02: Tokenizer Migration Summary

Deterministic tokenizer migration is promoted to canonical with persisted profile metadata and artifact rebuilds completed.

## Accomplishments

- Switched canonical default in `SensibLaw/src/text/lexeme_index.py` to `deterministic_legal`.
- Preserved legacy/rollback mode behind `ITIR_LEXEME_TOKENIZER_MODE=legacy_regex`.
- Rebuilt `SensibLaw/.cache_local/wiki_timeline_gwb.json` and `wiki_timeline_gwb_aoo.json` under deterministic canonical mode.
- Updated migration contract and status docs to reflect canonical promotion state.
- Expanded the deterministic lexer from span stability only into structural legal
  canonicalization (`act_ref`, `section_ref`, `article_ref`, `instrument_ref`,
  etc.) with no-regex parsing and explicit false-positive guards.
- Added a deterministic bridge layer so low-ambiguity institutions/courts link
  to Wikidata downstream while canonical lexer refs remain internal.
- Added benchmark/report follow-through:
  - structural legal-atom capture lane
  - linked-entity capture lane
  - canonical atom frequency report for DB normalization planning
- Added follow-through implementation:
  - canonical determiner normalization (`the ...`) for act/instrument refs
  - `VersionedStore` structural atom dictionary tables
  - bridge-to-external-refs batch emission for the existing ontology upsert path

## Files Created/Modified

- `SensibLaw/src/text/lexeme_index.py` - default canonical mode set to deterministic.
- `SensibLaw/src/ontology/entity_bridge.py` - deterministic seeded bridge from
  canonical refs to Wikidata IDs.
- `SensibLaw/src/wiki_timeline/sqlite_store.py` - root wiki-timeline DB now
  persists structural atom dictionaries/occurrences for high-yield canonical
  refs alongside normalized events.
- `SensibLaw/scripts/emit_bridge_external_refs_batch.py` - curated bridge batch
  emitter exercised end-to-end against `ontology external-refs-upsert`.
- `SensibLaw/src/ontology/entity_bridge.py` - DB-backed deterministic bridge
  substrate over `itir.sqlite` with seeded reviewed body/court slice and
  bridge-match receipts.
- `SensibLaw/data/ontology/wikidata_bridge_bodies_gwb_v1.json` - checked-in
  reviewed bridge slice for the current deterministic body/court set.
- `SensibLaw/docs/tokenizer_contract.md` - canonical stream description updated.
- `docs/planning/tokenizer_migration_plan_20260306.md` - execution status and checkpoint notes updated.
- `SensibLaw/todo.md` - migration milestone status updated.
- `checkpoints/page_20260304_214705/*` - pending parity capture refresh (not yet regenerated here).

## Decisions Made

- Canonical source-token stream decision: dedicated deterministic legal lexer
  (`deterministic_legal_v2`).
- Rollback strategy remains available: set `ITIR_LEXEME_TOKENIZER_MODE=legacy_regex`.
- Wikidata IDs are not canonical lexer identity; low-ambiguity refs are bridged
  downstream from internal canonical refs to external IDs.

## Issues Encountered

- Route-level byte-parity check for `/graphs/wiki-timeline*` initially blocked by local
  socket binding restrictions (`EPERM` for 127.0.0.1:4173).
- Resolved by offline extraction: checkpoint HTML payloads parsed and deterministic artifacts
  regenerated; hashes now match for all three routes (142 events each).

## Next Step

- Lock canonical tokenizer metadata to deterministic mode; retain legacy via env override.
- Keep offline payload extraction script (Node/vm) as the non-HTTP parity lane for future checkpoints.
- Normalize leading determiners in canonical act/instrument refs (`the ...`) so
  equivalent references collapse to one atom before DB atom-dictionary work. ✅
- Root-DB structural atom dictionary storage is now in place for the current
  high-yield kinds and includes `article_ref` / `instrument_ref` in addition to
  `case_ref`, `section_ref`, `subsection_ref`, `act_ref`, `paragraph_ref`,
  `institution_ref`, and `court_ref`.
- Bridge outputs now flow through the curated ontology external-ref substrate
  via emitted batches and the existing CLI upsert path; broader automatic
  persistence policy remains a separate design question, not an unimplemented
  blocker.
- Shared DB bridge management now exists via `ontology bridge-import` /
  `ontology bridge-report`; next follow-through is importing reviewed bridge
  slices for the remaining GWB U.S.-law bodies/courts that are lexically
  recognized but not yet seeded with pinned QIDs.
- Live `itir.sqlite` has now been backfilled through the new atom-persisting
  wiki timeline path; the current GWB route run reports `21` structural atom
  occurrences, `17` unique atoms, and `144` duplicate canonical bytes on the
  refreshed storage report.
- Canonical wiki-timeline storage has now moved off JSON-bearing list/tail
  rows for the route/report-critical path. Event fields, step fields, object
  resolver hints, and event/run list items persist through typed path/value
  tables instead, and the refreshed GWB storage report shows
  `residual_blob_bytes = 0`.
- Important scope clarification: this zero-residual push is about canonical
  product semantics, not about preserving arbitrary historical JSON export
  shapes losslessly inside the DB. If a field is not used by route/query/report
  behavior, it does not justify blob retention by itself.
- The eager rewrite into `.cache_local/itir.sqlite` was rerun after the
  zero-residual patch and now completes cleanly under foreign keys after
  replacing parent-run `INSERT OR REPLACE` writes with conflict updates and
  clearing legacy compatibility list rows during repersist.
- Live file sizes after the rewrite:
  - `.cache_local/itir.sqlite`: `9,605,120` bytes
  - backup `.cache_local/itir.sqlite.bak-pre-chat-20260306T163537Z`: `9,596,928` bytes
  - isolated `.cache_local/itir_chat_test.sqlite`: `552,960` bytes
- A bounded local chat-sample ingest path now exists for tokenizer/storage
  experiments only. It reads `~/chat_archive.sqlite`, stores hashed thread IDs
  plus minimal message fields into `.cache_local/itir_chat_test.sqlite`, and
  keeps chat-derived rows out of canonical `itir.sqlite`.
- Personal archive–derived test DBs are local-only and must never be promoted
  into canonical/shared repo artifacts. The isolated chat/Messenger test DBs
  exist only for local experiments and reporting.
- Chat-sample tokenizer/compression smoke pass on the isolated test DB:
  - messages: `100`
  - raw characters: `465,653`
  - tokens: `104,974`
  - avg chars/token: `4.4359`
  - avg tokens/message: `1049.74`
  - unique `(norm_text, kind)` pairs: `7,173`
  - reuse ratio: `0.9317`
  - structural tokens: `52`
- Richer chat structure breakdown:
  - token kinds: `word=62557`, `punct=31351`, `symbol=6143`, `number=4569`,
    `other=302`
  - structural kinds: `act_ref=36`, `section_ref=7`, `instrument_ref=6`,
    `part_ref=2`, `case_ref=1`
  - isolated chat DB structural atom dedupe: `52` occurrences, `44` unique atoms
- Relevant comparison points from existing deterministic corpus lanes:
  - GWB timeline prose: `4621` tokens at `5.04` chars/token
  - dense legal fixture bodies: `235395` tokens at `5.02` chars/token
  - mixed legal refs: `127` tokens at `6.79` chars/token
  - GWB reference snippets: `501` tokens at `5.83` chars/token
- Next scope now splits cleanly:
  - bridge expansion for the reviewed U.S. bodies/courts still missing from the
    live slice
  - structural-atom dedupe/storage reporting beyond wiki timeline
  - chat-ingest hardening with explicit retention/redaction metadata and richer
    kind-level reporting
  - first deterministic GWB U.S.-law linkage seed pack
- Bridge expansion progress this pass:
  - reviewed slice now includes `Department of Defense` (`Q11209`) and the
    `United States Court of Appeals for the Sixth Circuit` (`Q250472`)
  - live bridge import reports `12` entities and `49` aliases
- First deterministic GWB U.S.-law linkage starter pack is now checked in as
  `SensibLaw/data/ontology/gwb_us_law_linkage_seed_v1.json`.
- Structure reporting is no longer limited to legal `_ref` families. There is
  now a second deterministic operational/discourse lane covering:
  - chat/dialogue roles and speakers
  - shell/command blocks, flags, env vars, paths, code fences
  - transcript-style speaker/timestamp/QA/procedure markers
- The isolated chat report now answers the questions we actually needed:
  - what the structural atoms were
  - which atoms were most reused
  - which atoms were most interlinked/co-occurring
  - which atoms are likely more useful than junk according to a deterministic
    repeat/co-occurrence heuristic
- Updated isolated chat sample after operational false-positive tightening:
  - messages: `100`
  - raw characters: `465653`
  - token count: `107523`
  - structural token count: `2601`
  - unique structural atoms: `1027`
  - dominant kinds: `path_ref=777`, `message_boundary_ref=589`,
    `code_block_ref=508`, `timestamp_ref=351`, `task_ref=223`
  - legal kinds still present but much smaller: `act_ref=36`, `section_ref=7`,
    `instrument_ref=6`, `part_ref=2`, `case_ref=1`
- `SeaMeInIt/COMPACTIFIED_CONTEXT.md` and other large repo context files are
  now valid report inputs through the same corpus report path. Current context
  aggregate across `SeaMeInIt`, `StatiBaker`, `SensibLaw`, `__CONTEXT`, and
  `JesusCrust`:
  - units: `54`
  - raw chars: `48909`
  - tokens: `10729`
  - structural tokens: `352`
  - unique structural atoms: `316`
- Transcript input is now grounded in both a generic bracketed-message fixture
  and a real transcript-like sample under
  `/home/c/Documents/code/__OTHER/tirc_test_audio`.
- Transcript handling is now message/range aware:
  - one unit per bracketed/unbracketed speaker-timestamp message
  - one unit per subtitle-style timed utterance range
  - canonical range atoms like `tsrange:00_00_00_030__00_00_21_970`
- Side-by-side corpus comparison now exists through
  `report_structure_corpora.py --by-source`, so chat/context/transcript runs
  can be compared in one deterministic report.
