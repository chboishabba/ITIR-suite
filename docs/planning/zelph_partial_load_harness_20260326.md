# Zelph Partial-Load Harness (2026-03-26)

## ZKP Frame

O:
- Local actors: ITIR repo, patched `aur/zelph`, local `.bin` artifacts, harness runner.
- External actor: Stefan/upstream Zelph, who needs a concrete, repeatable acceptance loop.

R:
- We need a harness that separates:
  - selector correctness
  - manifest transport correctness
  - fallback safety
- The harness must tell us whether a run is:
  - direct success
  - fallback-mediated success
  - hard failure

C:
- Harness runner: `tools/run_zelph_partial_load_harness.py`
- Existing loader/index/manifest surfaces:
  - `aur/zelph/src/lib/command_executor.cpp`
  - `aur/zelph/src/lib/network/zelph_impl.hpp`
  - `tools/build_zelph_hf_manifest.py`

S:
- Current state:
  - direct `.bin` partial loads are viable
  - manifest loads can trigger Cap'n Proto decode failures on current shard artifacts
  - manifest path now degrades to sequential `.bin` loading instead of aborting
- Missing before this harness:
  - stable classification across artifacts/cases
  - one command that regenerates manifests and exercises the acceptance matrix

L:
- ad hoc repro
- scripted repro
- classified matrix
- stable non-fallback manifest transport

P:
- Use a bounded, fixed case matrix per artifact:
  - `.bin` meta-only
  - `.bin` left chunk probe
  - `v1` manifest meta-only
  - `v1` manifest left chunk probe
  - `v2` manifest meta-only
  - `v2` manifest left chunk probe
- Optional extension:
  - `nameOfNode=0`
  - `nodeOfName=0`
  - mixed section selectors such as `left=0` plus `nameOfNode=0`
- Emit JSON so later comparison is machine-readable.

G:
- Harness is good enough when:
  - it exits `0` only if every case is acceptable for its expected mode
  - fallback cases are explicitly identified, not silently treated as direct success
  - output can be attached to docs/issues/handoffs

F:
- Remaining gap after this harness:
  - fix extracted chunk/direct object readability so manifest probes stop requiring fallback

Synthesis:
- The harness is the required promotion loop for finishing the manifest loader implementation.

Adequacy:
- Adequate. It governs the next implementation move and gives us the missing evidence channel.

Next action:
- Run the harness on the smallest local bin first, then on the 2026 bin when needed.

## Harness contract

- Script:
  - `tools/run_zelph_partial_load_harness.py`
- Inputs:
  - one or more `--artifact /path/to/*.bin`
  - local Zelph binary
  - local manifest builder
- Generated intermediates per artifact:
  - `.index.json`
  - `hf-v1.json`
  - `hf-v2.json`
  - local shard tree for `v2`
- Output:
  - JSON summary of all cases with:
    - `ok`
    - `fallback_used`
    - `had_repl_error`
    - `fetch_plan`
    - wall-clock time
    - reported Zelph partial-load time
    - output excerpt

## Recommended runs

Smallest local artifact:

```bash
cd /home/c/Documents/code/ITIR-suite
python tools/run_zelph_partial_load_harness.py \
  --artifact /home/c/Documents/code/ITIR-suite/wikidata-20171227-pruned.bin
```

Extended coverage:

```bash
cd /home/c/Documents/code/ITIR-suite
python tools/run_zelph_partial_load_harness.py \
  --artifact /home/c/Documents/code/ITIR-suite/wikidata-20171227-pruned.bin \
  --artifact /home/c/Documents/code/ITIR-suite/wikidata-20260309-all-pruned.bin \
  --include-name-cases
```

## Acceptance meaning

- `ok` without fallback:
  - selector + transport path worked directly
- `ok` with fallback:
  - selector semantics still worked, but manifest chunk/object path is not yet promotable
- non-`ok`:
  - broken regression or uncaught loader failure

## First observed run

- Artifact:
  - `/home/c/Documents/code/ITIR-suite/wikidata-20171227-pruned.bin`
- Result:
  - `bin_meta_only`: direct success
  - `bin_left0`: direct success
  - `manifest_v1_meta_only`: direct success
  - `manifest_v1_left0`: fallback success
  - `manifest_v2_meta_only`: direct success
  - `manifest_v2_left0`: fallback success
- Summary JSON:
  - `/tmp/zelph-partial-load-harness/summary.json`

## Current observed run

- Artifacts:
  - `/home/c/Documents/code/ITIR-suite/wikidata-20171227-pruned.bin`
  - `/home/c/Documents/code/ITIR-suite/wikidata-20260309-all-pruned.bin`
- Extended matrix:
  - left adjacency probes
  - `nameOfNode=0` probes
  - `nodeOfName=0` probes
  - mixed `left=0` + `nameOfNode=0` probes
  - `v1` and `v2` manifest paths
- Result:
  - all tested cases are now direct successes
  - no fallback required in the current bounded matrix
  - summary entries now also emit the manifest-derived fetch plan:
    - `v1`: HTTP range reads against `artifact.bin`
    - `v2`: direct shard object paths under `shards/<section>/...`
- Root cause fixed:
  - sidecar offset accounting was previously distorted by buffered read-ahead in the indexers
