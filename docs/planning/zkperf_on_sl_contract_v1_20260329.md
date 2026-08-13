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

## Example fixture

Use:

- `docs/planning/jmd_fixtures/zkperf_on_sl_observation_v1.example.json`

as the first tiny shape check for this contract.
