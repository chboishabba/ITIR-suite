# zkperf PR1 Payload To Upstream

Date: 2026-03-31

## Goal

Freeze the concrete PR1 payload for `meta-introspector/zkperf` now that:

- the stream layer is physically split
- the package entrypoints are narrowed
- the local SL lane emits a generic register/flow surface
- a real HF-published rerun proved the new surface is present end to end

This note is the handoff contract for the upstream sync step.

## Current Proof Point

The local rerun published:

- stream id:
  - `zkperf-stream-wave1-real-au-regflow-20260331`
- stream revision:
  - `rev-20260319T142644Z`

Artifacts:

- `/tmp/zkperf-wave1-real-au-regflow-20260331/generated-zkperf-observation.json`
- `/tmp/zkperf-wave1-real-au-regflow-20260331/publish.json`
- `/tmp/zkperf-wave1-real-au-regflow-20260331/verify.json`
- `/tmp/zkperf-wave1-real-au-regflow-20260331/render-from-hf-regflow/summary.json`

The HF-resolved render now proves:

- `reg.AX.value`
- `reg.BX.value`
- `flow.transition.SL_ACCEPTANCE__SL_WORKBENCH`
- `flow.transition.AU_SEMANTIC`
- `flow.tag.AU_SEMANTIC`
- `flow.tag.REVIEW_QUEUE`
- `flow.tag.LEGAL_PROCEDURAL`
- `flow.region.SL_WORKBENCH`

That is enough evidence to treat the generic stream and vis lane as upstreamable.

## Upstream Reality Check

`../zkperf` currently does not have a Python package surface.

Observed state:

- standalone Python scripts already exist:
  - `scripts/compact-sample-trace.py`
  - `scripts/test-compact-sample-trace.py`
- no `pyproject.toml`
- no Python package directory
- no existing stream / fixture / vis module namespace

That means PR1 must either:

1. introduce a minimal Python package lane in `zkperf`
2. or flatten the code into standalone scripts, which is the worse option

Decision:

- introduce a small package lane for the generic stream and vis contract

## Proposed Destination Layout

Recommended upstream destination:

- `python/zkperf_stream/__init__.py`
- `python/zkperf_stream/core.py`
- `python/zkperf_stream/index.py`
- `python/zkperf_stream/transport.py`
- `python/zkperf_stream/viz.py`
- `python/tests/test_zkperf_stream.py`
- `python/tests/test_zkperf_viz.py`
- `docs/ZKPERF_STREAM_V1.md`

This keeps the Python lane explicit and bounded instead of smearing the
contract across `scripts/`.

## PR1 File Mapping

### Code

- source:
  - `itir_jmd_bridge/zkperf_stream_core.py`
  - destination:
    - `python/zkperf_stream/core.py`

- source:
  - `itir_jmd_bridge/zkperf_stream_index.py`
  - destination:
    - `python/zkperf_stream/index.py`

- source:
  - `itir_jmd_bridge/zkperf_stream_transport.py`
  - destination:
    - `python/zkperf_stream/transport.py`

- source:
  - `itir_jmd_bridge/zkperf_viz.py`
  - destination:
    - `python/zkperf_stream/viz.py`

### Package Surface

- source:
  - package exports derived from `itir_jmd_bridge/__init__.py`
  - destination:
    - `python/zkperf_stream/__init__.py`

Only expose the generic stream and visualization symbols there.

### Tests

- source:
  - `tests/test_zkperf_stream.py`
  - destination:
    - `python/tests/test_zkperf_stream.py`

- source:
  - `tests/test_zkperf_viz.py`
  - destination:
    - `python/tests/test_zkperf_viz.py`

Do not upstream:

- `tests/test_sl_zkperf.py`
- `tests/test_render_sl_zkperf_spectrogram.py`
- `tests/test_inspect_zkperf_clusters.py`

Those either depend on ITIR-local wrappers or operator drilldown surfaces.

### Docs

- source material:
  - `docs/planning/zkperf_stream_shard_contract_v1_20260330.md`
  - `docs/planning/zkperf_spectrogram_rendering_contract_20260330.md`
  - this note
  - destination:
    - `docs/ZKPERF_STREAM_V1.md`

That upstream doc should be concise:

- fixture contract
- index/latest contract
- register/flow observation expectations
- publish/resolve surface

## Keep Out Of PR1

Do not upstream in the first PR:

- `itir_jmd_bridge/sl_zkperf.py`
- `scripts/build_zkperf_observation_from_sl.py`
- `scripts/run_sl_with_zkperf.py`
- `scripts/render_sl_zkperf_spectrogram.py`
- `scripts/run_sl_zkperf_stream_hf.sh`
- any `SensibLaw` or `itir-svelte` fixtures
- any MCP or archive work

Those remain local adapters or operator wrappers.

## Open Decision

The only real remaining design choice is transport placement.

Two valid cuts:

- stricter PR1:
  - upstream `core.py`, `index.py`, `viz.py`
  - hold `transport.py` for PR2

- broader PR1:
  - upstream all four generic modules now
  - treat HF/IPFS as acceptable generic adapters

Current recommendation:

- start with the stricter PR1 cut
- keep `transport.py` ready but not required for first merge

Reason:

- `../zkperf` has no current Python package lane, so the first merge should
  establish the contract and tests with the smallest possible surface

## Draft PR Title

`Add zkperf stream fixture/index contract and register-aware visualization`

## Draft PR Body Skeleton

- introduces a small Python package lane for generic zkperf stream contracts
- adds:
  - fixture loading and observation grouping
  - bundle/index/latest construction
  - retention and window selection
  - register-aware and flow-aware visualization
- includes focused tests for:
  - stream fixture and index behavior
  - register and flow feature projection
- deliberately excludes:
  - SL and ITIR-specific producers
  - local operator wrappers
  - MCP integration

## Promotion Gate

Before copying into `../zkperf`:

1. pull latest `../zkperf`
2. create the bounded Python package lane there
3. transplant PR1 files only
4. run the focused upstream test slice
5. only then decide whether `transport.py` joins PR1 or remains PR2
