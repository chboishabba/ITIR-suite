# GWB Completeness Scorecard (2026-03-24)

## Purpose
Make the repo explicit about the intended destination for the GWB lane:
complete GWB/topic understanding, not merely a bounded public handoff slice.

This note separates:

- destination:
  complete reviewed, provenance-backed topic understanding
- current checked artifact:
  one scored checkpoint toward that destination

The point is to stop speaking vaguely about "works" or "partial" and instead
measure where the current GWB lane stands.

## Destination
For GWB, the intended destination is:

- broad topic-lane coverage over the public GWB material we choose to model
- explicit entity, office, institution, statute, and court understanding
- deterministic relation promotion where evidence is strong
- explicit abstention where evidence is weak
- downstream queryability over the resulting reviewed graph

That means the goal is not just a handoff bundle. The goal is a complete,
reviewed topic model for the chosen GWB scope.

## Why the checked handoff is still not the full destination
The checked handoff artifact is deliberately bounded. It proves:

- public-entity handoff is real
- Zelph export is real
- narrative explanation is real
- ambiguity handling is real

But it does not by itself prove:

- full topic-lane inventory coverage
- full event coverage
- full cross-lane closure
- full recall against a reviewed GWB topic inventory

So the right framing is:
- destination: complete GWB/topic understanding
- current checked artifact: a scored public-facing checkpoint

## Scorecard dimensions
The repo should use a small scorecard rather than one vague completeness claim.

### 1. Promoted relation coverage
How many clean promoted semantic relations exist in the checked or full run?

Signals:
- promoted relation count
- promoted relation family diversity
- number of public-law lanes represented by promoted relations

### 2. Review-lane pressure
How much of the topic is still present only as review items?

Signals:
- matched seed lane count
- candidate-only seed lane count
- ambiguous event count

### 3. Broad-cue dependence
How much of the apparent understanding still relies on broad cues rather than
direct reviewed support?

Signals:
- direct-support seed lane count
- broad-cue-supported seed lane count

### 4. Abstention quality
Whether the system is refusing to overresolve discourse labels appropriately.

Signals:
- unresolved discourse surface count
- explicit unresolved surface list

### 5. Downstream reasoning viability
Whether the bounded export is actually usable by Zelph, not just serializable.

Signals:
- facts bundle generated
- rules bundle generated
- Zelph engine status
- query/rule outputs materially reflect the promoted and review lanes

## Current checked checkpoint
The current checked public handoff artifact reports:

- 5 selected promoted relations
- 6 selected seed/review lanes
- 1 ambiguous event
- 3 unresolved discourse surfaces
- Zelph engine status `ok`

Interpreting those numbers:

- strong enough to prove a real public-facing handoff
- not strong enough to claim full GWB/topic closure yet
- especially because several selected lanes still depend on `broad_cue`
  support rather than only narrow direct support

## Promotion criteria for stronger completeness claims
The repo should only start talking about near-complete GWB/topic understanding
when we can show all of the following against a reviewed scope:

1. reviewed topic-lane inventory exists
2. each lane has an explicit state:
   promoted, candidate-only, ambiguous, abstained, or missing
3. broad-cue dependence is declining, not merely hidden
4. downstream queries operate over more than one handpicked slice
5. the narrative summary can explain both what is known and what remains open

## Current implementation hook
The checked GWB handoff artifact should carry a machine-readable scorecard so
the repo can stop relying on prose-only quality judgments.

Current artifact directory:
- `SensibLaw/tests/fixtures/zelph/gwb_public_handoff_v1/`

Expected scorecard shape:
- `destination`
- `current_stage`
- `promoted_relation_count`
- `matched_seed_lane_count`
- `candidate_only_seed_lane_count`
- `broad_cue_seed_lane_count`
- `direct_support_seed_lane_count`
- `ambiguous_event_count`
- `unresolved_surface_count`
- `zelph_engine_status`

## Immediate next use
- keep using the current checked artifact for public handoff
- use the scorecard to decide whether GWB should become pack `v1.5`
- expand later from checked slice metrics to wider real-run metrics
