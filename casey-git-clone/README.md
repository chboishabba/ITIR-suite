# Casey Git Clone

Standalone superposition-style versioning prototype.

## Purpose
Prototype coexistence-first conflict handling where divergent file edits can
persist as candidates until explicitly collapsed.

## Core Model
- Per-path candidate lattice, not a single mutable file state.
- Workspace view as explicit selection over candidates, not a fixed checkout.
- Conflict collapse as a deliberate governance action, not an implicit merge.
- Immutable build snapshots as deterministic projections of a chosen view.

## Local Testbed
- Casey now includes a minimal CLI-backed local testbed with a Casey-owned
  SQLite runtime store.
- Runtime state is separate from the observer ledgers: the runtime persists
  mutable tree/workspace/build state for local exercises, while ledger tables
  remain reference-only surfaces for downstream observers.
- Operational commands now emit Casey observer receipts automatically, write a
  small Casey observer bundle for replay/debug, and may ingest the resulting
  `casey_workspace_v1` overlay into a StatiBaker dashboard DB when `--sb-db` is
  supplied.
- For raw operational measurement or lightweight local use, `publish`, `sync`,
  `collapse`, and `build` also accept `--no-observer` to skip receipt/bundle
  emission on that command.
- Intended v1 walkthrough:
  - initialize runtime
  - create a second workspace
  - publish conflicting edits from stale/synced views
  - inspect tree/workspace state
  - collapse explicitly
  - freeze a build snapshot

Example:

```bash
python -m casey_git_clone init --db /tmp/casey.sqlite --workspace alice
python -m casey_git_clone workspace create --db /tmp/casey.sqlite --workspace bob
python -m casey_git_clone publish --db /tmp/casey.sqlite --workspace alice --path src/main.c --content "base"
python -m casey_git_clone sync --db /tmp/casey.sqlite --workspace bob
python -m casey_git_clone publish --db /tmp/casey.sqlite --workspace alice --path src/main.c --content "alice edit"
python -m casey_git_clone publish --db /tmp/casey.sqlite --workspace bob --path src/main.c --content "bob edit"
python -m casey_git_clone show tree --db /tmp/casey.sqlite
python -m casey_git_clone export --db /tmp/casey.sqlite --workspace alice --json
python -m casey_git_clone advise --db /tmp/casey.sqlite --workspace alice --json
python -m casey_git_clone publish --db /tmp/casey.sqlite --workspace alice --path src/main.c --content "next" --sb-db /tmp/sb.sqlite --json
```

## Layout
- `src/casey_git_clone/`: core model and operation primitives.
- `scripts/`: operator-facing utilities, including the Casey-vs-git benchmark.
- `tests/`: model and operation tests.
- `docs/interfaces.md`: intended intersections, interaction flow, and exchange
  channels.
- `docs/benchmarking.md`: benchmark lanes, metrics, and interpretation rules.

## Intended Intersections
- Model and workflow are defined in `docs/planning/casey-git-clone/`.
- `fuzzymodo/` can consume workspace/tree candidate facts for selector-based
  filtering and replay checks.
- ITIR suite orchestration can consume build snapshots as reproducible analysis
  inputs.
- The current `casey-git-clone -> StatiBaker` seam is observer-only and
  DB-backed, documented in
  `../docs/planning/casey_git_clone_statiBaker_interface_20260309.md`.
- The current `casey-git-clone -> fuzzymodo` seam is read-only and advisory,
  documented in
  `../docs/planning/casey_fuzzymodo_interface_contract_20260319.md`.
- The sharpened Casey observer receipt semantics for `StatiBaker` are
  documented in
  `../docs/planning/casey_statiBaker_receipt_schema_20260319.md`.

## Interaction Flow
1. Publish edits into `Blob` and `FileVersion` objects.
2. Merge per-path state into candidate sets in `TreeState`.
3. Sync workspace selections against latest tree state.
4. Collapse conflicts into resolved singleton candidates when requested.
5. Freeze selected candidates into immutable build snapshots.

## Exchange Channels
- Input channel: publish requests (path, content, provenance metadata).
- Input channel: sync/collapse commands (workspace id, path, selected candidate
  id).
- Output channel: tree/workspace state snapshots for UI or CLI tooling.
- Output channel: build-view manifest for deterministic replay/debug.
- Output channel: `casey.facts.v1` read-only export for Casey -> fuzzymodo
  advisory evaluation, including optional namespaced candidate feature bags.
- Output channel: `fuzzymodo.casey.advisory.v1` rendered back through Casey
  CLI without granting collapse authority to fuzzymodo; current path-level gaps
  are explanation-first divergence summaries rather than candidate-count-only
  severity stubs.
- Output channel: Casey observer bundles plus optional direct SB ingest for
  `casey_workspace_v1` overlays, backed by Casey-owned ledgers and bounded
  workspace/operation/build refs only.

## Planning Docs
See `docs/planning/casey-git-clone/`.
