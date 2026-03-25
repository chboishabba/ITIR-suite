# Zelph External Handoff Note (2026-03-20)

## Purpose
This note is the short, technically grounded document we can point a Zelph
developer at so they understand what SensibLaw/ITIR is doing, what has already
been demonstrated locally, and where we think a clean collaboration boundary
could exist.

If someone needs one short meeting-ready link that works for both the Wikidata
Ontology Working Group and the Zelph developer, start with:
- `docs/planning/wikidata_zelph_single_handoff_20260325.md`

Canonical doc index for this collaboration surface:
- `docs/planning/zelph_handoff_index_20260324.md`

It is intentionally upstream-facing and should not be read as a claim that
SensibLaw depends on Zelph or that a deep integration contract already exists.
Treat this note as the Zelph-specific appendix after the shared handoff note.

## Current Positioning
SensibLaw is working primarily at the text-to-structure boundary:

- deterministic ingest from messy source corpora into explicit facts,
  observations, claims, events, and review states
- provenance-preserving storage so downstream reasoning can always be traced
  back to source material
- operator-facing review surfaces to prevent silent fact inflation
- semantic materialization and benchmark loops to test stability before any
  stronger reasoning/export claims

The intended relationship to Zelph is:

- SensibLaw upstream:
  extract, normalize, review, and preserve provenance over facts from text
- Zelph downstream:
  reason over already-structured graph facts, constraints, and rules

This is a bridge/demo posture, not a dependency posture.

Canonical companion artifacts for the current pack are now:
- `docs/planning/zelph_real_world_pack_v1_20260324.md`
- `docs/planning/zelph_real_world_pack_v1.manifest.json`
- `docs/planning/zelph_real_world_pack_v1_5_20260324.md`
- `docs/planning/zelph_real_world_pack_v1_5.manifest.json`
- `docs/planning/zelph_real_world_pack_v1_6_20260325.md`
- `docs/planning/zelph_real_world_pack_v1_6.manifest.json`

Canonical companion artifact for the next public-entity handoff is now:
- `docs/planning/gwb_zelph_handoff_v1_20260324.md`
- `docs/planning/gwb_completeness_scorecard_20260324.md`
- `docs/planning/au_zelph_handoff_v1_20260324.md`
- `docs/planning/au_completeness_scorecard_20260324.md`

Corpus-level companion artifacts now also exist at:
- `SensibLaw/tests/fixtures/zelph/gwb_corpus_scorecard_v1/`
- `SensibLaw/tests/fixtures/zelph/gwb_broader_corpus_checkpoint_v1/`
- `SensibLaw/tests/fixtures/zelph/gwb_broader_promotion_diagnostics_v1/`
- `SensibLaw/tests/fixtures/zelph/au_corpus_scorecard_v1/`
- `SensibLaw/tests/fixtures/zelph/au_broader_corpus_diagnostics_v1/`

Reading discipline:
- use this note for external framing
- use the pack note for exact pack contents
- use the AU/GWB handoff notes for bounded artifact details
- use the AU/GWB completeness notes for corpus-level status

Current next-phase priority order:
1. broader AU transcript/WhisperX-backed corpus coverage
2. next genuinely new GWB broader-source family
3. safe real chat-history lane

Latest GWB corpus-expansion result:
- the broader GWB checkpoint now uses a richer public-bios timeline built from
  raw HTML pages rather than title-only rows
- the richer builder now preserves explicit statute-signing sentences such as
  the No Child Left Behind line that had previously been dropped by malformed
  HTML paragraph boundaries
- a broader-source seed-backed semantic pass now lifts both broader source
  families into independent promoted confirmation on one already-known
  relation family:
  each of the public-bios and corpus/book lanes now yields promoted
  `subject_of_review_by` confirmation on the Supreme Court family
- the richer public-bios lane now also contributes one genuinely new broader
  promoted public-law family:
  `George W. Bush -> signed -> No Child Left Behind Act`
- the richer public-bios lane now also contributes one genuinely new broader
  promoted executive-action family:
  `George W. Bush -> signed -> Northwestern Hawaiian Islands Marine National Monument`
- the corpus/book timeline has now improved materially as well:
  prioritizing legally salient late-book sentences surfaces real nomination and
  review material from `Decision Points` and related sources, including
  broader-source confirmation of the checked nomination family and one new
  broader relation:
  `George W. Bush -> ruled_by -> Supreme Court of the United States`
- the corpus/book lane now also independently confirms one already-checked
  legal-action family:
  a memoir-rooted first-person legal-action pass now promotes
  `George W. Bush -> vetoed -> Stem Cell Research Enhancement Act`
  from `Decision Points`, but that does not increase the deduped checkpoint
  count because the relation already existed in the checked handoff
- current broader checkpoint result is therefore:
  `18` distinct promoted relations after canonical dedupe and `3` new
  distinct promoted relations beyond the checked handoff
- a follow-on corpus disambiguation pass now abstains father/family-history
  bare-`Bush` rows rather than resolving them directly to George W. Bush
- practical reading: the next GWB bottleneck is no longer public-source
  availability; it is now widening beyond the Supreme Court confirmation and
  NCLB signing + marine-monument proclamation + corpus review/nomination
  confirmations into additional promotable broader-source families

## Current Status Snapshot (2026-03-24)
What is already real in the repo:
- small Zelph-facing demos exist and are still the cleanest shareable proof
  points
- persisted `real` fact-review/workbench bundles now exist and are stronger
  proof surfaces than the synthetic benchmark seeds for external positioning
- the current intended claim remains behavior-level:
  bounded downstream reasoning over exported fact structure, not raw-text
  ingestion inside Zelph
- there is still no comparably strong repo-stable real chat-history run artifact
  prepared as a Zelph-facing pack component
- AU now also has a broader corpus diagnostics companion, but it still points
  to the same real next gap: more reviewed transcript/raw-source material needs
  to graduate into persisted bundle coverage
- the AU dense hearing lane is now one step more structured internally:
  the dense transcript substrate carries a first hearing-act classification
  layer and bounded procedural-move assembly above the raw transcript-bearing
  fact layer, while staying internal-only for now

What is still uncertain:
- whether probability/uncertainty handling should remain entirely upstream for
  the first collaboration slice
- whether the cleanest first export is:
  graph facts, predicate-as-node exports, or a Janet-facing bridge
- which real run-derived artifacts are clean enough to externalize without
  leaking personal or case-linked material

## Zelph Dev Contact Surfaces
These are the repo surfaces a Zelph developer can be pointed at first.

Primary shareable entrypoints:
- `SensibLaw/sl_zelph_demo/run.sh`
- `SensibLaw/sl_zelph_demo/db_run.sh`
- `SensibLaw/sl_zelph_demo/wikidata_run.sh`
- `SensibLaw/tests/test_sl_zelph_demo_tools.py`
- this note

Primary code surfaces:
- `SensibLaw/sl_zelph_demo/compile_db.py`
- `SensibLaw/sl_zelph_demo/lex_to_zelph.py`
- `SensibLaw/scripts/zelph_runner.py`
- `SensibLaw/src/zelph_bridge.py`

Primary rule/demo packs:
- `SensibLaw/sl_zelph_demo/db_rules.zlp`
- `SensibLaw/sl_zelph_demo/wiki_lex_rules.zlp`
- `SensibLaw/sl_zelph_demo/ontology_rules.zlp`
- `SensibLaw/src/fact_intake/zelph_invariants.zlp`
- `SensibLaw/src/fact_intake/zelph_workbench_rules.zlp`

Primary caution surfaces:
- benchmark result JSONs under
  `SensibLaw/tests/fixtures/fact_semantic_bench/results/`
- any chat-derived or transcript-derived corpora
- any local analysis or export artifacts not explicitly reviewed for sharing

Clarification:
- this note names repo-facing technical contact surfaces only
- it does not record private personal contact details

## What Has Already Been Demonstrated
### 1. Database atom ingest into Zelph
Repo evidence:
- `SensibLaw/sl_zelph_demo/compile_db.py`
- `SensibLaw/sl_zelph_demo/db_rules.zlp`
- `SensibLaw/tests/test_sl_zelph_demo_tools.py`

Current demonstrated behavior:
- `compile_db.py` exports `rule_atoms` from SQLite into Zelph facts/rules
- modality atoms like `modality.must` and `modality.may` are projected into
  Zelph
- Zelph rules classify obligations and permissions over the exported atoms

### 2. Lexical graph projection into Zelph
Repo evidence:
- `SensibLaw/sl_zelph_demo/lex_to_zelph.py`
- `SensibLaw/sl_zelph_demo/wiki_lex_rules.zlp`
- `SensibLaw/sl_zelph_demo/wiki_inferred.txt`

Current demonstrated behavior:
- Wikipedia revision comments are tokenized into ordered lexical node sequences
- recursive Zelph rules match those lexical graphs
- the demo identifies narrow downstream behavior over revision-history
- patterns (reversion detection, volatility-style edit signals) that feed a
- bounded review signal

Clarification:
- this is a deliberately small demo of downstream reasoning over structured
  lexical facts
- it should not be read as establishing a stable formal ontology role for wiki
  editors
- the externally relevant claim is the behavior-level one: Zelph can consume a
  compact exported fact slice and infer bounded review-relevant signals from it
  (the old wiki/revert lane is now a minor review signal example, not the
  headline story)

### 3. Fact-semantic benchmark calibration
Repo evidence:
- `SensibLaw/scripts/benchmark_fact_semantics.py`
- `SensibLaw/scripts/run_fact_semantic_benchmark_matrix.py`
- `SensibLaw/tests/fixtures/fact_semantic_bench/README.md`
- `SensibLaw/tests/fixtures/fact_semantic_bench/results/`

Current demonstrated behavior:
- benchmark runs exist for:
  - `wiki_revision`
  - `chat_archive`
  - `transcript_handoff`
  - `au_legal`
- the benchmark records `refresh_status`, stage, fact counts, and elapsed time
- recent checked-in result fixtures show `refresh_status == "ok"` on the
  benchmark paths we are using as the current baseline

Clarification:
- these benchmark corpora are still primarily regression/calibration material
- they are not the main real-world proof pack when real run-derived artifacts
  already exist

## What We Are Actually Trying To Prove
The near-term claim is not "Zelph solves our ingest problem."

The near-term claim is:

1. SensibLaw can deterministically convert unstructured corpora into explicit,
   provenance-preserving fact structures.
2. A compact, meaningful subset of those facts can be projected into Zelph
   without losing the upstream provenance story.
3. Zelph can then reason over the exported structure in a way that is useful,
   testable, and clearly downstream of the ingest/review layer.

That is why the current bridge is intentionally tiny and deterministic.

## Stefan-facing Zelph pack
- demo scripts/tests (e.g., `SensibLaw/sl_zelph_demo/run.sh`,
  `SensibLaw/tests/test_sl_zelph_demo_tools.py`) remain the clean deterministic
  bridge proof
- real-world demo lead candidates should now come from persisted `real`
  workbench bundles rather than synthetic benchmark seeds

Current ranked candidates:
1. `itir-svelte/tests/fixtures/fact_review_wave1_real_au_demo_bundle.json`
   - strongest current legal/procedural review story
   - best current balance of technical credibility and shareability
2. `itir-svelte/tests/fixtures/fact_review_wave5_real_professional_handoff_demo_bundle.json`
   - strongest current real transcript/provenance/handoff story
   - very good downstream reasoning value
   - needs careful sanitization/review because transcript-adjacent material is
     higher-risk to share
3. `itir-svelte/tests/fixtures/fact_review_wave3_real_fragmented_support_demo_bundle.json`
   - strongest current fragmented/conflicted-support reconstruction story
   - also needs careful sanitization/review
4. `SensibLaw/tests/fixtures/wikidata/real_qualifier_imported_slice_20260307.json`
   - useful non-transcript real import example
   - better as a secondary structured-import slice than as the headline demo

Do not lead with:
- `SensibLaw/tests/fixtures/fact_semantic_bench/*_seed.json`
- older wiki/revert examples as the headline Zelph story

Current gap:
- there is no repo-stable real chat-history run artifact yet that matches the
  strength of the transcript/AU demo bundles
- if chat-history is meant to be a main real-world proof lane, it needs its own
  prepared run-derived export surface

Current V1 decision:
- the first canonical Zelph pack is a safer 2-slice real pack plus the
  deterministic DB/rule-atom bridge proof
- canonical V1 contents are:
  - deterministic DB/rule-atom bridge
  - `itir-svelte/tests/fixtures/fact_review_wave1_real_au_demo_bundle.json`
  - `SensibLaw/tests/fixtures/wikidata/real_qualifier_imported_slice_20260307.json`
- the transcript-derived real bundles stay ranked internal/next-pack candidates
  rather than the first canonical pack

Current next-step handoff decision:
- the outward-facing pack should now be treated as `v1.5`, not just `v1`
- reason:
  GWB is now checked and AU has been brought up to the same handoff shape
- concrete pack spec:
  `docs/planning/zelph_real_world_pack_v1_5_20260324.md`
- checked artifacts now exist at:
  `SensibLaw/tests/fixtures/zelph/gwb_public_handoff_v1/`
  and
  `SensibLaw/tests/fixtures/zelph/au_public_handoff_v1/`

Important clarification:
- the current AU and GWB checked artifacts are handoff checkpoints, not corpus
  completeness reports
- they prove that reviewed, downstream-safe Zelph exports are real
- they do not yet prove that AU or GWB extraction is exhaustive over the full
  available source families
- the new AU/GWB corpus scorecards are the first machine-readable bridge from
  those bounded handoff checkpoints toward broader source-family accounting
- for AU, the current checked slice is built from a real fact-review workbench
  bundle and should be read through the Mary-parity/operator-review lens
- for GWB, the broader completeness target must include source families beyond
  the current wiki/seed-oriented handoff slice, including the existing
  `demo/ingest/gwb/` book and public-bios surfaces

Current broader-GWB checkpoint result:
- the first broader machine-readable checkpoint now exists at
  `SensibLaw/tests/fixtures/zelph/gwb_broader_corpus_checkpoint_v1/`
- it widened source-family coverage, but did not add new promoted relations
  beyond the checked handoff
- that means the next GWB problem is promotion/admissibility over broader
  public sources, not merely source inventory

## Human-readable summary of the current real JSON artifacts
### 1. Wave 1 real AU procedural bundle
Path:
- `itir-svelte/tests/fixtures/fact_review_wave1_real_au_demo_bundle.json`

What it shows in plain terms:
- one real `au_semantic` procedural run reopened through the fact-review
  workbench
- six operator-facing acceptance stories all pass:
  community legal centre intake triage, NGO case assembly, paralegal evidence
  pack preparation, solicitor case-theory prep, barrister chronology prep, and
  judge/associate procedural reconstruction
- the run contains:
  3 statements, 27 observations, 3 facts, and 2 approximate events
- the review queue is small and interpretable:
  `Criminal appeal`, `Judicial review`, and `Orders`
- the workbench exposes multiple operator views such as:
  `intake_triage`, `chronology_prep`, `procedural_posture`,
  `claim_alignment`, and `contested_items`

Why it matters:
- this is currently the clearest repo-stable proof that SensibLaw/ITIR can
  ingest real procedural/legal material into a reviewable, provenance-backed
  operator surface rather than just a benchmark harness

### 2. Wave 5 real professional handoff bundle
Path:
- `itir-svelte/tests/fixtures/fact_review_wave5_real_professional_handoff_demo_bundle.json`

What it shows in plain terms:
- one real `transcript_semantic` handoff-oriented run reopened through the
  fact-review workbench
- two acceptance stories pass:
  personal-to-professional provenance handoff and false-coherence resistance
- the run contains:
  3 sources, 3 statements, 4 observations, and 3 facts
- it deliberately has no assembled events yet; all 3 facts remain in the
  `no_event` bucket, which is useful because it demonstrates read-only review
  over sparse/fragile material instead of fake completeness
- the review queue surfaces exactly 2 items:
  `Clinic letter` and `User journal account`

Why it matters:
- this is the strongest current transcript/provenance/handoff example for
  downstream reasoning because it preserves difficult boundary conditions rather
  than collapsing them into an overconfident event story

### 3. Wave 3 real fragmented support bundle
Path:
- `itir-svelte/tests/fixtures/fact_review_wave3_real_fragmented_support_demo_bundle.json`

What it shows in plain terms:
- one real `transcript_semantic` fragmented-support run reopened through the
  workbench
- two acceptance stories pass:
  trauma-survivor-safe reconstruction and support-worker/advocate timeline
  assist
- the run contains:
  3 sources, 3 statements, 4 observations, and 3 facts
- one fact is abstained, one chronology item is contested, and the review queue
  stays bounded around:
  `User incident fragment` and `Clinic presentation record`

Why it matters:
- this is the strongest current repo-stable example that the system can carry
  uncertainty, abstention, and source-boundary pressure through review without
  forcing false coherence

### 4. Real Wikidata qualifier import slice
Path:
- `SensibLaw/tests/fixtures/wikidata/real_qualifier_imported_slice_20260307.json`

What it shows in plain terms:
- a real imported Wikidata slice for property `P166`
- two time windows (`prev` / `current`) over real exported entity data
- the first window carries 4 statement bundles with real qualifiers, ranks, and
  references

Why it matters:
- this is a good secondary non-transcript example of real structured import and
  qualifier preservation, but it is not yet as strong an operator/workbench
  story as the transcript/AU bundles above

## GWB public-entity handoff in plain language
What it uses:
- a reviewed GWB U.S.-law seed set
- a deterministic linkage run over the GWB wiki timeline
- a deterministic semantic promotion/report layer over the same corpus

What it already proves:
- the repo can recover clean public-law relations like nomination, Senate
  confirmation, signing, veto, and court-review relations from public material
- the repo does not silently force broad discourse labels into canonical actors
  when the evidence is weak

What currently comes out cleanly:
- Bush nominated John Roberts
- John Roberts was confirmed by the Senate
- Bush signed the Military Commissions Act of 2006
- Bush vetoed the Stem Cell Research Enhancement Act
- district-court review stayed explicit in the Military Commissions Act lane

What intentionally stays unresolved:
- `the administration`
- `the President`
- `the court`

Why it matters for Zelph:
- it is the cleanest current public-entity example of
  `real ingest -> reviewed structure -> bounded downstream reasoning`
- it is safer than transcript/chat lanes and easier to explain than legal-intake
  workflows

Current checked artifact summary:
- bounded slice counts:
  19 promoted relations, 11 seed/review lanes, 9 ambiguous events, 7 unresolved
  discourse surfaces
- completeness scorecard currently reports:
  19 matched promoted relations,
  11 matched seed lanes,
  0 candidate-only seed lanes,
  5 broad-cue seed lanes,
  6 direct-support seed lanes
- checked prose summary exists in:
  `SensibLaw/tests/fixtures/zelph/gwb_public_handoff_v1/gwb_public_handoff_v1.summary.md`
- checked machine-readable slice exists in:
  `SensibLaw/tests/fixtures/zelph/gwb_public_handoff_v1/gwb_public_handoff_v1.slice.json`
- checked machine-readable scorecard exists in:
  `SensibLaw/tests/fixtures/zelph/gwb_public_handoff_v1/gwb_public_handoff_v1.scorecard.json`
- checked Zelph bundle exists in:
  `SensibLaw/tests/fixtures/zelph/gwb_public_handoff_v1/gwb_public_handoff_v1.facts.zlp`
  plus
  `SensibLaw/tests/fixtures/zelph/gwb_public_handoff_v1/gwb_public_handoff_v1.rules.zlp`
- broader corpus source-family checkpoint now exists in:
  `SensibLaw/tests/fixtures/zelph/gwb_corpus_scorecard_v1/`

Important framing clarification:
- destination is complete GWB/topic understanding
- the checked GWB handoff is the first scored public-facing checkpoint toward
  that destination, not the whole completeness claim

## AU corpus-level checkpoint in plain language
What it uses:
- the persisted real AU procedural workbench bundle
- the persisted real transcript-adjacent workbench bundles that currently form
  the wider AU-facing Mary-parity lane
- visible raw HCA transcript files as known backlog, not as silently-covered
  material

What currently comes out:
- 4 included real bundles
- 13 statements
- 40 observations
- 13 facts
- 2 events
- 11 review queue items
- 3 contested items

Why it matters:
- it is the first machine-readable answer to "what do we currently cover at
  corpus level?" rather than "what does the bounded AU handoff show?"
- it makes the current gap explicit:
  repo-visible raw transcript material still exists outside the current
  persisted real-bundle checkpoint

What changed internally after this checkpoint:
- the real HCA hearing transcript lane now also has a persisted
  structural/legal checkpoint under
  `SensibLaw/tests/fixtures/zelph/au_real_transcript_structural_checkpoint_v1/`
- that checkpoint covers 2 real transcript files, 1747 transcript units, 2224
  structural/legal tokens, and 12 selected high-signal excerpts
- this is useful because the raw transcript lane is no longer only backlog, but
  it is not yet treated as reviewed fact/event coverage
- the same two real HCA files now also flow into an internal dense transcript
  substrate artifact under
  `SensibLaw/tests/fixtures/zelph/au_real_transcript_dense_substrate_v1/`
- that dense artifact currently reports 1747 transcript units, 1747 facts,
  1482 observations, 0 events, and a 24-item secondary review-overlay
  projection
- this is the current repo-proof that AU transcript density is real at the
  substrate layer; the narrower reviewed/procedural overlay is a secondary
  projection rather than the primary transcript representation

Current corpus companion artifacts:
- `SensibLaw/tests/fixtures/zelph/au_corpus_scorecard_v1/au_corpus_scorecard_v1.json`
- `SensibLaw/tests/fixtures/zelph/au_corpus_scorecard_v1/au_corpus_scorecard_v1.summary.md`

## What We Think Is Interesting About Zelph
Based on Stefan's description and our own demo work, the most interesting
collaboration surfaces are:

- graph-native predicates as first-class nodes
- constraint/negation-oriented reasoning over already-structured facts
- probability-aware fact treatment, if that capability becomes script/runtime
  visible in a practical way
- Janet-enabled ingest/transform/runtime surfaces, where appropriate

The interesting overlap is not raw text parsing inside Zelph by default; it is
what Zelph can do once SensibLaw has already produced stable, provenance-backed
graph structure.

## Boundary We Want To Keep Clean
- SensibLaw should remain the authority for ingest, extraction, review, and
  source traceability.
- Zelph should be treated as a reasoning engine over exported graph structure.
- We should avoid describing the current work as a full runtime integration.
- We should avoid shipping personal or sensitive benchmark/result JSONs to third
  parties until they are reviewed and sanitized.

## What We Can Safely Point To
Likely safe to share after one final review:
- `SensibLaw/sl_zelph_demo/`
- `SensibLaw/tests/test_sl_zelph_demo_tools.py`
- `itir-svelte/tests/fixtures/fact_review_wave1_real_au_demo_bundle.json`
- this note

Needs review/sanitization before external sharing:
- `itir-svelte/tests/fixtures/fact_review_wave5_real_professional_handoff_demo_bundle.json`
- `itir-svelte/tests/fixtures/fact_review_wave3_real_fragmented_support_demo_bundle.json`
- benchmark result JSONs under
  `SensibLaw/tests/fixtures/fact_semantic_bench/results/`
- any chat-derived or transcript-derived corpora
- `SensibLaw/tests/fixtures/zelph/au_real_transcript_structural_checkpoint_v1/`
- any local analysis artifacts that may contain personal or case-linked content

## Open Collaboration Questions
- Which one or two of the ranked real-world bundles above should become the
  first canonical Zelph-facing examples?
- Are there additional log/metadata artifacts from the DB/rule-atom export path (`SensibLaw/sl_zelph_demo/compile_db.py`, `db_rules.zlp`, `db_run.sh`) that Zelph devs will need to believe the deterministic handoff story?
- What is the first repo-stable real chat-history run artifact we want to
  prepare so chat-derived material can join the pack without leaning on
  synthetic seeds?
- Should the first checked GWB handoff be shared as a reviewed JSON report
  slice, a compiled Zelph fact bundle, or both?

## Suggested Questions / Next Discussion Points
- Which one or two bounded Zelph rules should become the first GWB public-law
  reasoning demo:
  clean executive-public-law actions, ambiguity/review detection, or both?
- Which ontology/predicate-as-node exports under
  `SensibLaw/sl_zelph_demo/ontology_*` should be documented to showcase richer
  predicate bridging?
- Which real chat-history or development/math/public-event chat slices are safe
  enough to turn into the missing repo-stable chat-derived demo lane?
- once the first real chat-history lane exists, should the second canonical pack
  replace the structured-import slice or simply expand from 2 real slices to 3?

## Intended Next Tests
- keep the outward-facing handoff note aligned first with the persisted `real`
  workbench bundles and the deterministic DB/rule-atom export path
- add one small bridge-level regression that verifies the handoff claims remain
  true for the current demo outputs
- prefer real run-derived examples over synthetic benchmark seeds whenever both
  are available
- keep the older wiki/review lane as optional historical context only, not as
  the main proof surface

## One-sentence Summary
SensibLaw is trying to make text-derived facts stable, reviewable, and
provenance-preserving before handing a compact graph slice to Zelph for
downstream reasoning.
