# Latent State Over Promoted Truth (2026-03-27)

## Purpose
Define the safe repo reading of "latent state" so the phrase can be used for
global compression or reusable legal structure without creating a hidden
truth-bearing layer.

This note is planning-only. It does not introduce new runtime behavior.

## Source Context
- source: current working turn
- informed by the archived thread:
  - title: `Zero Trust Ontology`
  - online UUID: `69c68637-ca2c-839e-826c-f5e8a034ed2e`
  - canonical thread ID: `c2571b2b17183df38dd03704cf6e34f7bee44392`
  - source used: `db`
- adjacent governing notes:
  - `docs/architecture/admissibility_lattice.md`
  - `docs/planning/motif_candidate_promotion_legal_tree_20260327.md`
  - `docs/planning/jmd_sensiblaw_truth_construction_boundary_20260327.md`
  - `docs/planning/jmd_casey_mdl_contract_20260322.md`

## Main Decision
If the repo uses `latent state` language, the safe meaning is:

> a compressed, provenance-preserving, loss-bounded derived structure over
> promoted truth

and not:

- hidden truth inferred directly from raw text
- speculative ontology detached from promotion
- an authority layer that outranks promoted records

So the discipline is:

`latent_state = L(P)`

where `P` is already-promoted truth-bearing state.

## Pipeline Placement
The safe placement is:

`source -> annotation/signal -> candidate -> promoted -> latent/projection/reasoning`

This means:

- `latent_state` is downstream of promotion
- `latent_state` may support DASHI-style compression, motif reuse, conflict
  analysis, and proof-carrying transforms
- `latent_state` must not replace the promotion gate or silently feed truth
  back upstream

## Required Constraints
Any `L(P)` lane should satisfy all of the following.

### 1. Reconstruction
It must be possible to decode the structure back into the promoted basis it
claims to summarize, modulo explicitly declared loss bounds.

### 2. Anchor Preservation
Every latent node, edge, or derived subgraph must map back to:

- promoted records in `P`
- and, through them, source anchors in the substrate

### 3. Compression Discipline
The lane must justify why the latent structure is a real compression or
canonicalized reduction, not just a second copy of `P` with new names.

### 4. Consistency Preservation
The latent layer must not introduce contradictions that are absent from the
promotion-backed basis without surfacing them explicitly as conflicts or
diagnostics.

### 5. Downstream-Only Authority
`P` may justify `L(P)`, but `L(P)` does not by itself justify new truth in `P`
without going back through explicit review and promotion.

## Graph Reading
The intended reading is graph-like rather than strictly tree-like.

Typical latent graph elements may include:

- nodes for actors, obligations, conditions, events, references, or promoted
  motifs
- edges for implication, dependency, temporal order, jurisdictional relation,
  or cross-reference
- explicit constraints for consistency, precedence, and conflict handling

This remains acceptable only while it stays provenance-preserving and visibly
derived from promoted state.

## Motifs Inside Latent State
Motifs fit here only after the earlier discipline is respected:

- candidate motifs may exist below promotion
- only promoted or explicitly accepted motif-like structures may participate as
  reusable latent subgraphs
- global latent compression may reuse those promoted structures, but may not
  silently upgrade candidate motifs into truth

## DASHI / MDL Reading
`latent_state` is the right place for DASHI-style language if the repo wants:

- quotient / invariance / collapse over promoted structure
- MDL-governed transforms
- proof-carrying optimization of a promoted basis

But those transforms must remain:

- provenance-safe
- constraint-preserving
- explicitly reviewable
- non-authoritative with respect to new truth unless re-promoted

## Cohomology Reading
If cohomology language is used here, the safe reading is still analytical:

- connected components, cycles, or gluing failures over the latent graph
- conflict or ambiguity diagnostics
- structure discovery for review or optimization

It is not a substitute for promotion semantics.

## Non-Goals
- not a claim that a full latent graph schema already exists
- not a claim that the repo already has a complete decoder for `L(P)`
- not a claim that all motif reuse or transfer is formalized yet

## Followthrough
- if a future latent-state lane is proposed, require:
  - one bounded graph/schema note
  - one decode/reconstruction rule
  - one provenance-preservation rule
  - one explicit rule preventing latent outputs from acting as hidden truth
- if a prototype is built, start with:
  - promoted facts -> bounded graph
  - one motif reuse surface
  - one conflict-detection surface
  - no truth mutation from latent structure alone
