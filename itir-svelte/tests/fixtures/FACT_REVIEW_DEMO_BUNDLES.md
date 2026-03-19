# Fact Review Demo-Bundle Fixtures (Real)

Trimmed demo-bundle payloads captured directly from persisted runs via
`SensibLaw/scripts/query_fact_review.py demo-bundle`. Keep these aligned with
real persisted Mary runs; do not hand-edit payload fields.

## Capture commands

Run from repo root (`/home/c/Documents/code/ITIR-suite`):

```bash
# Wave 1 transcript (Mary baseline)
python3 SensibLaw/scripts/query_fact_review.py \
  --db-path .cache_local/itir.sqlite \
  demo-bundle \
  --workflow-kind transcript_semantic \
  --workflow-run-id transcript_acceptance_real_intake_v1 \
  --wave wave1_legal \
  --fixture-kind real \
  > itir-svelte/tests/fixtures/fact_review_wave1_real_demo_bundle.json

# Wave 1 AU procedural (latest)
python3 SensibLaw/scripts/query_fact_review.py \
  --db-path .cache_local/itir.sqlite \
  demo-bundle \
  --workflow-kind au_semantic \
  --workflow-run-id run:5ab560b645ee10d0badd59fe6ef0a9442bf5d41bc57e7ff950688ae5961ef12d \
  --wave wave1_legal \
  --fixture-kind real \
  > itir-svelte/tests/fixtures/fact_review_wave1_real_au_demo_bundle.json

# Wave 1 AU procedural (prior captured run)
python3 SensibLaw/scripts/query_fact_review.py \
  --db-path .cache_local/itir.sqlite \
  demo-bundle \
  --workflow-kind au_semantic \
  --workflow-run-id run:b0babf0805c27ce817d7e1526c94f3b3aee8529ced80e4ed2c74b19aaaff5bf0 \
  --wave wave1_legal \
  --fixture-kind real \
  > itir-svelte/tests/fixtures/fact_review_wave1_real_au_demo_bundle_b0babf.json

# Wave 3 trauma/support fragmented transcript
python3 SensibLaw/scripts/query_fact_review.py \
  --db-path .cache_local/itir.sqlite \
  demo-bundle \
  --workflow-kind transcript_semantic \
  --workflow-run-id real_transcript_fragmented_support_v1 \
  --wave wave3_trauma_advocacy \
  --fixture-kind real \
  > itir-svelte/tests/fixtures/fact_review_wave3_real_fragmented_support_demo_bundle.json

# Wave 5 professional handoff transcript
python3 SensibLaw/scripts/query_fact_review.py \
  --db-path .cache_local/itir.sqlite \
  demo-bundle \
  --workflow-kind transcript_semantic \
  --workflow-run-id real_transcript_professional_handoff_v1 \
  --wave wave5_handoff_false_coherence \
  --fixture-kind real \
  > itir-svelte/tests/fixtures/fact_review_wave5_real_professional_handoff_demo_bundle.json

# Wave 5 false-coherence transcript
python3 SensibLaw/scripts/query_fact_review.py \
  --db-path .cache_local/itir.sqlite \
  demo-bundle \
  --workflow-kind transcript_semantic \
  --workflow-run-id real_transcript_false_coherence_v1 \
  --wave wave5_handoff_false_coherence \
  --fixture-kind real \
  > itir-svelte/tests/fixtures/fact_review_wave5_real_false_coherence_demo_bundle.json
```

## Fixture index

| fixture file | workflow_kind | workflow_run_id | source_label | wave |
| --- | --- | --- | --- | --- |
| `fact_review_wave1_real_demo_bundle.json` | `transcript_semantic` | `transcript_acceptance_real_intake_v1` | `wave1:real_transcript_intake_v1` | `wave1_legal` |
| `fact_review_wave1_real_au_demo_bundle.json` | `au_semantic` | `run:5ab560b645ee10d0badd59fe6ef0a9442bf5d41bc57e7ff950688ae5961ef12d` | `wave1:real_au_procedural_v1` | `wave1_legal` |
| `fact_review_wave1_real_au_demo_bundle_b0babf.json` | `au_semantic` | `run:b0babf0805c27ce817d7e1526c94f3b3aee8529ced80e4ed2c74b19aaaff5bf0` | `wave1:real_au_procedural_v1` | `wave1_legal` |
| `fact_review_wave3_real_fragmented_support_demo_bundle.json` | `transcript_semantic` | `real_transcript_fragmented_support_v1` | `wave3:real_transcript_fragmented_support_v1` | `wave3_trauma_advocacy` |
| `fact_review_wave5_real_professional_handoff_demo_bundle.json` | `transcript_semantic` | `real_transcript_professional_handoff_v1` | `wave5:real_transcript_professional_handoff_v1` | `wave5_handoff_false_coherence` |
| `fact_review_wave5_real_false_coherence_demo_bundle.json` | `transcript_semantic` | `real_transcript_false_coherence_v1` | `wave5:real_transcript_false_coherence_v1` | `wave5_handoff_false_coherence` |

Notes:

- All payloads are the CLI-returned JSON with stable key ordering/indentation.
- Keep trims limited to removing unused top-level keys if needed; avoid editing
  nested payloads by hand to preserve contract integrity.
- `fact_review_wave1_real_au_demo_bundle.json` is the current AU baseline.
- `fact_review_wave1_real_au_demo_bundle_b0babf.json` is retained as a prior
  real capture for selector/history audit only; new route regressions should
  target the current AU baseline unless they are explicitly auditing drift.
