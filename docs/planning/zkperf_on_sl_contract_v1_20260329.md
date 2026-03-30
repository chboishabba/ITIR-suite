# ZKPerf on SL Contract `v1` (2026-03-29)

## Goal

Define the smallest useful `SL`-side representation for `zkperf` execution and
proof material so later ranking/artifact-linkage work has a disciplined input.

This contract is intentionally narrow.

## Scope

This contract is for observational `zkperf` material represented on the `SL`
side.

It is **not**:

- an `SL` truth-promotion contract
- a shard/artifact contract
- a spectral ranking contract
- a transport/wire contract

## Core decision

`zkperf` on `SL` is an observational, receipt-bearing structure.

It can:

- inform
- justify
- trace
- link

It cannot directly:

- promote canonical truth
- redefine facts
- replace source/provenance requirements

## Minimal object

Use one bounded object family:

- `ZKPerfObservation`

Required fields:

- `zkperf_observation_id`
- `trace_id`
- `run_id`
- `asserted_at`
- `source_ref`
- `status`
- `metrics`
- `trace_refs`
- `proof_refs`
- `related_artifact_refs`
- `hash`

## Field semantics

### Identity and lineage

- `zkperf_observation_id`
  - stable local identifier for the observational object
- `trace_id`
  - identifier for the trace or trace-window being referenced
- `run_id`
  - execution/run identifier for grouping observations from one run
- `asserted_at`
  - ISO-8601 timestamp for contract-level determinism

### Provenance

- `source_ref`
  - deterministic pointer to the local source of the observation
  - examples:
    - run artifact path
    - receipt id
    - prior object id
- `status`
  - one of:
    - `observed`
    - `replayed`
    - `failed`
    - `disputed`

### Structured metrics/events

- `metrics`
  - list of structured key/value entries or typed metric rows
  - examples:
    - elapsed time
    - memory pressure
    - loop count
    - transition count
    - compression ratio

### Receipt/proof links

- `trace_refs`
  - refs to trace logs, trace windows, or trace receipts
- `proof_refs`
  - refs to proof artifacts, proof attachments, or verification outputs

### Artifact linkage

- `related_artifact_refs`
  - optional refs to `artifactId`, `artifactRevision`, `shardId`, or other
    already-defined logical artifact identifiers

### Determinism

- `hash`
  - deterministic digest over canonicalized payload
- canonical observation identity (for cross-system inventory):
  - `observationId` (alias of `zkperf_observation_id`)
  - `runId`
  - `traceId`
  - `assertedAtUtc` (normalized UTC of `asserted_at`)
  - `hash`
  - `sourceRef`
  - `status`

## Mandatory invariants

- `zkperf_observation_id`, `trace_id`, `run_id`, `asserted_at`, `source_ref`,
  `status`, and `hash` are required
- `metrics` must be structured, not a free-form prose blob
- at least one of `trace_refs` or `proof_refs` must be present
- `related_artifact_refs` are optional, but when present they must use existing
  artifact/shard ids rather than sink paths

## Boundary rules

### What it may do

- support later ranking/comparison
- support operator drill-in
- support receipt/proof linkage
- support artifact/run correlation

### What it may not do

- directly create promoted `Claim` objects
- directly mutate canonical `Observation` truth state
- bypass SL source/provenance discipline

## Relationship to later layers

- spectral ranking may consume `ZKPerfObservation` features later
- shard/artifact layers may link to `related_artifact_refs`
- message/envelope layers may carry this object later
- stream/container publication may batch observations into explicit windows via:
  `docs/planning/zkperf_stream_shard_contract_v1_20260330.md`

But this contract itself remains local, bounded, and observational.

## Implemented versus intended layers

This contract is deliberately smaller than the full theoretical `zkperf`
surface discussed elsewhere in the repo and chats.

### Implemented now in ITIR-suite

- execution/runtime metrics
  - wall time
  - exit status
  - child CPU
  - RSS
  - stdout/stderr byte counts
  - page faults / context switches / basic OS counters
- measured execution-trace metrics
  - stepwise observations derived from CLI progress events
  - stage / section / status one-hot metrics
  - numeric progress details such as counts, elapsed seconds, and ratios
  - this is the primary spectrogram surface for execution dynamics
- payload / read-model structure metrics
  - payload size
  - tree size / depth
- affidavit-lane semantic counters
  - proposition counts
  - coverage / missing-review counts
  - conflict / support / relation buckets
  - source-review and Zelph fact counts
  - bounded semantic objective:
    - `semantic_gap_score`
- stream / publication metrics
  - window counts
  - observation counts
  - HF publish / index / verify timings
  - receipt / acknowledgement linkage
- optional external theory evidence ingestion
  - bounded `../dashi_agda` JSON evidence can be attached to an observation
  - current target surface:
    - MDL descent / monotonicity witnesses
    - cone / Fejér / closest-point admissibility flags when already present in
      the evidence artifact
  - this does not run Agda inside the wrapper; it materializes already-produced
    evidence into zkperf metrics and refs

### Not yet implemented in the live wrapper

- cone / contraction diagnostics
- native MDL descent trajectories generated by the wrapper itself
- local function-relative MDL surrogates (for example `local_function_mdl_v1`)
  are not yet implemented; only external witness ingestion exists today
- eigen / resonance / overlap diagnostics
- embedding basin / collapse diagnostics
- full `O/R/C/S/L/P/G/F` system summaries
- a single derived health readout such as:
  - `STRUCTURE`
  - `DYNAMICS`
  - `MDL`
  - `GEOMETRY`
  - `ALIGNMENT`

So the current repo state should be read as:

- `zkperf-operational-v1` is implemented
- `zkperf-full-theory` is not yet implemented

## Theory-level scaffold `v0`

The next honest step for theory-facing zkperf is a scaffold, not a fake metric
drop.

Bounded contract:

- theory-facing layers must be reported as one of:
  - `unavailable`
  - `scaffolded`
  - `implemented`
- unavailable layers must not emit synthetic numeric scores pretending the
  underlying cone / MDL / eigen machinery exists
- a future compact health readout must remain availability-aware, for example:
  - `STRUCTURE = implemented`
  - `DYNAMICS = scaffolded`
  - `MDL = unavailable`
  - `GEOMETRY = unavailable`
  - `ALIGNMENT = scaffolded`

Initial scaffold status for this repo before optional external theory evidence:

- `STRUCTURE`
  - `implemented`
- `SEMANTICS`
  - `implemented`
- `DYNAMICS`
  - `scaffolded`
  - execution-trace observations exist, but not cone/contraction diagnostics
- `MDL`
  - `unavailable`
- `GEOMETRY`
  - `scaffolded`
  - feature/PCA/query-conditioned renderers exist, but not eigen/resonance
    admissibility diagnostics
- `ALIGNMENT`
  - `scaffolded`
  - bounded query-conditioned retrieval/debug views exist, but not a
    theory-backed overlap/resonance proof surface

A future bounded bridge may also expose a function-relative empirical MDL
surface without claiming full formal MDL:

- `local_function_mdl_v1`
  - scoped to one function id, one output schema, and one normalization rule
  - comparable only within that function family unless explicitly calibrated
  - intended for anomaly / regression / novelty detection, not universal MDL
  - candidate core fields:
    - `local_mdl.code_length`
    - `local_mdl.delta_vs_baseline`
    - `local_mdl.z_score`
    - `local_mdl.novelty_ratio`
    - `local_mdl.training_sample_count`

When bounded external theory evidence is attached:

- `MDL`
  - may move to `implemented`
  - only if the observation carries concrete MDL witness metrics derived from
    an external evidence artifact
- `DYNAMICS`
  - may move from `scaffolded` to `implemented`
  - only when cone / Fejér / closest-point witness metrics are present from
    the same evidence surface

Governance:

- do not promote a unified health score until at least one nontrivial theory
  layer moves from `unavailable` to `implemented`
- operator summaries may expose scaffold state, but must label it explicitly as
  contract/status rather than measured truth

## Bounded semantic objective `v1`

The affidavit lane now allows one explicit semantic objective surface without
pretending the full theory-level Lyapunov / MDL integration already exists.

### Purpose

Turn affidavit semantic state from raw counts into one bounded, operator-facing
gap score.

This is:

- a heuristic objective
- additive and observational
- suitable for operator comparison across runs

This is not:

- a truth-promotion rule
- a full MDL / Lyapunov proof
- a replacement for reading the underlying counters

### Intended shape

`semantic_gap_score` is a weighted cost over the current affidavit semantic
state.

Initial inputs:

- `summary.missing_review_count`
- `summary.conflict_state.unresolved`
- `summary.contested_affidavit_count`
- `summary.covered_count`

Interpretation:

- higher = worse semantic gap
- lower = better semantic closure

### Governance

The score must remain clearly labeled as a bounded `semantic-v1` heuristic
objective until a stronger lattice/MDL integration exists.

## Example fixture

Use:

- `docs/planning/jmd_fixtures/zkperf_on_sl_observation_v1.example.json`

as the first tiny shape check for this contract.
