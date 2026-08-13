# ITIR Suite Capability Posture (Audit-Safe) (2026-02-08)

Purpose: prevent documentation drift where **roadmap targets** are mistakenly
described as **current production guarantees**, especially in high-stakes
contexts (legal proceedings, safety claims, evidentiary handling).

This document explicitly separates:
- **Current Capability**: confirmed by repo state and/or ratified contracts.
- **Target Capability (Roadmap)**: design goals, not yet guaranteed.

## Status Labels

- `CURRENT`: exists today (implementation and/or ratified contract).
- `CURRENT (CONTRACT)`: ratified contract exists; implementation may be partial.
- `TARGET`: roadmap/design intent only.

## Suite-Wide Constraints

### Context and Authority

- `CURRENT (CONTRACT)`: Interpretation is a non-authoritative overlay; canonical
  substrate is append-only and not rewritten by projections.
- `CURRENT (CONTRACT)`: Any cross-authority promotion (observer -> canonical,
  interpretive -> canonical, etc.) requires an explicit receipt/promotion
  boundary, not an implicit side effect.

### Audit Safety

- `CURRENT (CONTRACT)`: “Courtroom-grade” is a target posture, not an automatic
  claim. Any language implying evidentiary admissibility must be tied to
  concrete implemented guarantees and verifiable receipts.

## Component Breakdown (Current vs Target)

### TiRCorder (`tircorder-JOBBIE`) (Capture Authority)

Current:
- `CURRENT`: recording + transcription pipeline (Whisper/cTranslate2 class),
  producing exportable text/events with stable identifiers.
- `CURRENT (CONTRACT)`: provenance-first posture: preserve timestamps/metadata
  on ingest and avoid mutating captured substrate.

Target:
- `TARGET`: “trustless” decentralized storage and stronger cryptographic
  posture (e.g. DHT/IPFS-class backends) as an implementation, not an
  assumption.
- `TARGET`: granular consent/crypto-shredding UX (item-level controls).

### SensibLaw (`SensibLaw`) (Interpretive Authority)

Current:
- `CURRENT`: foundational primitives for document retrieval and distinguish-style
  comparison workflows.
- `CURRENT (CONTRACT)`: explicit boundary posture forbidding automated legal
  verdict behavior where not ratified. (See SensibLaw’s internal “no reasoning”
  contract for current restrictions.)

Target:
- `TARGET`: automated Receipts Pack generation as one-click, offline-verifiable
  bundles for *specific* claims, with audit-grade chain-of-custody semantics.
- `TARGET`: deeper persistence/ontology materialization as production schema.

### StatiBaker (`StatiBaker`) (Temporal Authority)

Current:
- `CURRENT`: temporal distillation as a “context prosthesis” (multi-source
  activity compilation into daily/lifetime dashboards).
- `CURRENT (CONTRACT)`: non-agentic compiler posture: observes/compresses;
  does not initiate real-world side effects.

Target:
- `TARGET`: “Expansion invariant” as an enforced economic guarantee (expand to
  raw IDs cheaper than re-summarization), with measurable tests.
- `TARGET`: read-only MCP query surface as a safe observer interface.

### Streamline / Ribbon (`itir-ribbon`) (Projection-Only)

Current:
- `CURRENT`: design and planning posture for proportional timeline/ribbon
  visualizations.

Target:
- `TARGET`: evidentiary UI rendering only what the database describes, with
  click-through to Layer-0 provenance and deterministic receipt verification.

## Trauma-Aware Context Envelopes (Design Posture)

This section is **not** a production guarantee unless and until the relevant
contracts are ratified and enforced end-to-end.

Target goals:
- `TARGET`: prevent “hindsight laundering” by distinguishing “known then” from
  later-discovered facts (epistemic grounding).
- `TARGET`: record overload/fatigue/context-collapse windows as constraints
  without smuggling interpretive conclusions into canonical state.
- `TARGET`: drift warnings when an artifact is moved across venues/audiences
  (e.g., therapeutic note -> adversarial filing) with explicit acknowledgements.
- `TARGET`: preserve gaps/contradictions as first-class objects instead of
  smoothing into false narratives.

Related planning docs (existing):
- `docs/planning/right_to_context.md`
- `docs/planning/context_envelope_schema.md`
- `docs/planning/context_envelope_db_sketch.md`

## Receipts Pack (Design Posture)

Receipts Packs are a **target** output shape unless specific commands and
verification surfaces are implemented and tested.

Target bundle shape:
- offline-verifiable bundle (HTML + manifest)
- reproducibility metadata (tool versions, commands, hashes)
- explicit chain-of-custody receipts for referenced artifacts

Related planning docs (existing):
- `docs/planning/receipts_pack_automation_contract_20260208.md`
- `docs/planning/tirc_sl_context_envelope_promotion_receipts_contract_20260208.md`

## Streamline Siphon/Asset-Flow Detection (Design Posture)

Target goals:
- proportional ribbon rendering of financial flows with click-through receipts
- multi-account layering without “spaghetti” graphs
- transfer inference as explicit, testable heuristics (candidate edges), not
  implied truth

## Update Policy

When adding marketing/sales/docs claims:
- If it’s not implemented and tested, it must be labeled `TARGET`.
- If it’s implemented but not yet enforced end-to-end, label `CURRENT (CONTRACT)`
  and state the missing enforcement surface.

