# AU Zelph Handoff V1 (2026-03-24)

## Purpose
Define the checked AU procedural handoff artifact so AU now has the same basic
handoff shape as GWB:

Companion index:
- `docs/planning/zelph_handoff_index_20260324.md`

- narrative summary
- bounded machine-readable slice
- Zelph facts bundle
- Zelph rules
- engine output
- completeness scorecard

Companion note:
- `docs/planning/au_completeness_scorecard_20260324.md`
- broader diagnostics companion:
  `SensibLaw/tests/fixtures/zelph/au_broader_corpus_diagnostics_v1/`
- internal transcript substrate companions:
  `SensibLaw/tests/fixtures/zelph/au_real_transcript_structural_checkpoint_v1/`
  and
  `SensibLaw/tests/fixtures/zelph/au_real_transcript_dense_substrate_v1/`

Role of this note:
- artifact-specific handoff spec only
- not the pack definition
- not the broader AU corpus-completeness note

## Source
Current source bundle:
- `itir-svelte/tests/fixtures/fact_review_wave1_real_au_demo_bundle.json`

This is a checked real workbench bundle, not a synthetic benchmark seed.

## Checked Artifact Now In Repo
Generated artifact directory:
- `SensibLaw/tests/fixtures/zelph/au_public_handoff_v1/`

Checked outputs:
- `SensibLaw/tests/fixtures/zelph/au_public_handoff_v1/au_public_handoff_v1.slice.json`
- `SensibLaw/tests/fixtures/zelph/au_public_handoff_v1/au_public_handoff_v1.summary.md`
- `SensibLaw/tests/fixtures/zelph/au_public_handoff_v1/au_public_handoff_v1.facts.zlp`
- `SensibLaw/tests/fixtures/zelph/au_public_handoff_v1/au_public_handoff_v1.rules.zlp`
- `SensibLaw/tests/fixtures/zelph/au_public_handoff_v1/au_public_handoff_v1.engine.json`
- `SensibLaw/tests/fixtures/zelph/au_public_handoff_v1/au_public_handoff_v1.scorecard.json`

## Current checked result
- 3 facts
- 27 observations
- 2 events
- 3 review queue items
- 1 contested item
- 2 approximate events
- 10 operator views
- Zelph engine status: `ok`

## Human-readable summary
The checked narrative summary already states, in prose, that the current slice
recovers:

- the House v The King appeal / hearing lane
- the Plaintiff S157 privative-clause challenge lane
- High Court ruling / ordered-to-proceed procedural outcome

It also states, explicitly, that the workbench still keeps this slice under
review rather than pretending it is fully settled.

## Scope / uncertainty statement
- This artifact is a **bounded AU handoff checkpoint**, not a complete AU corpus
  extraction claim.
- The 3-fact result is expected for this selected workbench wave; it does not mean
  AU extraction is that small overall.
- The real HCA hearing lane now has a separate dense transcript substrate
  artifact; that higher-density transcript layer is not the same thing as this
  bounded reviewed handoff slice.
- Out-of-scope for this artifact is broader AU transcript, longer-case history, and
  other source families that need additional source-family passes.
- This handoff is useful as a real ingest -> review -> Zelph story, and as a Mary-parity
  operator checkpoint showing review pressure on an AU legal procedure lane.
- Source lineage is tracked by `source_bundle_paths` and per-fact `source_bundles`.

## Rebuild / verification options
- single source (default):
  `cd /home/c/Documents/code/ITIR-suite && python SensibLaw/scripts/build_au_zelph_handoff.py`
- merge multiple real workbench source bundles:
  `cd /home/c/Documents/code/ITIR-suite && python SensibLaw/scripts/build_au_zelph_handoff.py --source-bundle itir-svelte/tests/fixtures/fact_review_wave1_real_au_demo_bundle.json --source-bundle itir-svelte/tests/fixtures/fact_review_wave1_real_au_demo_bundle_b0babf.json`

## Fixed Zelph questions
The current AU checked handoff answers two bounded questions:

1. Which facts in the AU slice are procedural facts?
2. Which facts remain under procedural review pressure?

These are implemented in:
- `SensibLaw/tests/fixtures/zelph/au_public_handoff_v1/au_public_handoff_v1.rules.zlp`

## Rebuild / verification
- rebuild:
  `cd /home/c/Documents/code/ITIR-suite && python SensibLaw/scripts/build_au_zelph_handoff.py`
- test:
  `cd /home/c/Documents/code/ITIR-suite/SensibLaw && ../.venv/bin/pytest -q tests/test_au_zelph_handoff.py`
  `cd /home/c/Documents/code/ITIR-suite/SensibLaw && ../.venv/bin/pytest -q tests/test_au_zelph_handoff.py -k \"supports_multi_source_bundles\"`

## Why this matters
This brings AU up to parity with GWB at the handoff shape level:

- both now have checked prose + JSON + ZLP + scorecard outputs
- both now have explicit completeness framing
- both can be discussed as scored checkpoints toward larger topic
  understanding, rather than as isolated demo files
- AU now also has a broader corpus diagnostics companion, so the repo can show
  both the checked handoff slice and the visible broader bundle/backlog state
  in one external reading path
- the real HCA hearing lane now also has internal structural and dense
  transcript substrate artifacts, so the repo can evaluate transcript density
  separately from the narrower reviewed Zelph handoff

## Related tracking
- scorecard + uncertainty framing:
  - `docs/planning/au_completeness_scorecard_20260324.md`
- Mary-parity checkpoint context:
  - `SensibLaw/docs/planning/mary_parity_acceptance_workbench_20260315.md`
