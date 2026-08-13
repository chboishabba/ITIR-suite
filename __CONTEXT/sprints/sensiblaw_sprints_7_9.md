# SensibLaw Sprint Plan (S7–S9, 2026-02-06)

## Sprint S7 — Span Authority & Provenance Closure
Goal: make every interpretive artifact provably traceable to canonical text.

Implemented:
- `TextSpan(revision_id, start_char, end_char)` model + storage columns.
- RuleAtoms/RuleElements carry optional TextSpan (legacy allowed but flagged).
- SpanRole/SpanSignal hypotheses use `span_source` (revision_id).
- Promotion receipts include span IDs; blocking signals enforced.
- Tests: rule-to-span attachment; span regeneration/hypothesis guards; storage round-trip.

Non-goals:
- No reasoning or compliance logic.
- No ontology expansion.

## Sprint S8 — Cross-Document Norm Topology (Non-Judgmental)
Goal: expose explicit cross-document relationships without precedence or inference.

Implemented:
- `obligation.crossdoc.v2` schema and extractor.
- Edge kinds: `repeals`, `modifies`, `references`, `cites` (text-derived only).
- Forbidden terms: conflict/override/prevails/controls (hard stop).
- Deterministic ordering + snapshot updates.

Non-goals:
- No conflict resolution, priority, or equivalence inference.

## Sprint S9 — Human Interfaces (Read-Only, Trust-First)
Goal: make outputs legible without mutating meaning.

Implemented:
- Obligations read-only tab with span inspector + optional signal/receipt sections.
- Fixture-mode UI contracts + Playwright smoke tests + forbidden language sweep.
- Labs surface explicitly quarantined (utilities tab banner).

Non-goals:
- No editing, approvals, or persistent annotations.
