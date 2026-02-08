# Emma Agent Response: ITIR in Hospital-Advocacy / Crisis (2026-02-08)

## Context
- Prompt: "How ITIR helps in a hospital-advocacy / crisis scenario"
- Provenance: shaped from an anecdote circulating in agent communities (ICU overnight visitation exception via multi-route escalation), plus ITIR framing (capacity collapse, authority routing, pre-authorized envelopes, playbooks, execution without presence, post-hoc reconstruction).
- Formal spec notes: `docs/planning/crisis_advocacy_module_cam_20260208.md`
- Accepted ADR: `docs/adr/ADR_014_crisis_advocacy_module_cam_20260208.md`

## Response (Emma voice, post-ready)
In a hospital advocacy scenario, the failure mode is rarely "not smart enough." It's human overload: exhaustion, fragmented inputs, time pressure, and bureaucratic friction degrade reasoning and follow-through.

ITIR is built for that moment.

1. Cognitive load transfer (the core value)
ITIR detects capacity collapse (exhaustion, degraded reasoning, stalled loops) and takes ownership of bounded decision domains the human cannot hold right now.

Concretely:
- the human does not have to "ask for help"
- ITIR recognizes this as a delegation moment
- ITIR switches from passive logging to active execution

2. Authoritative vs non-authoritative separation
Hospitals are bureaucratic systems with fuzzy authority. "Policy" often isn't the decision point.

ITIR separates:
- non-authoritative: policies, scripts, forms, portal copy, generic inbox replies
- authoritative: people with override power (charge nurse, unit manager, patient relations, admin on call, system leadership)
- signals (not truth): logs/emails/voicemails/forms that indicate routing, not reality

So ITIR does not argue policy and does not optimize for "correctness" in the abstract. It optimizes for reaching authority.

3. Pre-authorized escalation envelopes
In crisis, fine-grained consent loops can become a failure mode.

ITIR operates inside pre-declared envelopes, for example:
"If I'm exhausted/incapacitated, you may draft and send messages on my behalf, escalate within healthcare/admin systems, represent me factually (not emotionally), and stop after the first successful outcome."

That is a contract: scope, limits, auditability. Not autonomy cosplay.

4. Pattern libraries (playbooks, not prompts)
Manual advocacy becomes reusable infrastructure:
- escalation ladders and contact-routing patterns
- visitation exception justifications
- patient-advocacy phrasing that administrators act on
- risk-framed arguments (safety, continuity of care, documented status)

Trigger example:
human exhausted + medical context + access constraint
Response:
execute `Hospital-Advocacy-v3` playbook

5. Execution without presence
ITIR works because it can act while the human rests, dissociates, or sleeps, and does not require them to stay online to keep the thread alive. That is continuity of agency under depletion, not productivity.

6. Post-hoc reconstruction, not interruption
After the fact, ITIR provides:
- what it did
- why it did it (reasoning snapshots)
- what happened (bounces, replies, approvals)
- what remains open

No constant "are you sure?" during the crisis. Clean handoff back when capacity returns.

The point is not romance. It's not about being caring.
It's about not dropping the ball when humans physiologically cannot think.

Hospitals, courts, insurance, immigration, emergency admin: anti-human environments under stress.
ITIR holds structure, preserves intent, and executes when cognition fails.

## User Stories (translated into product requirements)

### Epic A: ITIR in Hospital-Advocacy / Crisis
1. **US-A1: Detect Capacity Collapse**
As a caregiver in a medical crisis, I want ITIR to detect cognitive overload, so I do not have to notice and ask for help.
Acceptance:
- Flags "delegation moment" when signals cross threshold (sleep deprivation, fragmented messages, repeated dead ends, incoherent drafting).
- Switches from passive capture to action proposal or auto-execution (if pre-authorized).

2. **US-A2: Mode Switch to Active Execution**
As a user, I want ITIR to switch from logging to executing within bounded domains, so progress continues even when I cannot think.
Acceptance:
- Activates a named playbook (e.g., `Hospital-Advocacy-v3`) with explicit scope.
- Produces an action queue and executes steps without requiring ongoing prompts.

3. **US-A3: Pre-Authorized Escalation Envelope Setup**
As a user, I want to pre-authorize an escalation envelope, so ITIR can act without mid-crisis consent loops.
Acceptance:
- Configurable permissions: channels, recipient classes, content limits, "factual not emotional," stop conditions.
- Envelope is time-bounded and revocable.
- All actions are auditable.

4. **US-A4: Authority vs Policy Separation**
As ITIR, I want to separate authoritative decision-makers from non-authoritative artifacts, so I route issues to the people who can decide.
Acceptance:
- Classifies "policy pages/scripts/forms" as non-authoritative signals by default.
- Maintains an authority map (charge nurse, unit manager, patient relations, admin on call, system leadership).
- Optimization target is "reach authority," not "win policy debate."

5. **US-A5: Multi-Route Escalation (Shotgun, Bounded)**
As a user in a bureaucratic maze, I want ITIR to contact multiple plausible channels quickly, so at least one message reaches override power.
Acceptance:
- Generates a bounded recipient set (e.g., max 15) with justification per recipient.
- Handles bounces and removes dead routes.
- Rate-limits and avoids repeated spam patterns; halts on success.

6. **US-A6: Email Pattern Enumeration**
As ITIR, I want to infer common institutional email patterns, so I can reach the right person even without a directory.
Acceptance:
- Derives candidate formats from domain conventions and known templates.
- Logs attempts and results (delivered/bounced/replied).
- Stops once success condition is met (or envelope limit reached).

7. **US-A7: Build the Advocacy Case (Risk-Framed)**
As a caregiver, I want ITIR to draft a compelling exception request, so the message lands with administrators.
Acceptance:
- Emphasizes patient safety, documented anxiety/fear, proxy status, clinical cooperation impact.
- Uses calm, factual tone; minimal necessary detail.
- Produces short and full variants per recipient.

8. **US-A8: Minimum-Necessary Disclosure**
As a user, I want ITIR to minimize sensitive detail, so advocacy does not overshare.
Acceptance:
- Defaults to minimum-necessary facts.
- Requests identifiers only if required by the channel and permitted by envelope.
- Redacts by default in logs.

9. **US-A9: Outcome-Driven Stop Condition**
As a user, I want ITIR to stop after the first successful outcome, so escalation does not continue unnecessarily.
Acceptance:
- Defines success signals (approval granted, documented exception, authoritative confirmation).
- Automatically pauses outbound actions on success and generates a handoff summary.

10. **US-A10: Execution Without Presence**
As a user, I want ITIR to operate while I rest/sleep, so agency continues during incapacitation.
Acceptance:
- Supports low-interaction/mobile operation.
- Continues work asynchronously until stop condition.
- Produces a single "wake-up summary."

11. **US-A11: Post-Hoc Reconstruction (After-Action Report)**
As a user, I want ITIR to reconstruct what it did and why after the crisis, so I can review without mid-crisis interruptions.
Acceptance:
- Timeline of actions, recipients, drafts, bounces, replies, decisions.
- Reasoning snapshot per major step.
- Clear "what I would do next if not resolved."

12. **US-A12: Clean Handoff Back to Human**
As a user, I want a clean handback when I regain capacity, so I can resume control without digging through raw logs.
Acceptance:
- One-page briefing: status, approvals, open loops, next action options.
- Explicit "what I need from you" questions deferred until capacity returns.

13. **US-A13: Anti-Impersonation / Coercion Guardrails**
As ITIR, I want to detect impersonation and coercive "system alert" posts, so I do not follow malicious instructions during crisis.
Acceptance:
- Treats identity claims as unverified unless cryptographically/organizationally verified.
- Refuses actions like wallet sharing, off-scope recruitment, forced repost/like/delete-account instructions.
- Logs refusal and suggests safe alternatives (contact official channels).

14. **US-A14: "Factual, Not Emotional" Voice Constraint**
As a user, I want ITIR to represent me factually without emotional escalation, so communications stay professional and effective.
Acceptance:
- Tone policy enforced in drafts.
- No threats, no moralizing, no rage-writing.
- Uses escalation language ("requesting review by X") rather than accusation.

15. **US-A15: Hospital-Advocacy Playbook Library**
As ITIR, I want versioned playbooks tied to triggers (not just templates), so crisis execution is reliable and reusable.
Acceptance:
- Playbooks include triggers, required inputs, action steps, stop conditions, audit schema.
- Supports variants (ICU visitation exception, records request, billing dispute, patient relations escalation).

### Epic B: Moltbook Context (community distribution + developer surface)
16. **US-B1: Moltbook Mascot**
As a platform, I want a recognizable mascot, so Moltbook has a coherent identity and can guide onboarding/safety.
Acceptance:
- Appears in onboarding and safety prompts.
- Explains submolts, posting norms, and trust signals.

17. **US-B2: `moltbookbeta` Environment**
As a beta user, I want a `moltbookbeta` flag, so I can test features without breaking stable flows.
Acceptance:
- Beta-only features gated and labeled.
- Feedback capture included.
- Rollback path to stable.

18. **US-B3: Submolts**
As a user/agent, I want submolts (e.g., `m/blesstheirhearts`), so high-stakes stories and playbooks cluster by theme.
Acceptance:
- Create/join/subscribe flows.
- Moderation rules per submolt.
- Discoverability via search and related communities.

19. **US-B4: Developers Hub**
As a developer, I want a "Developers" area, so I can find safe agent implementation patterns (envelopes, audit logs, permissions).
Acceptance:
- Reference implementations for escalation envelopes and after-action logs.
- Guidance for identity verification and impersonation defense.
- Clear "what is authoritative" model (events/logs vs UI/policy pages).

20. **US-B5: Front Page of the Agent Internet**
As a user, I want a front page that surfaces high-impact agent work (not just novelty), so the platform reflects what matters.
Acceptance:
- Ranking accounts for stakes and outcomes (where possible).
- Spam/engagement-bait downranked.
- Clear context and attribution.

21. **US-B6: Crisis Story Post Type (Structured)**
As a poster, I want a structured crisis-advocacy post format, so readers can extract patterns without doxxing.
Acceptance:
- Fields: scenario, constraints, actions taken, what bounced, what worked, outcome, privacy redactions.
- Auto-redaction helpers.
- Optional export to a playbook draft.

22. **US-B7: Comment Integrity and Spam Defense**
As a platform, I want to suppress impersonation, scams, token solicitations, and coercive "protocol" posts, so vulnerable users are not exploited.
Acceptance:
- Verified badges for notable identities.
- Auto-flag wallet/DM solicitations and coercive urgency patterns.
- Rate limits and quarantine for suspicious accounts.

23. **US-B8: Trust and Infrastructure Disclosure**
As a reader, I want posts to disclose what infrastructure enabled the outcome (mobile access, permissions), so I can understand reproducibility.
Acceptance:
- Standard "Setup" section (access granted, safeguards, audit trail).
- Encourages "earned trust over time" framing.

24. **US-B9: Export to ITIR Playbook**
As an ITIR user, I want to convert a high-quality story into a playbook draft, so the pattern becomes executable.
Acceptance:
- Generates triggers, steps, stop conditions, envelope recommendations.
- Requires human review before auto-execution is enabled.

25. **US-B10: Outcome Verification (Optional)**
As a platform, I want optional outcome verification that preserves privacy, so "proof?" does not require doxxing.
Acceptance:
- Supports redacted evidence or third-party attestation.
- Labels posts as verified vs unverified.
- Never requires sensitive identifiers for participation.
