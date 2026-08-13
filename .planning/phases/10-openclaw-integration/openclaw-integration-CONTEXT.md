# Phase 10: OpenClaw Integration - Context

**Gathered:** 2026-02-06
**Status:** Ready for planning

<vision>
## How This Should Work

OpenClaw is a goal-seeking action engine; StatiBaker/ITIR is a time-bounded
truth substrate. When users combine them, SB/ITIR should make agent activity
legible, bounded, and reversible without becoming an agent, optimizer, or
authority. SB should record what happened (time, scope, envelope, evidence)
while ITIR surfaces tension between claims and evidence. Humans decide.
</vision>

<essential>
## What Must Be Nailed

- SB remains a flight recorder: evidence only, no semantic authority.
- ITIR surfaces contradictions without acting or optimizing.
- OpenClaw remains the actor; SB/ITIR never become the control plane.
</essential>

<boundaries>
## What's Out of Scope

- Auto-optimization loops or prompt rewriting by SB/ITIR.
- SB inference of agent intent or correctness.
- Any auto-triggered execution based on ITIR output.
</boundaries>

<specifics>
## Specific Ideas

- Execution Envelope (sealed run header) as the atomic ingestion unit.
- Prompt hash first; prompt text only as optional content-addressed artifact.
- Explicit scope declarations, not permissions, to enable later auditing.
- Activity-event subtype for tool executions with envelope + artifacts.
</specifics>

<notes>
## Additional Context

SB should be the place where claims must cash out against evidence. It should
record explicit absence and human interventions; ITIR should only surface
patterned tensions (drift, scope creep, intervention frequency) without
recommending changes.
</notes>

---

*Phase: 10-openclaw-integration*
*Context gathered: 2026-02-06*
