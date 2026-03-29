# ITIR x SensibLaw Identity / Trust Alignment Layer (2026-03-28)

## Purpose
Refine the current receipts-first compiler spine so the repo does not treat
legal/evidential structure as sufficient on its own when the target user is
operating under trauma, dissociation, burnout, coercion, caregiver conflict,
or institutional abuse pressure.

This note does not introduce a new canonical truth layer. It clarifies that
ITIR/SensibLaw must preserve both formal legibility and trauma-tolerable
usability.

## Main Decision
SensibLaw should not be treated as only a legal compiler.

It should be treated as an alignment layer between:
- lived experience
- structured evidence
- formal rule systems
- trust-preserving interpretation
- actionable next steps

That means the suite must be able to convert messy evidence into durable,
auditable structure without forcing the user to repeatedly restate,
reconstruct, or defend their own reality from scratch.

## Organizational Reading
Three organizations are in play:

1. the person / survivor / household trying to preserve continuity under
   adversity
2. the adversarial or bureaucratic institutions applying pressure
3. the tooling stack as a counter-organization that converts fragmented
   experience into structured memory, proof, and action

The design problem is therefore not only `user vs law`.
It is:

> fragmented human state vs institutional power, with ITIR/SensibLaw as the
> translation and stabilization layer

## Requirement Refinement
The stronger requirement is:

> turn raw lived experience into structured, trustworthy, non-gaslighting
> legal and identity support without forcing the user to relive or restate
> everything from scratch

This sharpens the existing compiler spine in two ways:
- narrative continuity must be preserved over time
- truth that cannot be used safely by the user is incomplete system success

## Dual-Compiler Reading
The current legal/evidential compiler remains valid:

`text -> tokens -> rules -> atoms -> graph`

But the repo should also recognize a parallel internal/identity compiler:

`narrative -> signals -> patterns -> identity/trust atoms -> identity graph`

Typical internal extraction surfaces:
- `TrustBoundary`
- `FrictionNode`
- `ConfidenceDrop`
- `WorkflowPattern`
- `EvidenceStrategy`
- `PrimaryNeed`
- `RejectionCondition`
- `FailureMode`

These should remain bounded, user-sovereign, and non-diagnostic.
They are not a psychometric truth layer.

## State Reading
The suite must track two interacting state families:

- external state:
  tenancy facts, notices, transcripts, records, correspondence, timelines,
  institutional procedures, legal relations
- internal state:
  overload, dissociation, trust collapse, burnout, defensive evidence
  gathering, fear of misreading, tolerance for interpretation and action

The system fails if it models only the first and ignores the second.

## Lattice Refinement
The working lattice is not only legality or evidence quality.
It is the product of:

- legal validity
- evidential validity
- trust-preserving interpretability

A result can be legally and evidentially correct yet still fail if it is
experienced as invalidating, flattening, moralizing, or institutionally
captured.

## Governance Constraints
The suite should explicitly avoid:
- hallucinating identity or motive
- imposing diagnosis-shaped interpretations
- collapsing ambiguity too early
- producing institutionally biased or moralizing summaries
- weaponizing the preserved record against the person it is meant to protect

Required safeguards:
- provenance for every strong claim
- abstention as a first-class output
- preserved alternate interpretations where needed
- explicit user override / sovereignty
- preference for local/private operation where feasible
- explicit trust-boundary modeling for downstream renderers

## Relationship To The Receipts-First Compiler Spine
This note does not replace the five-layer compiler split.

It refines it by saying:
- promotion remains the canonical truth center
- reasoning and publishing stay downstream
- but downstream outputs must also be evaluated for trauma-tolerable usability
- internal/trust overlays may guide presentation, pacing, and action
  sequencing without silently changing promoted truth

## Best Next Milestone
The highest-value next milestone remains a bounded doctrine prototype, but the
success condition should now include one additional requirement:

- receipt-backed proof/action output that is also explicitly non-gaslighting
  and trust-preserving in presentation

That is, the prototype should prove both:
- fact -> rule legibility
- truth -> trust usability
