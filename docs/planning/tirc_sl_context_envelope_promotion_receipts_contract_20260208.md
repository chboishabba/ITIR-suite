# TiRC -> SL Reducer + Context Envelope + Promotion Receipt Contract (2026-02-08)

## Purpose
Define one implementation contract for:
- TiRCorder consumption of SL canonical reducer surfaces.
- Context Envelope use for trauma-aware temporal grounding.
- Promotion receipts for authority-crossing writes.

This is a planning/contract artifact only.

## 1) TiRCorder -> SL token/concept reducer contract

### Boundary
- TiRCorder owns capture/transcription/provenance emission.
- SL owns canonical text/token/lexeme/concept reduction semantics.
- TiRCorder must not create competing canonical semantic identity stores.

### Processing handshake (target path)
1. TiRCorder captures raw transcript text.
2. Text is normalized through shared SL-compatible normalization.
3. Normalized text is tokenized via deterministic SL reducer surface.
4. Tokens are linked to canonical lexeme/concept IDs.
5. TiRCorder emits/retains references to canonical IDs (not separate canonical
   identity authority).

### Semantic enrichment path
- TiRCorder may request concept trigger matching through shared reducer services.
- Resulting concept tags are semantic anchors with provenance pointers.
- Local TiRCorder heuristics remain non-canonical unless promoted via receipts.

### Definition-of-done criteria (target)
- Adapter path exists: transcript text -> canonical IDs.
- Deterministic outputs for fixed reducer/profile version.
- Cross-product identity checks pass (TiRCorder path vs SB path).
- Coverage/quality gates are explicit in CI (token/lemma/POS/dep expectations).

## 2) Context Envelope for trauma-aware reasoning

### Role
Context Envelopes are non-interpretive, time-bounded state snapshots used to
ground legal/interpretive reasoning in lived constraints without collapsing
authority boundaries.

### Direction
- SB -> SL: envelope ingestion (read-only context lane).
- SL consumes envelope context to explain timing/capacity effects on reasoning
  trajectory, not to rewrite legal substrate truth.

### Contract properties
- Envelopes remain additive overlays.
- They capture temporal/capacity constraints (e.g., overload/fatigue windows)
  with provenance.
- They must not auto-resolve contradictions or auto-promote legal conclusions.

## 3) Promotion receipts for authority-crossing writes

### Trigger condition
Any write crossing authority classes requires an explicit promotion receipt.

### Minimum receipt linkage
- `event_id`
- `idempotency_key`
- `payload_hash`
- `correlation_id`
- `causation_id`
- source/target `authority_class`
- provenance pointers to raw evidence IDs

### Conflict behavior
- Same key + same hash => no-op replay.
- Same key + different hash => hard conflict.

### Integrity posture
- Baseline verification (hash-manifest + verify script) is mandatory.
- Extended signatures can be layered, but promotion provenance must always be
  independently replay-verifiable.

## 4) Current vs target note

### Current confirmed surfaces
- TiRCorder connector doctrine already states SL owns NLP/semantics:
  `SensibLaw/docs/tircorder_connector.md`
- Baseline receipts tooling exists:
  `SensibLaw/cli/receipts.py`
  `SensibLaw/src/receipts/__init__.py`

### Target to implement
- Dedicated TiRCorder->SL canonical reducer adapter contract surface.
- Context-envelope usage tests for trauma/capacity grounding in reasoning flows.
- Authority-crossing promotion receipt conformance tests over exchange envelope
  fields and replay/conflict rules.

## 5) Related contracts
- `docs/planning/reducer_ownership_contract_20260208.md`
- `docs/planning/itir_idempotency_dedupe_cooperation_20260208.md`
- `docs/planning/receipts_pack_automation_contract_20260208.md`
- `docs/planning/itir_consumption_matrix_20260208.md`
