# All-Sources FactBundle and Reconciliation Boundary (2026-03-28)

## Purpose
Record the broader direction clarified by the refreshed `ZKP Analysis
WikiProject CC` thread so the repo does not accidentally frame
`Observation`/`Claim` work as Wikidata-only or as if structured review is the
entire target surface.

This is a planning note. It sharpens the next generalization target without
changing the current executable contracts.

## Source Context
- resolved via `robust-context-fetch`
- title: `ZKP Analysis WikiProject CC`
- online UUID: `69c68d65-c674-83a0-928f-29b9090ea5d4`
- canonical thread ID: `072e992adca680787e6de88f1efe3aa0f69c3e92`
- source used: `db` after direct UUID pull into `~/chat_archive.sqlite`

## Main Decision
Treat the current `Observation` / `Claim` seam as the near-term canonical fact
surface, but keep the next generalization target explicit:

- the intended substrate is broader than Wikidata
- the intended substrate is broader than any one legal corpus
- the repo should be able to ingest and compare evidence-bearing surfaces from
  multiple source families under one bounded canonical bundle grammar

The safe reading is:

> move toward a universal `FactBundle`-style reconciliation layer over promoted
> observations/claims from all source families, not toward a Wikidata-shaped
> ontology that everything else must flatten into

## Boundary
### Upstream source families
- Wikidata / Wikipedia statement and revision surfaces
- legal corpora and case materials
- transcript / affidavit / declaration text
- logs and other revision-locked evidence substrates

### Canonical middle layer
- source-anchored `Observation`
- source-linked `Claim`
- deterministic evidence links / conflict links
- promotion / abstention / provenance rules

### Downstream
- projection/export lanes such as RDF/Wikidata
- comparison / contradiction / reconciliation workflows
- review packs and operator-facing diagnostics

## Implications
- do not describe the canonical fact layer as a Wikidata migration feature
  with some extra reuse potential
- do not collapse "observed ontology" into one source family
- keep projection lanes explicitly downstream of the canonical fact layer
- when a broader `FactBundle` contract is introduced, it should be framed as a
  general reconciliation bundle over promoted observations/claims rather than
  as a new hidden truth layer

## Immediate Followthrough
- keep `docs/planning/sl_observation_claim_contract_20260327.md` as the
  current canonical contract note
- treat a future `FactBundle` contract as the generalization target above that
  seam, not as a replacement for promotion/provenance discipline
- map current bounded lanes against that broader direction:
  - Wikidata migration review
  - transcript/freeform observation extraction
  - affidavit/declaration coverage review
  - AU/GWB semantic promoted-relation lanes

## Non-Goals
- not a claim that a universal `FactBundle` runtime already exists
- not a claim that all current source families already reconcile under one
  executable schema
- not permission to widen current runtime contracts without fresh docs/tests
