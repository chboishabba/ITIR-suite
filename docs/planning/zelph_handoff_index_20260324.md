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
- `docs/planning/zelph_external_handoff_20260320.md`

What it is for:
- high-level collaboration framing
- what SensibLaw/ITIR does upstream
- what Zelph is expected to do downstream
- current real status and current gaps

### 2. Then read the current outward-facing pack spec
- `docs/planning/zelph_real_world_pack_v1_5_20260324.md`
- `docs/planning/zelph_real_world_pack_v1_5.manifest.json`

What it is for:
- exact pack contents
- why those artifacts are in the pack
- what is still excluded or deferred

### 3. Then read the checked handoff artifact notes
- GWB:
  `docs/planning/gwb_zelph_handoff_v1_20260324.md`
- AU:
  `docs/planning/au_zelph_handoff_v1_20260324.md`

What they are for:
- bounded downstream-safe exported slices
- human-legible narrative summaries
- exact fact/rule/query surfaces for the handoff artifacts

### 4. Then read the corpus-level companion notes
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
- GWB:
  `SensibLaw/tests/fixtures/zelph/gwb_public_handoff_v1/`
- AU:
  `SensibLaw/tests/fixtures/zelph/au_public_handoff_v1/`

### Corpus-level companion artifacts
- GWB:
  `SensibLaw/tests/fixtures/zelph/gwb_corpus_scorecard_v1/`
- AU:
  `SensibLaw/tests/fixtures/zelph/au_corpus_scorecard_v1/`

## Current Plain-Language Status
- SensibLaw/ITIR can already export bounded reviewed structure into Zelph.
- GWB is the cleanest public-facing downstream handoff artifact.
- AU is a real Mary-parity/operator-review artifact, but its current checked
  handoff slice is intentionally narrow.
- Corpus-level accounting now exists for both GWB and AU, but neither lane
  should yet be described as destination-complete.

## Use This Index When Sharing
If someone needs only one link first:
- send `docs/planning/zelph_external_handoff_20260320.md`

If they immediately ask "what exactly is in scope now?":
- send `docs/planning/zelph_real_world_pack_v1_5_20260324.md`

If they ask for concrete artifacts:
- send the relevant handoff fixture directory under
  `SensibLaw/tests/fixtures/zelph/`

If they ask "how complete is this really?":
- send the corresponding completeness note plus the corpus scorecard artifact
