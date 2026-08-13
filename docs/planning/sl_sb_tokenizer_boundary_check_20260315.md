# SL docs/capability check and SB tokenizer boundary start (2026-03-15)

## Scope
- Check recent SL capability direction and implications for SB.
- Update SB user stories for SL users.
- Start a concrete SB-side tokenizer boundary audit.

## SL capability check (latest planning inputs)
- `docs/planning/sl_whitepaper_followthrough_20260314.md`
  - SL keeps a richer event/observation/provenance core; RDF/Wikidata remains an adapter boundary.
  - Priority is the case-construction chain:
    `source/excerpt -> observation -> event/fact -> norm -> claim`.
  - Reasoning is framed as guarded state transitions with receipts.
- `docs/planning/mary_parity_roadmap_20260315.md`
  - Near-term pressure is practical parity on fact-review utility.
  - Role-shaped user outcomes are primary acceptance pressure.
- `docs/planning/tokenizer_migration_plan_20260306.md`
  - Canonical tokenizer mode is deterministic (`deterministic_legal`).
  - Explicit SB requirement: no SB re-tokenization for canonical identity.
  - SB token/context metrics are allowed only as bounded non-canonical diagnostics.

## User-story update completed
- Updated `StatiBaker/docs/user_stories.md` with:
  - `SB-SL-US-01` matter chronology lane for SL review
  - `SB-SL-US-02` claim/evidence seam visibility
  - `SB-SL-US-03` context-bound SB->SL handoff
  - `SB-SL-US-04` tokenizer boundary discipline

## SB tokenizer boundary audit (initial findings)

### Confirmed non-canonical token usage in SB
- `StatiBaker/sb/dashboard.py`
  - chat token counts are explicitly estimated via char heuristic:
    `max(1, round(chars/4.0))`
  - these are used for cost/context-overflow estimates.
- `StatiBaker/docs/api_costing_model.md`
  - documents the same char-based estimation model as approximate.
- `StatiBaker/sb/activity/sessionize.py`
  - local title tokenization is used for title drift Jaccard in activity
    sessionization.

### No direct evidence yet of SB creating a canonical SL token stream
- No SB import/use of `SensibLaw/src/text/deterministic_legal_tokenizer.py`.
- No SB import/use of `collect_lexeme_occurrences*` from SL lexeme index.
- Existing SB tokenization appears diagnostic/sessionization-only, not canonical
  identity generation.

## Risks to close next
- Implicit drift risk: any future SB metric lane that starts treating
  char-based token estimates as authoritative for SL-origin content.
- Interface ambiguity: SB docs should continue to mark token estimates as
  non-canonical, SL-identity-independent diagnostics.
- Regression risk: no automated guard currently proving "SB does not
  re-tokenize SL canonical text for identity."

## Next checks queued
1. Add an integration guard test in SB proving no import path to SL canonical
   tokenizer/lexeme canonicalization for identity logic.
2. Add an interface contract assertion: token metrics in SB are explicitly
   diagnostic-only and cannot affect canonical IDs/provenance.
3. Add a fixture-based SL->SB->SL roundtrip check for ID stability at the
   boundary (reference IDs unchanged; no synthetic token IDs introduced by SB).
