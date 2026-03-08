# Semantic Review Feedback + SB Mission Bridge (2026-03-08)

## Purpose
Connect the semantic report workbench to two adjacent seams without widening
authority boundaries:

1. human review feedback from `itir-svelte` back into ITIR/SensibLaw as
   append-only correction submissions
2. ITIR-produced mission/follow-up observer artifacts that SB can ingest as
   read-only overlays

## Shipped v1

### Review feedback seam
- `/graphs/semantic-report` now supports append-only correction submission from
  the active semantic selection.
- Submissions are now persisted in `itir.sqlite` via governed review tables:
  - `semantic_review_submissions`
  - `semantic_review_evidence_refs`
- Each record includes:
  - source/run/event/relation/anchor refs
  - action kind
  - structured proposed payload
  - evidence refs from the current viewer selection
  - operator provenance
- The workbench also shows recent corrections for the active corpus/run.

### Viewer -> graph loop
- Event/source document viewers can now request selection back into the token
  arc inspector by clicking a line containing a highlighted anchor span.
- This keeps the semantic workbench selection model route-owned rather than
  making the viewers semantic authorities.

### Mission observer seam
- Transcript/freeform semantic reports now emit a bounded `mission_observer`
  artifact.
- That artifact is now persisted canonically in `itir.sqlite` first and then
  reloaded into reports from:
  - `mission_runs`
  - `mission_nodes`
  - `mission_edges`
  - `mission_evidence_refs`
  - `mission_observer_overlays`
  - `mission_overlay_refs`
- Current method stays deterministic and local:
  - explicit task/mission cue phrases
  - explicit follow-up phrasing
  - source-local backtracking to prior topic mentions
  - deadline cue carry-forward only when textually grounded
  - abstention on unresolved follow-up references
- Reports also emit `sb_observer_overlays`:
  - reference-heavy records
  - no thread dumps
  - no raw event/state injection
  - intended for loose SB import

## Boundary decisions
- Corrections persist first on the ITIR/SensibLaw side, not in SB.
- Mission/follow-up extraction is observer-class and candidate-heavy.
- SB consumes mission overlays as read-only/additive observer material.
- The bridge uses refs, spans, canonical ids, and compact labels; it does not
  turn SB into a second semantic authority.

## Immediate follow-up
- Pressure-test mission extraction against more chat/message corpora before
  widening cue coverage.
- Keep mission overlays reference-heavy; do not allow free-form thread payloads
  across the SB seam.
- Broader SL DB / ITIR DB / SB DB separation still needs an explicit
  architecture pass; this implementation only formalizes the current
  ITIR/SB storage seam rather than solving all future multi-DB boundaries.
