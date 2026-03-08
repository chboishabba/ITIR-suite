# Changelog

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
