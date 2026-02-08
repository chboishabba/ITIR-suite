# Reducer Ownership Contract (SL x SB x TiRCorder) (2026-02-08)

## Purpose
Clarify reducer ownership and reuse so the suite benefits from SL compression
without:
- diluting SL authority boundaries, or
- reimplementing competing canonical reducers in SB/TiRCorder.

## Core answer

### Should SB/TiRCorder benefit from SL reducers?
Yes, for canonical text/token/lexeme/concept identity.

### Should SB keep its own reducers?
Yes, for temporal/state compilation logic.

### Should the canonical reducer be moved to its own thing?
Hybrid model: extract runtime distribution into a shared package/service surface,
but keep semantic governance and contract authority with SL.

### Practical framing (to stop drift)
- Shared reducer mechanism: yes.
- Shared semantic ownership: no.
- SB keeps temporal folds; SL keeps semantic equivalence authority.
- Temporal reducer logic remains SB-owned and is not moved into a shared
  semantic layer.

## Confirmation status
This contract is aligned with the currently confirmed framework:
- shared primitives + siloed semantics
- SL canonical semantic reduction authority
- SB temporal reduction authority
- TiRCorder capture authority
- Ribbon read-only projection authority

## Reducer taxonomy

### R0: Canonical text/semantic reducer (shared canonical)
- Function: text/span -> token/lexeme/concept IDs.
- Scope: canonical identity across the suite.
- Owner: SL contract authority.
- Consumers: TiRCorder, SB, SL, ribbon pipelines.

### R1: Capture normalization reducer (capture-local)
- Function: media/transcript/source normalization, retry-safe ingestion shaping.
- Scope: capture resilience.
- Owner: TiRCorder.

### R2: State reducers (state-local)
- Function: event folds, carryover/new/resolved transitions, blocker windows.
- Scope: temporal/state compilation.
- Owner: SB.

### R3: Interpretive reducers (interpretive-local)
- Function: legal/normative interpretation and profile-bound reasoning outputs.
- Scope: interpretive overlays.
- Owner: SL.

### R4: Projection reducers (view-local)
- Function: render segmentation/aggregation/cache keys for ribbon views.
- Scope: read-only projection.
- Owner: Ribbon/UI surfaces.

## Mechanism vs semantics split

### Shared primitives (mechanism)
- Exchange envelope, idempotency fields, payload hashing, replay conflict logic.
- Canonical reducer runtime surface (API/service packaging and version pinning).

### Siloed semantics (authority)
- SL decides semantic identity/equivalence rules and profile semantics.
- SB decides temporal/state fold semantics.
- TiRCorder decides capture/ingest shaping semantics.

This keeps one technical reducer runtime while preserving component authority
classes.

## Operational matrix (who consumes what)

| Producer | TiRCorder consumes | SL consumes | SB consumes | Ribbon consumes |
| --- | --- | --- | --- | --- |
| TiRCorder | — | Raw transcripts/events for interpretation | Raw event streams for state compilation | Narrative markers/event references |
| SL | Canonical R0 reducer outputs + semantic anchors | — | Canonical IDs + semantic anchors | Interpretive overlays + conservation metadata |
| SB | Null (non-agentic) | Context envelopes/time-state snapshots | — | State overlays/SITREP-derived lenses |
| Ribbon | Null (read-only) | Validation diagnostics only | Null (no canonical mutation) | — |

Notes:
- "Null" means no authority write path, not "no integration at all".
- Ribbon remains projection-only; diagnostics require promotion receipts before
  any authority impact.
- Canonical matrix source:
  `docs/planning/itir_consumption_matrix_20260208.md`

## SB <-> SL reducer handshake (explicit)

### SL -> SB
- Semantic anchors and canonical IDs (opaque to SB reducer internals).
- Versioned reducer/profile metadata for reproducibility.

### SB -> SL
- Temporal context envelopes and reducer receipts.
- State windows explaining "when/under-what-constraints" without changing SL
  semantic truth.

### Prohibited crossings
- SB reducer must not create or override canonical concept equivalence.
- SL reducers must not mutate SB temporal state history.

## Ownership model options

### Option A: Keep canonical reducer inside SL only
- Pros: strongest semantic control.
- Cons: weak reuse ergonomics; likely drift via ad hoc reimplementation.

### Option B: Move canonical reducer to neutral core with independent governance
- Pros: easy cross-project consumption.
- Cons: high dilution risk; semantic drift from SL contracts.

### Option C (recommended): Shared runtime, SL-governed contracts
- Canonical reducer distributed as shared package/service surface.
- Semantic schema/version governance remains SL-owned.
- SB/TiRCorder consume as clients, not co-owners of canonical semantics.

Decision posture:
- Treat Option C as the default operating posture now.
- Formal ratification still tracked under `Q11`.

## Recommended contract (enforceable)

### C1: Canonical reducer authority
Canonical token/lexeme/concept identity is SL-governed and versioned.

### C2: Shared runtime surface
Provide one supported integration surface for TiRCorder/SB:
- package API and/or service endpoint
- explicit version pinning
- compatibility matrix by reducer/profile version
- ownership metadata in envelopes (`reducer_runtime_version`,
  `semantic_contract_version`)

### C3: SB reducer boundary
SB reducers may consume canonical IDs but must not define competing canonical
identity/equivalence semantics.
SB temporal fold logic remains SB-local by design.

### C4: TiRCorder reducer boundary
TiRCorder may perform capture-local preprocessing, but canonical identity must
come from shared R0 outputs.

### C5: Drift guard
New canonical token/concept stores in SB/TiRCorder require explicit ADR approval.

### C6: Replay and expansion invariant
All reducer outputs must preserve expansion links to raw event IDs and receipts.
This is why SB temporal logic stays local: replayable lived-time reconstruction
must remain auditable without importing interpretive semantic side effects.

### C7: No duplicate canonical stores
TiRCorder/SB may cache reducer outputs, but cache tables are derivative only and
must not be treated as independent canonical identity stores.

## Testing requirements

### T1: Canonical consistency tests
Same input text across SL/TiRCorder/SB integration paths yields the same
canonical IDs for the same reducer/profile version.

### T2: Non-canonical fallback tests
Local fallback outputs are marked non-canonical and mapped/upgraded to canonical
IDs without silent replacement.

### T3: SB boundary tests
SB reducer changes do not alter canonical token/concept identity assignments.

### T4: Drift prevention tests
Build/test checks fail when SB/TiRCorder introduce unapproved canonical identity
stores.

### T5: Cross-product identity test
Same text artifact entering through TiRCorder and SB paths resolves to identical
canonical IDs for the same reducer/profile versions.

## Immediate followthrough
- Ratify Option C and freeze governance language.
- Define shared reducer integration surface and version contract.
- Add conformance/drift tests in TiRCorder and SB adapters.
