# Phase 18 Plan 02: Tokenizer Migration Summary

Deterministic tokenizer migration is promoted to canonical with persisted profile metadata and artifact rebuilds completed.

## Accomplishments

- Switched canonical default in `SensibLaw/src/text/lexeme_index.py` to `deterministic_legal`.
- Preserved legacy/rollback mode behind `ITIR_LEXEME_TOKENIZER_MODE=legacy_regex`.
- Rebuilt `SensibLaw/.cache_local/wiki_timeline_gwb.json` and `wiki_timeline_gwb_aoo.json` under deterministic canonical mode.
- Updated migration contract and status docs to reflect canonical promotion state.

## Files Created/Modified

- `SensibLaw/src/text/lexeme_index.py` - default canonical mode set to deterministic.
- `SensibLaw/docs/tokenizer_contract.md` - canonical stream description updated.
- `docs/planning/tokenizer_migration_plan_20260306.md` - execution status and checkpoint notes updated.
- `SensibLaw/todo.md` - migration milestone status updated.
- `checkpoints/page_20260304_214705/*` - pending parity capture refresh (not yet regenerated here).

## Decisions Made

- Canonical source-token stream decision: dedicated deterministic legal lexer
  (`deterministic_legal_v1`).
- Rollback strategy remains available: set `ITIR_LEXEME_TOKENIZER_MODE=legacy_regex`.

## Issues Encountered

- Route-level byte-parity check for `/graphs/wiki-timeline*` initially blocked by local
  socket binding restrictions (`EPERM` for 127.0.0.1:4173).
- Resolved by offline extraction: checkpoint HTML payloads parsed and deterministic artifacts
  regenerated; hashes now match for all three routes (142 events each).

## Next Step

- Lock canonical tokenizer metadata to deterministic mode; retain legacy via env override.
- Keep offline payload extraction script (Node/vm) as the non-HTTP parity lane for future checkpoints.
