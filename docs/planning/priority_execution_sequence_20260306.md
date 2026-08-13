# Priority Execution Sequence (2026-03-06)

Status: execution in progress.

## Scope
Align priority execution for:
- Lexeme layer implementation (P0)
- Regex → deterministic tokenizer migration (core dependency)
- Compression engine/profile followthrough (P1)
- Wikidata control-plane projection (P2)
- GWB seed pipeline + AAO timeline stabilization (P3)

This plan aligns with:
- `TODO.md`
- `SensibLaw/docs/tokenizer_contract.md`
- `SensibLaw/docs/lexeme_layer.md`
- `docs/planning/compression_engine.md`
- `docs/planning/sl_lce_profile_followthrough_20260208.md`
- `SensibLaw/docs/wikidata_epistemic_projection_operator_spec_v0_1.md`
- `SensibLaw/docs/planning/wikidata_transition_plan_20260306.md`
- `docs/planning/wiki_ingest_fact_tree_gwb_20260210.md`
- `docs/planning/wiki_timeline_extraction_gwb_20260211.md`

## Dependency Map (High-Level)
1. **Lexeme layer (P0)** is a prerequisite for shared compression infrastructure.
2. **Tokenizer migration** depends on lexeme invariants and drives parity checks.
3. **Compression engine followthrough (P1)** depends on lexeme layer + tokenizer decision.
4. **Wikidata control-plane (P2)** is parallelizable but depends on a reproducible slice and operator spec.
5. **GWB/AAO (P3)** is a downstream substrate and also supplies parity fixtures for tokenizer migration.

## Execution Order (Recommended)
1. **P0: Lexeme layer tables + ingestion + tests**
   - Deliverable: lexeme tables populated on revision ingest.
2. **Tokenizer migration plan and decision**
   - Deliverable: chosen deterministic tokenizer + migration plan.
3. **Tokenizer migration execution**
   - Deliverable: deterministic token stream with parity checkpoints (see below).
4. **P1: Compression engine/profile followthrough**
   - Deliverable: engine metadata artifact + profile contracts + lint + tests.
5. **P2: Wikidata projection slice**
   - Deliverable: deterministic operator prototype + EII on a bounded slice.
6. **P3: GWB seed pipeline + AAO stabilization**
   - Deliverable: reproducible seed envelope + AAO artifact + stable UI routes.

## Blocking Decisions
- Canonical token stream: lexeme-derived vs dedicated tokenizer stream.
- Tokenizer replacement path: deterministic spaCy config vs ICU/UDPipe.

## Parity Checkpoints (Tokenizer Migration)
Tokenizer migration acceptance currently requires three explicit backtest lanes:

### 1. GWB route payload parity
- Byte-identical hydration payloads for:
  - `/graphs/wiki-timeline`
  - `/graphs/wiki-timeline-aoo`
  - `/graphs/wiki-timeline-aoo-all`

### 2. Existing SL ingest regression corpus
- Re-run ingest and regression checks for:
  - `Mabo [No 2]`
  - `House v The King`
  - `Plaintiff S157`
  - `Native Title (NSW) Act 1994`
- Migration does not pass if these fixtures introduce new `TextSpan` failures or canonical span drift.

### 3. StatiBaker reducer and UI invariants
- Shared canonical ID stability across SL and SB paths.
- No SB re-tokenization.
- Compress to expand invariant remains true.
- No summary injection / no re-segmentation.
- Context-bound rendering invariants remain true.
- Tool-use / chat-context metric stability holds against existing SB fixtures.

The migration plan is tracked in:
- `docs/planning/tokenizer_migration_plan_20260306.md`

## Minimal Executable Slices
### Wikidata
- Two dumps or two edit windows forming a reproducible input slice.
- Limit properties to `P31`/`P279` + a curated set from
  `SensibLaw/docs/wikidata_queries.md`.
- Output: deterministic projection + EII report.

### GWB / AAO
- Revision-locked Wikipedia snapshots under `SensibLaw/.cache_local/wiki_snapshots*`.
- Candidate extraction artifact: `SensibLaw/.cache_local/wiki_candidates_gwb.json`.
- Timeline artifacts:
  - `SensibLaw/.cache_local/wiki_timeline_gwb.json`
  - `SensibLaw/.cache_local/wiki_timeline_gwb_aoo.json`

### Existing SL legal ingest corpus
- Existing legal PDFs/artifacts centered on:
  - `Mabo [No 2]`
  - `House v The King`
  - `Plaintiff S157`
  - `Native Title (NSW) Act 1994`
- Use these as regression fixtures for token/span determinism and ingest stability.

### StatiBaker fixtures
- Use SB contracts and fixtures to validate reducer and UI invariants:
  - `__CONTEXT/sprints/stati_baker_sprints.md`
  - `__CONTEXT/sprints/stati_baker_sprints_4_6.md`
  - `__CONTEXT/sprints/stati_baker_sprints_7_9.md`
  - `docs/user_stories.md`
  - `docs/planning/ui_invariant_test_runner.md`
  - `StatiBaker/runs/2026-01-22/outputs/dashboard_all.json`

## Notes
- GWB/AAO artifacts are both downstream deliverables and parity fixtures for tokenizer migration.
- Existing SL ingest fixtures are the second migration signoff lane and should block promotion if they regress.
- StatiBaker reducer and UI invariants are the third migration signoff lane and
  should block promotion if canonical ID stability, no-retokenization, or
  context-bound rendering invariants regress.
- Compression engine followthrough should not proceed until the tokenizer decision is recorded.
