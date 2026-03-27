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

## Missing first-class support

- no explicit parent/child orchestrator registry
- no `parent_orchestrator_id` contract
- no first-class lane or claim ownership file
- no sub-orchestrator lifecycle management
- no completion/escalation path back to a parent orchestrator

## Decision

Treat master/sub-orchestrator support as a next control-plane capability rather
than as already-shipped infrastructure.

Near-term rule:

- it is correct to use one top-level allocator/orchestrator plus multiple
  namespaced `autonomous-orchestrator` runners in the same repo
- it is not correct to claim that first-class hierarchical orchestrator support
  already exists

## Next implementation target

Add a small governed registry/ownership layer for orchestrator hierarchies:

- `parent_orchestrator_id`
- `lane`
- shared registry of active orchestrators
- claim/heartbeat metadata
- parent-facing completion/escalation reporting
