# Casey Git Clone: Workflow

## 1. Publish (`done`)
- Collect file edits into blobs and file versions.
- Merge into tree state by appending candidates when divergence exists.
- Persist commit/tree state.

## 2. Sync
- Advance workspace base to latest tree/commit.
- Preserve local selection when still valid.
- Re-select with policy only when chosen candidate disappeared.

## 3. Collapse Conflict
- Choose candidate or merged content.
- Create a new file version.
- Replace candidate set with singleton resolved id.

## 4. Build Snapshot
- Freeze workspace selections into a `BuildView`.
- Record exact selection map for replay/debug.
