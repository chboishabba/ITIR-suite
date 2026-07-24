# Shared Linkage-Depth Core

Date: 2026-07-04

## Purpose

Phase G.0 extracts the linkage-depth control-plane into
`SensibLaw/src/policy/linkage_depth.py`.

The purpose is not to make every lane look like Wikidata. The purpose is to
reuse one neutral contract/case/receipt/audit engine while letting each lane
keep its own typed ladder at the lane boundary.

## Boundary

Shared core owns:

- schema/version constants for contracts, cases, audits, and receipts
- generic contract builders/normalizers
- generic case builders/normalizers
- generic receipt builders/normalizers
- audit helpers for:
  - layer coverage
  - bridge completeness
  - typed path depth
  - anchor-to-terminal reachability
  - collapse points
  - collapse origin

Lane modules own:

- typed geometry
- lane-local composition over generic linkage adapters
- receipt attachment at the lane boundary
- CLI/domain compatibility wrappers

The core inherits contracts. It does not import climate, disjointness, GWB,
Brexit, AU, or affidavit geometry.

Invariant:

- the core audits
- the adapters emit
- the lane composes
- the wrapper attaches

That is how lanes become arbitrarily deep or rich without widening
`policy/linkage_depth.py`.

## First Three Families

### WD

Current WD adopters remain:

- climate review demonstrator
- disjointness report

Those stay as WD-specific case/receipt builders over the shared core.

### GWB/Brexit

The first non-WD adopter is `gwb_broader_review`.

First contract path:

```text
source follow anchor
-> legal-follow queue item
-> legal-follow claim/review candidate
-> operator authority/review surface
-> broader-review world-model surface
-> workflow/tranche anchor
```

WD stays optional enrichment here, not the native spine.

Phase G.2 now adds the first generic adapter-composition proof under:

- `SensibLaw/src/policy/linkage_adapters.py`
- `SensibLaw/src/policy/gwb_narrative_linkage.py`

Current narrative/timeline contract path:

```text
source anchor
-> source document container
-> timeline/event parse
-> relation/event candidate
-> narrative/timeline coalescence surface
-> authority/review surface
-> workflow/tranche anchor
```

The point is not a second bespoke GWB spine. The point is that the lane now
imports generic source/document/parse/claim/coalescence/authority/tranche
adapters and composes them into a deeper receipt. Optional Wikipedia/Wikidata
source enrichment stays additive rather than native.

Brexit belongs to this bounded proving-ground family rather than the richer AU
authority family.

Phase G.2 follow-ons now prove that the same adapter kit can carry different
lane-local ladders without widening the audit core:

- `SensibLaw/src/ontology/wikidata_superclass_linkage.py`
- `SensibLaw/src/policy/brexit_linkage.py`

Q43229 path:

```text
source discussion anchor
-> statement-edge candidate
-> counterexample cone
-> class-lattice pressure surface
-> repair candidate
-> community review surface
-> workflow/tranche anchor
```

Brexit archive/policy-intent path:

```text
archive source anchor
-> archive document container
-> parsed policy-intent surface
-> policy-intent claim candidate
-> review surface
-> archive authority surface
-> workflow/tranche anchor
```

Those are intentionally different ladders. The shared result is the audit
discipline, not a forced common lane geometry.

### AU

AU is the first semantically richer legal inheritor after the GWB smoke proof.

Phase G.1 now lands the first AU adopter under:

- `SensibLaw/src/policy/au_linkage_depth.py`
- `SensibLaw/src/policy/au_lane_receipts.py`

Current contract path:

```text
source anchor
-> legal text or event anchor
-> provision/legal-ref container
-> parsed legal/support surface
-> legal claim candidate
-> authority surface
-> fact-review bundle surface
-> workflow/tranche anchor
```

The point is to prove instrument, jurisdiction, and authority depth, not just
queue depth. The AU receipt now carries open-string metadata diagnostics for:

- `authority_boundary_visibility`
- `instrument_or_jurisdiction_visible`
- `candidate_vs_promoted_visibility`

### Affidavit

Affidavit is a separate contract family, not a subtype of AU/GWB/Brexit
legal-follow.

Planned contract path:

```text
proposition source anchor
-> normalized proposition
-> candidate response unit
-> reconciliation root or incident root
-> dominant relation decision
-> coverage/review surface
-> workflow/tranche anchor
```

The shared core therefore stays open enough for generic kinds such as:

- `response_candidate`
- `reconciliation_root`
- `relation_decision`
- `coverage_surface`

## Public Surface

In this tranche the public CLI stays stable:

- `sensiblaw wikidata linkage-depth` remains the compatibility command
- no generic top-level linkage-depth CLI is added yet
- GWB proof stays module/test-driven until AU also adopts the shared core
