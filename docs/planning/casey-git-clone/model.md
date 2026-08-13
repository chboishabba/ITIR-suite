# Casey Git Clone: Core Model

## Objects
- `Blob`: content-addressed bytes.
- `FileVersion`: references blob + provenance.
- `PathState`: set of candidate `FileVersion` ids for a path.
- `TreeState`: mapping path -> `PathState`.
- `Commit`: named durable `TreeState` with parents.
- `WorkspaceView`: path -> active candidate selection.
- `BuildView`: frozen selection snapshot for reproducible builds.

## MVP Invariants
- `PathState.candidates` is non-empty and deduplicated.
- `WorkspaceView.selection[path]` must exist in current `PathState.candidates`.
- `BuildView` is immutable once created.
- Conflict collapse creates a new `FileVersion` and reduces candidate set to one.
