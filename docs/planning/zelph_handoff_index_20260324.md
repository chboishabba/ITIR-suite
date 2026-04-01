# Zelph Handoff Index (2026-03-24)

## Purpose
Provide one canonical reading order for Zelph-facing and Wikidata-adjacent
external collaboration material.

The current problem is not lack of material. It is that the material exists at
several levels:
- external framing
- pack definition
- artifact-specific handoff notes
- corpus-level completeness notes

This index makes those levels explicit so people stop reading a checkpoint as a
completeness claim, or a pack note as if it were the whole technical contract.

## Recommended Reading Order
### 1. Start here for external orientation
- `docs/planning/wikidata_zelph_single_handoff_20260325.md`

What it is for:
- one short plain-language handoff that works for both the Wikidata Ontology
  Working Group and the Zelph developer
- exact current results, current direction, and audience-specific value

### 2. Then read the Zelph-specific framing note
- `docs/planning/zelph_external_handoff_20260320.md`

What it is for:
- high-level collaboration framing
- what SensibLaw/ITIR does upstream
- what Zelph is expected to do downstream
- current real status and current gaps

### 3. Then read the current outward-facing pack spec
- `docs/planning/zelph_real_world_pack_v1_6_20260325.md`
- `docs/planning/zelph_real_world_pack_v1_6.manifest.json`

What it is for:
- exact pack contents
- why those artifacts are in the pack
- what is still excluded or deferred

### 3.5. If the question is "what is the smallest grantable slice?"
- `docs/planning/zelph_nlnet_grant_draft_20260401.md`

What it is for:
- Stefan-facing bounded grant framing
- lower-bound deliverable wording
- explicit non-goals so the grant story does not overclaim deep integration

### 4. Then read the checked handoff artifact notes
- Wikidata:
  `docs/planning/wikidata_structural_handoff_v1_20260325.md`
- GWB:
  `docs/planning/gwb_zelph_handoff_v1_20260324.md`
- AU:
  `docs/planning/au_zelph_handoff_v1_20260324.md`

What they are for:
- bounded downstream-safe exported slices
- human-legible narrative summaries
- exact fact/rule/query surfaces for the handoff artifacts

### 5. Then read the corpus-level companion notes
- GWB:
  `docs/planning/gwb_completeness_scorecard_20260324.md`
- AU:
  `docs/planning/au_completeness_scorecard_20260324.md`

What they are for:
- separating bounded handoff checkpoints from broader corpus accounting
- recording what broader source-family coverage exists now
- naming the next completeness-expansion steps honestly

## Current Canonical Repo Artifacts
### Deterministic bridge proof
- `SensibLaw/sl_zelph_demo/compile_db.py`
- `SensibLaw/sl_zelph_demo/db_rules.zlp`
- `SensibLaw/tests/test_sl_zelph_demo_tools.py`

### Checked handoff artifacts
- Wikidata:
  `SensibLaw/tests/fixtures/zelph/wikidata_structural_handoff_v1/`
- GWB:
  `SensibLaw/tests/fixtures/zelph/gwb_public_handoff_v1/`
- AU:
  `SensibLaw/tests/fixtures/zelph/au_public_handoff_v1/`

### Corpus-level companion artifacts
- GWB:
  `SensibLaw/tests/fixtures/zelph/gwb_corpus_scorecard_v1/`
  `SensibLaw/tests/fixtures/zelph/gwb_broader_corpus_checkpoint_v1/`
  `SensibLaw/tests/fixtures/zelph/gwb_broader_promotion_diagnostics_v1/`
- AU:
  `SensibLaw/tests/fixtures/zelph/au_corpus_scorecard_v1/`
  `SensibLaw/tests/fixtures/zelph/au_broader_corpus_diagnostics_v1/`
  `SensibLaw/tests/fixtures/zelph/au_real_transcript_structural_checkpoint_v1/`
  `SensibLaw/tests/fixtures/zelph/au_real_transcript_dense_substrate_v1/`
  - internal dense-substrate reviewed projection (latest): 24 rows, 0.104751
    reviewed-event coverage ratio (`/tmp/au_real_round2_v2`), operator-only
    triage quality at this stage

## Current Plain-Language Status
- SensibLaw/ITIR can already export bounded reviewed structure into Zelph.
- Wikidata now also has a concrete checked structural handoff artifact with the
  same summary/JSON/ZLP/scorecard shape used by GWB and AU.
- GWB is the cleanest public-facing downstream handoff artifact.
- AU is a real Mary-parity/operator-review artifact, but its current checked
  handoff slice is intentionally narrow.
- AU now also has an internal dense transcript substrate artifact over the real
  HCA hearing; that substrate is primary for transcript-density evaluation, and
  the reviewed bundle remains a smaller secondary overlay.
  The latest 24-row reviewed-event projection is best treated as a high-coverage,
  low-trust operator queue until additional continuity/date/quality gates are in place.
- Corpus-level accounting now exists for both GWB and AU, but neither lane
  should yet be described as destination-complete.
- The wiki/Wikidata lane now has checked-handoff parity on artifact shape, but
  it remains a bounded structural-review lane rather than a completeness claim.

## Current Priority Order
For the next corpus-expansion phase, use this order unless a stronger safety
constraint appears:

1. AU broader transcript/WhisperX-backed corpus coverage
2. GWB next genuinely new broader-source family
3. Checked wiki/Wikidata structural handoff parity
4. Safe real chat-history lane

Reason:
- AU now has both a real transcript structural/legal checkpoint and a dense
  transcript substrate artifact, so the next bottleneck is converting more of
  that hearing lane into reviewed fact/event coverage without pretending dense
  transcript counts must be narrow.
- GWB is still the cleanest public-facing source family, but it has already
  moved further on broader-source confirmation than AU.
- wiki/Wikidata is now the right next bounded handoff-parity task because the
  internals are stronger than the current outward-facing artifact shape.
- chat-history remains valuable, but it is still the highest hygiene/safety
  burden of the remaining lanes.

## Use This Index When Sharing
If someone needs only one link first:
- send `docs/planning/wikidata_zelph_single_handoff_20260325.md`

If they immediately ask "what exactly is in scope now?":
- send `docs/planning/zelph_real_world_pack_v1_6_20260325.md`

If they ask for concrete artifacts:
- send the relevant handoff fixture directory under
  `SensibLaw/tests/fixtures/zelph/`

If they ask "how complete is this really?":
- send the corresponding completeness note plus the corpus scorecard artifact
