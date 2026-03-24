# Zelph Real-World Pack V1 (2026-03-24)

## Purpose
Define the first canonical Zelph-facing pack built from real run-derived
ITIR/SensibLaw artifacts rather than synthetic benchmark seeds.

This pack is intended to prove three things at once:

1. SensibLaw/ITIR can operate on real material.
2. The resulting structures are reviewable and provenance-backed.
3. Zelph can consume bounded exported structure downstream without becoming the
   ingest authority.

## V1 decisions
- optimize in this order:
  - technical credibility
  - downstream reasoning value
  - safety
- include a safer 2-slice real pack now, plus the deterministic DB/rule-atom
  bridge proof
- do not include transcript-derived real bundles in the first canonical pack
- do not include synthetic benchmark seeds as demo evidence
- treat the canonical chat-history DB lane as phase 2
- allow logic-tree artifacts only as exploratory/refinement material for the
  future chat lane, not as the canonical first chat demo surface

## Canonical V1 contents
### A. Deterministic bridge proof
Primary surfaces:
- `SensibLaw/sl_zelph_demo/compile_db.py`
- `SensibLaw/sl_zelph_demo/db_rules.zlp`
- `SensibLaw/sl_zelph_demo/db_run.sh`
- `SensibLaw/tests/test_sl_zelph_demo_tools.py`

Why it is in v1:
- it is the cleanest proof that the repo can export structured atoms into
  Zelph deterministically
- it gives Zelph developers a stable bridge surface before any more ambiguous
  real-world material is introduced

### B. Real AU procedural review slice
Primary artifact:
- `itir-svelte/tests/fixtures/fact_review_wave1_real_au_demo_bundle.json`

Human-readable summary:
- one real `au_semantic` procedural run reopened through the fact-review
  workbench
- six acceptance stories pass:
  community legal centre intake triage, NGO case assembly, paralegal evidence
  pack preparation, solicitor case-theory prep, barrister chronology prep, and
  judge/associate procedural reconstruction
- the run contains 3 statements, 27 observations, 3 facts, and 2 approximate
  events
- the review queue stays small and interpretable:
  `Criminal appeal`, `Judicial review`, and `Orders`

Why it is in v1:
- strongest current balance of technical credibility, operator-story richness,
  and relative share safety

### C. Real structured-import slice
Primary artifact:
- `SensibLaw/tests/fixtures/wikidata/real_qualifier_imported_slice_20260307.json`

Human-readable summary:
- real imported Wikidata slice for property `P166`
- two windows over prior/current exports
- the first window contains 4 statement bundles with qualifiers, rank, and
  references preserved

Why it is in v1:
- adds a non-transcript, non-workbench real-data example
- shows the repo can preserve structured-import detail cleanly

## Ranked but excluded from canonical V1
### Real transcript candidates
- `itir-svelte/tests/fixtures/fact_review_wave5_real_professional_handoff_demo_bundle.json`
- `itir-svelte/tests/fixtures/fact_review_wave3_real_fragmented_support_demo_bundle.json`

Why excluded from v1:
- both are strong technically
- both are still higher-risk transcript-adjacent artifacts and need more
  careful sanitization/review than the AU slice
- they should remain ranked internal/next-pack candidates, not the first
  canonical external-facing examples

### Synthetic benchmark corpora
- `SensibLaw/tests/fixtures/fact_semantic_bench/*_seed.json`

Why excluded:
- useful for regression and calibration
- not acceptable as primary evidence when real run-derived artifacts already
  exist

## Commands and reproducibility
### Deterministic bridge proof
- run:
  `cd /home/c/Documents/code/ITIR-suite/SensibLaw && ../.venv/bin/pytest -q tests/test_sl_zelph_demo_tools.py -k "compile_db_smoke or compile_db_extended"`

### Real AU procedural review slice
- inspect:
  `cd /home/c/Documents/code/ITIR-suite && python -m json.tool itir-svelte/tests/fixtures/fact_review_wave1_real_au_demo_bundle.json`
- workflow regression:
  `cd /home/c/Documents/code/ITIR-suite/SensibLaw && ../.venv/bin/pytest -q tests/test_au_fact_review_bundle.py`

### Real structured-import slice
- inspect:
  `cd /home/c/Documents/code/ITIR-suite && python -m json.tool SensibLaw/tests/fixtures/wikidata/real_qualifier_imported_slice_20260307.json`

## Acceptance criteria for V1
- one doc and one manifest tell the same story
- every included artifact is real or real-imported, not synthetic
- every included artifact has at least one exact inspection or regression
  command
- the pack story is legible without opening unrelated repo areas
- transcript-derived artifacts are explicitly ranked but not silently mixed into
  the canonical first pack

## Immediate next artifact after V1
The next recommended Zelph-facing artifact after the canonical v1 pack is not
the chat-history lane. It is the public GWB handoff:

- public figure and public events
- lower privacy risk than transcript/chat material
- already backed by reviewed linkage seeds plus deterministic linkage and
  semantic report surfaces

Companion spec:
- `docs/planning/gwb_zelph_handoff_v1_20260324.md`

## Phase 2: Canonical chat-history lane
Goal:
- add the missing repo-stable real chat-history demo lane so the pack proves
  real-world generality across another source family

Canonical source family:
- actual chat-history DB slices

Preferred content profile:
- development workflow
- math/general reasoning
- public-event discussion

Requirements:
- one reviewed repo-stable artifact
- one human-readable summary
- one Zelph-facing export/query surface
- no dependence on synthetic `chat_archive` benchmark seeds for demo value

Logic-tree role:
- allowed only as exploratory/refinement material to help choose or compress
  the chat lane
- not the canonical first chat demo artifact
