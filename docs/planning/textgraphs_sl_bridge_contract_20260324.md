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

Short doctrine:
- `TextGraphs` proposes
- `SensibLaw` promotes
- `Zelph` reasons

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

More explicitly:
- `TextGraphs` and `SensibLaw` overlap on tokenization, segmentation,
  lemma-capable paths, and deterministic preprocessing
- they do not enforce the same epistemic contract over outputs
- `TextGraphs` is an observational/derived layer
- `SensibLaw` canonical reducer outputs are the authority substrate
- `SensibLaw` spaCy outputs are auxiliary interpretation, not canonical

The architectural warning is:
- do not treat `SensibLaw`'s spaCy lane as equivalent to its canonical reducer
  lane
- doing so would blur evidence vs interpretation and weaken the promotion
  boundary

## Overlap Matrix
### Shared at the preprocessing level
- token sequence construction
- phrase/sentence-level segmentation
- lemma-capable paths
- deterministic baseline paths
- sliding-window or token-neighborhood analysis

### Present in `TextGraphs` but not in the SL canonical shared surface
- stemming as a first-class normalization path
- generic lemma/stem graph as a first-class product surface
- graph-native token/sentence metrics as the output surface itself

### Present in SL but not in `TextGraphs` as the main goal
- canonical span/provenance anchoring
- tokenizer profile/version contract
- legal/reference-aware token classes
- reversible lexeme and phrase atoms
- explicit promotion boundary before truth-bearing state exists

## Three-Layer Reading Inside SL
### 1. Canonical reducer lane
This is the supported cross-product authority surface.

Implemented in:
- `SensibLaw/src/text/deterministic_legal_tokenizer.py`
- `SensibLaw/src/text/lexeme_index.py`
- `SensibLaw/src/sensiblaw/interfaces/shared_reducer.py`
- `SensibLaw/docs/lexeme_layer.md`

Contract:
- deterministic
- span-safe
- reversible
- provenance-safe
- suitable for persistence, replay, and evidence anchoring

### 2. spaCy auxiliary lane
This is implemented and useful, but not the authority substrate.

Implemented in:
- `SensibLaw/src/nlp/spacy_adapter.py`
- `SensibLaw/src/text/sentences.py`

Contract:
- sentence segmentation, lemma, POS, dependency-style enrichment
- useful for semantic assistance, reports, candidate generation, and
  exploratory layers
- not the canonical reducer substrate

### 3. Promotion boundary
This is where SL decides what derived observations are allowed to mean.

Doctrine:
- canonical text/spans support evidence
- derived observations may inform candidates
- only promoted state becomes truth-bearing canonical record

## Interface Contract
The clean stack is:

`raw text -> SL canonical substrate -> derived observations -> SL candidates -> SL promotion -> Zelph reasoning`

Not:

`raw text -> TextGraphs graph -> Zelph facts`

The second path skips the authority boundary.

## Data Types
### Canonical substrate
Owned by `SensibLaw`.

Typical objects:
- document
- span
- token occurrence
- sentence
- lexeme occurrence
- reference anchor

Required invariants:
- reversibility
- stable provenance
- explicit tokenizer/reducer profile
- no semantic collapse by default

### Derived observation
Produced by `TextGraphs`, spaCy-style enrichment, or similar methods.

Typical outputs:
- co-occurrence edge
- lemma/stem cluster
- sentence/window participation
- graph metric
- candidate-support signal

These must remain explicitly non-canonical.

Minimal shape:

```json
{
  "id": "obs:1",
  "method": "textgraphs|spacy|rule_extractor|manual_review",
  "method_version": "v1",
  "input_refs": ["span:doc:start-end"],
  "output_type": "window_cooccurrence|lemma_cluster|graph_metric",
  "payload": {},
  "canonical_status": "derived_only"
}
```

### Semantic candidate
Owned by `SensibLaw`.

Typical outputs:
- candidate relation
- candidate entity merge
- candidate cluster
- candidate topic bridge

Contract:
- must cite canonical evidence refs
- may cite derived observations as support
- remains non-canonical until promoted

### Promoted semantic state
Owned by `SensibLaw`.

This is the first layer that downstream systems such as `Zelph` may safely
treat as fact-like.

Promotion requires:
- grounded canonical evidence
- complete provenance
- policy satisfaction
- explicit receipts

## Allowed Flows
Safe uses of `TextGraphs`-style outputs:

1. Candidate generation
   Derived graph structure may suggest candidate relations, candidate groups,
   or candidate cross-document/topic links.
2. Ranking signal
   Graph-derived observables may help rank or score candidates.
3. Review/inspection surface
   Graph projections may help operators inspect clusters, bridge terms, or
   anomaly regions.

In all cases:
- canonical evidence remains upstream authority
- graph outputs remain support, not truth

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

More concretely, never allow:
- stems or lemmas to become canonical identity by themselves
- co-occurrence or connectivity to become truth-bearing relation state by
  themselves
- graph-native ids to replace canonical source-anchored ids
- `Zelph` to consume raw graph observables as if they were already promoted
  facts

## Role of Stemming
`TextGraphs` has a stronger collapse tool in Snowball stemming, but not a
stronger authority layer.

Interpretation:
- stemming is stronger for graph compression and node merging
- stemming is weaker for semantic correctness and provenance preservation
- therefore stemming belongs in derived observation layers, not in the SL
  canonical substrate

The safe role of stemming is:
- candidate generator
- similarity layer
- clustering aid

Not:
- canonical identity
- provenance anchor
- promoted fact basis

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
- if cross-project experimentation needs text graphs, expose them as
  `derived_only` overlays rather than extending the SL canonical reducer
  contract
