# Changelog

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
