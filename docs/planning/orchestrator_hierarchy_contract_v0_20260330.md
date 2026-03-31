# Orchestrator Hierarchy Contract (V0)

Date: 2026-03-30

Purpose: define the first concrete, bounded control-plane contract for
hierarchical orchestration in `ITIR-suite` without claiming runtime support
that does not yet exist.

## Contract status

- contract-only (planning/governance artifact)
- no default runtime writer/reader is asserted by this document
- all paths below are canonical targets for future implementation, not evidence
  of current persistence

## Scope

This V0 contract covers four missing first-class surfaces:

1. `parent_orchestrator_id`
2. lane/claim ownership
3. registry heartbeat
4. completion/escalation reporting to parent orchestrators

## Canonical artifacts (planned)

- registry snapshot:
  - `.codex/orchestration/registry.v1.json`
- lane claim records:
  - `.codex/orchestration/claims/<claim_id>.json`
- parent-facing reports stream:
  - `.codex/orchestration/reports/<parent_orchestrator_id>.jsonl`

## Common identity fields

Required in all envelopes unless marked optional:

- `schema_version`: string
- `orchestrator_id`: string
- `parent_orchestrator_id`: string or `null`
- `run_id`: string
- `lane_id`: string
- `claim_id`: string
- `recorded_at`: RFC3339 timestamp

Rules:

- top-level allocator sets `parent_orchestrator_id: null`
- sub-orchestrators must set non-null `parent_orchestrator_id`
- `claim_id` must be globally unique within a run

## Registry entry contract

`schema_version`: `orchestrator.registry_entry.v1`

Required fields:

- common identity fields (except `claim_id` may be `""` before claim assignment)
- `role`: `allocator | worker`
- `state`: `starting | active | idle | blocked | completed | escalated | stopped`
- `heartbeat_at`: RFC3339 timestamp
- `started_at`: RFC3339 timestamp
- `last_progress_at`: RFC3339 timestamp
- `owner`: object
- `lane`: object

`owner`:

- `owner_kind`: `human | agent`
- `owner_id`: string

`lane`:

- `lane_id`: string (must match top-level `lane_id`)
- `lane_title`: string
- `claim_mode`: `exclusive`

## Claim ownership contract

`schema_version`: `orchestrator.claim.v1`

Required fields:

- common identity fields
- `claim_state`: `claimed | released | transferred | expired`
- `claimed_at`: RFC3339 timestamp
- `lease_seconds`: integer (recommended default: `300`)
- `lease_expires_at`: RFC3339 timestamp
- `ownership`: object

`ownership`:

- `owner_orchestrator_id`: string
- `owner_parent_orchestrator_id`: string or `null`
- `handoff_reason`: string (required for `transferred`)

Rules:

- at most one `claimed` record per `(run_id, lane_id)` at a time
- heartbeat refresh may extend lease only by rewriting
  `lease_expires_at` for the active owner
- a claim is considered stale when `now > lease_expires_at`

## Heartbeat semantics

Heartbeat writes update:

- registry `heartbeat_at`
- registry `state`
- registry `last_progress_at` when work advanced
- active claim `lease_expires_at`

Recommended governance thresholds:

- `heartbeat_interval_seconds`: `60`
- `stale_after_seconds`: `180`
- `expiry_after_seconds`: based on claim `lease_seconds` (default `300`)

Interpretation:

- stale registry entry: no heartbeat within `stale_after_seconds`
- expired claim: lease timestamp elapsed
- stale and expired are control-plane signals, not automatic destructive action

## Parent-facing completion/escalation contract

`schema_version`: `orchestrator.parent_report.v1`

Required fields:

- common identity fields
- `report_id`: string
- `report_kind`: `completion | escalation | heartbeat_summary`
- `report_state`: `info | requires_parent_action`
- `summary`: string
- `details`: object

`details` minimum:

- `objective_ref`: string
- `result_ref`: string or `null`
- `blocking_reason`: string or `null`
- `requested_parent_action`: string or `null`
- `next_recommended_step`: string or `null`

Rules:

- completion report:
  - must set `report_kind=completion`
  - must set `blocking_reason=null`
  - should include concrete `result_ref`
- escalation report:
  - must set `report_kind=escalation`
  - must set non-null `blocking_reason`
  - must set non-null `requested_parent_action`
- heartbeat summary:
  - informational only
  - cannot close a claim

## Minimal JSON examples

Registry entry:

```json
{
  "schema_version": "orchestrator.registry_entry.v1",
  "orchestrator_id": "orchestrator.lane.aao-all-shell",
  "parent_orchestrator_id": "orchestrator.top",
  "run_id": "run_20260330T120000Z",
  "lane_id": "lane.wiki_timeline_aoo_all_route_shell",
  "claim_id": "claim_01HV...",
  "recorded_at": "2026-03-30T12:05:00Z",
  "role": "worker",
  "state": "active",
  "heartbeat_at": "2026-03-30T12:05:00Z",
  "started_at": "2026-03-30T12:00:10Z",
  "last_progress_at": "2026-03-30T12:04:31Z",
  "owner": {
    "owner_kind": "agent",
    "owner_id": "codex"
  },
  "lane": {
    "lane_id": "lane.wiki_timeline_aoo_all_route_shell",
    "lane_title": "AAO-all route shell lane",
    "claim_mode": "exclusive"
  }
}
```

Claim:

```json
{
  "schema_version": "orchestrator.claim.v1",
  "orchestrator_id": "orchestrator.lane.aao-all-shell",
  "parent_orchestrator_id": "orchestrator.top",
  "run_id": "run_20260330T120000Z",
  "lane_id": "lane.wiki_timeline_aoo_all_route_shell",
  "claim_id": "claim_01HV...",
  "recorded_at": "2026-03-30T12:05:00Z",
  "claim_state": "claimed",
  "claimed_at": "2026-03-30T12:00:15Z",
  "lease_seconds": 300,
  "lease_expires_at": "2026-03-30T12:10:00Z",
  "ownership": {
    "owner_orchestrator_id": "orchestrator.lane.aao-all-shell",
    "owner_parent_orchestrator_id": "orchestrator.top",
    "handoff_reason": ""
  }
}
```

Escalation report:

```json
{
  "schema_version": "orchestrator.parent_report.v1",
  "orchestrator_id": "orchestrator.lane.aao-all-shell",
  "parent_orchestrator_id": "orchestrator.top",
  "run_id": "run_20260330T120000Z",
  "lane_id": "lane.wiki_timeline_aoo_all_route_shell",
  "claim_id": "claim_01HV...",
  "recorded_at": "2026-03-30T12:11:00Z",
  "report_id": "report_01HV...",
  "report_kind": "escalation",
  "report_state": "requires_parent_action",
  "summary": "Blocked by unresolved contract conflict with adjacent lane.",
  "details": {
    "objective_ref": "docs/planning/wiki_timeline_aoo_all_route_refactor_brief_20260328.md",
    "result_ref": null,
    "blocking_reason": "conflicting ownership over shared helper output fields",
    "requested_parent_action": "resolve lane boundary and assign owner of helper schema",
    "next_recommended_step": "replay extraction slice once boundary decision is logged"
  }
}
```

## Governance gates for future runtime adoption

A runtime implementation may claim first-class hierarchical support only when:

1. registry writes/reads validate against this contract
2. claim exclusivity + lease expiry behavior are enforced
3. parent report stream receives completion and escalation events
4. top-level allocator can reconcile stale/expired entries deterministically

Until then, docs may reference this contract only as:

- proposed
- planned
- not yet runtime-enforced

## Non-goals for V0

- no scheduler policy for lane prioritization
- no auto-reassignment after expiry
- no distributed lock service requirement
- no cross-repo registry federation
