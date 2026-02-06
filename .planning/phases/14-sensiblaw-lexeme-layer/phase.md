# Phase 14: SensibLaw Lexeme Layer

**Owner:** Codex
**Date:** 2026-02-06
**Status:** Planned → Implementing

## Goal
Introduce a redundancy-collapsing lexeme layer anchored to canonical spans,
with deterministic phrase atom promotion, without introducing semantics.

## Objectives
- Add lexeme dictionary + lexeme occurrence tables to the revision store.
- Record lexeme occurrences for new revisions using canonical body spans.
- Provide deterministic normalization + flags for surface variance.
- Keep phrase atoms as non-authoritative, reversible structures.

## Constraints
- Canonical text remains immutable; spans are authoritative.
- No semantic labels, no reasoning, no compliance logic.
- Changes must be additive and migration-safe.

## Deliverables
- Schema additions (lexemes, lexeme_occurrences, phrase_atoms, phrase_occurrences).
- Versioned store ingestion of lexeme occurrences.
- Tests: lexeme normalization, span anchoring, occurrence counts.
- Docs: `docs/lexeme_layer.md` referenced from tokenizer/corpus docs.

## Acceptance Criteria
- Adding a revision stores lexeme occurrences with correct char offsets.
- Normalization collapses casing without altering span anchors.
- Phrase atom scaffolding exists but remains non-authoritative.
- Tests pass for lexeme storage and retrieval.

## Open Questions
- Whether to persist surface_hash for diagnostic use.
- When to begin phrase atom promotion in the ingestion pipeline.

## Next Actions
1. Add tables in `versioned_store` schema.
2. Implement lexeme indexing helper (canonical body → occurrences).
3. Add tests and update changelog.
