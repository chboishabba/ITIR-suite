# ITIR Consumption/Production Matrix (Ratified) (2026-02-08)

## Purpose
Provide one canonical "who consumes what" matrix across:
- `SensibLaw` (SL)
- `tircorder-JOBBIE` (TiRCorder)
- `StatiBaker` (SB)
- `itir-ribbon` (Ribbon/Streamline)

This document is intended to reduce team drift by replacing ad hoc flow
descriptions with one ratified matrix.

## Governing principle
Shared primitives, siloed semantics.

- Shared primitives:
  - exchange envelope and replay/idempotency primitives
  - canonical reducer runtime surface
- Siloed semantics:
  - TiRCorder capture semantics
  - SB temporal/state fold semantics
  - SL semantic identity/equivalence and interpretive semantics
  - Ribbon projection semantics

## Authority classes (reference)
- `observer_capture`: TiRCorder
- `compiled_state`: SB
- `authoritative_substrate`: SL
- `projection_only`: Ribbon

## Matrix

| Producer | TiRCorder consumes | SL consumes | SB consumes | Ribbon consumes |
| --- | --- | --- | --- | --- |
| TiRCorder | — | Raw transcripts/events for interpretation | Raw event streams for state compilation | Narrative/event references for projection |
| SL | Canonical reducer outputs + semantic anchors | — | Canonical IDs + semantic anchors | Interpretive overlays + conservation metadata |
| SB | Null authority-write path | Context envelopes/time-state snapshots | — | State overlays/SITREP-derived lens inputs |
| Ribbon | Null authority-write path | Validation diagnostics only | Null authority-write path | — |

## Clarifications
- "Null" means no canonical authority-write path from that producer to that
  consumer. It does not mean "no integration at all."
- Ribbon is read-only projection; diagnostics remain non-authoritative unless
  explicitly promoted with receipts.

## Handshake summary

### SL -> SB/TiRCorder
- Canonical token/lexeme/concept identity outputs.
- Semantic anchors for labeling and traceability.

### SB -> SL
- Context envelopes describing lived-time constraints.
- Reducer receipts and temporal provenance.

### TiRCorder -> SL/SB
- Capture artifacts and resilient ingest event streams.
- No independent canonical semantic authority.

## Anti-dilution effect of semantic anchors
- Semantic anchors centralize meaning ownership in SL while allowing SB/TiRCorder
  to remain focused on temporal and capture concerns.
- SB/TiRCorder can label and correlate state/capture lanes without reimplementing
  SL equivalence logic.
- This preserves "shared primitives, siloed semantics" in operational practice.

## Promotion + provenance
- Local heuristics in TiRCorder/SB are non-canonical by default.
- Cross-authority promotion requires receipts and retained provenance.
- Summary outputs must expand cheaply back to raw event IDs/receipts.

## Related contracts
- `docs/planning/itir_idempotency_dedupe_cooperation_20260208.md`
- `docs/planning/reducer_ownership_contract_20260208.md`
- `docs/planning/sl_tircorder_ribbon_sb_intersection_20260208.md`
