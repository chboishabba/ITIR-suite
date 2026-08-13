# Mary Parity Roadmap

Date: 2026-03-15
Source thread: `Insights from Whitepaper`
Online UUID: `69b41f22-a514-839f-946c-fa0e9f75cc46`
Canonical thread ID: `eab13fe32136bc69aebdb9a21888b76215faab11`
Resolution source: `db`
Archived message count at refresh: `122`
Latest archived assistant timestamp: `2026-03-13T15:19:54+00:00`

## Priority statement

Priority shifts to **parity with Mary Technology as the first operator-facing
goal**, while preserving SL's longer-term differentiator as a richer legal
reasoning and state-transition system.

Interpretation:

- Mary is the near-term benchmark for:
  - fact management
  - chronology / timeline handling
  - provenance and contestation of statements
  - litigation-workflow operator surfaces
- SL should reach parity on that substrate first.
- SL's current whitepaper priorities remain valid, but they become
  **layer-two followthrough over a Mary-equivalent fact layer**, not the first
  user-facing promise.

## What parity means

Parity does **not** mean copying Mary's architecture wholesale.

It means SL must be able to support the same practical operator outcomes:

1. ingest source material into a structured fact/provenance substrate
2. maintain chronology and statement-level traceability
3. represent contestable observations/claims/facts rather than naïve flat
   summaries
4. support operator review and curation over those facts
5. expose the resulting substrate through practical workflow/report surfaces

SL should then extend beyond Mary by:

- explicit Observation / Claim discipline
- richer event/fact/norm/claim seams
- typed state transitions with guarded receipts
- explanation-first doctrinal similarity / retrieval

## Roadmap order

### Phase 1: Mary-equivalent fact substrate

Goal: reach practical parity on fact-management workflow surfaces.

Required slices:

- source/excerpt/statement capture with stable provenance handles
- a small explicit `Observation` layer over factual statements, using a stable
  low-cardinality predicate catalog rather than a sprawling intake ontology
- deterministic `EventCandidate` assembly over observations so chronology and
  review work on stable derived event objects rather than isolated rows
- chronology / timeline organization over captured facts/statements
- explicit contestation / ambiguity support over statements
- operator review surfaces for fact curation and external-ref linking
- robust external identity/reference support for the fact layer
- explicit abstention/status semantics and clean separation between structural
  identity and run/execution metadata
- public-knowledge review surfaces that can distinguish:
  - allegation vs finding
  - public-summary wording vs primary legal material
  - moderation/defamation risk vs adjudicated legal status
  - person vs office vs organization vs jurisdiction structure

This is the primary use of the current ontology/bridge work:

- branch-set bridge slices
- reviewed aliases
- explicit anchors
- receipts and abstention reporting

These should be framed as **fact-layer support infrastructure**.

### Phase 2: Mary-parity plus structured legal semantics

Goal: make the fact layer legally meaningful without skipping operator parity.

Required slices:

- explicit Observation layer
- explicit Claim / evidence-link contracts
- deterministic seam:
  `source/excerpt -> observation -> event/fact -> norm -> claim`
- jurisdiction / court / legislation / case / actor reference discipline
- report/debug surfaces that keep provenance and contestability visible

### Phase 3: Beyond Mary

Goal: add the things Mary-style systems do not natively provide.

- typed guarded state transitions for legal updates
- burden/threshold policy over posterior/update layers
- temporal law/versioning
- explanation-first p-adic / ultrametric legal similarity
- RDF/Wikidata projection as export/interoperability boundary only

## Immediate execution implications

Near-term work should be judged by one question:

> Does this make SL more capable of delivering Mary-equivalent fact management
> with provenance, chronology, contestation, and operator review?

So current work should be prioritized as:

1. fact/provenance/chronology parity infrastructure
2. review + linkage ergonomics
3. observation/claim seam
4. typed-transition / advanced reasoning followthrough

## Current status snapshot

As of 2026-03-15, the parity program has explicit passing acceptance gates for:
- `wave1_legal`
- `wave2_balanced`
- `wave3_trauma_advocacy`
- `wave3_public_knowledge`
- `wave4_family_law`
- `wave4_medical_regulatory`
- `wave5_handoff_false_coherence`

The current status audit is tracked in:
- `docs/planning/mary_parity_status_audit_20260315.md`

Interpretation:
- substrate parity is now credible
- the next limiting factors are real-fixture breadth and operator/workbench
  polish rather than missing core architecture

## Test → Ingest → Zelph bridge path (Mary-parity lens)

- Test surfaces to keep in the loop:
  - Wave 1–5 fact-review acceptance suites (transcript/AU + later families)
  - ingest regression corpus (legal fixtures + GWB/AAO payload parity)
  - chat-archive context pulls when upstream threads drive positioning
- Ingest seam (must stay deterministic and provenance-first):
  - run standard SL ingest paths (fact/observation/event) with explicit
    abstention/status and run-vs-structural IDs
  - treat uploaded/chat snippets as partial; fall back to file-search/full-doc
    lookup before answering or promoting to canonical facts
  - keep operator review surfaces (fact-review runs) as the gating layer
- Zelph bridge demo (scope explicitly tiny):
  - ≤20 facts, deterministic, legally meaningful negligence slice
  - source: ingested/curated fact graph from the acceptance substrates above
  - output: minimal SL -> Zelph handoff that shows immediate reasoning on the
    SL fact graph without live LLMs
  - positioning: SL upstream fact construction + provenance; Zelph downstream
    reasoning; avoid framing as dependency

## Current in-flight work that already fits

- reviewed ontology bridge / external-ref prepopulation
- branch-set population and debugging with receipts
- AU/GWB seed/linkage cleanup
- provenance-first report/debug surfaces

These are now explicitly subordinate to Mary-parity delivery rather than
standing alone as ontology work.
