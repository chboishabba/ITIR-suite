# ITIR x SensibLaw Operational Readiness Overlay (2026-03-28)

## Purpose
Record the strongest repo-facing additions pulled from the refreshed
`ZKP for ITIR SensibLaw` thread without changing the existing receipts-first
compiler spine.

This note is an operational overlay, not a replacement architecture.
It clarifies what is still missing if the suite is to function as a usable
service rather than only a coherent internal design.

## Resolved Thread Metadata
- title: `ZKP for ITIR SensibLaw`
- online UUID: `69c7b950-daec-839d-89a9-8fd8e22c9136`
- canonical thread ID: `31a47318f53b61cac9f82705e2595b1a08f9af66`
- source used: `db` after direct UUID pull into `~/chat_archive.sqlite`

## Main Decision
The current receipts-first / trust-preserving architecture still holds.

The main newly-sharpened gap is operational readiness:
- service levels are not yet defined
- incident vs problem handling is not yet explicit
- measurable success criteria are still missing
- explicit system-boundary and handoff views are still too implicit

So the next maturity step is not more ontology.
It is adding bounded service/quality/control definitions around the existing
compiler spine.

## Readiness Gaps
### 1. Service level definition
The suite still lacks bounded definitions for:
- response time expectations
- output reliability expectations
- escalation timing or handoff rules

Without this, the system may be structurally sound but operationally vague.

### 2. Incident vs problem distinction
The suite should distinguish:
- incident:
  immediate harm/risk requiring triage or urgent operator attention
- problem:
  repeatable systemic failure in extraction, promotion, interpretation, or
  output handling

Without that separation, there is no clean operational control loop.

### 3. Measurable success criteria
The architecture is strong, but success is still under-specified.

The repo should define bounded measures for:
- extraction coverage
- promotion precision / abstention appropriateness
- proof/output grounding quality
- user-trust / usability outcomes

### 4. Explicit system boundary views
The repo already contains the right conceptual layers, but the operational
view is still too implicit.

The next docs step should make system boundaries explicit across:
- source ingress
- promotion authority
- graph / proof derivation
- publish/output rendering
- operator escalation or override points

## Relationship To Existing Notes
This note refines, rather than replaces:
- `docs/planning/itir_sensiblaw_receipts_first_compiler_spine_20260328.md`
- `docs/planning/itir_sensiblaw_identity_trust_alignment_layer_20260328.md`

The combination now reads as:
- compiler spine:
  source -> extraction -> promotion -> reasoning -> publishing
- trust refinement:
  truth must remain usable and non-gaslighting
- readiness overlay:
  the service must also define operational control, success criteria, and
  boundary views

## Best Next Milestone Refinement
The bounded doctrine prototype should now demonstrate not only the core
compiler spine, but also the first operational-readiness slice:
- one explicit success metric set
- one incident vs problem distinction in operator flow
- one bounded system-context / handoff view

That is the smallest step that turns the current architecture from coherent
design into controlled service behavior.
