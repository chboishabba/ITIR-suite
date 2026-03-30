# ZKPerf Stream Shard Contract v1 (2026-03-30)

## Goal

Define the smallest useful stream-layer contract between `ZKPerfObservation`
and the now-working HF publish substrate.

This contract is for observational zkperf stream transport only.

## Scope

This contract is:

- stream/window identity
- stream manifest
- latest pointer artifact
- revision index artifact
- container membership
- HF publication of a bounded stream container
- revision-bound read-back

It is not:

- truth promotion
- a spectral/ranking contract
- a remote JMD endpoint contract

## Core decision

Treat zkperf as an append-oriented stream of observational windows.

The correct ordering is:

`ZKPerfObservation -> stream window -> stream manifest -> container -> HF object -> acknowledged revision`

## Minimal objects

### ZKPerfStreamManifest

Required fields:

- `contractVersion`
- `streamId`
- `streamRevision`
- `streamKind`
- `windowingMode`
- `createdAtUtc`
- `windowCount`
- `observationCount`
- `observationIndex[]` (canonical observation identity rows)
- `latestWindowId`
- `sequenceRange`
- `windows[]`
- `containerObjectRef`

### ZKPerfStreamLatest

Required fields:

- `contractVersion`
- `streamId`
- `latestRevision`
- `latestWindowId`
- `windowCount`
- `observationCount`
- `sequenceRange`
- `containerObjectRef`
- `acknowledgedRevision`
- `verified`

### ZKPerfStreamIndex

Required fields:

- `contractVersion`
- `streamId`
- `createdAtUtc`
- `latestRevision`
- `latestWindowId`
- `revisionCount`
- `observationCount` (mirrors latest revision)
- `observationIndex` (canonical observation identity rows for the revision)
- `revisions[]`
- `indexObjectRef`

### RetentionPolicy

`v1` supports one explicit lifecycle policy:

- `policyVersion = zkperf-retention/v1`
- `mode = retain-latest-n`
- `maxRevisionCount`

### ZKPerfStreamWindowRef

Required fields:

- `windowId`
- `sequence`
- `runId`
- `traceId`
- `observationIds[]`
- `memberPath`
- `contentDigest`
- `sizeBytes`
- `startedAtUtc`
- `endedAtUtc`

## Windowing rule

For `v1`, use explicit bounded windows.

Each window is:

- append-safe within one `streamRevision`
- immutable once published
- addressable by `windowId`
- ordered by `sequence`

This means `streamRevision` is the publication snapshot and `sequence` is the
window order inside that snapshot.

## Retention/update rule

`v1` uses snapshot publication, not in-place mutation.

Allowed:

- publish a new `streamRevision`
- carry forward prior windows unchanged
- append new windows at higher sequence numbers

Not allowed:

- mutate a published window payload in place
- redefine a prior window's `contentDigest`

Revision history is tracked by an index artifact with explicit retention.

Each revision record carries:

- `streamRevision`
- `acknowledgedRevision`
- `windowCount`
- `latestWindowId`
- `sequenceRange`
- `containerObjectRef`
- `verified`
- `observationCount`
- `observationIndex`

When `retain-latest-n` is active, the index may prune the oldest revision
records after appending a newer one. Published container objects remain
immutable; retention only changes the active index surface.

## HF publication rule

HF carries the stream container as one uploaded object plus a manifest.

Minimum bounded publication sequence:

1. build stream manifest
2. write JSON window payloads into one tar container
3. upload tar to HF
4. record acknowledged revision
5. update and publish the stream index artifact
6. read back by acknowledged revision
7. verify tar digest parity
8. resolve `windowId -> memberPath -> payload`

## Consumer rule

Consumer may resolve either:

- one explicit `windowId`
- the latest window
- a bounded sequence range

through:

`window selection -> memberPath -> HF object by acknowledged revision -> payload`

An index-driven consumer may also resolve through:

`HF index object -> latestRevision or chosen streamRevision -> acknowledged container revision -> window selection -> payload`

`v1` still does not require rolling compaction or partial tar offset indexes.

## Boundary rule

This contract stays observational.

A zkperf stream window may:

- trace
- justify
- correlate
- drive downstream operational analysis

It may not:

- promote SL truth
- replace source/provenance requirements
- silently become a canonical semantic claim

## Promotion criteria

Treat `v1` as good enough only if it shows:

- stable `windowId` / `sequence` ordering
- immutable window payload digests
- successful HF publication by acknowledged revision
- successful read-back digest parity
- successful `windowId` payload recovery from the remote tar
- successful latest-window recovery from the remote tar
- append-only revision-index growth without mutation of prior revision records
  within the active retention window

## Fixture pack

Use:

- `docs/planning/jmd_fixtures/zkperf_stream_v1.example.json`
- `docs/planning/jmd_fixtures/zkperf_on_sl_observation_v1.example.json`

as the first bounded shape check.
