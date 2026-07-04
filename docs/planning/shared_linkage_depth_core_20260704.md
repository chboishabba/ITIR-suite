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
- lane-specific node/edge construction
- receipt attachment at the lane boundary
- CLI/domain compatibility wrappers

The core inherits contracts. It does not import climate, disjointness, GWB,
Brexit, AU, or affidavit geometry.

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

Brexit belongs to this bounded proving-ground family rather than the richer AU
authority family.

### AU

AU is the first semantically richer legal inheritor after the GWB smoke proof.

Planned contract path:

```text
source anchor
-> sentence/provision or event/legal-ref container
-> parsed legal/support surface
-> legal claim candidate
-> authority surface
-> legal-follow graph or review bundle surface
-> workflow/tranche anchor
```

The point is to prove instrument, jurisdiction, and authority depth, not just
queue depth.

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
