# Zelph Real-World Pack V1.5 (2026-03-24)

## Purpose
Promote GWB into the outward-facing Zelph pack and bring AU up to the same
checked handoff shape.

Companion index:
- `docs/planning/zelph_handoff_index_20260324.md`

This pack supersedes the practical recommendation of `v1` while keeping the
earlier pack note historically useful.

## V1.5 changes
Relative to `v1`, this pack adds:

- the checked GWB public-entity handoff artifact
- the checked AU procedural handoff companion artifact

It keeps:
- deterministic DB/rule-atom bridge proof
- the real structured-import/Wikidata slice

## Canonical V1.5 contents
### A. Deterministic bridge proof
- `SensibLaw/sl_zelph_demo/compile_db.py`
- `SensibLaw/sl_zelph_demo/db_rules.zlp`
- `SensibLaw/sl_zelph_demo/db_run.sh`
- `SensibLaw/tests/test_sl_zelph_demo_tools.py`

### B. Checked AU procedural handoff
- `docs/planning/au_zelph_handoff_v1_20260324.md`
- `SensibLaw/tests/fixtures/zelph/au_public_handoff_v1/`

Why it matters:
- AU now has the same checked handoff shape as GWB
- the checked AU slice is built from the current real AU workbench bundle
- this is a reviewed handoff checkpoint, not a claim that the broader AU corpus
  or transcript scope has been exhaustively extracted

### C. Checked GWB public-entity handoff
- `docs/planning/gwb_zelph_handoff_v1_20260324.md`
- `SensibLaw/tests/fixtures/zelph/gwb_public_handoff_v1/`

Why it matters:
- public-entity reasoning is now checked, legible, and machine-readable
- GWB becomes the first outward-facing public-topic reasoning slice after v1
- this checked slice is narrower than the full GWB source inventory already in
  the repo and should not be mistaken for full topic closure

### D. Real structured-import slice
- `SensibLaw/tests/fixtures/wikidata/real_qualifier_imported_slice_20260307.json`

## Current recommendation
- treat this `v1.5` pack as the new outward-facing Zelph pack
- keep transcript-derived real bundles internal/next-pack candidates
- DONE: machine-readable GWB corpus scorecard over wider source families
- DONE: machine-readable AU corpus scorecard over persisted real workbench bundles
- next practical expansion:
  broader AU corpus completeness from fuller source-derived runs, or a safe
  chat-history lane

Current next implementation target:
- broader GWB public-source extraction checkpoint over:
  - checked handoff lane
  - public bios timeline lane
  - corpus/book timeline lane

Current result:
- DONE: first broader GWB extraction checkpoint now exists at
  `SensibLaw/tests/fixtures/zelph/gwb_broader_corpus_checkpoint_v1/`
- outcome:
  broader source families now widen promoted relation coverage beyond the
  checked handoff:
  `18` distinct promoted relations after canonical dedupe,
  `3` new distinct promoted relations beyond the checked handoff,
  and `5` seed lanes supported in multiple source families
- newly widened broader-source relation families currently include:
  `George W. Bush -> signed -> No Child Left Behind Act`
  `George W. Bush -> signed -> Northwestern Hawaiian Islands Marine National Monument`
  `George W. Bush -> ruled_by -> Supreme Court of the United States`

Current corpus-level companion artifacts:
- `SensibLaw/tests/fixtures/zelph/gwb_corpus_scorecard_v1/`
- `SensibLaw/tests/fixtures/zelph/au_corpus_scorecard_v1/`
