# ZKPerf on SL Roadmap (2026-03-29)

## Goal

Pin the intended roadmap for bringing `zkperf` onto `SL` before proceeding with
the next implementation-facing shard/container work.

This note is a staging/gating note, not a claim that the integration is already
implemented.

## Why this comes first

Current planning already says:

- `SL` remains the structured truth / promotion authority
- `erdfa`/Kant-style layers package logical artifacts
- `Zelph` consumes/querys those artifacts
- `zkperf` is part of the proof-first execution/receipt framing

If `zkperf` is going to matter in the stack, the cleanest place to pin it next
is on the `SL` side as structured, receipt-bearing execution/proof material.

That should happen before deeper work on:

1. HF container/index fixture/spec details
2. richer `erdfa-publish-rs` manifest promotion
3. rehearsal harnesses that assume the `zkperf` role is already clear

## Intended role of zkperf on SL

`zkperf` should be treated as:

- execution/proof/trace material
- structured receipt-bearing evidence
- input to ranking/optimization layers only after it has a disciplined SL-side
  representation

It should **not** be treated as:

- a replacement for SL truth promotion
- free-floating embedding material
- a reason to bypass the existing shard/artifact contract

## Minimal roadmap

### Phase 1 — bounded SL-side representation

Define the smallest useful SL-facing representation for `zkperf`:

- trace identity
- source/run provenance
- structured metrics/events
- explicit links to related facts/artifacts when present
- receipt/proof refs

Acceptance target:

- one bounded contract note plus one tiny fixture/example

### Phase 2 — proof/receipt discipline

Make the proof/receipt role explicit:

- what counts as a `zkperf` receipt
- what stays observational vs promotable
- how SL references it without confusing it for truth itself

Acceptance target:

- one explicit boundary note:
  `zkperf` receipts inform/justify/trace, but do not directly promote truth

### Phase 3 — artifact linkage

Define how `zkperf` links to the existing artifact/shard stack:

- `artifactId` / `artifactRevision` linkage
- shard-level or run-level refs where appropriate
- no sink-path semantics leakage

Acceptance target:

- one simple linkage shape that can be attached to the current logical artifact
  contract without redesigning it

### Phase 4 — only then proceed to 1/2/3

After the above is pinned, proceed in the implementation-facing order already
discussed:

1. tiny HF container/index fixture/spec
2. `erdfa-publish-rs` richer manifest promotion path
3. small rehearsal harness in ITIR

## Guardrails

- keep `zkperf` features structured and receipt-bearing
- keep `zkperf` downstream of SL representation discipline before using it in
  spectral ranking
- do not let `zkperf` turn into an excuse for raw-vector retrieval
- do not let `zkperf` redefine the logical shard contract

## Followthrough

That first gate is now complete:

- contract:
  `docs/planning/zkperf_on_sl_contract_v1_20260329.md`
- fixture:
  `docs/planning/jmd_fixtures/zkperf_on_sl_observation_v1.example.json`

The next bounded layer on top is now:

- `docs/planning/zkperf_stream_shard_contract_v1_20260330.md`

which carries observational `zkperf` windows into a stream/container/HF
publication path without changing `SL` truth authority.

The next bounded followthrough is now complete too:

- `scripts/run_sl_with_zkperf.py`
  - executes a real SL-producing command
  - captures bounded runtime metrics:
    `elapsed_ms`, `exit_code`, child CPU, max RSS, stdout bytes, stderr bytes
  - emits one observational `ZKPerfObservation`
- `scripts/run_sl_zkperf_stream_hf.sh`
  - now supports two modes:
    - existing payload mode via `--sl-input`
    - measured execution mode via `--sl-output ... -- COMMAND`
  - measured execution mode derives the observation, streams it, publishes it
    to HF, updates the per-stream index, and verifies from that index

This means `SL -> zkperf -> stream -> HF` is no longer only an artifact-wrapper
story. It now has a real execution boundary for bounded runtime metrics, while
still remaining observational rather than truth-promotive.

## Next roadmap split

The next work should not blur the already-implemented operational lane with the
full theoretical `zkperf` surface.

### Operational lane already implemented

- runtime / process metrics
- measured execution-trace metrics from progress events
- payload / read-model structure metrics
- affidavit semantic counters
- bounded semantic objective:
  - `semantic_gap_score`
- stream / publish / verify timings
- HF/IPFS receipt-bearing publication

### Theory-facing layers still to implement

1. dynamics
   - cone / contraction / monotonicity checks
   - phase-transition / flip diagnostics
2. optimization
   - MDL descent traces
   - diminishing-return / Lyapunov-style summaries
   - in parallel, a bounded empirical bridge may add function-relative MDL
     surrogates (`local_function_mdl_v1`) for within-function anomaly and
     regression tracking without overclaiming universal MDL
3. geometry / alignment
   - resonance / overlap
   - eigen / basin / collapse diagnostics
4. synthesis
   - one compact health readout over the implemented layers

The correct next design step is therefore:

- define a formal `zkperf` layer contract that marks:
  - implemented now
  - partially implemented
  - not yet implemented

before adding new deeper metrics.

That contract is now explicit at the documentation level:

- `STRUCTURE` / `SEMANTICS`
  - implemented
- `DYNAMICS` / `GEOMETRY` / `ALIGNMENT`
  - scaffolded only
- `MDL`
  - unavailable

Bounded bridge rule:

- before native theory execution exists in the wrapper, allow already-produced
  `../dashi_agda` JSON evidence to be attached to zkperf observations
- this can move:
  - `MDL` from `unavailable` to `implemented`
  - `DYNAMICS` from `scaffolded` to `implemented`
  only when concrete witness metrics are actually present

So the next theory-facing implementation step is narrower than "do zkperf
theory":

- add one measured layer at a time
- move it from `scaffolded` or `unavailable` to `implemented`
- only then widen any health-readout surface

## Immediate next bounded followthrough

Before deeper cone / MDL / resonance work, finish the execution-trace
followthrough:

- keep deriving stepwise observations from measured execution progress events
- make the execution-trace surface the default spectrogram input for dynamic
  views
- keep SQLite/read-model profiling as the semantic-state comparison surface,
  not the primary harmonic / phase surface

This keeps the operational lane honest: dynamics come from process progression,
while semantic closure comes from the persisted read model.
