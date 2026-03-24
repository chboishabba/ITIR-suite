# GWB Zelph Handoff V1 (2026-03-24)

## Purpose
Define the first concrete George W. Bush public-entity handoff slice for Zelph.

Important scope clarification:
- destination for the GWB lane is complete GWB/topic understanding
- this handoff artifact is one checked public-facing slice toward that
  destination, not the whole destination by itself

Companion completeness note:
- `docs/planning/gwb_completeness_scorecard_20260324.md`

This is not a new ingest lane. It is a bounded downstream handoff over repo
surfaces that already exist:

- reviewed GWB U.S.-law linkage seeds
- deterministic linkage matching over the GWB wiki timeline
- deterministic semantic promotion over the same corpus
- existing Zelph fact export/runtime surfaces on the SensibLaw side

The point of this slice is to give a Zelph developer one public, legible,
relatively safe example of:

1. real-world ingest into reviewed structure
2. explicit abstention on unresolved surfaces
3. bounded downstream reasoning over exported graph facts

## Why GWB is the right next handoff
- public figure and public events
- lower privacy risk than transcript or chat-history material
- already has a reviewed seed set and deterministic DB-backed reports
- easier to explain externally than legal-intake or personal handoff bundles
- naturally supports both positive relations and abstention/ambiguity stories

## Best Current GWB Artifacts
### 1. Reviewed authority seed
Primary artifact:
- `SensibLaw/data/ontology/gwb_us_law_linkage_seed_v1.json`

Why it matters:
- checked-in reviewed seed set
- 11 seed rows
- defines the public/legal lanes we are willing to reason over

Most useful current seed lanes:
- `gwb_us_law:clear_skies_2003`
- `gwb_us_law:syria_accountability_act`
- `gwb_us_law:supreme_court_appointments`
- `gwb_us_law:stem_cell_research_enhancement_act`
- `gwb_us_law:nsa_surveillance_review`
- `gwb_us_law:military_commissions_2006`

### 2. Deterministic linkage proof
Primary surfaces:
- `SensibLaw/scripts/gwb_us_law_linkage.py`
- `SensibLaw/tests/test_gwb_us_law_linkage.py`
- `docs/planning/gwb_us_law_linkage_seed_20260307.md`

What it proves:
- the reviewed seed set is not inert documentation
- deterministic matching exists against timeline events
- broad cues stay low-confidence or ambiguous rather than silently promoting

Current plain-language status:
- on the current DB-backed run recorded in the planning note:
  - 142 timeline events
  - 15 matched events
  - 8 ambiguous events
  - 11 / 11 reviewed seeds matched somewhere in the run
- strongest clean lanes are Clear Skies, Syria Accountability Act, Stem Cell,
  GINA, NSA surveillance review, and Supreme Court appointments

### 3. Deterministic semantic promotion proof
Primary surfaces:
- `SensibLaw/scripts/gwb_semantic.py`
- `SensibLaw/tests/test_gwb_semantic.py`
- `docs/planning/gwb_semantic_phase_v1_20260307.md`

What it proves:
- the GWB lane is not only keyword-to-seed matching
- the repo promotes bounded semantic relations over the shared entity spine
- unresolved discourse surfaces stay visible as abstentions

Current plain-language status from the checked test/report surface:
- promoted relations include:
  - Bush nominated John Roberts
  - John Roberts confirmed by the Senate
  - Bush signed the Military Commissions Act of 2006
  - Bush vetoed the Stem Cell Research Enhancement Act
  - a United States district court ruled on the Military Commissions Act lane
- unresolved surfaces intentionally remain unresolved:
  - `the administration`
  - `the President`
  - `the court`

### 4. Existing Zelph bridge/runtime surface
Primary surfaces:
- `SensibLaw/src/zelph_bridge.py`
- `SensibLaw/scripts/zelph_runner.py`
- `SensibLaw/sl_zelph_demo/`

Why it matters:
- we already have a working downstream export/runtime shape
- the GWB handoff should reuse this surface, not invent a separate reasoning
  engine or ontology stack

## Handoff Shape
### Inputs
- one deterministic GWB linkage report
- one deterministic GWB semantic report
- the reviewed seed JSON

### Output
One bounded Zelph-facing fact bundle over public-entity material only.

The first handoff should not try to export every raw event or every mention.
It should export only:

- promoted semantic relations
- reviewed seed linkage outcomes
- unresolved/abstained public discourse labels
- the minimum provenance needed to inspect why a relation or ambiguity exists

## Checked Artifact Now In Repo
Generated artifact directory:
- `SensibLaw/tests/fixtures/zelph/gwb_public_handoff_v1/`

Checked outputs:
- `SensibLaw/tests/fixtures/zelph/gwb_public_handoff_v1/gwb_public_handoff_v1.slice.json`
- `SensibLaw/tests/fixtures/zelph/gwb_public_handoff_v1/gwb_public_handoff_v1.summary.md`
- `SensibLaw/tests/fixtures/zelph/gwb_public_handoff_v1/gwb_public_handoff_v1.facts.zlp`
- `SensibLaw/tests/fixtures/zelph/gwb_public_handoff_v1/gwb_public_handoff_v1.rules.zlp`
- `SensibLaw/tests/fixtures/zelph/gwb_public_handoff_v1/gwb_public_handoff_v1.engine.json`
- `SensibLaw/tests/fixtures/zelph/gwb_public_handoff_v1/gwb_public_handoff_v1.scorecard.json`

Current checked result:
- 19 selected promoted relations
- 11 selected seed/review lanes
- 9 ambiguous events in the bounded slice
- 7 unresolved discourse surfaces
- Zelph engine run status: `ok`
- machine-readable scorecard written alongside the artifact

Current checked scorecard:
- destination:
  `complete_gwb_topic_understanding`
- current stage:
  `checked_public_handoff_checkpoint`
- matched seed lanes:
  `11`
- candidate-only seed lanes:
  `0`
- broad-cue seed lanes:
  `5`
- direct-support seed lanes:
  `6`

Human-legible summary already written:
- the narrative summary explicitly says, in prose, that the checked slice
  recovered Roberts nomination and confirmation, Stem Cell veto, Military
  Commissions signing, and district-court review, while keeping several seed
  lanes and discourse labels in review status instead of overresolving them

## Bounded Exported Graph Surface
The bounded graph should expose only four node families and four edge families.

### Node families
- `actor`
  - examples: `actor:george_w_bush`, `actor:john_roberts`,
    `actor:u_s_senate`
- `office`
  - example: `office:president_of_the_united_states`
- `legal_ref`
  - examples: `legal_ref:military_commissions_act_of_2006`,
    `legal_ref:stem_cell_research_enhancement_act`
- `review_item`
  - reviewed linkage seeds and unresolved discourse surfaces

### Edge families
- promoted semantic relation
  - examples: `nominated`, `confirmed_by`, `signed`, `vetoed`, `ruled_by`
- linkage relation
  - seed-to-event or seed-to-authority/institution support rows
- review-status relation
  - `matched`, `ambiguous`, `candidate_only`, `unresolved_surface`
- provenance relation
  - minimal source/run identifiers and receipt classes only

### What stays out of v1
- full raw timeline text export
- broad open-world entity linking
- unreviewed actor merges
- deep office/person collapse logic inside Zelph
- transcript/chat-style uncertainty semantics

## Bounded Query Surface
The first GWB Zelph handoff should answer only two bounded question families.

### Query family 1: What clean reviewed public-law relations were recovered?
Intended output:
- a short list of high-confidence promoted public-law relations involving
  George W. Bush, courts, institutions, or reviewed legal authorities

Example questions:
- Which reviewed legal authorities did Bush sign or veto in the current
  semantic/linkage slice?
- Which appointments or court-linked actions promoted cleanly into semantic
  relations?

### Query family 2: What stayed ambiguous or abstained?
Intended output:
- a short review list of ambiguous or unresolved public discourse surfaces

Example questions:
- Which GWB seed lanes are still only broad-cue or ambiguous matches?
- Which discourse labels stayed unresolved rather than collapsing into a
  canonical actor or institution?

## First Zelph Rules / Questions
These should stay small and demonstrably downstream of the exported graph.

### Rule / Question 1
`executive_public_law_action`

Plain-language question:
- Which reviewed public-law actions by George W. Bush promoted cleanly into
  high-confidence signed/vetoed/nominated relations?

Expected coverage from current checked surfaces:
- John Roberts nomination
- Military Commissions Act signing
- Stem Cell Research Enhancement Act veto

Minimal rule shape:
- if subject is `actor:george_w_bush`
- and predicate is one of `nominated`, `signed`, `vetoed`
- and object is a reviewed actor or legal reference
- then emit `executive_public_law_action`

### Rule / Question 2
`needs_review_due_to_ambiguity`

Plain-language question:
- Which GWB public-law lanes are still broad-cue, ambiguous, or unresolved and
  therefore should remain review items rather than canonical relations?

Expected coverage from current checked surfaces:
- broad `Iraq` / `veto` / `Congress` style cues in the linkage lane
- unresolved semantic surfaces like `the administration`, `the President`,
  `the court`

Minimal rule shape:
- if a linkage row is `ambiguous` or only `low` confidence from broad cues
- or a semantic mention remains unresolved
- then emit `needs_review_due_to_ambiguity`

## Reproducible Commands
### Proof surfaces
- linkage test:
  `cd /home/c/Documents/code/ITIR-suite/SensibLaw && ../.venv/bin/pytest -q tests/test_gwb_us_law_linkage.py`
- semantic test:
  `cd /home/c/Documents/code/ITIR-suite/SensibLaw && ../.venv/bin/pytest -q tests/test_gwb_semantic.py`
- handoff artifact test:
  `cd /home/c/Documents/code/ITIR-suite/SensibLaw && ../.venv/bin/pytest -q tests/test_gwb_zelph_handoff.py`

### CLI/report surfaces
- linkage report:
  `cd /home/c/Documents/code/ITIR-suite && .venv/bin/python SensibLaw/scripts/gwb_us_law_linkage.py --db-path SensibLaw/.cache_local/itir.sqlite report`
- semantic report:
  `cd /home/c/Documents/code/ITIR-suite && .venv/bin/python SensibLaw/scripts/gwb_semantic.py --db-path SensibLaw/.cache_local/itir.sqlite report`
- checked handoff artifact rebuild:
  `cd /home/c/Documents/code/ITIR-suite && python SensibLaw/scripts/build_gwb_zelph_handoff.py`

## Current Recommendation
- keep the current canonical Zelph pack v1 unchanged
- treat GWB as the next public-entity handoff artifact immediately after v1
- build the first Zelph-facing GWB bundle from deterministic linkage +
  deterministic semantic report surfaces
- use GWB before the chat-history lane because it is safer to externalize and
  easier to explain

## Open Followthrough
- decide whether the checked GWB artifact should enter the canonical pack as
  v1.5 or wait for v2
- decide whether to add one second checked public-entity lane alongside GWB
  before changing canonical pack scope
