# ITIR x SensibLaw Receipts-First Compiler Spine (2026-03-28)

## Purpose
Pin the strongest common architectural reading across the current ITIR and
SensibLaw materials:

- deterministic extraction first
- explicit promotion boundary second
- symbolic/typed reasoning third
- public-action packaging last

This note is architecture-first. It does not introduce a new runtime contract.
It clarifies what the repo should treat as the main spine when choosing new
modules, schemas, and milestones.

For the related identity/trust refinement, see:
`docs/planning/itir_sensiblaw_identity_trust_alignment_layer_20260328.md`.

## Main Decision
Treat ITIR/SensibLaw as a receipts-first compiler system with a hard promotion
boundary and a soft reasoning boundary.

That means:

1. extraction is not promotion
2. promotion is not reasoning
3. reasoning is not public messaging
4. public outputs must remain receipt-backed and downstream of promoted truth

The system should be organized around five layers.

## Five-Layer Split
### 1. Source substrate
Raw text, OCR cleanup, spans, offsets, document structure, revisions, and
citation anchors.

Typical objects:
- `SourceDocument`
- `SpanAnchor`
- `CitationAnchor`
- `DocumentRevision`

### 2. Deterministic extraction
Rule/FST-first extraction into typed clause/candidate atoms.

Typical outputs:
- `ClauseCandidate`
- modality/actor/action/condition/exception/penalty/reference atoms
- char-span anchored receipts for every extracted field

This is the compiler front end.

### 3. Promotion boundary
Candidate facts are not truth yet.
Promotion creates the canonical truth layer, with abstention and conflict sets
preserved explicitly.

Typical objects:
- `CandidateFact`
- `PromotionDecision`
- `PromotedFact`
- `Abstention`
- `ConflictSet`
- `ProvenanceWitness`

This is the architectural center of the system.

### 4. Reasoning / graph layer
Typed graph, symbolic traversal, treatment tables, proof trees, checklist
evaluation, temporal queries, and doctrine/factor relations.

Embeddings may rank or assist candidate discovery, but symbolic justification
must remain the explanation surface.

Typical outputs:
- `ProofTree`
- `TreatmentTable`
- typed graph nodes/edges over promoted truth

### 5. Public-action layer
Receipts packs, distinguish reports, action kits, frame-compiler outputs,
corrections ledgers, and briefing surfaces.

Typical outputs:
- `ReceiptsPack`
- `DistinguishReport`
- `ActionKit`
- public thesis / briefing outputs

This layer is downstream packaging, not canonical truth construction.

## State Model
Use state to separate what is known from what is merely proposed.

Safe minimal state split:
- `S_source`: anchored text substrate
- `S_parse`: extracted clause candidates
- `S_promote`: promoted truths + abstentions + unresolved conflicts
- `S_graph`: typed graph consequences over promoted truths
- `S_publish`: public/action-facing packages

Only `S_promote` is canonical truth.

That means:
- `S_parse` remains reversible analysis residue
- `S_graph` is a derived reasoning layer
- `S_publish` is downstream packaging

## Architectural Invariants
- every promoted object must point back to exact spans
- LLMs must not be the canonical interpreter
- downstream reasoning must consume promoted truths or explicitly typed
  non-canonical overlays, not silently flattened raw text
- public-facing outputs must be grounded in promoted nodes and receipts only
- abstention is a valid terminal state and must be preserved explicitly

## Why Promotion Is Central
The most important design choice is to center the system on promotion rather
than on extraction quality, graph richness, or embeddings.

Reason:
- extraction can be partial and still useful
- graph layers can be powerful and still be non-canonical
- public messaging can be valuable only if it remains receipt-backed

The integrity of ITIR/SensibLaw depends on whether promoted truth is:
- explicit
- reversible to source spans
- abstention-capable
- isolated from rhetorical packaging

## Non-Goals
- not a claim that embeddings or graph ML become the authority surface
- not a claim that reasoning layers may silently promote candidate outputs
- not a claim that public-action packaging may outrun the proof base
- not a replacement for the existing admissibility/promotion doctrine

## Best Next Milestone
The highest-value milestone is a bounded end-to-end prototype on one doctrine
that proves the contract.

Success artifact should include:
- raw legal text
- extracted clause JSON with spans
- promoted facts with abstentions
- typed graph
- proof tree
- one public-facing thesis/briefing/action kit where every sentence is
  receipt-backed

Presentation should also remain explicitly non-gaslighting and
trust-preserving rather than assuming legal/evidential correctness alone is
enough.

This is the smallest milestone that validates the whole receipts-first
compiler spine at once.
