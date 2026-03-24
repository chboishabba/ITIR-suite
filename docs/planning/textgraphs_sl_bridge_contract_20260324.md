# TextGraphs x SensibLaw Bridge Contract (2026-03-24)

## Purpose
Define the safe borrowing boundary between `TextGraphs`-style text-surface
graph work and `SensibLaw`'s source-anchored admissibility lattice.

This note is not a claim that `TextGraphs` is a peer authority layer to
`SensibLaw`. It is a bounded bridge note describing:

- what `SensibLaw` may borrow from `TextGraphs`
- what `TextGraphs`-style work may borrow from `SensibLaw`
- which shared interfaces are admissible
- which crossovers are forbidden

Canonical architecture note:
- `docs/architecture/admissibility_lattice.md`

## Core Reading
The correct relationship is:

- `TextGraphs`-style layers are non-canonical analytical, diagnostic, or
  candidate-producing overlays over text surface
- `SensibLaw` is the source-anchored compiler and promotion boundary for
  truth-bearing semantic/provenance state

So:

- `TextGraphs` may enrich `SensibLaw` below promotion
- `SensibLaw` may discipline `TextGraphs` below canonicality
- neither should collapse the distinction between candidate state and promoted
  truth

## What SensibLaw May Borrow From TextGraphs
Admissible borrowing from `TextGraphs`-style work includes:

- token, lemma, phrase, and windowed graph observables
- co-occurrence and recurrence diagnostics
- clustering and similarity hints
- comparative graph measurements over anchored text units
- candidate-signal production for later review or promotion

These are admissible only as:

- annotation or signal
- candidate structure
- non-canonical diagnostic overlay

They must not arrive as already-accepted fact state.

## What TextGraphs-Style Work May Borrow From SensibLaw
Admissible borrowing from `SensibLaw` includes:

- source-anchor discipline
- revision-aware identity
- provenance-bearing refs
- separation between candidate state and accepted/promoted state
- explicit promotion and abstention semantics
- explicit supersession instead of silent mutation

This allows text-surface graph work to stay exploratory without pretending that
every measured edge or cluster is already canonical structure.

## Shared Interface Shape
A safe shared record should remain explicit about its layer and derivation.

Minimal shape:

```json
{
  "source_ref": "doc:revision:start-end",
  "layer": "annotation|signal|candidate|projection",
  "derivation_method": "textgraphs|spacy|rule_extractor|manual_review",
  "payload_type": "lemma_cluster|cooccurrence_edge|candidate_relation|projection",
  "canonical": false
}
```

If a downstream lane needs truth-bearing canonical state, it must consume a
promoted `SensibLaw` record instead of this shared overlay form.

## Allowed Bridge Shapes
Safe bridge patterns include:

1. Source-anchored measurement overlay
   `TextGraphs`-style observables over anchored text units for operator review,
   diagnostics, or comparison.
2. Candidate producer
   A `TextGraphs`-style layer may emit candidate relations, candidate groups,
   or candidate signals for later `SensibLaw` review/promotion.
3. Projection consumer
   `TextGraphs`-style tooling may render graph projections over already
   promoted `SensibLaw` records as long as the projection is explicitly typed
   and does not replace canonical identity.

## Forbidden Crossovers
The bridge must not allow:

- `TextGraphs` edges or clusters to become canonical fact state without
  promotion
- graph-native ids to replace source-anchored ids
- downstream reasoning to depend on opaque `TextGraphs` artifacts as if they
  were promoted truth
- graph richness, connectivity, SCC lift, or centrality movement to count as
  success by themselves
- silent mutation of promoted records based on downstream graph analysis

## Bridge Success Criteria
A useful bridge is not "we made a graph".

The bridge should first prove:

- one canonical source anchor or source object identity
- one reversible or traceable mapping into the graph/overlay surface
- one explicit distinction between overlay/candidate state and promoted state

Only then should it optimize for richer observables, and those should be judged
by whether they reveal:

- semantic drift
- provenance tension
- chronology tension
- repeated or cluster structure that matters to review

not merely whether they make the graph denser or more visually interesting.

## Relationship to Other Bridge Notes
- `docs/architecture/admissibility_lattice.md`:
  repo-wide source/candidate/promoted/projection doctrine
- `docs/planning/jmd_sl_corpus_bridge_contract_20260319.md`:
  read-safe external object graph -> SL corpus bridge
- `docs/planning/jmd_triage_roadmap_20260320.md`:
  staged rollout and conservative-first bridge policy

## Near-Term Followthrough
- keep `TextGraphs`-style work explicitly below promotion in docs and adapters
- add typed layer labels where graph/signal outputs are currently near-canonical
- prefer source-anchored comparison fixtures over generic "graph quality"
  claims
- add bridge examples only when they preserve source identity and make the
  candidate/promoted split inspectable
