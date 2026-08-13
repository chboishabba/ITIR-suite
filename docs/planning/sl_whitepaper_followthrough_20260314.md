# SL Whitepaper Followthrough

## Source context
- Resolved with `robust-context-fetch`
- Title: `Insights from Whitepaper`
- Online UUID: `69b41f22-a514-839f-946c-fa0e9f75cc46`
- Canonical thread ID: `eab13fe32136bc69aebdb9a21888b76215faab11`
- Source used: `db` after pulling the online UUID into `~/chat_archive.sqlite`
- Refreshed after additional online tail posts; latest archived assistant turn at
  `2026-03-13T14:58:51+00:00`

## Purpose
Convert the archived whitepaper discussion into explicit planning constraints
for SensibLaw/ITIR so future implementation does not drift toward a flattened
RDF-only ontology.

## Ratified direction

### 1. Preserve SL's richer core graph
- SL already has a near-triple shape (`actor -> action -> target`), but the
  event node carries semantics that plain triples lose:
  - time
  - source / provenance
  - confidence
  - jurisdiction
  - observation linkage
  - legal consequences
- Therefore SL should not be remodelled as "just RDF".

### 2. Make Observation explicit
- Separate:
  - `event`: what is asserted to have happened
  - `observation`: a statement about that event
  - `source`: where the statement came from
- This is the missing abstraction that prevents:
  - source text from silently becoming truth
  - evidence and fact objects from collapsing together
  - later contradiction handling from becoming schema debt

### 3. Prioritize case-construction primitives over ontology growth
- The next major SL-facing capability is not broader ontology enumeration.
- Prioritize a first-class chain:
  - `source/excerpt -> observation -> event/fact -> norm -> claim`
- Claim objects and evidence links should remain provenance-first and
  reviewable.

### 4. Keep RDF/Wikidata as an adapter boundary
- RDF/Wikidata integration remains useful, but as:
  - export/projection
  - external-reference linking
  - interoperability
- It should not become the authority model for SL's internal legal semantics.
- When projecting outward, treat SL events/observations as reified or n-ary
  relations rather than collapsing them into lossy binary edges.

### 5. Avoid ontology explosion
- Prefer a lean primitive set with typed relations and attributes.
- Do not proliferate node classes for every doctrinal nuance when the nuance is
  better represented as:
  - relation qualifiers
  - norm metadata
  - temporal/jurisdiction constraints
  - claim/evidence linkage

### 6. Queue the hidden infrastructure gaps explicitly
- After the observation/case-construction seam is explicit, the next critical
  infrastructure gaps are:
  - legal versioning / temporal law evaluation
  - jurisdiction hierarchy and applicability

### 7. Treat legal reasoning as guarded state transitions
- The added tail posts sharpen the architectural direction:
  - legal reasoning is often expressible as
    `current legal state + new observation + applicable norm -> updated legal state`
  - this is closer to a typed transition system than a bag-of-facts graph query
- Design implication:
  - model SL/SL-reasoner reasoning steps as explicit state transitions with:
    - guards
    - receipts / traces
    - typed state deltas
    - provenance-preserving checkpoints
- "Reversible seams" is useful as a design target for auditability and local
  rollback/explanation, but should not be overstated as a literal property of
  all legal reasoning.

### 8. Explore p-adic / ultrametric similarity as a non-embedding path
- The refreshed thread adds a plausible retrieval/formalism direction:
  - use hierarchical doctrinal addresses or similar ultrametric structure for
    case similarity and clustering
  - avoid assuming vector embeddings are the default similarity surface
- Proposed use:
  - doctrine-aware nearest-neighbour retrieval
  - hierarchical clustering by jurisdiction / cause of action / posture /
    protected interest
  - explicit, auditable similarity explanations based on shared structure
- This remains exploratory and should be treated as a planning hypothesis until
  a bounded prototype exists.

### 9. Narrow the Wikidata prepopulation target
- The refreshed thread sharpens which Wikidata shapes matter most.
- Prioritize external-reference/prepopulation support for:
  - jurisdiction and territorial entities
  - courts and court hierarchies
  - legislation / statutory instruments
  - cases, citations, and court-of-decision metadata
  - actors/organizations where identity resolution is useful
  - temporal validity / amendment / succession style relations
- Deprioritize broad generic triple import that does not preserve the SL
  event/observation/provenance spine.

## Proposed execution slice

### Phase 1: contract ratification
- Define `Observation`, `Claim`, and evidence-link contracts in docs before
  implementation.
- Clarify which fields are deterministic SL responsibilities versus optional
  `SL-reasoner` derivations.
- Phase 1 is now contract-ratified in:
  - `docs/planning/sl_observation_claim_contract_20260327.md`

### Phase 2: projection boundary
- Define an RDF/Wikidata projection contract that preserves:
  - provenance
  - time validity
  - jurisdiction
  - confidence / observation status
- Make lossy projection explicit rather than implicit.
- Define a bounded Wikidata prepopulation contract around the high-signal shapes
  above rather than an open-ended ontology sync.

### Phase 3: implementation followthrough
- Add deterministic schema/read-model support for `Observation` and claim/evidence
  seams in SL-owned code.
- Keep temporal-law and jurisdiction wiring as the next follow-on milestone
  rather than scope-creeping this slice.

### Phase 4: exploratory formalism prototype
- Prototype one bounded similarity/reasoning lane using:
  - typed transition receipts for rule application
  - optionally a p-adic / ultrametric case-address experiment
- Success criterion:
  - explanation-first retrieval or state progression that is more auditable than
    opaque embedding similarity or unconstrained graph traversal

## Non-goals
- Replacing the internal SL model with RDF triples
- Expanding the ontology by adding large numbers of new node classes before the
  observation seam exists
- Treating derived claims as source-equivalent facts

## Immediate next action
- Treat this document as the planning source for the next SL architecture/spec
  pass and queue a bounded implementation milestone around:
  - observation layer contract
  - claim/evidence seam
  - RDF/Wikidata projection boundary
  - typed transition receipt surface
  - bounded ultrametric similarity prototype criteria
