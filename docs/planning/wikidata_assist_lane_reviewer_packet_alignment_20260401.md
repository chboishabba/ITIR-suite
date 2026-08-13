# Wikidata Assist Lane Reviewer Packet Alignment

Date: 2026-04-01

## Purpose

Describe how the Peter/Ege/Rosario assist lane should adopt the reviewer-packet
grammar already exercised by the Nat lane while keeping the assist effort
explicitly nonblocking and disjoint from Nat implementation work.

## Nonblocking Context

- The assist lane stays review-first and intentionally lacks the Nat migration or
  completion automation; adjust expectations accordingly.
- Reviewers should treat packets here as safe annotations for future coverage,
  not as signals to accelerate or parallel-run Nat automation. `reviewer_prompt`
  entries stay localized to review-state queries.
- Follow the same packet grammar with the understanding that `progress_claim`
  remains `reviewable_packet` until new coverage milestones materially
  expand the assist lane.

## Required Packet Fields

- `lane_id`
- `packet_id`
- `completion_baseline` (e.g., `4 / 7`)
- `case_list`: array of `{ case_id, qids, properties, summary }`
- `culprit_summary`: human-readable explanation
- `qualifier_reference_index`: per case metadata documenting qualifier/reference coverage
- `progress_claim`: explicit statement (`reviewable_packet`)
- `governance_flags`: `fail_closed`, `automation_allowed:false`, `promotion_guard`
- `reviewer_prompt`: short checklist or next decision question

## Grammar Reuse Notes

- The assist lane reuses each Nat field (e.g., `culprit_summary`,
  `qualifier_reference_index`) but populates them with reviewer-quality artifacts
  (context summaries, qualifier/reference checks) instead of migration outcomes.
- `promotion_guard` defaults to `hold` until a coverage milestone (see
  `docs/planning/wikidata_assist_lane_packet_fixture_note_20260402.md`) shows
  disjointness beyond the two seed cases.
- Assist reviewers default to Nat’s field names, but document assumptions
  locally so Nat coverage claims do not propagate automatically.

## Missing Inputs

1. broader disjointness coverage beyond the two seed cases
2. culprit sophistication metrics (hierarchical or contextual signals)
3. mapping from each packet case to the Nat-style split-plan or migration-plan lanes
4. explicit candidate-level qualifier/reference status to trigger promotion

## Promotion Guards

- `fail_closed` flag prevents treating the packet as a migration executor
- qualifier/reference index must be populated before any export claim
- continue to hold milestone `5 / 7` until follow-up packets show materially broader coverage

## Next Steps

1. Normalize future assist packets to include the same `qualifier_reference_index` as Nat cases.
2. Treat new cases as reviewer-grade entries until coverage + culprit metrics justify completion-model updates.

## Example Packet Mapping

- `case_id`: `disjointness_p2738_mack_group`
  - `properties`: `P2738`, `P31`, `P361`
  - `qualifier_reference_index`: `{ qualifiers: ["P2738"], refs: ["P854"] }`
  - `reviewer_prompt`: "Does this disjointness violation pair with subclass claims in a resolvable way?"
  - `promotion_guard`: `hold`

- `case_id`: `disjointness_p2738_durapower`
  - `properties`: `P2738`, `P11260`, `P31`
  - `qualifier_reference_index`: `{ qualifiers: ["P11260"], refs: [] }`
  - `reviewer_prompt`: "Is there sufficient culprit narrative to escalate review?"
  - `promotion_guard`: `hold`

## ITIL/ISO/Six Sigma

- ITIL: packet is a standard change to the assist review surface.
- ISO 9000: packet defines a reproducible deliverable for reviewers.
- Six Sigma: guard against promoting marginal coverage gains without a culprit story.
