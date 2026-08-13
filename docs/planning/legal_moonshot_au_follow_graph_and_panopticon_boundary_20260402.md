# Legal Moonshot: AU Follow Graph and Panopticon Boundary

Date: 2026-04-02

## Purpose

Reframe the next legal-expansion round so it advances the broader ITIR
moonshot without drifting into surveillance, predictive judgment, or hidden
authority claims.

The long-range target is large:

- understand laws across jurisdictions and languages
- compare them structurally
- find commonalities, disjoint regions, and transfer limits
- emit reviewable products rather than magical conclusions

But the safe near-term shape stays bounded:

- evidence bundle in
- promoted outcomes or abstentions out
- derived packet/report/graph surfaces after that

## Main Decision

Treat AU legal expansion as the first serious legal compiler adopter after the
shared compiler contract, AU/GWB product normalization, product gate, and
workflow slice.

That means the next AU/legal work should focus on:

1. case follow and authority follow
2. supporting legislation / cited instrument understanding
3. derived legal-follow graph surfaces
4. explicit governance against panopticon drift

Not on:

- predictive decisionmaking
- hidden identity resolution
- declaring a single canonical interpretation of a legal history
- silently promoting graph overlays into truth

## AU Read

The AU lane already has most of the necessary substrate:

- bounded AustLII / JADE / citation-follow seams
- AU semantic linkage
- authority follow receipts
- compiler contract + promotion gate
- fact-review workbench + workflow summary

What is missing is one normalized derived legal-follow surface that makes
authority, citation, legal-reference, and support relationships inspectable
without pretending they settle doctrine automatically.

## Bounded Implementation Slice

The next bounded slice should add one AU legal-follow graph derived from the
already-emitted AU semantic context.

Safe graph contents:

- event nodes
- authority-title nodes
- legal-reference nodes
- citation nodes
- authority-receipt nodes
- explicit typed edges showing:
  - event mentions authority
  - event mentions legal reference
  - event mentions citation
  - event resolved to authority receipt
  - authority receipt supports event

Safe graph posture:

- derived only
- challengeable
- optional
- not a truth layer

## Global-Law Moonshot Read

The moonshot can still be ambitious:

- graph-union across legal systems
- commonality and disjointness mapping
- basin-like clustering over promoted legal products
- international law / UN / conflict / cyber and adjacent lanes later

But those should be built from promoted, bounded products rather than from
open-ended free-text inference.

So the reusable pattern remains:

- source-grounded evidence
- typed extraction
- promotion / abstain gate
- derived graph and comparison layers
- explicit transfer constraints

## Progress Read

Current rough read:

- recent legal/compiler program: roughly `70-80%`
- broader legal-moonshot preparation: roughly `35-45%`
- full end-state moonshot: roughly `15-25%`

Why it is still far from the end state:

- follow depth is still shallow
- cross-jurisdiction union is only just starting
- cross-language work is barely started
- legal-role understanding remains partial and bounded
- global commonality / disjointness / basin analysis is not yet a mature
  operator surface

## Full Flow At Moonshot

The intended end-state flow is:

1. evidence intake from bounded legal and law-adjacent sources
2. canonicalization of source identity, anchors, jurisdiction, language, and
   provenance
3. typed extraction of legal and factual observations with uncertainty and
   conflict preserved
4. bounded follow planning over cases, statutes, delegated instruments,
   parent legislation, treaty articles, implementing domestic law,
   institutional acts, and justified cross-jurisdiction links
5. bounded follow execution, with each hop explicitly justified and
   attributable
6. promotion / abstain / hold over reviewable legal products
7. derived graph construction for legal follow, dependency, comparison,
   institutional interaction, and conflict surfaces
8. graph union across jurisdictions, languages, institutions, legal families,
   and time
9. analysis over commonality, disjointness, inherited doctrines,
   implementation chains, dependency basins, contradiction zones, and
   possible resolution pathways
10. operator workflow over why each node exists, what supports it, what is
    uncertain, and what follow remains outstanding
11. product emission as packets, reviews, comparison reports,
    conflict-resolution maps, and other bounded downstream outputs
12. governance through replayable audit, explicit abstention, and
    anti-panopticon controls

This is not “legal omniscience.” It is a compiler-like, evidence-grounded,
provenance-backed, reviewable legal-union system.

## Anti-Panopticon Boundary

Legal expansion does not relax the existing refusal posture.

The following remain prohibited:

- predictive scoring of judges, officials, parties, or communities
- hidden global identity resolution across legal and non-legal domains
- surveillance-style central memory authority
- person-risk forecasting
- graph outputs framed as verdicts

Allowed surfaces are descriptive, reviewable, and bounded:

- source-grounded authority follow
- cited-instrument and supporting-legislation mapping
- competing interpretation display
- explicit abstention when evidence is insufficient

## Red-Team Requirement

This moonshot lane now requires explicit anti-panopticon red-team coverage.

At minimum, red-team docs should test for:

- hidden authority promotion from support material
- predictive or evaluative language on people
- cross-context identity stitching
- graph-overclaim that turns support edges into conclusions
- silent collapse of disagreement or uncertainty

## Worker Split

One bounded lane per worker:

- Ramanujan:
  shared legal evidence-bundle -> promoted-outcome contract refinement only
  where needed for AU/legal follow surfaces
- Erdos:
  AU case follow / supporting-legislation / cited-instrument product
  normalization
- Lorentz:
  GWB legal-linkage follow surfaces under the same compiler rule
- Euler:
  minimal shared primitive/comparison support for legal-follow products
- Ohm:
  derived legal/case-follow graph discipline, optional and challengeable
- Huygens:
  anti-panopticon, abstain, and audit gate hardening for legal graph outputs

## Immediate Next Slice

Implement one AU derived legal-follow graph inside the existing fact-review
bundle semantic context, then validate that:

- it is sourced only from existing authority receipts / legal refs / citations
- it does not widen truth claims
- it behaves as a derived product under the compiler contract

## Status

Landed on 2026-04-02.

Implementation result:

- `SensibLaw/src/policy/legal_follow_graph.py` now builds one bounded AU
  legal-follow graph from existing authority receipts, legal refs, and
  citation hints
- `SensibLaw/src/au_semantic/semantic.py` now enriches AU authority-receipt
  context with:
  - `legal_ref_details`
  - `candidate_citation_details`
  - legal-ref class counts
- `SensibLaw/src/fact_intake/au_review_bundle.py` now emits:
  - `semantic_context.legal_follow_graph`
  - `operator_views.legal_follow_graph.summary`
- `SensibLaw/src/policy/compiler_contract.py` now records
  `legal_follow_graph` as an explicit derived AU product

Current bounded read:

- case-like refs remain visible as `case_ref`
- Act/statute-style refs are surfaced as `supporting_legislation`
- instrument/regulation-style refs are surfaced as `cited_instrument`
- graph output remains derived-only and challengeable

Validation:

- focused gate: `19 passed`
- touched modules: `py_compile` clean

## Next Likely Lane

Keep the next AU/legal slice bounded:

- improve cited-instrument / supporting-legislation attachment depth
- surface the derived legal-follow graph in the operator workflow only after
  the current bounded graph proves stable enough to inspect

## Dual-Slice Decision

The current bounded round does both, but in the narrowest safe form:

1. deepen AU supporting-legislation / cited-instrument attachment provenance
2. surface the derived legal-follow graph in the fact-review operator workflow
   as a read-only inspection surface

The UI cut stays constrained:

- derived-only
- summary + inspect surface only
- no claim of canonical legal interpretation
- no promotion of graph edges into truth

Status:

- landed
- AU legal-follow graph now reports bounded supporting-receipt and
  supporting-authority-kind counts in its summary
- AU authority receipts and follow-queue payloads now also carry bounded
  jurisdiction-hint and instrument-kind semantics for attached legal refs
- AU legal-follow graph now preserves those same jurisdiction/instrument
  hints on supporting-legislation and cited-instrument nodes and edges, and
  reports bounded summary counts for them
- the fact-review workbench now surfaces that graph as a read-only derived
  inspection pane:
  - summary card
  - authority/receipt list
  - ref/citation list
  - typed-link list
  - bounded distribution grids when the derived graph exposes distribution
    counts
- focused AU/legal/compiler gate: `21 passed`
- frontend check remains blocked only by pre-existing unrelated
  `wiki-timeline-aoo-all` errors

## Cross-Lane Follow-Through

The same compiler-shaped rule now also applies to GWB legal-linkage review
products.

Bounded landed cut:

- `SensibLaw/src/policy/gwb_legal_follow_graph.py` adds one derived GWB
  legal-linkage graph helper
- `gwb_public_review` and `gwb_broader_review` now emit
  `legal_follow_graph`
- the existing GWB review summaries now expose that graph in a bounded
  read-only way via a "Derived Legal-Linkage Graph" section
- the fact-review workbench typing/surface can now also display bounded
  distribution counts when a legal-follow graph exposes them, which keeps the
  GWB parity path aligned with the AU read-only graph posture
- the GWB compiler contract now lists `legal_linkage_graph` as an explicit
  derived product for those review outputs

Current read:

- this is parity in product shape, not parity in legal semantics
- GWB does not pretend to have AU-style case-follow depth
- the graph remains derived-only, challengeable, and non-authoritative

## Latest Follow-Through

Bounded landed cut:

- AU legal-follow summaries now expose one more typed layer without widening
  authority claims:
  - `reference_kind_counts`
  - `reference_class_counts`
  - `ref_kind_counts`
  - `edge_kind_counts`
  - `edge_reference_class_counts`
  - `edge_ref_kind_counts`
  - `supporting_legislation_role_counts` surfaces enabling/constraining/procedural/amending roles
- `authority_follow` queue items and summaries now also expose
  `ref_kind_counts`
- GWB review markdowns now include a bounded read-only graph inspection layer:
  - `Graph inspection`
  - `Sample typed links`

Read:

- AU is now slightly deeper semantically at the attachment/provenance layer
- supporting legislation role counts now make enabling/constraining/procedural links visible
- GWB is now more inspectable for operators without inventing a fake GWB
  workbench or overstating semantics
- both lanes still obey the same compiler-shaped rule:
  - evidence in
  - promoted/review products out
  - derived graph after that

Validation:

- focused Python gate: `25 passed`
- touched modules: `py_compile` clean

## Latest Follow-Through 3

Bounded landed cut:

- AU supporting-legislation nodes now keep one more inspectable semantic layer:
  - `supporting_legislation_roles`
  - `supporting_legislation_role_counts`
- current role recovery is intentionally narrow:
  - enabling
  - constraining
  - procedural
  - delegated-instrument parent
  - amending
- GWB legal-linkage follow now has one bounded followed-source receipt seam
  when review rows already carry HTTP links:
  - followed-source nodes are derived from receipt URL material already in hand
  - no open-ended crawling was added
  - no promotion or truth-boundary widening was added
- GWB fact-review operator parity is now real:
  - the existing workbench renders one bounded read-only
    `operator_views.legal_follow_graph` block for GWB workflows
  - summary, highlight nodes, and sample typed links are visible without
    implying AU-style legal semantics

Program read:

- this legal moonshot is now a normal program lane, not a speculative side note
- AU remains the semantically richer legal lane
- GWB now has both artifact-level and operator-level legal-follow surfaces
- AU should now also permit one bounded cross-jurisdiction follow hop when
  existing AU evidence explicitly points to UK/British authority, legislation,
  or inherited instrument lineage
- the next GWB widening should stay concrete and review-first:
  - followed-source receipts from selected article/source links
  - then subject expansion where legal consequences are visible in public
    source geometry

Named bounded proving grounds:

- AU -> UK/British follow:
  - one explicit cross-jurisdiction hop when current AU evidence already points
    there
  - useful for inherited-instrument, cited-authority, and supporting-law
    lineage
- Brexit legal-union proving ground:
  - treat Brexit-era UK/EU legal interaction as a first-class bounded legal
    union testbed, not just a subject-cohort example
  - useful because UK domestic law, EU-derived law, institutional procedure,
    and later divergence pressure are all visible in public legal/source
    geometry
  - keep it bounded to reviewable products, not personality-led coverage

Suggested bounded GWB subject cohorts:

- previous US presidents where executive action, litigation, and institutional
  response create legible legal-follow pressure
- controversial UK Brexit-era politicians where UK/EU legal interactions make
  legal-linkage and supporting-instrument follow especially visible

Boundary reminder:

- these cohort suggestions are for bounded review surfaces and legal-follow
  pressure, not for personality-led expansion or surveillance-style coverage
- anti-panopticon doctrine remains load-bearing here
- bounded AU -> UK/British follow means:
  - one explicit justified hop only
  - provenance-backed
  - derived-only
  - review-first
  - no broad common-law ancestry crawl
- `npm run check` still fails only on the pre-existing unrelated
  `itir-svelte/src/routes/graphs/wiki-timeline-aoo-all/+page.svelte` errors

## Latest Follow-Through 2

Bounded landed cut:

- AU legal-follow semantics are now slightly deeper on the citation side:
  - graph summaries now also expose `citation_court_hint_counts` and
    `citation_year_counts`
  - `authority_follow` queue items and summaries now also expose those same
    citation-court and citation-year counts
- GWB now has a real JSON operator-view surface over its derived legal-linkage
  graph:
  - `operator_views.legal_follow_graph.available`
  - `operator_views.legal_follow_graph.summary`
  - `operator_views.legal_follow_graph.highlight_nodes`
  - `operator_views.legal_follow_graph.sample_edges`

Read:

- AU keeps getting semantically richer without widening beyond derived,
  challengeable legal-follow products
- GWB now has bounded operator-surface parity beyond markdown-only exposure,
  but still without pretending AU-style legal understanding
- Brexit should now be treated as the clearest named bounded GWB legal-union
  proving ground rather than only as an example cohort

## Latest Follow-Through 4

Bounded landed cut:

- AU now derives one explicit UK/British follow target when current authority
  receipts, ref detail, or citation detail already point there
- that target remains:
  - derived-only
  - provenance-backed
  - review-first
  - non-recursive
- GWB followed-source URLs now surface explicit legal-cite classes in the
  derived legal-linkage graph
- GWB legal-linkage summaries now also expose bounded Brexit-related follow
  counts when the followed-source URL/text already carries that pressure

Read:

- AU now has the first real bounded cross-jurisdiction follow surface without
  widening into ancestry crawl
- GWB Brexit/legal-cite follow is still URL/classification-based, not live
  crawling, which keeps the lane review-first and anti-panopticon-safe

## Latest Follow-Through 5

Bounded landed cut:

- GWB legal-linkage can now seed followed-source receipts from the canonical
  foundation-source catalog when a review row already names a known UK/EU legal
  source
- this is still bounded and derived-only:
  - no live fetch
  - no speculative crawl
  - no doctrinal overclaim
- the first seeded proving-ground path covers named Brexit-relevant sources such
  as:
  - European Union (Withdrawal) Act 2018 (UK)
  - European Union (Withdrawal Agreement) Act 2020 (UK)
  - Treaty on European Union

Read:

- GWB Brexit follow is now more than passive URL classification
- it has a bounded legal-cite seeding path from named legal sources already
  recognized by the repo

Validation:

- focused Python gate: `25 passed`
- touched modules: `py_compile` clean
