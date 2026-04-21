# Legal IR `Phi` Composition and Admissibility Boundary

Date: 2026-04-17

## Purpose

Pin the next repo-facing boundary above minimal `Phi` emissions so future legal
IR work does not blur:

- canonical normalized substrate
- candidate composition
- admissibility / promotion
- MDL / latent compression

This note is planning-first. It documents the intended control boundary and
worker lanes without claiming the full stack is already implemented end to end.

## Source Context

- source: internal planning/archive note, sanitized for repo-facing documentation
- specific chat/archive identifiers intentionally omitted
- adjacent governing notes:
  - `docs/architecture/admissibility_lattice.md`
  - `docs/planning/latent_state_over_promoted_truth_20260327.md`
  - `docs/planning/global_latent_legal_state_cross_system_20260327.md`
  - `docs/planning/phi_mapping_and_latent_graph_schema_20260328.md`

## Main Decision

The clean stack is:

```text
Phi -> composed candidate nodes -> admissibility -> promoted records -> derived graph
```

The hard boundary is:

- `Phi` is the minimal canonical normalized substrate
- composition above `Phi` binds multiple local emissions into one
  challengeable candidate node
- admissibility is the authority boundary that decides
  `promote | audit | abstain`
- MDL is not admissibility and is not promotion; it only names repeated stable
  shapes after or alongside admissible candidate signatures

So the repo should not read:

```text
Phi -> graph -> truth
```

and should not let MDL-style compression silently behave like a truth gate.

## Normalization Discipline

If this lane advances, keep the normalization surface small and canonical:

- emit the smallest cross-domain `Phi` atom set that preserves
  reconstructability
- keep `Phi` source-anchored and receipt-backed
- keep one canonical owner for composition semantics instead of spreading local
  ad hoc node-building logic across adapters
- keep one canonical owner for admissibility semantics instead of letting graph
  richness or ranking heuristics decide truth implicitly
- keep MDL / latent naming derived and replayable from candidate signatures
- never replace source anchors with graph-native identity
- never treat dense graph structure or cluster reuse as proof of admissibility

## Composition Contract Above `Phi`

Composition is the first coherence layer above local atoms. Its job is narrow:

> bind multiple local `Phi` emissions into one stable, referenceable candidate
> proposition/event node without creating truth by side effect

The candidate-node surface should preserve at least:

- `kind`
- `predicate_family`
- `slots`
- `content_refs`
- `authority_wrapper`
- `status`
- `support_phi_ids`
- `span_refs`
- `provenance_receipts`
- `section`
- `genre`

This keeps the candidate node reversible back to:

- source spans
- contributing `Phi` rows
- explicit provenance receipts
- wrapper/status evidence

## Admissibility Boundary

Admissibility must be wrapper-aware, provenance-hard, and fail-closed.

Node promotion should require at least:

- non-empty `span_refs`
- non-empty contributing `support_phi_ids`
- non-empty `provenance_receipts`
- valid authority wrapper for the claimed node kind
- slot/content consistency
- section/genre compatibility with the proposed edge and node kinds
- no contradiction with accepted constraints already above the candidate layer

Edge admissibility should remain separate and should require:

- admissible endpoint nodes
- typed edge compatibility
- support from explicit shared spans, receipts, or accepted constraints
- no section/genre shortcut that turns proposal language into authority

If those conditions fail, the output stays in candidate, audit, abstain, or
diagnostic space. It does not become canonical truth.

## MDL and Latent Naming Boundary

MDL operates over repeated candidate signatures such as:

- `content_refs`
- wrapper shape
- role structure
- stable qualifier patterns

MDL may help name recurring structures such as latent `authority_action`
families, but only under these rules:

- compression does not create admissibility
- compression does not erase source spans or receipts
- latent names remain challengeable back to candidate signatures
- promoted truth still depends on admissibility, not on cluster frequency

## Immediate Worker Lanes

Keep one owner per lane and avoid overlapping write surfaces.

### Lane 1: `Phi` substrate owner

- freeze the smallest canonical atom surface
- confirm source/span/receipt fields are sufficient for replay
- reject duplicate near-canonical emissions that belong in projection instead

### Lane 2: composition owner

- define the shared candidate-node contract above `Phi`
- centralize composition logic instead of scattering local node builders
- preserve authority wrapper, section, and genre constraints on the node

### Lane 3: admissibility owner

- formalize node and edge admissibility as explicit gates
- keep decisions fail-closed: `promote | audit | abstain`
- ensure graph/export consumers cannot bypass this gate

### Lane 4: MDL / latent owner

- operate only on candidate signatures and promoted outputs as allowed
- keep latent naming derived, replayable, and non-authoritative
- do not merge this lane into admissibility or source normalization

### Lane 5: verification and docs owner

- maintain fixtures and tests proving reversibility to spans and receipts
- keep README / TODO / context notes aligned with the actual boundary
- update downstream graph docs only when the canonical boundary changes

## Acceptance Read

This boundary is in good normalized shape when:

- `Phi` stays minimal and canonical
- composition is centralized and reversible
- admissibility remains the sole authority gate above candidates
- MDL remains derived rather than promotive
- downstream graph surfaces consume promoted records or explicitly labeled
  derived overlays, not mixed hidden truth
