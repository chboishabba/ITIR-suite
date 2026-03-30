# Profile SL to HF

## Goal

Run a bounded `SL -> zkperf -> stream -> HF -> verify` cycle without having to
reconstruct the workflow from planning notes.

This is an operator runbook.

## What this does

The profiling lane records observational execution evidence for an `SL` payload
or an `SL`-producing command, then publishes that evidence to HF as a bounded
zkperf stream.

Current runtime metrics include:

- `elapsed_ms`
- `exit_code`
- `child_user_cpu_seconds`
- `child_system_cpu_seconds`
- `max_rss_kb`
- `stdout_bytes`
- `stderr_bytes`

This is not full GPU profiling.

Unless the invoked command itself exposes GPU metrics, the emitted observation
only captures bounded host-side execution facts plus payload structure and any
available semantic summary counts.

For the affidavit lane, the emitted observation now also includes:

- raw semantic counters
- one bounded heuristic objective:
  - `semantic_gap_score`

This score is a `semantic-v1` heuristic objective over the current affidavit
semantic state. It is useful for comparing runs, but it is not a truth
promotion rule or a full MDL/Lyapunov proof.

## Prerequisites

- repo root:
  `/home/c/Documents/code/ITIR-suite`
- Python environment exists:
  `.venv`
- HF credentials are already configured for write access
- the SL command either:
  - already produced a JSON payload, or
  - can be invoked so it writes one JSON payload to a known output path

## Three modes

### 1. Existing payload mode

Use this when the SL payload already exists on disk.

```bash
cd /home/c/Documents/code/ITIR-suite
scripts/run_sl_zkperf_stream_hf.sh \
  --sl-input /absolute/path/to/your/sl-payload.json \
  --retain-latest-n 2
```

### 2. Measured execution mode

Use this when you want the wrapper to execute the SL-producing command and
capture runtime metrics directly.

```bash
cd /home/c/Documents/code/ITIR-suite
scripts/run_sl_zkperf_stream_hf.sh \
  --sl-output /tmp/my-sl-output.json \
  --retain-latest-n 2 \
  -- python your_sl_script.py --output /tmp/my-sl-output.json
```

If the command also emits the shared `SensibLaw` progress stream, measured
execution mode now captures a second perf surface:

- a summary observation for the whole run
- stepwise trace observations derived from progress events

This is the preferred input for spectrogram rendering, because it carries real
execution progression instead of final-state counts only.

If you only need local SQLite/read-model spectrograms from one affidavit run,
use the dedicated wrapper rather than stitching the observation, fixture, and
render steps together manually:

- `scripts/render_sl_zkperf_spectrogram.py`

Supported wrapper modes:
- SQLite/read-model run:
  - `--db-path`
  - optional `--review-run-id`
- local observation JSON / NDJSON:
  - `--observations`
- local zkperf fixture:
  - `--fixture`
- remote HF-resolved stream windows:
  - `--index-hf-uri` plus a local `--fixture-seed`

Current transport note:
- HF is supported as a remote zkperf stream source
- IPFS remains a deferred zkperf-stream rendering mode; the repo already has
  IPFS fetch/publish primitives, but not yet the equivalent indexed zkperf
  stream resolution path

The rule is:

- `--sl-input`
  - payload already exists
- `--sl-db-path`
  - a persisted contested-review run already exists in SQLite and JSON is not
    the working surface
- `--sl-output ... -- COMMAND`
  - command creates the payload and the wrapper measures execution

### 3. Existing SQLite contested-review mode

Use this when the affidavit lane has already persisted a contested-review run
to SQLite and you want zkperf to profile the read-model surface directly.

```bash
cd /home/c/Documents/code/ITIR-suite
scripts/run_sl_zkperf_stream_hf.sh \
  --sl-db-path /tmp/dad_johl_zkperf_full/itir.sqlite \
  --stream-id zkperf-stream-dad-johl-affidavit-full \
  --retain-latest-n 3
```

If the SQLite file contains multiple contested-review runs, pin one explicitly:

```bash
cd /home/c/Documents/code/ITIR-suite
scripts/run_sl_zkperf_stream_hf.sh \
  --sl-db-path /tmp/dad_johl_zkperf_full/itir.sqlite \
  --sl-review-run-id contested_review:... \
  --stream-id zkperf-stream-dad-johl-affidavit-full \
  --retain-latest-n 3
```

## Real examples

### Existing bundle fixture

```bash
cd /home/c/Documents/code/ITIR-suite
scripts/run_sl_zkperf_stream_hf.sh \
  --sl-input /home/c/Documents/code/ITIR-suite/itir-svelte/tests/fixtures/fact_review_wave1_real_au_demo_bundle.json \
  --stream-id zkperf-stream-wave1-real-au \
  --retain-latest-n 2
```

### Measured smoke run

```bash
cd /home/c/Documents/code/ITIR-suite
scripts/run_sl_zkperf_stream_hf.sh \
  --sl-output /tmp/sl-runtime-smoke.json \
  --stream-id zkperf-stream-runtime-smoke \
  --retain-latest-n 2 \
  -- python -c "import json, pathlib; pathlib.Path('/tmp/sl-runtime-smoke.json').write_text(json.dumps({'run': {'semantic_run_id': 'run:runtime-smoke'}, 'summary': {'event_count': 3}}, sort_keys=True), encoding='utf-8')"
```

## What gets written locally

Default output root:

- `/tmp/sl-zkperf-stream-run`

Typical files:

- `generated-zkperf-observation.json`
- `generated-zkperf-trace-observations.json` when measured execution emits
  progress events
- `generated-zkperf-stream-observations.json` when measured execution combines
  trace observations with the final summary observation for stream publication
- `generated-zkperf-stream.json`
- `publish.json`
- `verify.json`
- `timings.json`

The published stream artifacts are also written under:

- `<output-root>/<stream-id>/<stream-revision>/`

Typical contents there:

- `stream-manifest.json`
- `stream-latest.json`
- `stream-index.json`
- `hf-receipt.json`
- `stream-index-receipt.json`

## How to read the result

### Observation

Look at:

- `generated-zkperf-observation.json`

This is the bounded observational object. It includes:

- `run_id`
- `trace_id`
- `metrics`
- `trace_refs`
- `proof_refs`
- `related_artifact_refs`

For measured execution runs with progress events, also look at:

- `generated-zkperf-trace-observations.json`

This is the stepwise execution-trace surface. It is the right source for:

- feature spectrograms
- PCA spectrograms
- later query-conditioned trace views

The SQLite/read-model mode remains useful for semantic-state comparison, but it
is not expected to show rich spectrogram dynamics on its own.

## Trace follow-up tools

Once a measured execution run has produced trace observations, use:

- `scripts/summarize_zkperf_trace.py`
  - prints a compact stage/section/status summary from
    `generated-zkperf-trace-observations.json`
- `scripts/render_sl_zkperf_spectrogram.py`
  - renders both feature and PCA spectrograms from:
    - an output root / local fixture
    - observation JSON
    - SQLite contested-review state
    - HF/IPFS-resolved index selections
- `scripts/compare_zkperf_runs.py`
  - compares two runs from either output roots or explicit observation files
  - reports bounded metric deltas such as:
    - `semantic_gap_score`
    - `elapsed_ms`
    - `max_rss_kb`
    - `payload_bytes`
- `scripts/inspect_zkperf_clusters.py`
  - reads cluster-aware spectrogram metadata and prints cluster membership /
    counts
  - also surfaces dominant stage/domain signals, window counts, and bounded
    retrieval candidates

The core visualization library now also includes a query-conditioned renderer:

- `itir_jmd_bridge.zkperf_viz.render_zkperf_query_spectrogram`

The operator wrapper can now expose that view too:

```bash
cd /home/c/Documents/code/ITIR-suite
scripts/render_sl_zkperf_spectrogram.py \
  --fixture /path/to/generated-zkperf-stream.json \
  --output-dir /tmp/zkperf-render \
  --query-metric summary.covered_count=1 \
  --query-metric summary.missing_review_count=-1
```

That writes:

- `zkperf-query-spectrogram.png`
- `zkperf-query-spectrogram.json`

The wrapper also supports bounded higher-level query presets:

```bash
cd /home/c/Documents/code/ITIR-suite
scripts/render_sl_zkperf_spectrogram.py \
  --fixture /path/to/generated-zkperf-stream.json \
  --output-dir /tmp/zkperf-render \
  --query-preset semantic-gap \
  --query-preset trace-motion
```

Current preset names:

- `semantic-gap`
- `coverage-focus`
- `conflict-pressure`
- `trace-motion`
- `runtime-cost`

These presets are still thin operator conveniences over the existing metric
alignment surface. They do not change the underlying query math.

The wrapper also supports higher-level query intents over those presets:

- `coverage-recovery`
- `conflict-audit`
- `trace-debug`

Print the live preset/intent catalog with:

```bash
cd /home/c/Documents/code/ITIR-suite
scripts/render_sl_zkperf_spectrogram.py --list-query-presets
```

For cluster-aware drilldown over a real rendered run, use either:

- `scripts/inspect_zkperf_clusters.py --input <path-to-feature-metadata.json> --fixture <path-to-zkperf-stream.json>`
- or generate the report directly from the wrapper:

```bash
cd /home/c/Documents/code/ITIR-suite
scripts/render_sl_zkperf_spectrogram.py \
  --fixture /path/to/generated-zkperf-stream.json \
  --output-dir /tmp/zkperf-render \
  --cluster-k 4 \
  --cluster-report \
  --cluster-top-metrics 8
```

That writes:

- `zkperf-cluster-report.json`
- `zkperf-selection-fixture.json` when query-aware selection is available

If you also provide query metrics, a query observation, or a query preset, the
cluster report now includes a bounded selection path:

- recommended cluster labels
- recommended row labels
- query-alignment ranking within the selected clusters
- a materialized subfixture of the recommended rows

Example:

```bash
cd /home/c/Documents/code/ITIR-suite
scripts/render_sl_zkperf_spectrogram.py \
  --fixture /path/to/generated-zkperf-stream.json \
  --output-dir /tmp/zkperf-render \
  --cluster-k 4 \
  --cluster-report \
  --query-preset semantic-gap
```

For direct CLI drilldown on an existing render, use:

```bash
cd /home/c/Documents/code/ITIR-suite
scripts/inspect_zkperf_clusters.py \
  --input /path/to/zkperf-feature-spectrogram.json \
  --fixture /path/to/generated-zkperf-stream.json \
  --query-metadata /path/to/zkperf-query-spectrogram.json \
  --select-top-clusters 1 \
  --select-top-rows 5 \
  --selection-fixture-output /tmp/zkperf-selection.json \
  --json
```

Measured execution traces now also carry coarse domain-role features such as
affidavit / coverage / matching families when those roles can be derived from
progress-stage content. This keeps the trace surface more useful for
spectrogram/debug work without claiming full theory-level semantics.

They now also carry coarse domain-signal flags such as:

- `review_gap`
- `coverage_recovered`
- `conflict_pressure`
- `persistence_boundary`
- `publish_boundary`

The compact trace summary now exposes an availability-aware health readout:

- `STRUCTURE = implemented`
- `SEMANTICS = implemented`
- `DYNAMICS = scaffolded|implemented`
- `MDL = unavailable|implemented`
- `GEOMETRY = scaffolded`
- `ALIGNMENT = scaffolded`

This remains a status/readout surface, not a claim that full cone, MDL, or
resonance machinery is already implemented.

If you already have bounded theory evidence from `../dashi_agda` or a direct `mdl-evidence-v1` JSON, you can
attach it during observation generation:

```bash
cd /home/c/Documents/code/ITIR-suite
scripts/run_sl_zkperf_stream_hf.sh \
  --sl-db-path /path/to/itir.sqlite \
  --theory-evidence-json ../dashi_agda/artifacts/regime_test/family_classification_latest.json \
  --theory-family z_pt_7tev_atlas \
  --output-root /tmp/zkperf-with-theory
```

Current evidence bridge supports already-materialized JSON such as:

- family classification lists
- family latest regime-test reports
- tail-boundary batch aggregates

That can make:

- `MDL = implemented`
- `DYNAMICS = implemented`

for the specific observation when concrete MDL / admissibility witness metrics
are present.

### Publish receipt

Look at:

- `publish.json`

Important fields:

- `timings`
  - stage timings for the wrapper and publish/verify boundaries
- `hfReceipt.acknowledgedRevision`
  - HF revision for the tar object
- `streamIndexReceipt.acknowledgedRevision`
  - HF revision for the index object
- `streamManifest.containerObjectRef.uri`
  - the HF object path used for the stream tar

### Verification

Look at:

- `verify.json`

Important fields:

- `timings`
  - verify-stage timings for the index read-back path
- `streamIndex.resolvedStreamRevision`
- `selection.selectedWindowIds`
- `windows[].payload.json.observations[]`

If verification succeeded, the wrapper has:

- resolved the active index
- fetched the tar by acknowledged revision
- extracted the selected window
- recovered the same observation payload

## Choosing identifiers

### `stream-id`

Use a stable name for one logical stream family.

Good examples:

- `zkperf-stream-wave1-real-au`
- `zkperf-stream-transcript-semantic-intake`
- `zkperf-stream-au-semantic-profile`

Avoid reusing a shared demo stream id unless you intentionally want to append to
that existing stream.

### `retain-latest-n`

Controls how many revisions the active index keeps.

- `2`
  - good default for smoke runs
- larger values
  - useful when you want a longer visible revision history in HF

Published tar objects remain immutable. Retention only changes the active index
surface.

## Troubleshooting

### `SL input file does not exist`

You used `--sl-input` with a bad path.

Fix:

- pass a real existing JSON file

### `Missing SL command after --`

You used `--sl-output` but did not provide the command to create the JSON.

Fix:

- add `-- your_command ...`

### `SL output file was not created`

The wrapped command ran, but it did not write the JSON where you told the
wrapper to expect it.

Fix:

- ensure the command writes exactly to the `--sl-output` path

### HF upload/auth failure

The wrapper reached publish time, but HF rejected the write.

Fix:

- verify HF auth is configured
- verify the target dataset path is writable
- note that the HF upload helper now retries one transient network/DNS failure
  automatically before failing hard

### Wrong stream resolves during verify

This usually means you reused an index/object path from a different stream.

Fix:

- choose a unique `--stream-id`, or
- explicitly set `--hf-uri` and `--index-hf-uri`

## Related files

- `scripts/run_sl_zkperf_stream_hf.sh`
- `scripts/run_sl_with_zkperf.py`
- `scripts/build_zkperf_observation_from_sl.py`
- `docs/planning/zkperf_on_sl_contract_v1_20260329.md`
- `docs/planning/zkperf_stream_shard_contract_v1_20260330.md`
