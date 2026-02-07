# Casey Git Clone

Standalone superposition-style versioning prototype.

## Purpose
Prototype coexistence-first conflict handling where divergent file edits can
persist as candidates until explicitly collapsed.

## Layout
- `src/casey_git_clone/`: core model and operation primitives.
- `tests/`: model and operation tests.
- `docs/interfaces.md`: intended intersections, interaction flow, and exchange
  channels.

## Intended Intersections
- Model and workflow are defined in `docs/planning/casey-git-clone/`.
- `fuzzymodo/` can consume workspace/tree candidate facts for selector-based
  filtering and replay checks.
- ITIR suite orchestration can consume build snapshots as reproducible analysis
  inputs.

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

## Planning Docs
See `docs/planning/casey-git-clone/`.
