# Zelph Real-World Pack V1.6 (2026-03-25)

## Purpose
Promote the corpus-level companion artifacts into the current outward-facing
Zelph pack without pretending that either GWB or AU is destination-complete.

Companion index:
- `docs/planning/zelph_handoff_index_20260324.md`

This pack supersedes `v1.5` as the current outward-facing pack.
Treat `v1.5` as the earlier checked-handoff milestone and `v1.6` as the first
pack that includes both checked handoffs and broader corpus companions.

## V1.6 changes
Relative to `v1.5`, this pack adds:

- the broader GWB checkpoint + diagnostics companions
- the broader AU diagnostics companion beside the AU corpus scorecard
- the clarified external framing that distinguishes:
  checked handoff, broader corpus accounting, and still-open backlog

It keeps:
- deterministic DB/rule-atom bridge proof
- checked GWB handoff
- checked AU handoff
- real structured-import/Wikidata slice

Freeze note:
- `v1.6` remains the current outward-facing pack
- newer internal corpus-expansion artifacts may exist in-repo without being
  added to the external pack until they are reviewed for sharing
- the first checked wiki/Wikidata handoff parity artifact may land in-repo
  beside `v1.6` without automatically changing the frozen pack boundary
  - this has now happened:
    `SensibLaw/tests/fixtures/zelph/wikidata_structural_handoff_v1/`

## Canonical V1.6 contents
### A. Deterministic bridge proof
- `SensibLaw/sl_zelph_demo/compile_db.py`
- `SensibLaw/sl_zelph_demo/db_rules.zlp`
- `SensibLaw/sl_zelph_demo/db_run.sh`
- `SensibLaw/tests/test_sl_zelph_demo_tools.py`

### B. Checked GWB handoff + broader companions
- `docs/planning/gwb_zelph_handoff_v1_20260324.md`
- `docs/planning/gwb_completeness_scorecard_20260324.md`
- `SensibLaw/tests/fixtures/zelph/gwb_public_handoff_v1/`
- `SensibLaw/tests/fixtures/zelph/gwb_broader_corpus_checkpoint_v1/`
- `SensibLaw/tests/fixtures/zelph/gwb_broader_promotion_diagnostics_v1/`
- `SensibLaw/tests/fixtures/zelph/gwb_corpus_scorecard_v1/`

Why it matters:
- GWB remains the cleanest public-facing handoff lane
- broader-source GWB is no longer just repeated confirmation:
  the public-bios and corpus/book lanes widen or independently confirm
  several checked families while staying provenance-first
- current merged broader checkpoint remains honest:
  `18` distinct promoted relations after canonical dedupe,
  `3` new distinct promoted relations beyond the checked handoff,
  and `5` seed lanes supported in multiple source families

### C. Checked AU handoff + broader companions
- `docs/planning/au_zelph_handoff_v1_20260324.md`
- `docs/planning/au_completeness_scorecard_20260324.md`
- `SensibLaw/tests/fixtures/zelph/au_public_handoff_v1/`
- `SensibLaw/tests/fixtures/zelph/au_corpus_scorecard_v1/`
- `SensibLaw/tests/fixtures/zelph/au_broader_corpus_diagnostics_v1/`

Why it matters:
- AU still has the same checked handoff shape as GWB
- AU now also has a broader corpus companion that makes the transcript-semantic
  lane and the visible raw transcript backlog explicit
- current broader AU checkpoint remains honest:
  4 real bundles,
  2 workflow kinds,
  13 facts,
  40 observations,
  11 review queue items,
  and 4 visible raw transcript files not yet promoted into persisted reviewed
  bundle coverage
- an internal-only AU transcript structural checkpoint now exists beside the
  pack, but it is not part of outward-facing `v1.6` until sharing review is
  complete:
  `SensibLaw/tests/fixtures/zelph/au_real_transcript_structural_checkpoint_v1/`
- an internal-only AU dense transcript substrate artifact now also exists
  beside the pack, likewise outside outward-facing `v1.6` until sharing review
  is complete:
  `SensibLaw/tests/fixtures/zelph/au_real_transcript_dense_substrate_v1/`
- latest internal dense-substrate reviewed-event projection (`/tmp/au_real_round2_v2`):
  24 reviewed items, `reviewed_event_ratio=0.104751`, used for quality-aware
  operator triage rather than promoted coverage claims

### D. Real structured-import slice
- `SensibLaw/tests/fixtures/wikidata/real_qualifier_imported_slice_20260307.json`

### E. Pending checked wiki/Wikidata parity artifact
- docs/spec note:
  `docs/planning/wikidata_structural_handoff_v1_20260325.md`
- artifact directory:
  `SensibLaw/tests/fixtures/zelph/wikidata_structural_handoff_v1/`

Why it matters:
- the wiki/Wikidata lane is now strong enough internally that the main missing
  piece is handoff legibility, not raw diagnostics
- this bounded parity task is now implemented in-repo, but it is intentionally
  not folded into frozen outward-facing `v1.6` yet

## Current recommendation
- treat this `v1.6` pack as the current outward-facing Zelph pack
- use the checked handoff artifacts when the audience needs a bounded exported
  fact slice
- use the broader companions when the audience asks “how real is this beyond
  the demo?”
- keep transcript-derived private or personal material outside the external
  pack until separately reviewed for sharing

## Practical reading
- GWB is now strong enough to carry the public-facing reasoning story
- AU is now less scattered because the repo shows both the checked slice and
  the broader bundle/backlog accounting in one pack
- the next real bottleneck is still corpus expansion, not another pack
  definition pass
