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
- corpus-to-affidavit coverage accounting over a legal work product

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

Checked AU affidavit-coverage artifact:
- `SensibLaw/tests/fixtures/zelph/au_affidavit_coverage_review_v1/`
- generated outputs:
  - `affidavit_coverage_review_v1.json`
  - `affidavit_coverage_review_v1.summary.md`

Checked AU dense affidavit-coverage artifact:
- `SensibLaw/tests/fixtures/zelph/au_dense_affidavit_coverage_review_v1/`
- generated outputs:
  - `affidavit_coverage_review_v1.json`
  - `affidavit_coverage_review_v1.summary.md`

Current generated affidavit-coverage reading:
- first bounded source-to-draft comparison now exists for AU
- source side is the checked `au_public_handoff_v1` slice
- current checked artifact lands as:
  - `1` covered affidavit proposition
  - `2` unsupported affidavit propositions
  - `2` missing-review source rows
- the contract can also emit:
  `partial`, `contested_source`, and `abstained_source`
- this is still a bounded filing-support checkpoint, not full corpus-to-filing
  closure

Current generated dense affidavit-coverage reading:
- first broader AU source-to-draft comparison now also exists over the 24-row
  dense overlay projection from the real transcript substrate artifact
- this makes corpus-side review pressure more visible than the 3-fact checked
  handoff slice
- current checked dense artifact lands as:
  - `2` partial affidavit propositions
  - `1` unsupported affidavit proposition
  - `22` missing-review source rows
- current checked dense artifact remains conservative and omission-heavy by
  design; it proves comparison/accounting over a larger AU source surface, not
  full filing parity

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
  a first classified hearing-act layer,
  a first assembled procedural-move layer,
  a first conservative hearing-event assembly layer,
  and a reviewed hearing-event projection that is limited by
  `reviewed_event_limit` (default 12), currently 24 selected rows in the
  `/tmp/au_real_round2_v2` run with `--reviewed-event-limit 24`
- this is the current repo-proof that transcript density is real at the
  substrate layer, while reviewed procedural/event coverage still lags behind
  but is no longer just a flat procedural-candidate list

### 24 reviewed-item projection quality pass

Run command:
- `cd /home/c/Documents/code/ITIR-suite && python SensibLaw/scripts/build_au_transcript_dense_substrate.py --output-dir /tmp/au_real_round2_v2 --progress --progress-format json --reviewed-event-limit 24`

Observed outcomes:
- reviewed-event coverage ratio: `0.104751` (183 review-queue links / 1747 candidates)
- selected reviewed hearing events: `24`
- reviewed hearing-event candidates: `583`
- reviewed hearing-event exclusions: `0`
- selected reviewed hearing-event rows in overlay: `24`

Quality assessment:
- Precision: Moderate, useful for operator triage and review pressure, but not yet
  review-complete.
- Source anchoring: Good; rows remain linked to transcript moves and review items.
- Review-readiness: Low-to-moderate. Frequent reasons include
  `unreviewed`, `event_missing`, `chronology_undated`, `missing_actor`,
  `missing_date`, `statement_only_fact`.
- Chunk quality: Mixed; some excerpts are clean, several are truncated or
  boundary-fragmented.
- False-positive risk: Non-trivial without stronger actor/date/chronology gating.

Decision:
- treat this 24-row output as a high-coverage, low-trust operator queue today;
  not as accepted reviewed facts.
- next direction is quality-first filtering (speaker/actor continuity, chronology,
  truncation guardrails, and explicit event-production readiness) before further
  coverage-raise attempts.

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

## Next AU operator lane beyond dense substrate

The next AU legal-operator lane should now be stated explicitly:
- use the dense transcript/source substrate plus persisted fact-review runs as
  the source side for a later affidavit/declaration coverage review surface
- do not collapse this into the claim that the current 24-row reviewed queue is
  already affidavit-ready
- keep the distinction clear between:
  - dense source-grounded coverage
  - reviewed procedural/event coverage
  - affidavit proposition extraction
  - coverage/omission review

This is the point where AU stops being only a transcript-density proof and
starts becoming a filing-support proof surface.

Purpose of the dense transcript substrate artifact:
- make transcript-density itself first-class rather than treating it as a failed
  version of a narrow handoff
- keep the existing fact-review bundle as a smaller secondary overlay/projection
  rather than the primary AU transcript representation
- add a first hearing-understanding layer over the dense substrate:
  classified `hearing_act` rows, bounded `procedural_move` assembly,
  and a first conservative hearing-event layer
- that hearing-event layer now includes short local exchange/cluster assembly,
  not only one-move lifts
- it now also exposes coverage over the procedural-move layer, so AU progress
  can be tracked as "how much of the move layer is being lifted into bounded
  hearing events" rather than by event counts alone
- speaker continuity is now preserved across hearing acts, procedural moves,
  and assembled events, so local bench/counsel structure is less dependent on
  topic overlap alone
- the current conservative assembly is therefore driven by:
  local cues + speaker continuity + bounded topic continuity,
  rather than any one signal alone
- an important implementation constraint is now explicit too:
  exchange/event assembly must operate over transcript order, not ranked move
  order, or local hearing structure gets scrambled
- statute/authority continuity is also now stronger:
  section references and case-style authority cues are normalized into topic
  tokens so adjacent turns can stay connected on legal substance more reliably
- the next reviewed-layer target is now explicit:
  derive a smaller operator-facing hearing-event projection from assembled
  local events rather than relying only on the dense fact overlay
- that reviewed hearing-event projection now exists internally too:
  the dense AU artifact carries a smaller event-oriented operator layer derived
  from assembled hearing events plus linked fact/review support
- show exactly what is currently missing:
  broader event assembly coverage and higher-quality reviewed hearing-event
  coverage, not transcript-bearing statement/fact density
