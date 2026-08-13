# Fact Review Operator Workflow Slice

Date: 2026-04-02

## Purpose

Land the first operator-grade workflow layer over the normalized review outputs.

This should not create a new workflow system.
It should turn the existing fact-review workbench into a clearer
inspect -> decide -> record -> follow-up surface.

## Decision

Use the fact-review workbench as the first host.

The workbench already has:

- review queue state
- chronology state
- contested/follow-up state
- reopen navigation
- compiler contract and promotion gate in semantic context for AU

The missing piece is one explicit workflow summary that says:

- what stage the operator is in
- what the next action is
- which existing view is the best place to do it
- why that path is being recommended

## First Bounded Contract

Add one small `workflow_summary` block to the persisted workbench payload.

Fields:

- `stage`
  - `inspect`
  - `decide`
  - `record`
  - `follow_up`
- `title`
- `recommended_view`
- `recommended_filter`
- `focus_fact_id`
- `reason`
- `counts`
- `promotion_gate`

## First Routing Rule

Keep the rule small and explicit:

- if the authority-follow queue is non-empty:
  - stage = `follow_up`
  - view = `authority_follow`
- else if there are contested items needing follow-up:
  - stage = `follow_up`
  - view = `contested_items`
- else if the review queue is non-empty:
  - stage = `decide`
  - view = `intake_triage`
- else if chronology still has undated/no-event pressure:
  - stage = `inspect`
  - view = `chronology_prep`
- else:
  - stage = `record`
  - view = `professional_handoff`

The promotion gate is advisory context, not the only driver.

## Acceptance Gate

This slice is complete when:

- the workbench payload emits one stable `workflow_summary`
- the fact-review route surfaces that summary clearly
- the route gives one obvious next action without hiding the existing review
  detail
- backend and route checks pass

## Outcome

Landed as the first bounded operator workflow slice.

Implemented:

- `SensibLaw/src/fact_intake/read_model.py`
  - workbench now emits:
    - `semantic_context`
    - `workflow_summary`
- `itir-svelte/src/routes/graphs/fact-review/+page.svelte`
  - route now surfaces:
    - current workflow stage
    - recommended next view
    - suggested fact focus
    - compact workflow pressure counts

Validation:

- backend:
  - `30 passed`
- Python compile:
  - `py_compile` passed for `read_model.py`
- frontend:
  - this slice's route-local error was fixed
  - repo-wide `npm run check` still fails on unrelated pre-existing errors in
    `itir-svelte/src/routes/graphs/wiki-timeline-aoo-all/+page.svelte`

## Next Lane

The next pinned operator lane is the first bounded annotation / QA workbench
slice over the existing fact-review/read-model spine.
