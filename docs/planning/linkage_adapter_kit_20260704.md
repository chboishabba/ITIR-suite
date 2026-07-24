# Linkage Adapter Kit

Date: 2026-07-04

## Purpose

After Phase G.1, the next priority is not a growing list of bespoke lane
contracts. The next priority is a generic linkage-adapter layer so any lane can
compose arbitrary depth without widening the shared audit core.

Rule:

- the core audits
- the adapters emit
- the lane composes
- the wrapper attaches

Public naming rule:

- lane identity belongs in the module or selector
- public callable names stay generic

Examples:

- `nat.load_fixture(profile=...)`
- `brexit.build_report(...)`
- `au.build_report(...)`
- `gwb.attach_receipt(...)`

## First Kit

The first adapter kit lives in:

- `SensibLaw/src/policy/linkage_adapters.py`

Initial adapter fragments:

- source
- document
- parse
- claim
- coalescence/review
- authority
- external bridge
- tranche
- generic projection/collection fragments with lane-local layer labels

Each adapter emits standard linkage nodes/edges plus expected anchor or
terminal ids where appropriate. The adapters are intentionally open-string,
accept lane-local layer labels, and do not freeze a closed ontology.

## First Proof

The first adapter-composition proof is:

- `SensibLaw/src/policy/gwb_narrative_linkage.py`

It composes:

- source anchors across multiple source documents
- document containers
- timeline/event parses
- relation candidates
- coalesced narrative/timeline review surface
- operator authority surface
- workflow/tranche anchor
- optional Wikipedia/Wikidata external-source enrichment

The underlying `build_gwb_semantic_report(...)` surface remains receipt-free.
The lane wrapper attaches the receipt at the boundary through the shared
workflow helper.

## Next Proofs

The same adapter kit now also drives:

- `SensibLaw/src/ontology/wikidata_superclass_linkage.py`
- `SensibLaw/src/policy/brexit_linkage.py`

Q43229 composes:

- source discussion anchor
- statement-edge candidate
- counterexample cone
- class-lattice pressure surface
- repair candidate
- community review surface
- workflow/tranche anchor

Brexit archive/policy-intent composes:

- archive source anchor
- archive document container
- parsed policy-intent surface
- policy-intent claim candidate
- review surface
- archive authority surface
- workflow/tranche anchor

In both lanes the underlying report builders remain receipt-free and the
wrapper owns receipt attachment through lane-prefilled modules plus the shared
workflow helper.

## Follow-ons

Next adopters should prefer composition over hand-built ladders:

- AU:
  source + text/document + parse + claim + authority + review + tranche
- Q43229:
  source + statement + counterexample cone + lattice pressure + repair +
  review + tranche
- Brexit:
  source + document + parse + claim + policy surface + authority + tranche
- Affidavit:
  source + proposition + response + reconciliation + coverage + tranche

The shared core should only grow when all of those families need the same new
audit concept. It should not grow merely because one lane wants a richer
ladder.
