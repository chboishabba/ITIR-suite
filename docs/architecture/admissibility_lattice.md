# Admissibility Lattice

## Status
This note defines the intended repo-wide boundary doctrine for `SensibLaw` and
adjacent consumers. It reflects current architecture direction and existing
planning posture. It does not claim that every lane already enforces these
rules uniformly in code.

## Core Theorem
`SensibLaw` is a compiler-governed admissibility lattice in which:

- revision-anchored source forms the canonical substrate
- annotations, signals, and candidates are non-authoritative intermediate state
- promotion is the sole path to truth-bearing canonical records
- promoted records are immutable and may evolve only by explicit supersession
- downstream artifacts are typed projections over promoted records and source
  provenance
- every promoted record and downstream projection must be traceable to source
  anchors and promotion basis

## Record Lattice
```text
raw source anchor
  < annotation / signal
  < candidate
  < promoted record
  < projection / export artifact
```

This ordering is monotone:

- canonicality increases only through promotion
- projection does not create new truth-bearing canonical state
- candidate or overlay state must not bypass promotion by side effect

## Canonical Source Substrate
The substrate is source-anchored, revision-aware, and non-rewritable:

- revision-locked text or source object identity
- span and offset anchors
- source refs and provenance anchors
- minimal normalized atom layers such as `Phi` when they remain
  source-anchored, receipt-backed, and below promotion

This layer is canonical substrate, not promoted truth-bearing fact state.

## Canonical Promoted Layer
Truth-bearing canonical records begin only at promotion. Depending on lane,
this includes promoted, provenance-bearing families such as:

- `RuleAtom`-like records
- accepted observations
- accepted event records
- promoted semantic relations
- accepted mention/entity links where that lane supports promotion

Promoted records:

- are immutable
- may be versioned or superseded explicitly
- must not be silently rewritten in place

## Non-Canonical Intermediate State
The following are non-authoritative unless and until a lane promotes them:

- tokenization
- lemma, POS, and dependency output
- composition above local normalized atoms into proposition/event candidates
- co-occurrence, clustering, and similarity structures
- MDL or latent naming over candidate signatures
- `TextGraphs`-style measurement graphs
- candidate events
- candidate relations
- other derived analytical overlays

These layers may be recomputed. They may support review, diagnostics,
measurement, or candidate generation. They are not canonical truth stores.

If a lane uses `Phi` or similar minimal normalized atoms, the intended stack is:

```text
canonical substrate (`Phi`, spans, receipts)
  < composed candidate node
  < admissibility / promotion
  < derived graph or export artifact
```

Composition and latent naming do not create truth-bearing canonical state by
themselves.

## TextGraphs Boundary
`TextGraphs`-style layers are admissible inside the ecosystem only as
non-canonical, source-anchored analytical, diagnostic, or
candidate-producing overlays.

They may be useful for:

- text-surface measurement
- graph observables over tokens, lemmas, phrases, and windows
- comparative diagnostics
- candidate-signal production below promotion

They must not:

- define canonical facts by themselves
- replace source-anchored identity with graph-native identity
- bypass promotion or provenance requirements
- become a hidden truth layer for downstream reasoning

## Hard Invariants
- Raw source is never overwritten.
- Source-anchored identity is never replaced by derived graph identity.
- Promotion is the sole path to truth-bearing canonical records.
- Promoted records are immutable and evolve only by explicit supersession.
- Downstream artifacts are projections over promoted records plus provenance,
  not replacement truth stores.
- Source anchors and explicitly flagged non-canonical overlays may be consumed
  only as supporting or diagnostic material, not as truth-bearing input.

## Downstream Consumer Rules
Downstream systems such as `Zelph`, `StatiBaker`, reports, and graph/export
surfaces may consume:

- promoted records as truth-bearing input
- source anchors and provenance refs as supporting material
- explicitly typed non-canonical overlays as diagnostic/supporting material

They must not:

- treat candidate or overlay state as canonical by accident
- depend on opaque graph artifacts that cannot be traced back to source anchors
  and promotion basis
- mutate promoted records in place

## Proof Obligations
To claim conformity with this doctrine, a lane should satisfy:

1. Separation
   Substrate, annotation/signal, candidate, promoted, and projection layers
   are distinct in schema or lifecycle.
2. Monotonicity
   Canonicality increases only through promotion.
3. Traceability
   Promoted records and projections can be traced to source anchors and
   promotion basis.
4. Projection Discipline
   Downstream projections do not masquerade as replacement truth stores.

## Forbidden Shortcuts
- treating candidate layers as if they were accepted facts
- letting measurement overlays behave like canonical semantic state
- replacing source anchors with opaque graph ids
- mutating promoted records in place instead of superseding them
- judging bridge quality by graph richness alone without reversibility,
  provenance, and semantic usefulness

## Near-Term Formalization Work
The repo already points in this direction, but several areas still need tighter
formalization:

- globally typed lattice levels across lanes
- explicit promotion contracts
- explicit supersession semantics
- clearer consumer discipline at cross-project boundaries
- consistent labeling of non-canonical overlays
