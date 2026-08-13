# ADR-CTX-001: Context as a First-Class Invariant

**Status:** Proposed  
**Date:** 2026-02-06  
**Applies to:** ITIR, SensibLaw (SL), StatiBaker (SB)  
**Decision Drivers:** determinism, auditability, resistance to narrative coercion,
legal/forensic safety

---

## Problem Statement

Modern information systems allow artifacts (quotes, emails, images, transcripts,
jokes, logs) to circulate detached from their original interpretive frame.

This detachment produces two systemic failures:

1. False exoneration (loss of pattern visibility)
2. False condemnation (loss of intent, venue, or epistemic state)

Both outcomes stem from the same root cause: context collapse.

Without enforceable context, meaning becomes manipulable, retrofitted,
laundered, and weaponized. This is incompatible with ITIR/SB/SL's core
invariants of determinism, provenance, and non-inventive interpretation.

---

## Decision

Context SHALL be treated as a first-class invariant, not metadata.

No artifact may be viewed, exported, summarized, interpreted, or
cross-referenced without an attached, queryable context envelope.

Context is not optional, compressible away, or inferable later.

---

## Definition: Context Envelope

Every artifact MUST be bound to a Context Envelope containing, at minimum:

### Temporal
- Creation timestamp
- Duration / span
- Sequence position relative to other artifacts

### Venue
- Medium (private email, comedy stage, court filing, interview, etc.)
- Intended audience
- Visibility scope at time of creation

### Epistemic State
- What was publicly known at the time
- Legal status at the time
- Investigative status at the time
- Later-discovered facts (explicitly separated)

### Role and Power
- Speaker role
- Recipient role
- Institutional / status asymmetry flags (non-interpretive)

---

## Consequences

### Positive
- Prevents hindsight laundering
- Prevents context stripping
- Enables pattern recognition without narrative coercion
- Supports adversarial legal scrutiny

### Negative
- Increases UI and data model complexity
- Prevents "viral excerpt" UX by design
- Requires user education

These costs are accepted intentionally.

---

## Rejected Alternatives

- Context as optional metadata
- Context inferred from neighboring artifacts
- Context reconstructed at interpretation time
- Context flattened into summaries

All rejected due to non-determinism and abuse risk.

---

## Invariants Introduced

1. No context-free rendering
2. No silent context loss
3. Context expansion must be cheaper than context removal
4. Interpretation is always an overlay, never canon
