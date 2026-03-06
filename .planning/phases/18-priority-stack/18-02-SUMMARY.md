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
- Design root-DB structural atom dictionary storage around the high-yield kinds:
  `case_ref`, `section_ref`, `subsection_ref`, `act_ref`, `paragraph_ref`, plus
  `institution_ref`/`court_ref`. Baseline implemented in `VersionedStore`; root
  DB follow-through still pending.
- Connect bridge outputs into the ontology external-ref substrate via curated
  batch emission; direct root-DB persistence remains follow-up work.
