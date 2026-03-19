# Casey Benchmarking

## Purpose
Benchmark Casey against local git on workloads Casey is actually designed to
care about:

- preserving divergence without branch juggling
- explicit multi-candidate state
- workspace selection over conflicting candidates
- frozen build projections
- integrated observer/receipt traceability

This benchmark surface is not meant to claim Casey beats git at every linear
version-control task. It is meant to make Casey-vs-git comparisons explicit,
reproducible, and storage-aware on Casey-native workflows.

## Benchmark Surface
- script:
  `scripts/benchmark_casey_vs_git.py`
- smoke test:
  `tests/test_benchmark_casey_vs_git_smoke.py`

The script reports:
- JSON on stdout
- a Markdown summary table on stderr

For the Casey CLI lane, the harness uses `--no-observer` in
`baseline_linear`, `divergence_native`, and `build_freeze` so those lanes
measure core CLI/runtime cost rather than bundled observer overhead.
`traceability_cost` leaves observer emission enabled.

## Fixed v1 matrix
### Tiers
- `small`
- `medium`
- `large`

### Lanes
- `baseline_linear`
- `divergence_native`
- `build_freeze`
- `traceability_cost`

### Surfaces
- `cli`
- `library`

## Metrics
The harness records both timing and storage-accounting metrics, including:

- elapsed wall-clock time
- logical content bytes touched
- working-tree payload bytes
- Casey runtime DB bytes and deltas
- Casey ledger DB bytes and deltas
- Casey observer bundle bytes and per-file sizes
- sqlite page count and page size
- Casey ledger/runtime row counts
- git `.git` bytes and deltas
- git object counts where available
- command counts
- amplification ratios:
  - persisted bytes / logical content bytes
  - metadata bytes / logical content bytes

## Interpretation
- `baseline_linear` is the honesty lane and may still favor git.
- `divergence_native` is the main Casey-native lane.
- `traceability_cost` is where Casey may win on integrated auditability.
- Raw byte size alone is not the only criterion; the benchmark should be read
  as bytes-per-capability and time-per-capability.
- Current working interpretation of the measured results:
  - Casey `library` is close to the "competing with git if git were in Python"
    regime, because Casey library medians are already beating subprocess-driven
    git timings in several lanes.
  - Casey `cli` is not in that regime yet; it still pays substantial Python
    process startup and command-path overhead even after `--no-observer`,
    lazy-import, and command-scoped runtime batching improvements.
  - So benchmark claims should currently distinguish:
    - Casey library vs subprocess git: competitive to favorable in Casey-native
      lanes
    - Casey CLI vs git CLI: still materially behind overall

## Current State
- After the `--no-observer` split, lazy-export/import cleanup, and
  command-scoped runtime SQLite batching, Casey CLI improved materially but is
  still not broadly ahead of git CLI.
- The latest stored comparison in this working session moved the overall result
  mix from `git_ahead=15 / mixed=7 / casey_ahead=2` to
  `git_ahead=12 / mixed=9 / casey_ahead=3`.
- The clearest improvement was Casey CLI on larger divergence-heavy workloads,
  but the remaining bottlenecks are now mostly:
  - Python process startup
  - remaining CLI command-path overhead
  - observer/receipt cost in `traceability_cost`
