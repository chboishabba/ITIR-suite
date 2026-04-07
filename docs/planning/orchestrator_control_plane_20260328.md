# Orchestrator Control-Plane Status

Date: 2026-03-28

## Scope

Record the current control-plane state for shared Codex orchestration skills as
used by `ITIR-suite`.

## Current supported state

- Shared project docs are the canonical common context:
  - `spec.md`
  - `architecture.md`
  - `plan.md`
  - `devlog.md`
  - `COMPACTIFIED_CONTEXT.md`
- Runner-local orchestrator state is now namespaced per orchestrator instance:
  - `status.<id>.json`
  - `orchestrator.<id>.log`
  - `orchestrator.<id>.child.log`
- Child handoffs now start from:
  - a compact ZKP `O/R/C/S/L/P/G/F` frame
  - a compact model-allocation block with runtime scorecard, selected model,
    escalation rule, de-escalation rule, and fallback model
- Optional `chatter.log` is advisory only.

## Supported by convention, not yet first-class

- A master orchestrator may coordinate multiple sub-orchestrators in the same
  repo by:
  - assigning each runner a distinct `orchestrator_id`
  - sharing project docs
  - keeping runner-local state/logs separate
  - optionally using `chatter.log` for bounded advisory handoff

This is workable today, but it is still a convention rather than a governed
runtime architecture.

## First-class hierarchy support

- shared Codex runtime now emits `parent_orchestrator_id` metadata for each
  orchestrator, binding sub-orchestrator state and lane ownership to the
  coordinating parent
- lane and lane-claim ownership metadata now live under
  `.autonomous-orchestrator/lane_claims/<orchestrator>.json`, giving each runner
  a persistent lease plus ownership footprint for its current lane
- an active registry with heartbeats appears at
  `.autonomous-orchestrator/registry.json`, keeping `parent_orchestrator_id`,
  lane, heartbeat, and claim references for every live orchestrator instance
- parent-facing completion and escalation history is persisted underneath
  `.autonomous-orchestrator/parent_reports/<parent>.json` so the next tier can
  observe when children finish or escalate
- even the idle-complete path writes metadata, registry, and parent completion
  surfaces so the documented control-plane state stays accurate across both
  busy and idle transitions

## Decision

Treat master/sub-orchestrator support as shipped shared-runtime infrastructure
for bounded hierarchy metadata, ownership, and reporting.

Current rule:

- it is correct to use one top-level allocator/orchestrator plus multiple
  namespaced `autonomous-orchestrator` runners in the same repo
- it is correct to rely on the runtime-owned `parent_orchestrator_id`,
  lane-claim, registry, and parent-report surfaces rather than treating them as
  convention-only behavior

## Next implementation target

Keep the newly-deployed registry and ownership surfaces healthy and transparent:

- monitor `.autonomous-orchestrator/registry.json` and `.autonomous-orchestrator/lane_claims/*.json`
  to ensure heartbeats, lane ownership, and claim metadata remain current
- keep `.autonomous-orchestrator/parent_reports/<parent>.json` aligned with
  completion and escalation outcomes so the next rung can observe each leaf
  orchestration decision
- document any further control-plane behavior changes so the described
  canonical state stays accurate for future coordinators
