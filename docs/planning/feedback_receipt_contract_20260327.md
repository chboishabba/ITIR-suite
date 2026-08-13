# Feedback Receipt Contract

Date: 2026-03-27

Purpose: define a bounded, canonical receipt for user feedback so competitor
frustrations, frustrations with our current suite, and delight/retention
signals can be stored with provenance instead of remaining ad hoc chat lore.

## Core rule

Feedback receipts are evidence about user experience, not semantic truth about
the underlying corpus. They must remain:

- quoted where possible
- provenance-bearing
- date-scoped
- role/task-scoped
- explicit about whether they are direct user evidence or a derived note

## Canonical receiver

The canonical receiver is the suite SQLite path used for bounded read models:

- `itir.sqlite`

JSON examples may exist for fixtures/tests, but runtime feedback state should
persist in sqlite.

## Receipt classes

Allowed `feedback_class` values:

- `competitor_frustration`
- `suite_frustration`
- `delight_signal`

These are intentionally small and should not proliferate.

## Mandatory fields

Every receipt must provide:

- `schema_version`
- `feedback_class`
- `role_label`
- `task_label`
- `source_kind`
- `summary`
- `quote_text`
- `severity`
- `captured_at`

## Optional but strongly preferred fields

- `target_product`
- `target_surface`
- `workflow_label`
- `desired_outcome`
- `sentiment`
- `provenance`
- `tags`

## Field meanings

- `feedback_class`
  - whether the receipt is about a competitor/current mainstream workflow, our
    own suite, or a positive/delight signal
- `role_label`
  - user/persona or operator role (for example `lawyer`, `psychologist`,
    `builder`, `investor`, `support_worker`)
- `task_label`
  - the concrete job attempted (for example `prepare_case`, `browse_corpus`,
    `recover_day_state`, `transcribe_session`)
- `source_kind`
  - the evidence origin:
    - `interview`
    - `usability_session`
    - `chat_thread`
    - `operator_note`
    - `story_proxy`
- `summary`
  - one short normalized sentence describing the feedback
- `quote_text`
  - the closest exact complaint/like wording available; if synthesized from a
    note, say so conservatively
- `severity`
  - one of:
    - `low`
    - `medium`
    - `high`
    - `critical`
- `captured_at`
  - ISO timestamp/date for when the feedback was captured or recorded
- `desired_outcome`
  - what the user actually wanted instead

## Provenance rule

`story_proxy` is allowed, but it must be visible as such.

That means:

- real user interview/usability evidence and proxy/story-derived synthesis may
  share a receiver
- but they must never be silently collapsed together

Where a receipt points to an internal suite object, provenance should prefer a
stable ref over only a page label. Examples:

- canonical thread id
- fact-review selector (`workflow_kind`, `workflow_run_id`, `source_label`)
- contested review run id

Those refs remain optional, but they are the preferred basis for drill-ins.

## Minimal runtime operations

The first bounded runtime lane must support:

1. add one receipt directly from the CLI
2. import a bounded batch of receipts from a local JSONL file
3. list recent receipts with filters
4. show one receipt in full

This is enough to:

- gather evidence without manual sqlite seeding
- review evidence
- prioritize against evidence later

## First ergonomic intake path

The first ergonomic intake path is intentionally narrow:

- use `scripts/query_fact_review.py feedback-add` for one receipt
- use `scripts/query_fact_review.py feedback-import` for local JSONL batches

Boundary:

- this is a capture helper over the canonical sqlite receiver
- it is not yet a polished interview app or end-user UI
- it should not infer fields that the collector did not provide, except for a
  conservative default `captured_at` timestamp when omitted at the CLI layer

## Non-goals

- no sentiment-analysis inference
- no automatic clustering or prioritization
- no “AI summary of all feedback” truth surface
- no silent promotion of proxy notes into direct user evidence

## Example minimal payload

```json
{
  "schema_version": "feedback.receipt.v1",
  "feedback_class": "suite_frustration",
  "role_label": "lawyer",
  "task_label": "browse_corpus",
  "target_product": "itir-svelte",
  "target_surface": "/corpora/processed/personal",
  "workflow_label": "personal_results_review",
  "source_kind": "interview",
  "summary": "The user could find the data but not the next action.",
  "quote_text": "I can see the results, but I still don't know what I'm supposed to do next.",
  "severity": "high",
  "desired_outcome": "One obvious next step from the results page.",
  "captured_at": "2026-03-27T14:00:00Z",
  "sentiment": "negative",
  "tags": ["navigation", "workflow", "ui"],
  "provenance": {
    "collector": "manual_note",
    "source_ref": "user_interview_20260327_01"
  }
}
```
