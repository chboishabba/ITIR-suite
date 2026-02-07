# Casey Git Clone Interface Contract (Intended)

## 1. Intersections
- Planning source of truth:
  `docs/planning/casey-git-clone/model.md` and
  `docs/planning/casey-git-clone/workflow.md`.
- Upstream producers:
  edit/provenance inputs from local workspace tooling.
- Cross-project consumer:
  `fuzzymodo/` (future adapter) for selector-based filtering over candidate
  file-version state.
- Downstream consumers:
  reproducible build/test tools that consume immutable `BuildView` snapshots.

## 2. Interaction Model
1. Publish path edits into `Blob` + `FileVersion`.
2. Merge into `PathState.candidates` in current `TreeState`.
3. Sync workspace selection map against latest tree.
4. Collapse conflict by selecting or synthesizing a resolved candidate.
5. Freeze `WorkspaceView` into immutable `BuildView`.

## 3. Exchange Channels

### Channel A: Publish Ingress
- Transport: API/CLI request payload (initially in-process Python objects).
- Required fields: `path`, `content`, `author`, `source_ref` (or equivalent
  provenance).
- Output side effect: new `Blob` and `FileVersion` ids plus updated `TreeState`.

### Channel B: Sync Command
- Transport: command payload (`workspace_id`, optional policy flags).
- Behavior: preserve valid selections, re-select only invalidated paths.
- Output: updated `WorkspaceView` plus per-path sync status.

### Channel C: Conflict Collapse Command
- Transport: command payload (`workspace_id`, `path`, `candidate_id` or merged
  content).
- Behavior: create new resolved `FileVersion`, replace candidate set with
  singleton.
- Output: updated `TreeState` and collapse provenance record.

### Channel D: Build Snapshot Egress
- Transport: structured build-view manifest (JSON-serializable).
- Required contents: immutable path->candidate map and source commit/tree id.
- Purpose: deterministic replay/debug and integration-test pinning.

### Channel E: Cross-Project Facts Export (Fuzzymodo Hook)
- Transport: JSON bundle (future adapter).
- Suggested fields: path, candidate ids, provenance metadata, change lineage.
- Consumer: Fuzzymodo selector evaluator over structural/execution/build facts.
