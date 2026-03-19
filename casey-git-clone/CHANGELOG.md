# Changelog

## 2026-03-19
- Refined `README.md` and `docs/interfaces.md` to state Casey's core posture
  more explicitly: per-path candidate lattice, workspace-as-selection,
  governance-explicit collapse, and immutable build projections.
- Added a minimal local CLI testbed backed by a Casey-owned SQLite runtime
  store, covering init, workspace creation, publish, sync, explicit collapse,
  tree/workspace inspection, and build snapshot flow.
- Added suite-level contract references for the next two Casey boundaries:
  read-only Casey -> fuzzymodo export/advisory flow and the sharpened
  Casey -> StatiBaker receipt/reference schema.
- Implemented the first Casey -> fuzzymodo boundary slice:
  `export_casey_facts(...)` now emits `casey.facts.v1`, and the CLI exposes it
  via `casey export --json`.
- Refined the Casey export payload so candidate rows now carry optional
  namespaced feature bags derived from Casey-known metadata, keeping the seam
  ready for future SL/LCE-derived signals without revising the base export
  version.
- Added export-focused tests covering deterministic Casey fact export and the
  Alice/Bob divergence case.
- Added Casey advisory rendering via `casey advise --json`, which evaluates the
  exported Casey facts through the fuzzymodo Casey adapter without transferring
  collapse authority.
- Upgraded the Casey advisory path so the returned
  `fuzzymodo.casey.advisory.v1` gap payload is explanation-first: path-local
  divergence summaries now include a primary axis, structured gap items, and
  suggested next actions instead of only candidate-count severity.
- Added first-class Casey receipt builders for the observer-only
  Casey -> StatiBaker seam, including workspace summary refs, operation
  receipts, build receipts, and overlay emission helpers backed by the Casey
  ledgers.
- Wired Casey `publish`, `sync`, `collapse`, and `build` commands to emit
  deterministic operation/build receipts automatically, write Casey observer
  bundles, and optionally ingest `casey_workspace_v1` overlays into
  StatiBaker dashboard DBs.
- Added end-to-end tests covering Casey bundle emission, Casey ledger
  persistence, and optional SB overlay ingestion from the Casey CLI/runtime
  lane.
- Added a Casey-vs-git benchmark harness at
  `scripts/benchmark_casey_vs_git.py` with fixed `small`/`medium`/`large`
  tiers, `baseline_linear` / `divergence_native` / `build_freeze` /
  `traceability_cost` lanes, and both `cli` and `library` Casey surfaces.
- Added storage-accounting metrics to the benchmark output, including runtime
  DB deltas, ledger DB deltas, observer bundle sizes, git `.git` size deltas,
  trace bundle sizes, sqlite page metrics, and persisted-bytes/logical-bytes
  ratios.
- Added a benchmark smoke test at
  `tests/test_benchmark_casey_vs_git_smoke.py` and documented the benchmark
  surface in `docs/benchmarking.md`.
- Added `--no-observer` to Casey `publish`, `sync`, `collapse`, and `build` so
  the benchmark and local operators can separate core CLI/runtime cost from
  observer receipt and bundle overhead.

## 2026-03-09
- Clarified the intended `casey-git-clone -> StatiBaker` seam as observer-only
  and DB-backed via suite planning note
  `docs/planning/casey_git_clone_statiBaker_interface_20260309.md`.
- Updated `docs/interfaces.md` and `README.md` so Casey workspace/candidate/
  build authority stays local while SB is limited to receipt/build refs and
  observer overlays.

## 2026-02-07
- Expanded core model layer with deterministic hashing helpers and full object
  set: `Blob`, `FileVersion`, `PathState`, `TreeState`, `Commit`,
  `WorkspacePolicy`, `WorkspaceView`, and immutable `BuildView`.
- Implemented non-blocking superposition workflows in
  `src/casey_git_clone/operations.py`: publish, sync, collapse conflict, and
  build snapshot.
- Added model and operations tests (`tests/test_models.py`,
  `tests/test_operations.py`) covering candidate invariants and state
  transitions.
