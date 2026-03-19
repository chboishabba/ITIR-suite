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
- Observer-only SB seam:
  `../docs/planning/casey_git_clone_statiBaker_interface_20260309.md` at the
  suite root defines the minimal safe handoff into `StatiBaker`.
- Future read-only revision-monitor seam:
  `SensibLaw` revision-monitor run, pair, and contested-region graph artifacts
  may be referenced for orchestration or build provenance, but Casey does not
  own pair scoring, article state, graph production, or revision selection.
- Downstream consumers:
  reproducible build/test tools that consume immutable `BuildView` snapshots.

## 2. Interaction Model
1. Publish path edits into `Blob` + `FileVersion`.
2. Merge into `PathState.candidates` in current `TreeState`; divergence is valid
   state, not an error.
3. Sync workspace selection map against latest tree; the workspace remains an
   explicit choice over candidates rather than a hidden checkout.
4. Collapse conflict by selecting or synthesizing a resolved candidate; this is
   the governance step, not an automatic side effect of publish/sync.
5. Freeze `WorkspaceView` into immutable `BuildView`.

## 3. Exchange Channels

### Channel A: Publish Ingress
- Transport: CLI request payload for the local testbed, with in-process Python
  objects remaining the library boundary.
- Required fields: `path`, `content`, `author`, `source_ref` (or equivalent
  provenance).
- Output side effect: new `Blob` and `FileVersion` ids plus updated `TreeState`.

### Channel B: Sync Command
- Transport: CLI command payload (`workspace_id`, optional policy flags).
- Behavior: preserve valid selections, re-select only invalidated paths.
- Output: updated `WorkspaceView` plus per-path sync status.

### Channel C: Conflict Collapse Command
- Transport: CLI command payload (`workspace_id`, `path`, `candidate_id` or
  merged content).
- Behavior: create new resolved `FileVersion`, replace candidate set with
  singleton, and make the governance/collapse decision explicit in the record.
- Output: updated `TreeState` and collapse provenance record.

### Channel D: Build Snapshot Egress
- Transport: CLI-triggered structured build-view manifest (JSON-serializable).
- Required contents: immutable path->candidate map and source commit/tree id.
- Purpose: deterministic replay/debug and integration-test pinning.

### Channel E: Cross-Project Facts Export (Fuzzymodo Hook)
- Transport: JSON bundle (`casey.facts.v1`).
- Fields: tree id, workspace policy/selection, per-path candidate sets,
  candidate provenance metadata, optional build context.
- Consumer: Fuzzymodo selector evaluator over structural/execution/build facts.

### Channel E2: Advisory Return (Fuzzymodo -> Casey)
- Transport: structured JSON bundle (`fuzzymodo.casey.advisory.v1`).
- Behavior: advisory ranking and gap reporting only.
- Current v1 surface: Casey CLI can render the advisory via `advise`; it does
  not grant fuzzymodo collapse authority.

### Channel F: Observer Handoff to `StatiBaker`
- Transport: DB-backed observer rows or reference-heavy overlay rows only.
- Contract:
  - suite-level seam note:
    `docs/planning/casey_git_clone_statiBaker_interface_20260309.md`
- Allowed role:
  - emit append-only operation/build receipts and refs into Casey-owned ledgers
  - emit Casey observer bundles for replay/debug
  - optionally ingest the resulting `casey_workspace_v1` overlay into
    SB-owned observer tables
  - summarize workspace context through bounded workspace refs rather than full
    mutable selection state
- Forbidden role:
  - transfer mutable candidate graphs or collapse authority into SB canonical
    state
