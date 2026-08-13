# NotebookLM Metadata Review Parity v1

Date: 2026-03-11
Status: implementing first functional standardization slice

## Intent

Bring NotebookLM up to the same functional standard as the stronger suite
pipelines without pretending the current capture is rich enough for full
activity accounting.

Chosen posture:
- keep NotebookLM metadata-first for now
- improve producer/query/read-model quality first
- reuse NotebookLM as a source/review lane before upgrading it into a true
  waterfall/timeline activity lane

## Current repo reality

Current NotebookLM capture is bounded and honest:
- `StatiBaker/scripts/capture_notebooklm_meta.py` snapshots notebook/source/
  artifact/context state
- `StatiBaker/adapters/notebooklm_meta.py` normalizes that into `notes_meta`
  rows with `app: notebooklm`
- the SB reducer counts NotebookLM lifecycle/hour bins and folds them into a
  synthetic `tool_use_summary` family
- `itir-svelte` can render NotebookLM meta threads and source indexes in the
  normal thread viewer

What it does **not** capture:
- per-ask chat interactions
- note edits as first-class activity
- artifact-generation request/result flows
- notebook navigation/session continuity

That means the current lane is sufficient for:
- lifecycle review
- source/artifact inspection
- source-local text reuse
- privacy-preserving broad-theme review from notebook summaries or asks when
  local docs are not enough

It is **not** yet sufficient for:
- honest waterfall/timeline activity parity
- duration/session accounting
- mission actual-side attribution as a first-class work stream

## First milestone

Implement NotebookLM metadata/review parity as a neutral reporting seam.

Deliverables:
- a producer-owned NotebookLM observer read model in `SensibLaw`
- query helpers and a bounded JSON CLI over existing `runs/<date>/logs/notes`
- source-unit projection from NotebookLM source summaries/snippets for reuse in
  structure/semantic/narrative lanes

Non-goals for this slice:
- GUI-first workbench expansion
- new waterfall/timeline accounting
- redefining `notes_meta` as activity
- silent mission or semantic promotion from NotebookLM metadata

## Functional standard for this lane

NotebookLM should converge on the same cross-pipeline standard as OpenRecall
and the stronger semantic/report lanes:
- explicit source ownership
- deterministic read models
- bounded query/report entrypoints
- source-local text-unit reuse
- explicit observer/authority boundary

## Planned interfaces

### Observer report

NotebookLM should expose a bounded report/query surface with:
- date coverage
- notebook summaries
- source summaries
- artifact summaries
- event counts by kind
- bounded recent-event rows
- provenance-rich source snippets/keywords
- privacy-preserving thematic answers derived from notebook asks/history when:
  - the operator asks broad workflow/product questions
  - local docs are shallow or fragmented
  - no private facts need to be exported into repo records

### Source-unit projection

NotebookLM source summaries/snippets should be projectable into `TextUnit`s so
downstream structure and semantic lanes can consume them without learning
NotebookLM-specific parsing.

## Deferred

The later capture/activity upgrade remains separate.

That later slice should define explicit interaction-grade NotebookLM events
before any attempt to:
- sessionize NotebookLM usage
- place it into waterfall/timeline accounting as a peer of chat/shell
- treat it as a stronger mission-lens actual lane

Until then, NotebookLM remains:
- metadata observer
- source/review substrate
- source-local text provider
- optional privacy-preserving synthesis aid for broad product questions, not a
  truth-promotion lane
