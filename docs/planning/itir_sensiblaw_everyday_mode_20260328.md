# ITIR x SensibLaw Everyday Mode (2026-03-28)

## Purpose
Clarify how the existing ITIR/SensibLaw service architecture should apply to
ordinary, low-stakes, non-adversarial scenarios without inventing a second
system.

This note is an application-mode refinement.
It does not replace the receipts-first compiler spine or the standard service
application model.

## Main Decision
The suite should be treated as one system with at least two operating modes:
- crisis / adversarial mode
- everyday / navigation mode

The architecture stays the same.
What changes are:
- thresholds
- defaults
- surface area
- output style

## Everyday Service Reading
In everyday use, the service should be request-driven rather than primarily
incident-driven.

Typical requests:
- help me understand this message
- help me organize this situation
- help me decide what to do next
- help me reduce uncertainty quickly

The user value shifts from:
- survival / defense / enforceability

to:
- navigation / clarity / optimization / confidence

## Quality Shift
For ordinary users, quality should emphasize:
- clarity
- speed
- usefulness
- confidence increase
- low-friction interaction

Output is acceptable if:
- it is quickly understandable
- it reduces confusion
- it suggests a concrete next step
- it does not feel preachy, robotic, or over-engineered

## Everyday Defect Grammar
Common everyday failures:
- over-complexity
- irrelevance
- tone mismatch
- too many options
- no clear next action

These are still defects, even when the output is formally correct.

## Architectural Reading
The container/application view does not change:
- input
- processing
- identity
- graph
- alignment
- obligation
- output
- governance

But the internal emphasis changes:
- identity layer becomes lighter:
  habits, preferences, goals, friction points
- obligation layer becomes softer:
  next best action, effort level, likely outcome, fallback

In everyday mode, "obligation" is better read as a recommended next action
surface rather than a formal enforceability surface.

## Dual State Still Applies
Even ordinary users still have:
- external state:
  facts, tasks, emails, schedules, commitments
- internal state:
  uncertainty, stress, confidence, preference, tolerance for effort

The same dual-state model applies, only at lower intensity.

## Gap Function In Everyday Mode
The same gap exists, but at lower severity:
- what is happening?
- what does it mean?
- what should I do next?
- can I trust my interpretation?

So the everyday mode still bridges:
fact -> meaning -> next step

## Relationship To Existing Notes
This note extends:
- `docs/planning/itir_sensiblaw_standard_service_application_model_20260328.md`
- `docs/planning/itir_sensiblaw_identity_trust_alignment_layer_20260328.md`
- `docs/planning/itir_sensiblaw_operational_readiness_overlay_20260328.md`

Together they now say:
- one architecture
- one standard service flow
- different operating modes depending on risk, urgency, and user burden

## Best Next Milestone Refinement
The next prototype/design pass should make the mode distinction explicit by
showing:
- one crisis/adversarial output path
- one everyday/lightweight output path
- bounded switching criteria between the two

That is the smallest step that proves the system can serve both high-stakes
and ordinary users without splitting into two unrelated products.
