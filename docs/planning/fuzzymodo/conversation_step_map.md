# Conversation Step Map -> Implementation Artifacts

## Source
- Conversation ID: `698686e2-6e48-839e-ad0f-91e6fa4697f8`
- Title: `OSS-Fuzz Bug Detection`
- Latest assistant timestamp: `2026-02-07T03:05:48.055634Z`
- Related context thread: `6986c9f5-3988-839d-ad80-9338ea8a04eb`
  - Title: `Conductor vs SB/ITIR`
  - Latest assistant timestamp: `2026-02-08T03:09:11.241219Z`
  - Relevance: state-governance/cloud-observer boundary for fuzzer evidence
    ingest and non-authoritative execution logs; includes explicit separation of
    post-mortem forensic tools from SB memory authority.

## Step Mapping
1. Define scope selectors per graph layer
- Artifact: `selector_dsl_spec.md` (Graph Layer Field Catalog section)

2. Define selector DSL syntax
- Artifact: `selector_dsl_spec.md` (Grammar and Clause Shape sections)

3. Define composition semantics (`all_of`, `any_of`, `not`)
- Artifact: `selector_dsl_spec.md` (Composition and Evaluation section)

4. Define executable norm constraints
- Artifact: `norm_constraint_spec.md`

5. Define deterministic replay/hashing
- Artifact: `canonical_hashing.md`

6. Make it implementation-ready
- Artifacts:
  - `selector_dsl.schema.json`
  - `norm_constraint.schema.json`
  - `fixtures/selector_samples.yaml`
  - `fixtures/norm_constraint_samples.yaml`
  - `fuzzymodo/src/selector_dsl/*`

7. Treat selector evaluation as speculation + rollback, not exhaustive search
- Artifacts:
  - `speculation_policy.md`
  - `fuzzymodo/src/selector_dsl/speculation.py`
  - `fuzzymodo/tests/test_speculation.py`

8. Keep normative effects behind explicit retirement/approval
- Artifacts:
  - `speculation_policy.md` (normative buffer + retirement section)
  - `fuzzymodo/src/selector_dsl/speculation.py` (decision state transitions)

9. Make selector predicates predictor-like: narrow, revocable, data-bound
- Artifacts:
  - `selector_dsl_spec.md` (operator discipline)
  - `fuzzymodo/src/selector_dsl/evaluator.py`
  - `fuzzymodo/tests/test_evaluator.py`
