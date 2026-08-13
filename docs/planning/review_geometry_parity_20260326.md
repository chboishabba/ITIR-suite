# Review Geometry Parity (2026-03-26)

This note records the first cross-lane review-geometry parity state across AU,
Wikidata, and GWB. The point is not that the domains now mean the same thing;
it is that they now expose comparable operator-facing review surfaces:

- review items
- source review rows
- unresolved clusters
- cues / anchors
- ranked provisional rows
- bundled review queues

The current repo state is therefore:

- geometry parity: yes
- normalized metric parity: yes
- semantic parity: partial
- shared review-core extraction: not yet

The new additive comparison artifact for this layer is:

- `SensibLaw/tests/fixtures/zelph/review_geometry_normalized_summary_v1/review_geometry_normalized_summary_v1.summary.md`

The next useful move after this checkpoint is to use that normalized metric
layer to decide which workload/ranking primitives are stable enough to extract
into shared code.

## Wikidata checked review

Artifact:
- `SensibLaw/tests/fixtures/zelph/wikidata_structural_review_v1/wikidata_structural_review_v1.summary.md`

Reading:
- This is a compact structural review queue over `9` review items.
- The top unresolved items are not vague; they are:
  - `fixed_construction_contradiction`: `immaterial entity vs material entity`
  - `working_fluid_contradiction`: `gas vs liquid`
  - held hotspot pack `software_entity_kind_collapse_pack_v0`, with concrete
    questions:
    - `Is 'GNU' an instance of 'operating system'?`
    - `Is 'GNU' a subtype of 'Unix-like operating system'?`
  - qualifier drift case `Q100104196|P166`, summarized as:
    - `Qualifier drift for Q100104196|P166 at severity=medium from t1 to t2.`
- In plain terms: the checked Wikidata queue is already legible as a small set
  of named structural disputes and one governance-held hotspot.

## Wikidata dense review

Artifact:
- `SensibLaw/tests/fixtures/zelph/wikidata_dense_structural_review_v1/wikidata_dense_structural_review_v1.summary.md`

Reading:
- This expands the same `9` review items into `53` raw structural source rows.
- The top dense contradiction bundle is the fixed-construction chain:
  - `independent continuant (Q53617489) P2738 list of values as qualifiers (Q23766486)`
  - `geolocatable entity (Q123349660) P279 material entity (Q53617407)`
  - `spatial region (Q124711484) P279 immaterial entity (Q124711467)`
  - `region of space (Q26713767) P279 spatial region (Q124711484)`
  - `geographic entity (Q27096213) P279 geolocatable entity (Q123349660)`
  - `geographic entity (Q27096213) P279 region of space (Q26713767)`
  - `geographical feature (Q618123) P279 geographic entity (Q27096213)`
  - `fixed construction (Q811430) P279 geographical feature (Q618123)`
  - `framing (Q2131593) P279 fixed construction (Q811430)`
- The second contradiction bundle is the working-fluid case:
  - `fluid (Q102205) P2738 list of values as qualifiers (Q23766486)`
  - `working fluid (Q217236) P31 gas (Q11432)`
  - `working fluid (Q217236) P31 liquid (Q11435)`
- The dense hotspot-governance bundle is also concrete:
  - `software_entity_kind_collapse_pack_v0`
  - focus QIDs `Q44571`, `Q7598`
  - cluster families `edge_yes`, `edge_inv`, `kind_disambiguation`,
    `property_inheritance`
- In plain terms: dense Wikidata is now a real structural evidence queue, not
  just a status summary.

## GWB checked review

Artifact:
- `SensibLaw/tests/fixtures/zelph/gwb_public_review_v1/gwb_public_review_v1.summary.md`

Reading:
- This is much noisier than Wikidata because the row unit is event text, not
  structural case.
- The biggest unresolved checked cluster is
  `gwb_us_law:congressional_subpoena_litigation`.
- Its top bundle texts include:
  - `In 1978, Bush ran for the U.S. House of Representatives from Texas's 19th congressional district.`
  - `On March 10, 2008, the Congress filed a federal lawsuit to enforce their issued subpoenas.`
  - `In August 2006, a U.S. district court judge ruled that the NSA electronic surveillance program was unconstitutional, but on July 6, 2007, the ruling was vacated by the United States Court of Appeals for the Sixth Circuit on the grounds that the plaintiffs lacked standing.`
  - `On January 17, 2007, Attorney General Alberto Gonzales informed U.S. Senate leaders that the program would not be reauthorized by the President, but would be subjected to judicial oversight.`
  - `He was confirmed by the Senate on September 29, 2005. U.S. Senate Roll Call Votes – Nomination of John Roberts, senate.gov.`
  - `Representative Dennis Kucinich ... introduced 35 articles of impeachment ... against Bush on June 9, 2008 ...`
- Another top unresolved row is under `gwb_us_law:defense_executive_operations`:
  - `In May 1968, Bush joined the United States Air Force and was commissioned into the Texas Air National Guard.`
- In plain terms: the checked GWB queue still contains substantial topical
  bleed. The anchors are real, but many rows are only loosely linked to the
  intended seed lane.

## GWB broader review

Artifact:
- `SensibLaw/tests/fixtures/zelph/gwb_broader_review_v1/gwb_broader_review_v1.summary.md`

Reading:
- This is less about raw quoted events and more about cross-family review
  pressure.
- The top bundles are currently family-level pressure summaries:
  - `checked_handoff ambiguous_events=9 unresolved_surfaces=7`
  - `corpus_book_timeline ambiguous_events=144 unresolved_surfaces=91`
  - `public_bios_timeline ambiguous_events=10 unresolved_surfaces=12`
- Then the queue drops to lane/family support gaps such as:
  - `gwb_us_law:congressional_subpoena_litigation in corpus_book_timeline`
  - `gwb_us_law:defense_executive_operations in public_bios_timeline`
  - `gwb_us_law:genetic_information_nondiscrimination_act in corpus_book_timeline`
  - `gwb_us_law:military_commissions_2006 in public_bios_timeline`
  - `gwb_us_law:schip_veto in corpus_book_timeline`
- In plain terms: broader GWB is telling us where the multi-family extraction
  pressure sits, especially that `corpus_book_timeline` is the dominant
  unresolved workload source.

## Current read

- AU, Wikidata, and GWB now have review-geometry parity.
- They now also have one additive normalized metric vocabulary over source
  status, review-item status, workload pressure, and queue density.
- They do not yet have full semantic parity or a shared implementation core.
- A shared code core is therefore still not the first missing piece.
- The first remaining missing piece is deciding which normalized workload and
  queue primitives are stable enough to extract into a shared review-core.
- External Wikimedia grant/funding state is a separate question from this
  review-geometry parity note:
  - online check on 2026-03-26 confirmed open/active movement funding paths,
    but not a single clean global list of currently active Wikidata-specific
    grants
  - repo docs should therefore distinguish:
    - internal active diagnostics/review surfaces
    - external open/funded Wikimedia grant programs
