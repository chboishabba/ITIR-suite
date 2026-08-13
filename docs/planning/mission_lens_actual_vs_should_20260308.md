# Mission Lens: Actual vs Should (2026-03-08)

## Purpose
Add a fused mission surface that renders:

- where observed activity actually went
- where commitments / missions / tasks say attention should go

This remains an ITIR-owned semantic/planning lens rendered against SB’s
process-lens data. It does not redefine SB as the planning authority.

## Shipped bounded slice
- `itir.sqlite` now contains mission planning tables:
  - `mission_plan_nodes`
  - `mission_plan_edges`
  - `mission_plan_deadlines`
  - `mission_plan_receipts`
- Current planning nodes are seeded from persisted `mission_observer` rows.
- A new `SensibLaw/scripts/mission_lens.py` script now:
  - builds a fused mission-lens artifact from `itir.sqlite` + `dashboard.sqlite`
  - exposes `report`
  - exposes bounded authoring via `add-node`
  - exposes reviewed actual-to-mission linking via `add-mapping`
- `itir-svelte` now exposes `/graphs/mission-lens`:
  - bipartite actual-vs-should flow view
  - layered mission/phase/task graph
  - deadline semantics panel
  - drift summary
  - bounded planning-node creation form
  - reviewed actual mapping panel over concrete SB activity rows

## Deadline semantics
Current deadline handling is explicit and conservative:

- `exact_time`
- `day_bound`
- `range_bound`
- `horizon_bound`
- `ambiguous`

Raw phrases are preserved. Calendar-grade normalization only happens when the
phrase already carries enough support.

## Current limits
- Actual-to-mission mapping now has two tiers:
  - reviewed links persisted in `itir.sqlite` (`mission_actual_mappings`)
  - bounded lexical fallback over timeline/detail/title text when no reviewed
    link exists
- Automatic mapping is still heuristic when no reviewed link exists:
  timeline/detail/title lexical matches over existing SB payloads, plus unmapped
  activity fallback.
- Planning authoring is still minimal:
  create node + parent + target weight + deadline semantics.
- Repeated/routine task extraction is not part of this slice yet.
