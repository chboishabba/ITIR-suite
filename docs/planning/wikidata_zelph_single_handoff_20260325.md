# Wikidata + Zelph Single Handoff (2026-03-25)

## Purpose
This is the first link to send to:

- the Wikidata Ontology Working Group
- the Zelph developer

It is the shortest repo-backed explanation of:

1. what we have already demonstrated
2. what direction we are taking next
3. what we are not claiming yet
4. why this work is useful to both audiences

## One-line summary
SensibLaw/ITIR turns messy source material into reviewed structured data with
source traceability, then exports small checked slices for two different jobs:
bounded Wikidata diagnostics and bounded Zelph reasoning.

## What already exists
### 1. Wikidata lane
What the repo already has:

- a bounded structural review pack for `P31` / `P279`
- 2 confirmed live SCC neighborhoods in the current review pack
- 2 confirmed current mixed-order neighborhoods in the current review pack
- 1 real imported qualifier-bearing baseline slice
- 1 bounded synthetic qualifier-drift fixture
- 2 repo-pinned live qualifier-drift cases:
  - `Q100104196|P166` (`2277985537 -> 2277985693`)
  - `Q100152461|P54` (`2456615151 -> 2456615274`)
- a parthood pilot pack under
  `SensibLaw/tests/fixtures/wikidata/parthood_pilot_pack_20260308/`
- an importer-backed parthood pack under
  `SensibLaw/tests/fixtures/wikidata/parthood_imported_pack_20260308/`

Primary repo surfaces:

- status note:
  `SensibLaw/docs/wikidata_working_group_status.md`
- checked handoff note:
  `docs/planning/wikidata_structural_handoff_v1_20260325.md`
- checked handoff artifact:
  `SensibLaw/tests/fixtures/zelph/wikidata_structural_handoff_v1/`
- review pass:
  `SensibLaw/docs/planning/wikidata_working_group_review_pass_20260307.md`
- report contract:
  `SensibLaw/docs/wikidata_report_contract_v0_1.md`
- tests:
  `SensibLaw/tests/test_wikidata_projection.py`
  `SensibLaw/tests/test_wikidata_finder.py`
  `SensibLaw/tests/test_wikidata_cli.py`

Plain-language reading:
- we can already turn live or imported Wikidata slices into deterministic
  review reports
- we are surfacing problematic structures and drift clearly
- we are not trying to auto-fix Wikidata from this repo
- we now also have one checked handoff artifact with the same
  summary/JSON/ZLP/scorecard shape already used for GWB and AU

### 2. Zelph lane
What the repo already has:

- a deterministic export proof from SensibLaw into Zelph:
  `SensibLaw/sl_zelph_demo/`
- a checked GWB public handoff with:
  - 19 promoted relations
  - 11 seed/review lanes
  - 9 ambiguous events
  - 7 unresolved discourse surfaces
  - Zelph engine status `ok`
- a first broader GWB checkpoint with:
  - 3 source families counted
  - 18 distinct promoted relations after canonical dedupe
  - 3 new promoted relations beyond the checked handoff
  - 5 seed lanes supported in multiple source families
- a first AU broader-substrate checkpoint status from real HCA:
  - dense-substrate run (`/tmp/au_real_round2_v2`) reports a 24-row reviewed
    hearing-event projection at 0.104751 reviewed-event ratio,
    currently triage-only quality until stronger continuity/date gating is added
- a checked AU procedural handoff with:
  - 3 facts
  - 27 observations
  - 2 events
  - 3 review queue items
  - 1 contested item
  - Zelph engine status `ok`
- corpus-level companion scorecards:
  - GWB:
    `SensibLaw/tests/fixtures/zelph/gwb_corpus_scorecard_v1/`
    `SensibLaw/tests/fixtures/zelph/gwb_broader_corpus_checkpoint_v1/`
    `SensibLaw/tests/fixtures/zelph/gwb_broader_promotion_diagnostics_v1/`
  - AU:
    `SensibLaw/tests/fixtures/zelph/au_corpus_scorecard_v1/`
    `SensibLaw/tests/fixtures/zelph/au_broader_corpus_diagnostics_v1/`

Primary repo surfaces:

- pack/index:
  `docs/planning/zelph_handoff_index_20260324.md`
  `docs/planning/zelph_real_world_pack_v1_6_20260325.md`
- GWB handoff:
  `docs/planning/gwb_zelph_handoff_v1_20260324.md`
- AU handoff:
  `docs/planning/au_zelph_handoff_v1_20260324.md`
- bridge/runtime code:
  `SensibLaw/src/zelph_bridge.py`
  `SensibLaw/scripts/zelph_runner.py`

Plain-language reading:
- we can already hand Zelph small checked fact bundles from real repo material
- those bundles include both "what we think is clean" and "what we are still
  keeping under review"
- the handoff is real, still intentionally bounded, and now extends beyond the
  original checked wiki slice into broader public-bios and corpus-book support

## What we are not claiming
- We are not claiming full ontology cleanup for Wikidata.
- We are not claiming full topic completeness for GWB or AU.
- We are not claiming Zelph should ingest raw text directly from our corpora.
- We are not claiming the current packs are the final collaboration contract.

## Intended direction
### Shared direction
Keep the boundary clean:

- SensibLaw/ITIR upstream:
  extract, normalize, review, and preserve source traceability
- Wikidata lane:
  produce bounded deterministic diagnostics and review packs
- Zelph downstream:
  reason over checked exported structure, not raw ingest

### Next for the Wikidata working group
- keep the work bounded and reproducible
- continue using importer-backed slices rather than hand-edited JSON
- grow the typed parthood/property lane carefully
- keep the focus on review support, not bot-style ontology correction
- treat the lane as domain-agnostic structural diagnostics, not only as a
  finance/property semantics exercise
- use software/project examples such as `GNU` / `GNU Project` alongside
  finance/product examples to show the same machinery catches entity-kind
  collapse across domains
- materialize the first checked `wikidata_structural_handoff_v1` artifact from:
  promoted hotspot exemplars, real disjointness packs, and the importer-backed
  qualifier baseline

### Next for Zelph collaboration
- keep using the existing checked export path rather than inventing a new one
- treat the current outward-facing pack as `v1.6`
- widen GWB beyond the current broader-source gains:
  repeated Supreme Court review confirmation,
  `George W. Bush -> signed -> No Child Left Behind Act`,
  `George W. Bush -> signed -> Northwestern Hawaiian Islands Marine National Monument`,
  and corpus-lane confirmation/review material including
  `George W. Bush -> ruled_by -> Supreme Court of the United States`
- widen AU beyond the narrow checked checkpoint via stronger reviewed-substrate
  promotion quality (actor continuity, chronology/date completeness, truncation
  checks) before expanding outward-facing breadth
- keep chat-history as a later lane only after hygiene/shareability is strong

## Why this is useful to each audience
### Value to the Wikidata Ontology Working Group
- The repo gives concrete, reproducible examples of structural problems instead
  of abstract complaints.
- It separates "diagnose and review" from "fix and govern", which makes the
  collaboration safer.
- It provides fixture-backed tests and report contracts that can be discussed
  repeatedly without live-query drift changing the conversation every time.
- It opens a practical pressure-test lane for parthood, qualifier drift, and
  mixed class/instance use.
- It can be extended into a bounded hotspot benchmark lane where every test
  cluster is justified by a visible structural pathology rather than by generic
  ontology flattening alone.

### Value to the Zelph developer
- The repo already provides checked graph-like inputs with source traceability.
- The handoff bundles include abstention and review pressure, not just forced
  answers.
- The current GWB slice is public and relatively safe to discuss externally.
- The broader GWB lane is no longer only a repeated-confirmation story; it now
  shows real public-bios and corpus-book widening while remaining conservative
  about overpromotion.
- The corpus-book lane now also independently confirms one already-checked
  stem-cell veto family via a memoir-rooted first-person legal-action path,
  which improves corpus credibility even though it does not change the deduped
  distinct-relation count.
- The AU slice shows the same handoff shape on a real procedural/legal bundle.
- The bridge is small enough to be testable now, while still pointing toward a
  richer later collaboration surface.

## Best reading order after this note
If the reader wants:

- Wikidata detail:
  `SensibLaw/docs/wikidata_working_group_status.md`
- Zelph pack detail:
  `docs/planning/zelph_real_world_pack_v1_6_20260325.md`
- concrete GWB artifact:
  `docs/planning/gwb_zelph_handoff_v1_20260324.md`
- concrete AU artifact:
  `docs/planning/au_zelph_handoff_v1_20260324.md`

## Bottom line
The exact current result is modest but real:

- bounded Wikidata diagnostics are working on real and pinned slices
- the repo now also has a concrete checked wiki/Wikidata handoff artifact
  parallel to GWB/AU
- bounded Zelph handoffs are working on checked GWB and AU artifacts
- broader GWB corpus work now widens the checked handoff with 3 new distinct
  promoted relations beyond the original checked slice
- both lanes are now backed by repo fixtures, tests, and explicit "not complete
  yet" framing

That is the collaboration offer:
small, honest, reproducible interfaces first, then broader coverage after the
bounded surfaces stay stable.
