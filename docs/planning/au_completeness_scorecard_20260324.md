# AU Completeness Scorecard (2026-03-24)

## Purpose
Define the AU-side counterpart to the GWB completeness framing.

Companion index:
- `docs/planning/zelph_handoff_index_20260324.md`

Destination:
- complete AU/topic understanding for the chosen procedural/legal scope

Current checked artifact:
- one scored checkpoint built from the current real AU procedural workbench
  bundle

Role of this note:
- broader completeness/corpus-accounting note
- not the bounded handoff spec
- not the pack-definition doc

## Destination
For AU, the intended destination is:

- reviewed procedural/legal topic understanding over the chosen AU scope
- explicit actor, forum, authority, and action handling
- chronology-aware event grouping
- explicit review and contestation instead of fake closure
- downstream queryability over exported reviewed structure

## Current checked checkpoint
The current checked AU handoff artifact reports:

- 3 facts
- 27 observations
- 2 events
- 3 review queue items
- 1 contested item
- 2 approximate events
- 10 operator views
- Zelph engine status `ok`

Interpretation:
- strong enough to prove a real AU reviewed handoff path
- still a checkpoint, not full AU scope closure

Why this is not enough for corpus-level claims:
- the checked artifact is built from the current persisted fact-review
  workbench bundle, not from an exhaustive corpus-completeness report
- that workbench shape is aligned with the Mary-parity/operator-review goal:
  a reviewable, provenance-backed checkpoint with operator views, contestation,
  and chronology seams
- it should not be misread as saying "the AU corpus only yields 3 facts"
- if the underlying source family includes a long transcript or broader
  procedural corpus, the completeness target is necessarily larger than this
  handoff slice

## Checked slice vs broader AU completeness
The repo should now distinguish two AU layers explicitly.

### 1. Checked AU handoff slice
This is the current public-facing Zelph artifact:
- reviewed
- legible
- bounded
- safe to reason over downstream

Current implementation:
- `SensibLaw/tests/fixtures/zelph/au_public_handoff_v1/`
- built from
  `itir-svelte/tests/fixtures/fact_review_wave1_real_au_demo_bundle.json`

Use it to prove:
- the AU ingest -> review -> Zelph handoff path is real
- operator-facing Mary-parity review surfaces are real
- contestation and chronology can survive into a downstream-safe export

Do not use it to prove:
- full AU transcript/corpus coverage
- full event inventory
- full topic closure for any larger AU corpus

### 2. Broader AU corpus completeness target
This is the real destination if AU is meant to stand for a long transcript or
larger procedural corpus.

That broader target should be assessed against fuller source-derived surfaces,
for example:
- transcript-semantic runs
- transcript fact-review bundles
- WhisperX-derived transcript imports where available and reviewed
- wider Mary-parity wave material beyond the narrowed handoff bundle

The key question is:
- what fraction of the underlying AU corpus is represented as statements,
  observations, facts, events, contested items, and unresolved review lanes?

## Recommended broader AU scorecard additions
The current handoff scorecard is useful, but it is too narrow for corpus
completeness. Add:

- source family inventory
- corpus/source count
- source duration or document span where available
- statement count
- source-to-statement coverage notes
- event family diversity
- unresolved lane inventory
- handoff-slice-to-full-run ratio

## Current repo reading
The current checked AU artifact proves:
- Mary-parity-style operator review over real AU material is working
- the Zelph handoff shape is real

It does not yet prove:
- broad AU corpus understanding
- completeness over a long transcript or any larger AU corpus

## Scorecard dimensions
- fact count
- observation count
- event count
- review queue count
- contested item count
- approximate event count
- operator view count
- Zelph engine status

## Current implementation hook
Checked artifact directory:
- `SensibLaw/tests/fixtures/zelph/au_public_handoff_v1/`

Scorecard file:
- `SensibLaw/tests/fixtures/zelph/au_public_handoff_v1/au_public_handoff_v1.scorecard.json`

Near-term corpus-level companion artifact:
- `SensibLaw/tests/fixtures/zelph/au_corpus_scorecard_v1/`
- generated outputs:
  - `au_corpus_scorecard_v1.json`
  - `au_corpus_scorecard_v1.summary.md`

Broader diagnostics companion artifact:
- `SensibLaw/tests/fixtures/zelph/au_broader_corpus_diagnostics_v1/`
- generated outputs:
  - `au_broader_corpus_diagnostics_v1.json`
  - `au_broader_corpus_diagnostics_v1.summary.md`

Current generated checkpoint:
- 4 persisted real bundles counted
- 13 facts
- 40 observations
- 2 events
- 11 review queue items
- known raw transcript backlog still visible separately

Current generated diagnostics reading:
- the broader AU checkpoint now spans 2 workflow kinds:
  `au_semantic` and `transcript_semantic`
- 3 of the 4 persisted real bundles are transcript-semantic bundles
- the current highest review-pressure bundle is
  `wave5:real_transcript_false_coherence_v1`
- 4 raw transcript files remain visible as backlog rather than being silently
  treated as covered

Internal transcript-structure checkpoint:
- `SensibLaw/tests/fixtures/zelph/au_real_transcript_structural_checkpoint_v1/`
- generated outputs:
  - `au_real_transcript_structural_checkpoint_v1.json`
  - `au_real_transcript_structural_checkpoint_v1.summary.md`

Internal dense transcript substrate artifact:
- `SensibLaw/tests/fixtures/zelph/au_real_transcript_dense_substrate_v1/`
- generated outputs:
  - `au_real_transcript_dense_substrate_v1.json`
  - `au_real_transcript_dense_substrate_v1.summary.md`

Current generated transcript-structure reading:
- 2 real HCA transcript files are now promoted into a persisted structural/legal
  checkpoint
- current checkpoint covers:
  1747 transcript units,
  2224 structural/legal tokens,
  1348 unique structural atoms,
  and 12 selected high-signal excerpts
- this is not yet reviewed fact/event coverage
- it does, however, mean the raw HCA hearing lane is no longer only a counted
  backlog item

Current generated dense-substrate reading:
- 2 real HCA transcript files now also flow into a persisted dense transcript
  substrate artifact
- current dense artifact reports:
  1747 transcript units,
  1747 facts,
  1482 observations,
  0 events,
  and a 24-item secondary review-overlay projection
- this is the current repo-proof that transcript density is real at the
  substrate layer, while reviewed procedural/event coverage still lags behind

Command:
- `cd /home/c/Documents/code/ITIR-suite && python SensibLaw/scripts/build_au_corpus_scorecard.py`

Purpose of the corpus-level companion:
- aggregate the persisted real AU and transcript-adjacent workbench bundles
- make broader source-family coverage visible without pretending that the
  bounded AU handoff slice is corpus-complete
- record known raw source families that are present but not yet covered by the
  current real-bundle checkpoint

Purpose of the diagnostics companion:
- show where current AU review pressure is concentrated across real bundles
- make transcript-semantic coverage legible in the same repo surface as the AU
  procedural lane
- give AU a broader-corpus companion comparable in role to the GWB broader
  diagnostics artifact, while staying honest that the next real move is still
  more reviewed transcript promotion rather than more packaging

Purpose of the transcript-structure checkpoint:
- promote the real HCA hearing files into a persisted AU corpus artifact without
  pretending they are already reviewed fact coverage
- preserve legal/procedural structural signal from the actual transcript source
- make the next AU move narrower and clearer: convert more of that hearing lane
  from structural signal into reviewed fact/event coverage

Purpose of the dense transcript substrate artifact:
- make transcript-density itself first-class rather than treating it as a failed
  version of a narrow handoff
- keep the existing fact-review bundle as a smaller secondary overlay/projection
  rather than the primary AU transcript representation
- show exactly what is currently missing:
  event assembly and reviewed procedural promotion, not transcript-bearing
  statement/fact density
