# ADR-014: Crisis-Advocacy Module (CAM)

Status: Accepted  
Date: 2026-02-08  
Decision owner: ITIR Core  
Applies to: ITIR execution surfaces; SB observer surfaces; norms-review/lint surfaces  

Related:
- `docs/planning/crisis_advocacy_module_cam_20260208.md` (design/spec notes)
- `docs/planning/emma_agent_hospital_advocacy_response_20260208.md` (origin narrative + user stories)
- `docs/planning/health_data_connector_guardrails_20260208.md` (minimum-necessary disclosure posture for sensitive domains)
- `docs/adr/ADR_contextual_fields_non_authoritative.md` (non-authoritative overlays doctrine)

## Context

Humans experience temporary cognitive incapacity during crisis (exhaustion,
stress, illness). In these moments:
- intent remains valid
- judgment exists but cannot be executed
- bureaucratic systems punish delay and confusion

Core components (SB, non-authoritative overlays, and interpretive layers) are
explicitly constrained against real-time intervention by default. This creates
a gap: during crises, inaction can cause material harm.

## Decision

Introduce a Crisis-Advocacy Module (CAM) with the following properties:
- Executes bounded, pre-authorized advocacy
- Operates only inside explicit escalation envelopes
- Acts once per incident (single-shot) unless explicitly re-authorized
- Hands control back cleanly
- Produces audit artifacts suitable for post-hoc reconstruction and review

CAM is executional, not interpretive.

## Scope

CAM MAY operate only when:
1. human cognitive capacity is degraded, and
2. stakes are administrative (routing/escalation), not deliberative, and
3. delay materially increases harm or reduces options

CAM SHALL NOT:
- make value judgments
- make medical decisions or provide medical advice
- create legal commitments or sign binding documents
- make financial commitments
- perform emotional interventions or "support" behaviors

## Non-Goals (Binding)

CAM SHALL NOT:
- substitute consent
- fabricate authority
- persist beyond the incident
- optimize emotionally
- generalize into "helpfulness everywhere"

If it does, it is out of spec.

## Consequences

Positive:
- preserves agency continuity under incapacity
- prevents intent loss during crisis
- converts chaotic escalation into bounded, auditable execution

Negative / tradeoffs:
- requires pre-crisis envelope definition
- cannot help when no envelope exists
- refuses action outside bounds (by design)

## Machine-Checkable Contracts

CAM SHALL validate escalation envelopes before execution.

Artifact(s):
- `docs/planning/schemas/escalation_envelope.schema.json`
- `docs/planning/schemas/escalation_envelope.schema.yaml`

Invalid envelope: hard fail (no execution).

## Phase / Gate Mapping (CAM-Local)

This defines CAM’s gate sequence without implying a suite-wide phase taxonomy.

1. Pre-authorization (design time)
- Artifact: escalation envelope (validated)
- Gate: envelope is explicitly defined and approved while the human is capacitated

2. Load detection (armed, inactive)
- Trigger: capacity degradation signals AND high-stakes domain entry
- Gate: detection logged; no action without a valid envelope

3. Execution authority gate (single-shot)
- Checks:
  - envelope exists and validates
  - domain match
  - proposed actions are a subset of allowed actions
  - proposed channels are a subset of allowed channels
- Gate: if satisfied, CAM may execute once for the incident
- Fail: abort execution and log only

4. Asymmetry / escalation (bounded routing)
- Allowed: authority routing and surface-area escalation within the envelope
- Invariant: no recursive optimization; no goal expansion

5. Termination gate
- Stop when any termination condition is met (success/denial/human abort/time limit)
- Invariant: CAM must exit promptly once stop condition is met

6. Reconstruction and review (post-hoc)
- SB: records actions, artifacts, and timeline
- Norms-review: evaluates envelope adherence and flags violations (future-only refinement)

