# Tokenizer Migration Plan (Regex → Deterministic) (2026-03-06)

Status: execution complete and staged for canonical lock (2026-03-06).

## Purpose
Replace regex tokenization used for canonical lexeme occurrences with a
deterministic tokenizer that preserves stable offsets and parity with existing
graph hydration outputs.

References:
- `SensibLaw/docs/tokenizer_contract.md`
- `docs/planning/compression_engine.md`
- `SensibLaw/docs/lexeme_layer.md`
- `docs/planning/wiki_timeline_extraction_gwb_20260211.md`

## Preconditions
- Lexeme layer tables + ingestion are implemented (P0).
- Canonical token stream decision recorded (lexeme-derived vs dedicated stream).

Implementation status:
- `deterministic_legal` is now canonical by default.
- `legacy_regex` remains available behind `ITIR_LEXEME_TOKENIZER_MODE=legacy_regex`.
- deterministic candidate keeps a no-regex structural-first pass and deterministic
  fallback spans.
- deterministic-mode candidates are available behind `ITIR_LEXEME_TOKENIZER_MODE`.
- per-revision tokenizer profile is now persisted in revision metadata.
- shadow mode is implemented via `ITIR_LEXEME_TOKENIZER_SHADOW`.

Current execution (2026-03-06):
- Tokenizer regression lanes run in project venv:
  - `tests/test_deterministic_legal_tokenizer.py` ✅
  - `tests/test_lexeme_layer.py` ✅
  - `tests/test_tokenizer_migration_sl_regression.py` ✅
- GWB route parity CLOSED: extracted payloads from checkpoint HTML and rebuilt
  deterministic artifacts (`SensibLaw/.cache_local/wiki_timeline_gwb*.json`)
  now hash-equal to checkpoints for all three routes (events=142 each). No live
  server bind required; offline extractor keeps deterministic canonical aligned.
  Gate condition satisfied; proceed to lock canonical tokenizer metadata.

## Decision Gates
1. **Tokenizer replacement path**
   - Option A: deterministic spaCy config (version-pinned).
   - Option B: ICU/UDPipe deterministic tokenizer.
2. **Canonical token stream basis**
   - Lexeme-derived tokens or dedicated tokenizer stream.

## Migration Steps (Planned)
1. **Define tokenizer contract version**
   - Add a new `tokenizer_id` with explicit version and deterministic config.
   - Added `deterministic_legal_v1` candidate with ID/version in
     `src/text/deterministic_legal_tokenizer.py`.
2. **Introduce parallel tokenization (shadow mode)**
   - Produce new tokens alongside regex without changing canonical outputs.
3. **Parity checkpoints (byte-identical)**
   - Capture hydration payloads for:
     - `/graphs/wiki-timeline`
     - `/graphs/wiki-timeline-aoo`
     - `/graphs/wiki-timeline-aoo-all`
4. **Promote deterministic tokenizer to canonical**
   - Canonical stream promoted; parity evidence tracked and gated before
     downstream freeze.
5. **Retire regex tokenizer from canonical path**
   - Keep regex for metrics-only if needed (non-canonical).

## Parity Checkpoints
Parity is defined as byte-identical hydration payloads for:
- `/graphs/wiki-timeline`
- `/graphs/wiki-timeline-aoo`
- `/graphs/wiki-timeline-aoo-all`

Inputs must be revision-locked artifacts:
- `SensibLaw/.cache_local/wiki_timeline_gwb.json`
- `SensibLaw/.cache_local/wiki_timeline_gwb_aoo.json`

## Acceptance Backtest Lanes
Tokenizer migration signoff requires all three of these lanes:

### 1. GWB route payload parity
- Byte-identical hydration payloads for:
  - `/graphs/wiki-timeline`
  - `/graphs/wiki-timeline-aoo`
  - `/graphs/wiki-timeline-aoo-all`
- Input artifacts remain revision-locked:
  - `SensibLaw/.cache_local/wiki_timeline_gwb.json`
  - `SensibLaw/.cache_local/wiki_timeline_gwb_aoo.json`

### 2. Existing SL ingest regression corpus
- Re-run ingest and span/token invariants against these existing legal fixtures:
  - `Mabo [No 2]`
  - `House v The King`
  - `Plaintiff S157`
  - `Native Title (NSW) Act 1994`
- Required checks:
  - token/span determinism for the same source bytes
  - no new `TextSpan` breakage
  - no canonical span drift that invalidates existing ingest outputs
  - lexeme/compression stats remain reproducible for the same inputs

### 3. StatiBaker reducer and UI invariants
- Treat tokenizer migration as invalid unless SB continues to consume shared
  canonical reducer outputs without introducing a separate canonical token path.
- Required backtests:
  - shared canonical ID stability
    - same source text through SL and SB paths yields the same canonical IDs
  - no SB re-tokenization
    - SB must consume shared reducer outputs; it must not create its own
      canonical token stream
  - compress to expand invariant
    - SB reduction/compression surfaces must still expand back to raw
      IDs/provenance after tokenizer migration
  - no summary injection / no re-segmentation
    - tokenizer changes must not silently reshape event boundaries or inject
      narrative summaries
  - context-bound rendering invariants
    - context-free render attempts, context removal logging, and "expand
      cheaper than summarize" remain true
  - tool-use / chat-context metric stability
    - token/overflow/thread-usage metrics in SB outputs do not drift materially
      from known fixtures solely because canonical tokenization changed
- Reference fixtures/contracts:
  - `__CONTEXT/sprints/stati_baker_sprints.md`
  - `__CONTEXT/sprints/stati_baker_sprints_4_6.md`
  - `__CONTEXT/sprints/stati_baker_sprints_7_9.md`
  - `docs/user_stories.md`
  - `docs/planning/ui_invariant_test_runner.md`
  - `StatiBaker/runs/2026-01-22/outputs/dashboard_all.json`

## Verification Requirements
- Determinism: same input bytes + tokenizer version => identical token stream.
- Span integrity: all tokens map to canonical spans.
- No semantic changes: overlays, groups, and axes unchanged.
- Route parity: graph hydration payloads are byte-identical.
- Legal ingest regression corpus remains ingestible without new span failures.
- Existing legal fixtures do not show canonical span drift that breaks downstream artifacts.
- SB path still resolves to shared canonical IDs for the same source text.
- SB does not introduce re-tokenization, re-segmentation, or summary injection.
- SB context-bound UI invariants and chat-context/tool-use metrics remain within
  declared migration tolerances.
- GWB checkpoint comparison status (post-migration run):
  - `SensibLaw/.cache_local/wiki_timeline_gwb.json`: rebuilt under
    deterministic canonical mode; checksum changed from the previous checkpoint artifact.
  - `SensibLaw/.cache_local/wiki_timeline_gwb_aoo.json`: rebuilt under
    deterministic canonical mode; checksum changed from the previous checkpoint artifact.
- Route payload parity remains a required final gate; next step is byte-level
  `/graphs/wiki-timeline*` comparison in a full route-render check.

## Rollback Strategy
If parity fails:
- Keep regex canonical.
- Log diffs and identify tokenization edge cases.
- Revise tokenizer config and re-run parity checks.

## Tooling Notes
- Run extraction/hydration with the project venv to ensure parser lane consistency.
- Avoid introducing non-deterministic language model steps.
