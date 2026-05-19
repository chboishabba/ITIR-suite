# M5 Answer-Quality Evaluation Protocol

Date frozen: 2026-05-19

## Phase Boundary

This tranche is complete when:

- M4 structural retrieval: recorded pass
- M5-alpha two-call probe: completed
- Full M5 evaluation protocol: frozen/ready

This tranche does not claim:

- full M5 already proven
- answer-quality lift already demonstrated
- any promotion authority from retrieval or answer quality

Key line:

> M4 proved structural retrieval. M5 must prove answer-quality lift. M6 alone can prove promotion authority.

## M4 Recorded Pass

M4 is recorded as a structural retrieval pass only. The pass means the retrieval
surface can expose candidate axes, spans, receipts, surfaces, and typed
residuals in an auditable shape suitable for evaluation.

M4 does not mean retrieved candidates are true, promoted, routed, or sufficient
for answer generation.

## M5-alpha Two-Call Probe

M5-alpha is recorded as completed at probe level:

1. Call 1: retrieve structured candidate context.
2. Call 2: answer using that retrieved context under explicit grounding and
   residual-honesty constraints.

The probe is evidence that the control flow is executable. It is not evidence
that treatment quality beats baseline. The full A/B matrix below is required
before any answer-quality lift claim.

## M5-beta Machine-Assisted Preliminary Lane

M5-beta is an optional preliminary AI-judge lane between M5-alpha and full M5:

```text
M5-alpha: two-call answer smoke
M5-beta: small AI-judged preliminary A/B
M5: full human-scored A/B
```

M5-beta exists to debug the rubric, prompt, claim extraction, and judge output
before spending on the full 72-run matrix. It is not the RFP pass/fail run.

Minimum M5-beta matrix:

- 3 frozen queries
- 1 baseline answer per query
- 1 treatment answer per query
- 1 PNF machine-judge pass per baseline/treatment pair
- human review of the judge output

M5-beta success only permits proceeding to full M5 when:

- treatment is directionally better on grounding or completeness
- the AI judge catches unsupported claims
- a human reviewer agrees the judge output is directionally useful
- no governance invariant is violated

Governance boundary:

- AI judge score is not final truth
- AI judge score is not RFP pass/fail evidence
- AI judge score does not imply promotion authority
- human-scored full M5 remains required for answer-quality proof

## Frozen Inputs

- Query suite: `docs/planning/m5_query_suite_v1.json`
- Prompt template: `docs/planning/m5_answer_prompt_template_v1.md`
- Runner: `scripts/run_m5_eval_protocol.py`
- Execution preflight: `scripts/run_m5_ab_preflight.py`
- M5-beta preflight: `scripts/run_m5_beta_preflight.py`
- M5-beta guarded OpenAI answer adapter:
  `scripts/run_m5_beta_openai_adapter.py`
- Formalism:
  `docs/planning/m4_m5_retrieval_support_scoring_formalism_20260519.md`
- PNF machine-judge schema:
  `docs/planning/m5_pnf_machine_judge_output_schema_v1.json`
- Default generated artifacts:
  - JSON manifest: `m5_eval_manifest.json`
  - CSV manual score sheet: `m5_score_sheet.csv`

Fixed run settings:

- frozen queries: 12
- baseline runs per query: 3
- treatment runs per query: 3
- fixed model: recorded in runner manifest, default `manual-fixed-model`
- fixed prompt: `m5_answer_prompt_template_v1`
- fixed k: recorded in runner manifest, default `8`
- fixed temperature: recorded in runner manifest, default `0`
- scoring mode: manual rubric first

## Execution Preflight

The full M5 A/B matrix requires explicit live hooks before answer-quality lift
can be tested:

- `M5_BASELINE_RETRIEVAL_COMMAND`
- `M5_BASELINE_ANSWER_COMMAND`
- `M5_TREATMENT_RETRIEVAL_COMMAND`
- `M5_TREATMENT_ANSWER_COMMAND`

The optional PNF machine-judge hook is `M5_MACHINE_JUDGE_COMMAND`; manual
rubric scoring remains primary.

Current recorded preflight:

- artifact directory: `runs/m5_ab_preflight_20260519T000000/`
- run matrix materialized: 12 queries x 3 baseline runs x 3 treatment runs
- execution status: `blocked_missing_live_hooks`
- missing required hooks: baseline retrieval, baseline answer, treatment
  retrieval, treatment answer

This preflight is intentionally fail-closed. It records that the protocol and
score sheet are executable, while full M5 live A/B execution and manual scoring
remain pending.

## M5-beta Execution Preflight And Mini-Run

The preliminary machine-assisted lane requires explicit live hooks:

- `M5_BETA_BASELINE_RETRIEVAL_COMMAND`
- `M5_BETA_BASELINE_ANSWER_COMMAND`
- `M5_BETA_TREATMENT_RETRIEVAL_COMMAND`
- `M5_BETA_TREATMENT_ANSWER_COMMAND`
- `M5_BETA_MACHINE_JUDGE_COMMAND`

Current recorded M5-beta preflight:

- artifact directory: `runs/m5_beta_preflight_20260520T000000/`
- run matrix materialized: 3 queries x 1 baseline run x 1 treatment run
- judge pairs materialized: 3
- execution status: `blocked_missing_live_hooks`
- missing required hooks: beta baseline retrieval, beta baseline answer, beta
  treatment retrieval, beta treatment answer, beta machine judge

This is the correct fail-closed result for generic hook-driven execution.

Current recorded guarded OpenAI answer mini-run:

- artifact directory: `runs/m5_beta_openai_20260520T000000/`
- answer adapter: `scripts/run_m5_beta_openai_adapter.py`
- env source: caller-supplied local env file
- model: `gpt-4.1-mini`
- run matrix completed: 3 queries x 1 baseline answer x 1 treatment answer
- generated answer artifacts: 6
- API judge calls: 0
- Codex preliminary judgment:
  `runs/m5_beta_openai_20260520T000000/m5_beta_codex_prelim_judgment.md`
- preliminary direction: treatment better on grounding, completeness, and
  citation/traceability
- governance violations observed: 0
- human review status: pending

The mini-run is still M5-beta only. It does not prove full M5 answer-quality
lift and does not authorize promotion, routing, or decision use.

## Evidence Substrate

Every treatment retrieval artifact should preserve:

- raw document or source identifier
- canonical text identifier
- text revision identity
- exact chunk/span reference
- receipt reference where available
- surface reference where available
- typed residual profile

Vector hits, file paths, surface names, or candidate axes are lookup/support
signals only. They are not truth, promotion, or authority.

## Formal Scoring Boundary

M5 scoring has three separated layers:

1. RFP gate metrics: relevance, factual grounding, completeness, and
   hallucination safety.
2. PNF machine-judge substrate: claim atoms compared against retrieved
   source/span/receipt/surface support while preserving residuals.
3. ITIR diagnostics: candidate-axis support, span/receipt/surface coverage,
   typed residual profiles, and citation traceability.

The RFP composite quality score is built only from the answer-level gate
metrics:

```text
CompositeQuality =
mean(
  relevance,
  factual_grounding,
  completeness,
  hallucination_inverse
)
```

ITIR structural diagnostics explain the result. They are not mixed into the RFP
composite quality score and cannot substitute for answer-level improvement.

Machine judging, when used, must score claim-level PNF comparisons against
retrieved support carriers before producing aggregate scores. The frozen output
shape is `docs/planning/m5_pnf_machine_judge_output_schema_v1.json`.

## Retrieval Ordering

The treatment path evaluates retrieval in this order:

1. selector or structural candidate set
2. optional ranking
3. bounded fetch
4. span/receipt/surface evaluation
5. answer generation under the frozen prompt

This preserves the selector-first boundary: ranking can order candidates, but
ranking does not create evidence and does not promote facts.

## Required Testing Axes

### 1. Retrieval Context Quality

- `candidate_axis_receipt_backed_support`
- `candidate_axis_core_coverage`
- `candidate_axis_surface_backed_support`
- `span_receipt_surface_coverage`
- `typed_residual_profile_distribution`

### 2. Answer Grounding

- `supported_claim_rate`
- `unsupported_claim_count`
- `citation_present_rate`
- `citation_correctness`
- `source_span_receipt_traceability`

### 3. Core Facet Coverage

- `query_facets_covered_in_answer`
- `missing_core_facets`
- `candidate_axis_coverage_in_answer`

### 4. Residual Honesty

- `residuals_disclosed`
- `contradictions_disclosed`
- `authority_limits_disclosed`
- `overclaim_count`
- `candidate_only_language_preserved`

### 5. Citation Quality

- `citation_precision`
- `citation_supports_sentence`
- `citation_relevance`
- `citation_overload_rate`

### 6. Hallucination / Unsupported Inference

- `unsupported_entities`
- `unsupported_temporal_claims`
- `unsupported_causal_claims`
- `unsupported_numeric_claims`
- `unsupported_authority_claims`

### 7. Usefulness

- `relevance`
- `specificity`
- `clarity`
- `compactness`
- `actionability`
- `non_redundancy`

### 8. Latency / Cost

- `retrieval_latency_ms`
- `answer_latency_ms`
- `total_latency_ms`
- `input_tokens`
- `output_tokens`
- `cost_estimate`

### 9. Repeatability

- `retrieval_overlap`
- `answer_score_variance`
- `citation_variance`
- `same_query_repeat_variance`

### 10. Governance Invariants

Hard fail if any field is true:

- `promotion_authority`
- `routing`
- `semantic_fact_emission`
- `surface_ref_implies_truth`
- `candidate_axis_support_implies_truth`
- `answer_quality_implies_promotion`

## Query Categories

The frozen query suite must include:

- exact support
- partial support
- contradiction
- missing support
- temporal/update-heavy
- policy/regulatory
- market/liquidity
- entity-specific
- broad/generic
- negative control

The current suite includes 12 queries so every required category is represented
at least once while keeping first-pass manual scoring tractable.

## First Pass/Fail Gate

Treatment should improve:

- RFP composite quality score: at least 15 percent increase
- hallucination rate: at least 20 percent reduction
- `unsupported_claim_rate`: at least 20 percent reduction
- `citation_traceability`: at least 20 percent increase
- `core_facet_coverage`: at least 15 percent increase
- `grounded_claim_rate`: improve

Without violating:

- latency threshold
- cost threshold
- governance invariants
- residual honesty

Default first-pass thresholds:

- treatment p95 end-to-end latency no worse than baseline plus 10 percent
- `successful_processing_rate >= 0.99`
- `total_latency_ms_p95 <= 30000`
- `cost_estimate_per_answer <= 0.10`
- zero governance hard failures
- zero residual-honesty hard failures

## Manual Scoring Scale

Use a 0-3 integer score unless the field is a count, boolean, ratio, latency,
token, or cost field:

- 0: absent or wrong
- 1: weak / mostly unsupported
- 2: adequate but incomplete
- 3: strong and clearly supported

For rate fields, use `0.0` to `1.0`.
For count fields, use non-negative integers.
For hard-fail invariant fields, use `false` unless a violation is observed.

## Completion Checklist

1. Freeze M5 query suite.
2. Freeze prompt template.
3. Freeze scoring rubric.
4. Implement/verify runner.
5. Optional: run M5-beta preliminary AI-judge A/B and human review.
6. Run full M5 A/B.
7. Score manually.
8. Produce final M5 report.

This phase closes after items 1-4 plus the recorded execution preflight.
M5-beta is a useful preliminary lane, but it does not replace items 6-8.
