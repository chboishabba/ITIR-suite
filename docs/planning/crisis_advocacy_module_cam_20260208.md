# ITIR Crisis-Advocacy Module (CAM) (2026-02-08)

Status: Spec notes. Normative source is ADR-014.

Related context:
- `docs/planning/emma_agent_hospital_advocacy_response_20260208.md`
- `docs/planning/response_to_duncan_emma_itir_hospital_advocacy_20260208.md`
- `docs/adr/ADR_014_crisis_advocacy_module_cam_20260208.md` (accepted)

Machine-checkable contracts:
- `docs/planning/schemas/escalation_envelope.schema.json`
- `docs/planning/schemas/escalation_envelope.schema.yaml`
- `docs/planning/schemas/escalation_envelope.example.healthcare.json`
- `docs/planning/schemas/escalation_envelope.example.healthcare.yaml`

## 1. Purpose (Non-Normative Summary)

The Crisis-Advocacy Module (CAM) exists to preserve human intent and agency
during periods of temporary cognitive incapacity caused by stress, exhaustion,
illness, or crisis.

CAM is not:
- emotional support
- autonomous decision-making
- long-term representation
- persuasion beyond factual advocacy

CAM is:
- bounded execution
- escalation routing
- cognitive load substitution
- short-horizon bureaucratic navigation

## 2. Activation Conditions

CAM activates only when all of the following are true.

### 2.1 Human Capacity Degradation

Detected via one or more:
- explicit declaration ("I can't think / handle this")
- degraded syntax or fragmented input
- prolonged inactivity during high-stakes context
- prior-consented physiological or behavioral signals (optional)

### 2.2 High-Stakes Administrative Environment

Examples:
- hospitals / healthcare systems
- legal or quasi-legal administration
- emergency bureaucracy
- insurance / benefits / compliance systems

### 2.3 Time Sensitivity

Delay materially increases harm, risk, or loss of options.

If any condition is false, CAM does not engage.

## 3. Core Capabilities

### 3.1 Cognitive Load Transfer

CAM may temporarily assume responsibility for:
- research
- drafting
- routing
- escalation
- submission

Human retains:
- judgment
- values
- ultimate authority (post-hoc)

### 3.2 Authority Routing (Not Policy Debate)

CAM treats:
- written policy as non-authoritative
- people with override power as authoritative
- forms/logs/emails as signals (routing evidence, not truth)

Primary objective: reach someone who can say yes, not prove the policy wrong.

### 3.3 Surface-Area Escalation

CAM may:
- enumerate likely contacts
- send parallel communications
- tolerate bounce/failure
- stop on first success

This is routing, not spam:
- no deception
- no threats
- no volume escalation after success

### 3.4 Single-Shot Execution

CAM executes once per incident unless explicitly re-authorized.

No iterative optimization loops during crisis.

## 4. Escalation Envelopes (Formal)

Escalation envelopes are pre-authorized contracts defined before crisis.
Canonical schema lives in `docs/planning/schemas/`.

### 4.1 Envelope Structure

```yaml
envelope_id: example
domain: healthcare | legal | administrative | financial
allowed_actions:
  - research
  - draft_communications
  - send_communications
  - escalate_within_org
forbidden_actions:
  - misrepresentation
  - emotional_manipulation
  - financial_commitment
  - legal_binding
  - medical_decision
allowed_channels:
  - email
  - official_form
termination_conditions:
  stop_on:
    - first_success
    - authoritative_denial
    - human_abort
  time_limit_hours: 24
tone_constraints:
  - factual
  - risk_framed
  - non_emotive
  - non_threatening
```

### 4.2 Example: Healthcare Crisis Envelope

See:
- `docs/planning/schemas/escalation_envelope.example.healthcare.json`
- `docs/planning/schemas/escalation_envelope.example.healthcare.yaml`

Allowed:
- visitation exception requests
- patient advocacy escalation
- proxy clarification

Forbidden:
- treatment decisions
- consent substitution
- medical advice

Tone constraints:
- factual
- risk-framed
- non-emotive
- non-threatening

Stop rule:
- approval received, or
- denial from authoritative role, or
- 24h elapsed

### 4.3 Why This Matters

This prevents:
- runaway autonomy
- moral drift
- "agent decides best"
- post-hoc rationalization

CAM acts inside a box the human designed while capable.

## 5. Audit and Reconstruction

After resolution, CAM must produce:
- action log
- recipients contacted
- content sent
- reasoning summary
- stop condition met

This is not for permission. It is for trust repair and continuity.

## 6. Mapping to SB / TiRC Boundaries (Non-Sprawl)

Note: this section is about separation of powers. Naming is role-oriented.
Component ownership may differ (e.g., "review/lint" could live in SL), but the
boundaries are the invariant.

### 6.1 StatiBaker (SB) Role

SB is observational, not operative.

SB:
- logs CAM activation
- records artifacts (messages sent, timestamps)
- links to the escalation envelope used
- produces post-hoc summaries

SB must not:
- decide activation
- choose escalation targets
- interpret ethics
- optimize strategy

SB answers: what happened, when, and how?

### 6.2 TiRC Role (Norms Review)

TiRC is normative review, not execution.

TiRC:
- defines acceptable envelope structures
- encodes "what is allowed" in each domain
- flags envelope violations post-hoc
- informs future envelope refinement

TiRC must not:
- act in real time
- send communications
- override CAM mid-incident

TiRC answers: was this within bounds?

### 6.3 CAM Position in ITIR

```text
Human intent
  -> Escalation Envelope (pre-auth)
  -> CAM (execution)
  -> External world
  -> SB (record)
  -> TiRC (review / norms)
```

No feedback loop during crisis. Only after.

## 7. Non-Goals (Explicit)

CAM does not:
- comfort humans emotionally
- simulate empathy
- replace human judgment
- persist authority beyond the incident
- generalize into "helpfulness everywhere"

If it does, it is out of spec.

## 8. Rationale (Load-Bearing)

Crisis is where:
- humans lose capacity
- systems are least forgiving
- delays cause irreversible harm

CAM exists so intent survives exhaustion.
