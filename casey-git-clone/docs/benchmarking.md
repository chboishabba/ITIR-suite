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
