# ITIR x SensibLaw Standard Service Application Model (2026-03-28)

## Purpose
Turn the current receipts-first, trust-preserving, operational-readiness
architecture into a repeatable application pattern that can be used across new
case families without redesigning the system per scenario.

This note is service/application guidance.
It does not introduce a new truth contract.

## Main Decision
The suite should be applied to new cases through one standard service pattern
rather than by case-specific redesign.

The structure stays constant.
Only the input rule libraries, risk models, and institution-specific details
change.

## Universal Intake Pattern
Treat each new case as a hybrid of:
- service request:
  help me understand, organize, or act
- incident:
  something is wrong, harmful, urgent, or degrading

Required intake fields:
- person
- context domain
- immediate risk level
- evidence sources
- desired outcome

## Standard Value Stream
Every case should pass through the same bounded service flow:

1. intake
2. evidence structuring
3. identity/context modelling
4. alignment
5. obligation assignment
6. output
7. monitoring and escalation

This is the repeatable service pipeline above any case-specific library.

## SLA Layer
Each case family should define bounded expectations for:
- response time
- action time
- escalation trigger

These values will vary by case family, but the slots themselves should remain
standardized.

## Standard Output Requirements
Every processed case should produce:
- structured facts / atoms
- identity/context factors
- traceable graph links
- action recommendation
- evidence-backed justification

## Acceptance Criteria
Output is acceptable only if:
- every strong claim is traceable to evidence
- uncertainty is explicitly marked
- no hidden assumptions are silently introduced
- the output is usable by the affected person, not just formally correct

## Nonconformance Pattern
Treat these as standard nonconformance triggers:
- user rejects output as unusable or invalidating
- incorrect fact -> rule mapping
- key evidence omission
- emotional harm or trust breakdown caused by the output
- no clear next step or fallback path

Required response:
- flag the case
- classify the failure type
- adjust model/rules/operator path as needed
- reprocess rather than silently overwrite

## Universal CTQs
Track the same critical-to-quality dimensions across all case families:
- accuracy
- traceability
- trust acceptance
- time reduction
- actionability

## Universal Defect Types
Use one defect grammar across cases:
- mapping defect
- omission defect
- trust defect
- action defect
- escalation defect

## Measurement Model
Each case family should eventually support comparable measures for:
- traceable-output percentage
- user acceptance / trust score
- time saved versus baseline
- number of corrections or rework loops
- time to action

## Standard Container/Application View
The stable application pattern is:
- input interface
- processing engine
- identity engine
- graph engine
- alignment engine
- obligation layer
- output engine
- governance layer

The obligation layer is mandatory between alignment and output.
It assigns responsibility, time constraints, status, and fallback escalation.

## Universal Case Application Template
For any new scenario:

1. classify case type
2. build dual state:
   external facts/evidence/rules and internal trust/stress/confidence state
3. build legal/evidence graph and identity/trust graph
4. align conflicts, gaps, and misinterpretations
5. assign obligation:
   responsible actor, required action, deadline, fallback actor
6. generate explanation, action steps, risks, and alternatives
7. monitor whether action occurred and whether trust improved or degraded

## What Changes Across Cases
The structure does not change.
Only these case-specific inputs vary:
- rule set
- risk model
- trust sensitivity profile
- SLA values

## Relationship To Existing Notes
This note extends:
- `docs/planning/itir_sensiblaw_receipts_first_compiler_spine_20260328.md`
- `docs/planning/itir_sensiblaw_identity_trust_alignment_layer_20260328.md`
- `docs/planning/itir_sensiblaw_operational_readiness_overlay_20260328.md`

Together they now say:
- compiler spine:
  how truth is built
- trust refinement:
  how truth remains usable
- readiness overlay:
  what must exist for controlled service operation
- standard service application model:
  how to apply the same structure to any new case family

## Best Next Milestone Refinement
The first bounded doctrine prototype should now also demonstrate:
- one standardized intake shape
- one obligation-layer output
- one explicit nonconformance path
- one basic metric set for acceptance / traceability / actionability

That is the smallest step that proves the architecture can be applied
repeatably rather than only argued case by case.
