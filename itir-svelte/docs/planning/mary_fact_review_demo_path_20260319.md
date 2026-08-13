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
- trauma/support real-path parity is locked for `ITIR-US-13` and `ITIR-US-14`
  via:
  - `wave3:real_transcript_fragmented_support_v1`
  - `transcript_semantic`
  - `real_transcript_fragmented_support_v1`
- professional handoff / false-coherence real-path parity is locked for
  `ITIR-US-15` and `ITIR-US-16` via:
  - `wave5:real_transcript_professional_handoff_v1`
  - `real_transcript_professional_handoff_v1`
  - `wave5:real_transcript_false_coherence_v1`
  - `real_transcript_false_coherence_v1`

Trauma/support capture command:

```bash
cd /home/c/Documents/code/ITIR-suite
python3 SensibLaw/scripts/query_fact_review.py \
  --db-path .cache_local/itir.sqlite \
  demo-bundle \
  --workflow-kind transcript_semantic \
  --workflow-run-id real_transcript_fragmented_support_v1 \
  --wave wave3_trauma_advocacy \
  --fixture-kind real
```

Wave-5 professional handoff capture command:

```bash
cd /home/c/Documents/code/ITIR-suite
python3 SensibLaw/scripts/query_fact_review.py \
  --db-path .cache_local/itir.sqlite \
  demo-bundle \
  --workflow-kind transcript_semantic \
  --workflow-run-id real_transcript_professional_handoff_v1 \
  --wave wave5_handoff_false_coherence \
  --fixture-kind real
```

Wave-5 false-coherence capture command:

```bash
cd /home/c/Documents/code/ITIR-suite
python3 SensibLaw/scripts/query_fact_review.py \
  --db-path .cache_local/itir.sqlite \
  demo-bundle \
  --workflow-kind transcript_semantic \
  --workflow-run-id real_transcript_false_coherence_v1 \
  --wave wave5_handoff_false_coherence \
  --fixture-kind real
```

## Contract stance

- `SensibLaw` owns the persisted `workbench` / `acceptance` / `sources` bundle shape.
- `itir-svelte` consumes that contract read-only.
- Captured demo fixtures should come from the `demo-bundle` CLI seam, not hand-invented UI-only payloads.
- Operator presentation can add clearer provenance, abstention, and story-family cues, but it must not invent semantics beyond the persisted bundle.
