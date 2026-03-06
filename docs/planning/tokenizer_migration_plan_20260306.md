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
- canonical deterministic stream has since been expanded beyond v1 section spans:
  it now emits structural legal atoms for act/section/article/rule/schedule/etc.
  and seeded institution/court references, with explicit ambiguity guards.
- seeded institutional identity is now treated as a bridge:
  canonical lexer output stays internal/pre-semantic (`institution:*`, `court:*`)
  and a downstream deterministic bridge attaches Wikidata IDs for the low-ambiguity
  seed set.

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

Follow-through status (2026-03-07):
- Deterministic lexer upgraded to `deterministic_legal_v2` /
  `itir_legal_lexer_v2`.
- Cross-corpus benchmark now records:
  - structural legal-atom capture
  - linked-entity capture (via the bridge layer)
- Current benchmark signal:
  - GWB prose: deterministic legal-atom capture `1.0`, linked-entity capture `1.0`
  - mixed legal refs: deterministic legal-atom capture `0.8`, linked-entity capture `1.0`
  - GWB reference snippets: deterministic legal-atom capture `1.0`, linked-entity capture `1.0`
  - dense legal fixtures remain the main structural dedupe opportunity
    (`case_ref`, `section_ref`, `act_ref`, `paragraph_ref` dominate)
- Reference tokenizer/compression stats (deterministic lane):
  - GWB timeline prose: `4621` tokens, `5.04` chars/token, legal-atom capture `1.0`
  - dense legal fixture bodies: `235395` tokens, `5.02` chars/token, legal-atom capture `0.5`
  - mixed general + legal refs: `127` tokens, `6.79` chars/token, legal-atom capture `0.8`
  - GWB reference snippets: `501` tokens, `5.83` chars/token, legal-atom capture `1.0`
  - isolated chat sample (`.cache_local/itir_chat_test.sqlite`, `100` messages): `104974` tokens,
    `4.4359` chars/token, `7173` unique `(norm_text, kind)` pairs, reuse ratio `0.9317`,
    `52` structural tokens across `465653` raw characters
  - isolated chat sample richer kind breakdown:
    - `word=62557`, `punct=31351`, `symbol=6143`, `number=4569`, `other=302`
    - structural kinds: `act_ref=36`, `section_ref=7`, `instrument_ref=6`,
      `part_ref=2`, `case_ref=1`
    - persisted structural atom dedupe in the isolated chat DB:
      `52` occurrences, `44` unique atoms
- `legal_principles` timeline lane contains no meaningful structural legal refs,
  so deterministic and legacy remain identical there by design.
- Follow-through implementation now also includes:
  - leading-determiner normalization for canonical act/instrument refs
  - structural atom dictionary persistence in `VersionedStore`
  - a deterministic bridge batch emitter for the existing ontology
    external-ref upsert flow

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
- Cross-corpus benchmark should continue to demonstrate:
  - deterministic legal-atom capture above regex/spaCy baselines on legal/GWB lanes
  - linked-entity capture for the seeded bridge set without changing canonical
    lexeme identity
- Canonical lexeme identity must remain free of external IDs; Wikidata stays in
  the bridge/entity layer, not in tokenizer identity.
- Repeated structural atoms now have dedicated dictionary storage in both
  `VersionedStore` and the root wiki-timeline SQLite store for the current
  high-yield kinds (`case_ref`, `section_ref`, `subsection_ref`, `act_ref`,
  `paragraph_ref`, `article_ref`, `instrument_ref`, `institution_ref`,
  `court_ref`).
- External IDs remain outside lexeme identity and now flow through the curated
  bridge-batch -> `ontology external-refs-upsert` path with regression
  coverage.
- Canonical wiki-timeline storage no longer depends on JSON-bearing event/run
  list blobs for the current route/report path. Remaining route/query/report-
  critical tails are persisted through typed path/value rows, and the refreshed
  canonical GWB run now reports `residual_blob_bytes = 0` in
  `wiki_timeline_storage_report.py`.
- Lossless reconstruction of every prior JSON export shape is not itself a
  migration requirement. The requirement is preserving canonical product
  semantics from typed storage: route payloads, ordering, parity-critical
  fields, joins, and audit metadata.
- The eager rewrite/backfill command was rerun successfully against
  `.cache_local/itir.sqlite` after fixing parent-run upserts and compatibility
  cleanup for legacy list rows.
- A bounded chat-sample ingest path exists for tokenizer/storage experiments
  only: `SensibLaw/scripts/ingest_chat_sample_to_itir_test_db.py` reads the
  local chat archive and writes to isolated `.cache_local/itir_chat_test.sqlite`
  using hashed thread IDs, leaving canonical `itir.sqlite` untouched aside from
  an explicit pre-chat backup.
- Personal archive–derived test DBs are local-only artifacts. They must never
  be promoted into canonical/shared repo artifacts or checked-in storage. This
  includes isolated chat and Messenger/Facebook test DBs under `.cache_local/`.
- The isolated chat ingest path now persists explicit retention/redaction
  metadata (`source_namespace`, `source_class`, `retention_policy`,
  `redaction_policy`) and its own structural atom dictionary/occurrence tables.
- Reviewed bridge slice `seeded_body_refs_v1` now includes:
  - `institution:united_states_department_of_defense -> wikidata:Q11209`
  - `court:united_states_court_of_appeals_for_the_sixth_circuit -> wikidata:Q250472`
  - live shared DB bridge import now reports `12` entities and `49` aliases
- Initial deterministic GWB U.S.-law linkage seed is checked in at
  `SensibLaw/data/ontology/gwb_us_law_linkage_seed_v1.json`.
- Chat-sample structure reporting should not stop at `_ref` token counts. For
  chat-like corpora, track:
  - all token kinds
  - `_ref` structural kinds
  - top canonical structural atoms
  so prose-heavy samples are not misread as "structure-free" simply because
  legal refs are sparse.
- That richer reporting lane now exists. The isolated chat report now emits:
  - top reused structural atoms with counts and bounded examples
  - per-kind top atom tables
  - "useful" atom ranking based on repeat rate, cross-unit reuse, and
    co-occurrence degree
  - top interlinked atoms and top co-occurring atom pairs
- The second deterministic structure lane is now active for non-legal corpora:
  - chat/dialogue: `role_ref`, `speaker_ref`, `task_ref`,
    `message_boundary_ref`, `quote_block_ref`
  - shell/ops: `command_ref`, `flag_ref`, `path_ref`, `env_var_ref`,
    `code_block_ref`, `trace_ref`, `exit_code_ref`
  - transcript/hearing: `speaker_ref`, `timestamp_ref`, `qa_ref`,
    `procedure_ref`, `exhibit_ref`
- Current isolated chat sample after false-positive tightening:
  - messages: `100`
  - raw characters: `465653`
  - token count: `107523`
  - avg chars/token: `4.3307`
  - reuse ratio: `0.9241`
  - structural token count: `2601`
  - unique structural atoms: `1027`
  - dominant non-legal structure is now visible:
    - `path_ref=777`
    - `message_boundary_ref=589`
    - `code_block_ref=508`
    - `timestamp_ref=351`
    - `task_ref=223`
    - `quote_block_ref=66`
  - legal refs remain a minority but are still preserved:
    - `act_ref=36`, `section_ref=7`, `instrument_ref=6`, `part_ref=2`,
      `case_ref=1`
- Example high-yield chat atoms now surfaced by the report:
  - most reused/useful: `code:fenced_block`, `quote:markdown_block`,
    `task:1`, `task:2`, `task:3`, `task:4`
  - most reused/interlinked path/task structure:
    `path:chatgpt_com`, `path:e8_leech`, `path:dashi_sensiblaw`,
    `task:1 <-> task:2`, `task:1 <-> task:3`,
    `code:fenced_block <-> quote:markdown_block`
- `CONTEXT.md` / `COMPACTIFIED_CONTEXT.md` files are now valid first-class
  report inputs through `report_structure_corpora.py`, so repo context history
  can be analyzed the same way as chat DB samples. Current aggregate
  `COMPACTIFIED_CONTEXT.md` benchmark across `SeaMeInIt`, `StatiBaker`,
  `SensibLaw`, `__CONTEXT`, and `JesusCrust`:
  - units: `54`
  - raw characters: `48909`
  - token count: `10729`
  - structural token count: `352`
  - unique structural atoms: `316`
  - dominant kinds: `path_ref=284`, `message_boundary_ref=50`,
    `timestamp_ref=10`, `flag_ref=4`, `command_ref=2`, `env_var_ref=1`
  - top useful atoms include:
    `path:docs_planning_project_interfaces_md`, `flag:--view`,
    `ts:06:01:41`, `path:context_convo_ids_md`, `path:engine_profile`,
    `path:docs_planning_readme_md`
- Transcript coverage is no longer limited to the original in-repo fixture. The
  transcript lane now treats these as generic bracketed message transcripts,
  not app-specific exports. The report path also accepts real transcript-like
  files from
  `/home/c/Documents/code/__OTHER/tirc_test_audio`. A live sample run against
  `2025-12-10_10-14-32.txt` is now part of the side-by-side comparison lane.
- Generic bracketed timestamped-message handling now collapses duplicate
  time-only timestamp atoms when a full date-time atom is already present, and
  normalizes transcript timestamps to canonical forms like
  `ts:2021_01_01_10_00` and `ts:2026_03_05_20_50`.
- Transcript normalization now also recognizes subtitle-style timing ranges
  like `[00:00:00,030 -> 00:00:21,970]` and emits a single canonical
  `timestamp_range_ref` atom such as
  `tsrange:00_00_00_030__00_00_21_970`, which fits the same start/end interval
  semantics used in the bounded Wikidata qualifier-drift work (`P580` / `P582`
  start/end-style qualifiers, `P585` point-in-time qualifiers) without pulling
  the full Wikidata layer into transcript tokenization.
- Transcript file unitization is now transcript-aware rather than generic
  paragraph splitting:
  - bracketed/unbracketed timestamped speaker lines become one unit per message
  - subtitle-style range lines become one unit per timed utterance block
  - multiline continuations stay attached to their message/range header
- `report_structure_corpora.py` now supports `--by-source` to emit an overall
  summary plus per-source breakdowns for chat DB runs, context files, and
  transcript inputs in one deterministic report.

## Rollback Strategy
If parity fails:
- Keep regex canonical.
- Log diffs and identify tokenization edge cases.
- Revise tokenizer config and re-run parity checks.

## Tooling Notes
- Run extraction/hydration with the project venv to ensure parser lane consistency.
- Avoid introducing non-deterministic language model steps.
