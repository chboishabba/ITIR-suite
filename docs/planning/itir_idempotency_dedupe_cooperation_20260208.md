# ITIR Idempotency + Dedupe Cooperation Notes (2026-02-08)

## Purpose
Integrate current notes on how idempotency, deduplication, and authority
boundaries should cooperate across:
- `SensibLaw` (SL)
- `tircorder-JOBBIE`
- `StatiBaker` (SB)
- `itir-ribbon`

This document is a planning/contract addendum; no runtime change is introduced
here.

## Ratified direction (from integration notes)

### D1: Shared invariants are suite-level, not project-local
Across all component boundaries, the exchange envelope should carry:
- `event_id`
- `idempotency_key`
- `payload_hash`
- `correlation_id`
- `causation_id`
- `authority_class`

### D2: Shared conflict rule is strict
- Same `idempotency_key` + same `payload_hash` => idempotent no-op replay.
- Same `idempotency_key` + different `payload_hash` => hard conflict.

### D3: Authority crossing requires receipts
Any write crossing authority classes (observer/capture/projection into
authoritative/compiled lanes) requires explicit promotion receipts with
provenance retention.

### D4: Shared primitive, siloed semantics
Idempotency/dedupe primitives are reused suite-wide, but each component keeps
its own semantic interpretation and reduction logic.

### D5: SL compression/reduction is reusable infrastructure
SL token/lexeme/concept compression work should be consumed by other components
as shared infrastructure, not reimplemented in parallel.

### D6: No dilution, no duplication
- Reuse of SL reducers by SB/TiRCorder must not dilute SL authority boundaries.
- SB/TiRCorder must not introduce competing canonical token/concept identity
  systems.
- Domain-specific interpretation remains profile-bound; shared reducers remain
  deterministic and profile-aware.

### D7: Semantic anchors are anti-dilution control
Semantic anchors centralize meaning ownership in SL while allowing SB and
TiRCorder to consume canonical identities without absorbing interpretive
authority.

## Porous boundary clarification

Porous boundaries are expected at integration edges, but ownership remains
stable:
- TiRCorder: capture/transcription and ingest resilience authority.
- SB: temporal/state compilation authority.
- SL: semantic identity/equivalence and interpretive authority.

The contract is not "strict isolation"; it is "shared substrate with explicit
authority classes and promotion receipts."

## Confirmation status
The current framework is treated as confirmed for documentation and planning:
- TiRCorder/SB consume SL-origin canonical reduction surfaces.
- Local heuristics remain non-canonical unless promoted with receipts.
- SL interpretation over TiRCorder/SB data is additive/read-only by default.
- Expansion-to-raw remains a hard verification invariant.

## Responsibility matrix

### Shared ITIR-wide invariants (generalized)
- Envelope identity and replay keys.
- Conflict/no-op rule.
- Promotion-receipt requirement for authority crossing.
- Deterministic replay requirement.

### SL-specific (siloed)
- Owns token/span identity and concept-equivalence semantics.
- Owns legal/normative interpretive identity layers.
- Applies substrate idempotency at text/token/span layer.
- Exposes shared reduction services for non-SL components to consume.

### TiRCorder-specific (siloed)
- Owns capture ingest resilience and replay-safe delivery handling.
- Keeps local/fuzzy correlation heuristics as non-authoritative signals.
- Does not define suite-wide semantic equivalence.
- Sends transcript text through shared SL-compatible reducers for canonical IDs.

### SB-specific (siloed)
- Owns append-only state compilation over reduced records.
- Owns temporal reduction semantics and state transitions.
- Corrections are additive (reversal/supersession), never in-place mutation.
- Reuses canonical text/concept IDs from shared reducers rather than maintaining
  an independent canonical semantic substrate.

### Ribbon-specific (siloed)
- Read-only projection layer; no canonical state mutation.
- Uses upstream IDs for render/caching dedupe only.
- Emits diagnostics/validation, not authority writes.

## Shared reducer contract (draft policy)

### R-Policy 1: Canonical reduction service
Canonical text/token/concept reduction should be offered as a shared
SL-origin service surface (or extracted shared package governed by SL contracts)
that other components call.

### R-Policy 2: Local fallback is non-canonical
If TiRCorder/SB run local tokenizer/indexing steps for performance or UX, those
outputs must be marked non-canonical and be reproducible/upgradable to canonical
shared IDs.

### R-Policy 3: Profile separation
Generalized reducers and legal-profile reducers must remain separable so
non-legal contexts can reuse the core machinery without inheriting legal
interpretation assumptions.

### R-Policy 4: Read-only semantic interpretation over external graphs
SL may interpret TiRCorder/SB/ITIR graph data via explicit adapters, but those
interpretations are additive overlays and must not mutate upstream capture/state
history without promotion receipts.

Reducer ownership details for SB-vs-SL-vs-TiRCorder are specified in:
- `docs/planning/reducer_ownership_contract_20260208.md`

## Authority-crossing handshake

### SB -> SL/ITIR lane
SB provides temporal envelope and reduced state context with event references
and provenance.

### SL -> SB/Ribbon lane
SL provides semantic anchors (identity/equivalence bindings) that can annotate
state/timeline views without rewriting capture history.

### Handshake invariant
Cross-lane enrichment is additive and traceable; it must not silently merge or
rewrite authority classes.

## Anti-enshittification verification invariant

To preserve auditability and avoid opaque compression drift:

> It must remain computationally and cognitively cheaper to expand a summary to
> raw event IDs/provenance than to re-summarize original raw inputs.

Operational consequence:
- Every reduced output must keep stable back-references to raw event IDs and
  transformation receipts.
- Expansion paths must be first-class test targets.

## Open decisions queue (before schema freeze)
These are the primary unresolved questions to ratify before freezing
`itir.exchange.v1` and adapter contracts.

### Q1: Unified timeline axis policy
How `platform/siphon/contact/account-layer` dimensions map onto shared
`Streamline` X/Y/Z semantics.

### Q2: SB "mechanical should" representation
Whether actionable output is stored as machine flags only (UI labels later) vs
stored imperative strings.

### Q3: Narrative frame storage model
Whether public narrative frames are modeled as dedicated frame tables or as
graph-linked extrinsic material nodes.

### Q4: Dual-role subject/object modeling
When an entity can be both interest subject and interest object in the same harm
instance, whether to enforce dual references or a unified polymorphic pattern.

### Q5: Action kit ontology placement
Whether action templates remain static jurisdiction templates or are promoted to
Layer-6 remedy-class entities.

### Q6: Authority-crossing conflict semantics
Whether layer-specific reinterpretations of one raw artifact share an idempotency
collision domain or are separated by authority/layer scope.

### Q7: Customary law precedence policy
Whether customary/indigenous law is modeled as parallel authority with
reconciliation flags or assigned comparable rank semantics.

### Q8: Expansion trace depth
Whether expansion exposes raw IDs only or also reducer/rule traces by default.

### Q9: Evidence overlap cardinality
Whether evidence nodes are canonical many-to-many references across Event/Claim/
Case/Brief layers without single-parent assumptions.

### Q10: Clinic mode offline semantics
Whether higher-order inference engines must run fully local in clinic mode or
may use deferred/online shadow processing.

### Q11: Canonical reducer runtime ownership model
Whether to ratify Option C (shared runtime distribution with SL-governed
semantic contracts) as the default ownership model.

## Drift-control defaults (proposed for immediate team alignment)
Until the full decision queue is ratified, apply these defaults:
- TiRCorder/SB do not introduce new canonical token/concept identity stores.
- Canonical text/concept identity references must originate from shared reducer
  outputs.
- Any local heuristic tags remain advisory unless promoted with receipts.
- SL interpretation over SB/TiRCorder data is read-only by default.

## Immediate followthrough
- Keep `docs/planning/sl_tircorder_ribbon_sb_intersection_20260208.md` as the
  edge map and this document as the cooperation/decision addendum.
- Use `docs/planning/itir_consumption_matrix_20260208.md` as the canonical
  producer/consumer matrix during adapter and conformance implementation.
- Resolve `Q1`-`Q11` before freezing `itir.exchange.v1`.
- After ratification, convert accepted decisions into schema fields, transition
  rules, and contract tests.
