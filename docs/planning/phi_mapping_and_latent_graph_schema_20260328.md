# Phi Mapping and Latent Graph Schema (2026-03-28)

## Purpose
Pin the richer formal reading of cross-system `Phi` and `L(P)` graph structure
to the repo in a way that composes with the existing bounded `v1` executable
schema instead of pretending that the richer semantics are already implemented.

This note is planning-first. It defines the intended next formal layer over the
current machine-readable `sl.cross_system_phi.contract.v1` slice.

## Source Context
- source: current working turn
- informed by the same archived thread already resolved into the canonical
  archive:
  - title: `Zero Trust Ontology`
  - online UUID: `69c68637-ca2c-839e-826c-f5e8a034ed2e`
  - canonical thread ID: `c2571b2b17183df38dd03704cf6e34f7bee44392`
  - source used: `db`
- adjacent governing notes:
  - `docs/planning/global_latent_legal_state_cross_system_20260327.md`
  - `docs/planning/latent_state_over_promoted_truth_20260327.md`
  - `docs/architecture/admissibility_lattice.md`
  - `SensibLaw/schemas/sl.cross_system_phi.contract.v1.schema.yaml`

## Main Decision
Treat the current executable `v1` `Phi` schema as the conservative bounded
transport contract, and treat the richer `Phi` relation below as the next
formal semantics layer to be reconciled later.

That means:

- current executable `v1` status grammar remains:
  `exact`, `partial`, `incompatible`, `undefined`
- richer formal mapping kinds are documented now, but are not yet claimed as
  the shipped schema enum
- any migration from the bounded `v1` status grammar to richer relation kinds
  must be explicit and backward-safe

## Formal Definition of `Phi`
For legal systems indexed by `i, j in I`, let:

- `P_i` = promoted facts for system `i`
- `M_i` = promoted motifs derived from `P_i`
- `G_i` = typed legal graph built from `P_i`

Then define cross-system mapping as a typed relation over motifs or graph
fragments, not a plain function over raw nodes:

`Phi_ij : M_i x M_j -> MappingValue`

where:

- `kind`
- `score`
- `witness`
- `constraints`

and the richer intended kind set is:

- `exact`
- `refinement`
- `abstraction`
- `analogue`
- `conflict`
- `none`

The purpose of the relation is not to assert identity. It is to record:

- what relationship holds
- how strong it is
- what evidence supports it
- what constraints must hold before transfer is valid

## Compatibility with the Current Executable `v1`
The currently implemented schema is intentionally coarser:

- `exact` -> `exact`
- `refinement` / `abstraction` / `analogue` -> currently collapse into
  `partial`
- `conflict` -> currently represented by `incompatible`
- `none` -> currently represented by `undefined` or omitted candidate pairs

So the repo should read the richer model as `Phi vNext semantics`, not as a
claim that the current executable schema already exposes all of those
distinctions.

## Domain Restriction
`Phi_ij` should only be considered for motifs with coarse type compatibility.

Safe top-level compatibility examples:

- obligation <-> obligation
- liability <-> liability
- actor-role <-> actor-role
- procedure <-> procedure
- remedy <-> remedy

This means the mapping domain is already constrained before scoring begins.

## Mapping Score
The intended next scoring surface is a weighted combination of:

- role similarity
- predicate similarity
- causal similarity
- context similarity
- support overlap
- conflict penalty

The exact numeric weighting remains a future contract detail, but the repo now
records that `Phi` should be justified by structural/provenance evidence rather
than by vague semantic intuition alone.

## Transfer Rule
Cross-system transfer remains a guarded operation.

The safe rule is:

- transfer is allowed only for checked positive mapping kinds
- transfer must satisfy target-system constraints
- transfer must preserve provenance to the local promoted basis
- transfer never directly mutates local truth without explicit review and
  promotion

## Composition and Obstruction
The repo should expect weak composition only:

- pairwise mappings may compose imperfectly
- accumulated witness and mismatch penalties should remain visible
- non-gluing across `i -> j -> k` is a real diagnostic, not a bug to hide

This is the safe place for cohomology-style obstruction language:

- as a diagnosis of why pairwise mappings fail to glue
- not as a substitute for promotion, anchors, or explicit contradiction
  reporting

## Exact Graph Schema for `L(P)`
For one system:

`L(P_i) = G_i = (V_i, E_i, C_i, T_i)`

For the global multi-system case:

`L_global = (V, E, C, T, Phi)`

### Node Schema
Each node should carry at least:

- `id`
- `system_id`
- `node_type`
- `label`
- `payload`
- `provenance`
- `confidence`
- `temporal_scope`
- `jurisdiction_scope`

Safe initial node types include:

- `actor`
- `role`
- `action`
- `event`
- `fact`
- `motif`
- `rule`
- `obligation`
- `permission`
- `prohibition`
- `exception`
- `remedy`
- `sanction`
- `authority`
- `procedure`
- `document`
- `citation`
- `concept`

### Edge Schema
Each edge should carry at least:

- `id`
- `src`
- `dst`
- `edge_type`
- `payload`
- `provenance`
- `confidence`

Safe initial edge types include:

- `implies`
- `triggered_by`
- `caused_by`
- `refers_to`
- `cites`
- `modifies`
- `overrides`
- `conflicts_with`
- `exception_to`
- `analogises_to`
- `equivalent_to`
- `refinement_of`
- `abstraction_of`
- `precedes`
- `follows`
- `depends_on`
- `applies_to`
- `instantiated_by`
- `member_of`

### Constraint Schema
Constraints should be first-class objects, not comments.

Each constraint should carry at least:

- `id`
- `constraint_type`
- `scope`
- `expression`
- `provenance`
- `severity`

Safe initial constraint classes include:

- `type_constraint`
- `temporal_constraint`
- `jurisdiction_constraint`
- `cardinality_constraint`
- `exclusivity_constraint`
- `precedence_constraint`
- `deontic_constraint`
- `transfer_constraint`
- `consistency_constraint`

### Typing Discipline
The graph needs an explicit typing relation `T` over
`(node_type, edge_type, node_type)` so the latent graph cannot degrade into an
untyped bag of edges.

## Provenance Requirement
Every node and edge in the latent graph must map back to promoted records and,
through them, to source anchors.

That remains the non-negotiable rule that keeps the graph below the hidden
truth threshold.

## Prototype Correspondence
The intended prototype pipeline is now explicitly:

`P_i -> G_i -> M_i -> Phi_ij(M_i, M_j) -> conflict / transfer analysis`

Safe first prototype requirements remain:

- promoted facts only
- two systems only
- one small promoted motif family
- one checked mapping table
- one mismatch report

The prototype may be implementation-guided by a compact Python slice, but the
repo should still freeze the schema/typing/provenance rules before widening the
runtime surface.

## Followthrough
- keep the current `v1` executable schema as the bounded transport contract
- treat this note as the next formalization target for:
  - richer mapping kinds
  - witness structure
  - graph typing
  - provenance-preserving transfer rules
- if a `v2` schema is proposed later, it must explicitly explain how it
  relates to or supersedes the current bounded `v1` status grammar
