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

Each adapter emits standard linkage nodes/edges plus expected anchor or
terminal ids where appropriate. The adapters are intentionally open-string and
do not freeze a closed ontology.

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
`src/policy/gwb_lane_receipts.py` attaches the lane receipt at the wrapper
boundary.

## Follow-ons

Next adopters should prefer composition over hand-built ladders:

- AU:
  source + text/document + parse + claim + authority + review + tranche
- Q43229:
  source + claim + lattice-pressure/coalescence + review + tranche
- Brexit:
  source + document + claim + narrative/policy surface + review + tranche
- Affidavit:
  source + proposition + response + reconciliation + coverage + tranche

The shared core should only grow when all of those families need the same new
audit concept. It should not grow merely because one lane wants a richer
ladder.
