# ITIR Suite User Stories

## Purpose
These user stories codify how ITIR, SensibLaw (SL), and StatiBaker (SB) protect
context, resist narrative coercion, and prevent evidentiary collapse when
handling adversarial corpora (e.g., large, fragmentary, reputationally charged
datasets).

## Suite-Level Invariants (Non-Negotiable)
- Context is mandatory: artifacts must never be interpreted without temporal,
  social, and epistemic frame metadata.
- Interpretation is optional: the system does not render moral or legal verdicts.
- It must be cheaper to expand context than to compress it.
- Context removal is explicit and logged.

---

# ITIR (Interpretive / Temporal Record)

## ITIR-US-01: Context-Bound Artifact Viewing
As a user, I want to view any artifact only within its original context so that
meaning is not distorted by temporal or situational drift.

Acceptance criteria:
- Every artifact view shows date/time, venue/medium, intended audience, and
  known public facts at the time.
- Raw excerpt viewing is not the default.
- Removing context requires an explicit user action with a warning.

## ITIR-US-02: Epistemic State Overlay
As a user, I want to see what was knowable at the time an artifact was created
so I can distinguish hindsight judgment from contemporaneous knowledge.

Acceptance criteria:
- Timeline overlays show public knowledge, legal status, and investigative
  status at the time of creation.
- Later revelations are visually separated.
- UI labels distinguish "known then", "known later", and "unknown at time".

## ITIR-US-03: Context Drift Detection
As a user, I want the system to flag when an artifact is interpreted outside
its original frame so I can recognize when meaning may be distorted.

Acceptance criteria:
- System detects cross-audience reuse, temporal reuse beyond a configured
  context horizon, and medium shifts (private to public, comedy to moral claim).
- A warning banner indicates the drift and offers the original frame.

---

# SL (SensibLaw) - Claim Discipline

## SL-US-04: Claim Type Enforcement
As a user, I want every assertion to be typed so I can see whether I am reading
adjudicated fact, primary evidence, testimony, inference, or opinion.

Acceptance criteria:
- Untyped claims are rejected or must be explicitly typed before save/share.
- Inference claims require a linked evidence graph.
- Narrative or PR framing language is flagged.

## SL-US-05: Denial Pattern Surfacing
As a user, I want to see when denials follow shared templates so I can
distinguish independent testimony from coordinated narrative.

Acceptance criteria:
- Similar denial language is clustered and timestamped.
- Counsel or PR involvement is flagged when known.
- The system does not infer guilt; it only shows patterning.

---

# SB (StatiBaker) - Pattern Without Narrative

## SB-US-06: Reputational Exposure Map (No Verdict Mode)
As a user, I want to see networks of association, assistance, and protection
without the system implying guilt or innocence.

Acceptance criteria:
- Graphs show contact, assistance, reputation management, and timing.
- No labels like "criminal" or "predator" appear.
- Users apply their own interpretation.

## SB-US-07: Power Asymmetry Indicator
As a user, I want to see when accountability differs by status so I can
understand systemic imbalance without conspiracy framing.

Acceptance criteria:
- Status indicators include wealth, institutional protection, and legal
  insulation.
- Visual comparisons show consequences faced versus evidence volume.
- The system does not assert causality.

---

# Cross-Suite UI Invariants (Testable)

## UI-INV-01: No Context-Free Excerpts
Any excerpt rendered alone must show a warning badge.

## UI-INV-02: Interpretation Is Always Optional
The system never produces moral judgment, legal conclusion, or psychological
inference as default output.

## UI-INV-03: Expand Context Is Cheaper Than Summarize
Raw artifacts are always one click away; no irreversible compression.

## UI-INV-04: Context Removal Is Logged
Any user action that removes or suppresses context is logged with a timestamp.

---

## Design Sentence (Suite-Wide)
ITIR preserves what happened, SL constrains what can be claimed, and SB refuses
to tell you what it means.
