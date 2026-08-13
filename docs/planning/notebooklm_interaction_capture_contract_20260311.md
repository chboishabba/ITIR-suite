# NotebookLM Interaction Capture Contract v1

Date: 2026-03-11
Status: implemented bounded interaction capture after metadata/review parity

## Intent

Add a separate NotebookLM interaction lane without reinterpreting existing
`notes_meta` snapshots as activity sessions.

This slice is deliberately narrower than full activity-accounting parity.

Chosen posture:
- keep `notes_meta` as the lifecycle/source/artifact observer lane
- add a second, additive interaction lane for:
  - conversation history observations
  - note observations
- keep both lanes queryable and source-reusable
- do not claim waterfall/timeline parity yet

## Why a second lane is needed

Current NotebookLM metadata capture is honest but thin:
- notebook observed
- source observed
- artifact observed
- context observed

That is good enough for:
- lifecycle counters
- notebook/source/artifact review
- source-summary text reuse

It is not good enough for:
- question/answer interaction review
- note-level textual reuse
- later sessionization inputs

So the correct next move is not to stretch `notes_meta`. It is to add a
separate interaction contract.

## v1 contract

### Raw capture events

The raw capture script should emit additive records like:
- `conversation_observed`
- `note_observed`

Required fields by family:

`conversation_observed`
- `ts`
- `collected_at`
- `event_type`
- `notebook_id`
- `notebook_title`
- `conversation_id`
- `query_preview`
- `answer_preview`
- optional `conversation_turn_ts`

`note_observed`
- `ts`
- `collected_at`
- `event_type`
- `notebook_id`
- `notebook_title`
- `note_id`
- `note_title`
- `note_preview`
- optional `note_length`

### Normalized interaction signal

Normalized rows should use a separate signal:
- `signal: notebooklm_activity`
- `app: notebooklm`

This avoids conflating:
- lifecycle/source metadata
- interaction-bearing observations

Normalized rows should preserve:
- hashed notebook/note/conversation IDs
- bounded previews only
- provenance (`source`, `collected_at`)

They should not preserve:
- full notebook/source bodies by default
- unbounded answer/note payloads
- inferred duration/session claims

## Initial consumers

This slice is intended to support:
- query/read-model parity
- source-local text reuse
- future mission-lens evidence reuse
- later sessionization design work
- privacy-preserving review of prior NotebookLM conversations for product
  improvement themes, when retained only as sanitized workflow findings

It is not intended to support, yet:
- SB waterfall/timeline integration
- duration accounting
- mission actual-side automatic work attribution

## Shipped artifacts

### Raw outputs

Under `runs/<date>/outputs/notebooklm/`:
- `notebooklm_activity_raw.jsonl`
- `notebooklm_activity_normalized.jsonl`

### Query/read-model surface

Current implementation exposes a producer-owned report/query seam with:
- date coverage
- notebook summaries
- conversation counts
- note counts
- bounded recent interaction rows
- text-unit projection from previews

## Constraints

- Keep this additive to current NotebookLM metadata capture.
- Do not write these rows into `logs/notes/<date>.jsonl`.
- Do not fold them into dashboard activity accounting yet.
- Do not invent session spans from sparse observations.
- Do not copy private case facts, names, or sensitive allegations from
  NotebookLM conversation history into repo docs, TODOs, or changelogs.
- When NotebookLM history informs product work, retain only sanitized themes:
  workflow pain points, review/matching/provenance requirements,
  contradiction-handling patterns, privacy controls, and operator-experience
  needs.

## Follow-on milestone

Only after this contract is stable should the suite define a true
interaction-grade NotebookLM activity/session model for:
- ask/chat turns with better timestamps
- note edits
- artifact generation request/result events
- notebook switching/open/revisit events
- sessionization and honest waterfall/timeline accounting
