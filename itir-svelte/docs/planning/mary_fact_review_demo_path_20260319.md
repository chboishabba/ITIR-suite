# Mary Fact Review Demo Path

Date: 2026-03-19

## Purpose

Pin one repeatable operator/demo path for Mary-parity fact review.

## Preferred open flow

1. Resolve a persisted run from `SensibLaw/scripts/query_fact_review.py` using `demo-bundle`.

```bash
cd /home/c/Documents/code/ITIR-suite
python3 SensibLaw/scripts/query_fact_review.py \
  --db-path .cache_local/itir.sqlite \
  demo-bundle \
  --workflow-kind transcript_semantic \
  --workflow-run-id transcript_acceptance_real_intake_v1 \
  --wave wave1_legal \
  --fixture-kind real
```

2. Use the returned selector fields:
   - `workflow_kind`
   - `workflow_run_id`
   - `source_label`
   - `wave`
3. Open `/graphs/fact-review` with those query params.

Canonical route today:

```text
/graphs/fact-review?workflow=transcript_semantic&workflowRunId=transcript_acceptance_real_intake_v1&sourceLabel=wave1:real_transcript_intake_v1&wave=wave1_legal&view=intake_triage
```

4. Verify:
   - current persisted run link
   - recent/source-centric reopen rows
   - canonical issue filters
   - inspector classification lanes
   - chronology buckets

## Real baselines

Primary Mary baseline:

- `wave1:real_transcript_intake_v1`
- `transcript_semantic`
- `transcript_acceptance_real_intake_v1`

AU/legal widening baseline:

- `wave1:real_au_procedural_v1`
- `au_semantic`
- `run:5ab560b645ee10d0badd59fe6ef0a9442bf5d41bc57e7ff950688ae5961ef12d`

AU capture command:

```bash
cd /home/c/Documents/code/ITIR-suite
python3 SensibLaw/scripts/query_fact_review.py \
  --db-path .cache_local/itir.sqlite \
  demo-bundle \
  --workflow-kind au_semantic \
  --workflow-run-id run:5ab560b645ee10d0badd59fe6ef0a9442bf5d41bc57e7ff950688ae5961ef12d \
  --wave wave1_legal \
  --fixture-kind real
```

Current widening status:

- transcript real-path parity is locked for `SL-US-09` to `SL-US-11`
- AU real-path parity is locked for `SL-US-12` to `SL-US-14`
- next widening target is trauma/handoff real-path proof

## Contract stance

- `SensibLaw` owns the persisted `workbench` / `acceptance` / `sources` bundle shape.
- `itir-svelte` consumes that contract read-only.
- Captured demo fixtures should come from the `demo-bundle` CLI seam, not hand-invented UI-only payloads.
