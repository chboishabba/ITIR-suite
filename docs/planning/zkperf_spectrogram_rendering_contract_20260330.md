# ZKPerf Spectrogram Rendering Contract (2026-03-30)

## Goal

Define the first honest visualization contract for rendering structured zkperf
traces as spectrogram-like views.

This is not an audio spectrogram contract.

It is a structure-over-execution contract.

## Core decision

Render:

- trace progression on one axis
- structured feature or spectral mode position on the other axis
- activation / alignment / contribution as color

Interpret the result as:

- persistent structure
- bursts / transitions
- collapse / flattening
- query-aligned resonance

Do not interpret it as sound/frequency analysis.

## Boundary rules

The visualization input must come from:

- structured `SL` facts
- zkperf-derived trace features
- explicitly derived spectral projections

The visualization input must not come primarily from:

- raw token overlap
- generic embedding similarity
- sink/layout accidents

## View stack

### View 1 — Structured feature spectrogram

- y-axis:
  - trace step / window / iteration
- x-axis:
  - ordered structured features or feature families from `Phi`
- color:
  - activation / alignment magnitude

Purpose:

- first truthful debugging view
- easiest to build
- least distorted by dimensionality reduction

### View 2 — PCA spectrogram

- y-axis:
  - trace step / window / iteration
- x-axis:
  - principal components `PC1..PCk`
- color:
  - projection magnitude

Purpose:

- the first properly spectral view
- shows dominant directions cleanly
- closest analogue to a “real” spectrogram

### View 3 — Query-conditioned spectrogram

- y-axis:
  - trace step / window / iteration
- x-axis:
  - query-conditioned basis or query-aligned projection
- color:
  - alignment with query dominant direction

Purpose:

- retrieval debugging
- showing which trace regions actually resonate with the query

## Supporting views

These remain useful, but they are not the primary spectrogram contract:

- spectral profile panel
- projection map
- harmony heatmap
- retrieval waterfall
- feature-family contribution chart

## Ordering rules

Raw feature order is usually misleading.

So:

- feature views must order by:
  - feature family, or
  - variance / importance / explained energy
- PCA views must order by:
  - explained variance rank

Without explicit ordering, the result risks looking like noise even when the
underlying trace is structured.

## Intended first implementation

Use one affidavit zkperf run as the first rendering target, but keep the two
surfaces explicit:

- execution-trace surface
  - emitted from measured execution mode by parsing staged progress / trace
    events from the SL command
  - this is the primary spectrogram surface because it carries stepwise
    variation
- SQLite/read-model surface
  - emitted from persisted contested-review state
  - useful for semantic summary and state comparison
  - not expected to show strong spectrogram dynamics by itself

Start with:

1. structured feature spectrogram
2. PCA spectrogram

Only after that add:

3. query-conditioned spectrogram

## Current constraint

The current repo has:

- runtime/process metrics
- payload/read-model structure
- affidavit semantic counters
- bounded semantic objective `semantic_gap_score`
- stream/publish/verify timings

It does not yet have the full theory-level:

- cone/contraction layer
- MDL trajectories
- eigen/resonance layer
- unified health readout

So the first spectrogram renderer must be honest about that narrower input
surface.

For the affidavit lane specifically:

- SQLite/read-model spectrograms are expected to look flat or nearly flat
  because they render final state, not execution progression
- meaningful harmonic / phase views require the measured execution trace
  surface, ideally from the shared CLI progress stream

## Acceptance target

The first rendering pass is acceptable when it:

- uses structured zkperf/SL inputs only
- clearly distinguishes feature-space from spectral-space views
- shows persistent bands versus collapse clearly on a real affidavit run
- does not imply theory-level diagnostics that are not implemented yet

## Operator wrapper followthrough

The renderer surfaces now need one operator-facing wrapper over the existing
primitives.

Required wrapper shape:

- one local entrypoint for:
  - SQLite/read-model affidavit runs
  - raw observation JSON
  - local zkperf stream fixtures
  - remote HF-resolved zkperf stream windows
- one consistent output bundle containing:
  - feature spectrogram PNG
  - PCA spectrogram PNG
  - metadata JSON for each render
  - intermediate observation / fixture only when explicitly requested

First-class supported input modes:

1. SQLite/read-model
   - input:
     - `db_path`
     - optional `review_run_id`
   - behavior:
     - derive one bounded observation
     - build a one-window fixture
     - render feature and PCA spectrograms

2. Observation JSON / NDJSON
   - input:
     - one observation object
     - or an observation list/NDJSON file
   - behavior:
     - build the fixture directly
     - render feature and PCA spectrograms

3. Local fixture
   - input:
     - one zkperf stream fixture JSON
   - behavior:
     - render directly with no rebuild

4. Remote HF stream resolution
   - input:
     - `index_hf_uri`
     - local `fixture_seed` path used as the stream manifest seed
     - optional window/range selection
   - behavior:
     - resolve remote windows from the HF index object
     - render feature and PCA spectrograms from the resolved fixture

Deferred mode:

- remote IPFS stream resolution
  - rationale:
    the repo already has generic IPFS transport primitives, but not yet a
    first-class zkperf stream resolver parallel to the HF index path

Boundary rule:

- the wrapper should not invent a new spectrogram logic layer
- it should only compose:
  - `sl_zkperf`
  - `zkperf_stream`
  - `zkperf_viz`
  - existing HF resolver surfaces
