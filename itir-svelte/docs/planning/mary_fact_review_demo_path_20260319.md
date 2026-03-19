# Mary Fact Review Demo Path

Date: 2026-03-19

## Purpose

Pin one repeatable operator/demo path for Mary-parity fact review.

## Preferred open flow

1. Resolve a persisted run from `SensibLaw/scripts/query_fact_review.py` using `demo-bundle`.
2. Use the returned selector fields:
   - `workflow_kind`
   - `workflow_run_id`
   - `source_label`
   - `wave`
3. Open `/graphs/fact-review` with those query params.
4. Verify:
   - current persisted run link
   - recent/source-centric reopen rows
   - canonical issue filters
   - inspector classification lanes
   - chronology buckets

## Contract stance

- `SensibLaw` owns the persisted `workbench` / `acceptance` / `sources` bundle shape.
- `itir-svelte` consumes that contract read-only.
- Captured demo fixtures should come from the `demo-bundle` CLI seam, not hand-invented UI-only payloads.
