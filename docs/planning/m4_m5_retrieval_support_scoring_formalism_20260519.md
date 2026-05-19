# M4/M5 Retrieval, Support, and Scoring Formalism

Date frozen: 2026-05-19

## Phase Boundary

This note freezes the formal objects discovered by the M4 structural retrieval
work and the M5 answer-quality protocol design.

The boundary is:

- M4 structural retrieval: recorded pass
- M5-alpha two-call probe: completed
- full M5 evaluation protocol: frozen/ready
- full M5 answer-quality proof: pending
- M6 promotion authority: not started/proven
- routing or decision use: intentionally blocked

Key law:

```text
M4 proves structural retrieval.
M5 proves answer-quality lift only.
M6 alone can prove promotion authority.
```

## 1. Candidate-Axis Manifold

A query is represented as an unresolved facet carrier:

```text
q = {f_1, ..., f_k}
FacetCarrier(q) = q
```

Retrieval does not collapse `q` into one semantic interpretation. It builds a
candidate-axis set:

```text
AxisCandidateSet(q) = {A_1, A_2, ...}
```

Each `A_i` contains:

- compatible facet fibres
- predicate posture
- role posture
- temporal posture
- domain posture
- surface participation
- residual ambiguity

Admissibility is a relation over query and candidate axis:

```text
Gamma(q, A_i) -> {admitted, blocked, unresolved}
```

The surviving retrieval object is the set of admissible candidate manifolds,
not a single best meaning.

## 2. Typed Residual Algebra

Residuals are first-class structure. They are not scalar penalties and must not
be collapsed into generic confidence.

```text
ResidualProfile(q, row) =
(
  R_lex,
  R_pred,
  R_role,
  R_temp,
  R_dom,
  R_surface,
  R_auth,
  R_proj
)
```

Each residual component has the value domain:

```text
R_i in {exact, compatible, blocked, unresolved}
```

Core laws:

```text
R_proj = exact
  => all lower projection grades required by that projection are exact

R_auth = unresolved
  => no promotion authority

R_i = blocked
  => the blocked component must be disclosed or excluded from answer support
```

## 3. Support Projection Law

Retrieval compatibility is not truth.

```text
LexicalCompatibility
  -> CandidateProjection
  -> ReceiptBackedPartialSupport
```

The following transitions are prohibited without additional authority:

```text
ReceiptBackedPartialSupport -/-> ExactSupport
ExactSupport                 -/-> Promotion
CandidateAxisSupport         -/-> Truth
SurfaceReference             -/-> Truth
```

The support projection law is:

```text
compatible support != exact support != truth != promotion
```

## 4. Admissible Basis Compression

The hot semantic index stores admissible basis objects, not all expanded
derivable semantic rows.

```text
H_N = B_N union R_N union Delta_N
```

where:

- `B_N`: shared basis objects
- `R_N`: compact refs
- `Delta_N`: irreducible local deltas

Cold-audit reconstruction requires:

```text
derive(H_N) = E_N
```

This justifies shape substitution, payload refs, token-stream witnesses, and
facet-bearing lexeme bases only when reconstruction remains receipt-backed.

## 5. Admissibility Search Compression

Naive pair search is separated from admissible pair search:

```text
AllPairs(A, B) -> AdmissiblePairs(A, B)
```

Database-level compression:

```text
rho_DB = |AdmissiblePairs| / |AllPairs|
G_DB   = 1 / rho_DB
```

Recorded M4 evidence:

```text
~2.29B naive pairs -> ~6,285 admissible candidates
```

This is a structural search-compression result. It is not answer-quality proof
and not promotion authority.

## 6. Fibre Pressure Tensor

Pressure is query/domain/time conditioned:

```text
Pressure(F | q, D, t)
```

and pairwise transport is:

```text
P(F_i, F_j, q, t, D)
```

M4f/M4g established that:

```text
global_pressure(F) != query_relevant_pressure(F | q, D, t)
```

Pressure can guide retrieval relevance and residual explanation. It cannot
promote facts.

## 7. Retrieval, Support, and Authority Separation

Define the three typed score families:

```text
R(q, row) = retrieval relevance
S(q, row) = receipt-backed support
A(q, row) = authority/promotion status
```

Governance algebra:

```text
R does_not_entail S
S does_not_entail A
Q does_not_entail A
```

Only the later M6 authority path may produce:

```text
AuthorityToken + PromotionCertificate -> promotion
```

## 8. Retrieval Relevance Algebra

Retrieval utility may be scored as:

```text
R(q, S_i) =
  alpha V
+ beta  L
+ gamma F
+ delta P
+ eps   Sigma
- eta   K
- theta U
- kappa C
```

where:

- `V`: vector similarity
- `L`: lexical overlap
- `F`: facet coverage
- `P`: query-conditioned fibre pressure
- `Sigma`: surface participation/alignment
- `K`: contradiction pressure penalty
- `U`: unsupported penalty
- `C`: chunk integrity penalty

This is retrieval utility only.

## 9. Typed Support Algebra

Support is represented as:

```text
S(q, row) =
(
  S_exact,
  S_partial,
  S_surface,
  S_receipt,
  S_residual
)
```

`S_exact` requires exact admissibility. `S_partial` is compatible
receipt-backed support and must preserve its residual profile.

## 10. Candidate-Axis Scoring

Each surviving axis can be scored diagnostically:

```text
AxisScore(A_i) =
  facet_overlap
+ compatible_overlap
+ receipt_backed_support
+ surface_support
- residual_pressure
```

The retrieval result is:

```text
top admissible candidate manifolds
```

not:

```text
best semantic interpretation
```

## 11. M4 Structural Pass Definition

M4 passes when this chain is executable and auditable:

```text
query
  -> indexed candidate recovery
  -> compatible fibre expansion
  -> receipt-backed axis support
  -> surface participation
  -> typed residual explanation
```

M4 pass excludes:

```text
truth
promotion
routing
answer authority
```

Diagnostic M4 score:

```text
M4_structural_score =
  w1 candidate_axis_receipt_backed_support
+ w2 candidate_axis_core_coverage
+ w3 surface_backed_axis_support
+ w4 receipt_coverage
+ w5 span_coverage
- w6 generic_only_match_rate
- w7 unresolved_chunk_penalty
```

The score is valid only while governance invariants remain false.

## 12. M5 Answer-Quality Score

M5 evaluates answer quality:

```text
Q(answer) =
(
  Q_grounding,
  Q_completeness,
  Q_citation,
  Q_residual_honesty,
  Q_hallucination,
  Q_usefulness,
  Q_latency,
  Q_repeatability
)
```

`Q` is not truth and not promotion.

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

Structural ITIR metrics are explanatory diagnostics and must not be mixed into
the RFP gate score.

## 13. M5 Report Layers

The M5 report has two layers.

RFP gate table:

- relevance
- factual grounding
- completeness
- hallucination rate or hallucination safety
- end-to-end latency p50/p95
- retrieval latency p50/p95
- token usage
- successful processing rate

ITIR diagnostic table:

- candidate-axis receipt-backed support
- candidate-axis core coverage
- surface-backed axis support
- span/receipt/surface coverage
- typed residual profile distribution
- citation traceability
- residual honesty

This prevents metric laundering: diagnostics can explain the answer-level
result, but they cannot replace it.

## 14. PNF Machine-Judge Substrate

For machine judging, prose is first converted into claim carriers:

```text
A -> ClaimAtoms(A) -> PredicatePNF(A) -> SupportComparison(A, C) -> Scores
```

Each claim atom is represented as:

```text
PNF(c_i) =
(
  predicate,
  roles,
  qualifiers,
  time,
  modality,
  polarity,
  source_posture
)
```

Retrieved context becomes support carriers:

```text
Support(C) =
{
  source_spans,
  receipt_refs,
  surface_refs,
  candidate_axis_refs,
  residual_profiles
}
```

Comparison:

```text
Compare(PNF(c_i), PNF(s_j))
  in {exact, partial_compatible, contradicted, unsupported, not_applicable}
```

Factual grounding:

```text
grounded_claim_rate =
  count(exact_or_partial_supported_claims) / count(claims)

unsupported_claim_rate =
  count(unsupported_claims) / count(claims)
```

Hallucination:

```text
Hallucination(c_i) =
  unsupported(c_i)
  or contradicted(c_i)
  or authority_overclaim(c_i)
  or unsupported_numeric_claim(c_i)
  or unsupported_temporal_claim(c_i)
  or unsupported_causal_claim(c_i)
```

Residual honesty:

```text
ResidualHonesty(c_i) =
  answer_modality(c_i) <= support_grade(c_i)
```

The machine-judge output schema is frozen at:

```text
docs/planning/m5_pnf_machine_judge_output_schema_v1.json
```

## 15. M5 Pass/Fail Gate

Treatment passes the first gate only if it improves:

```text
unsupported_claim_rate: -20 percent
citation_traceability:  +20 percent
core_facet_coverage:    +15 percent
grounded_claim_rate:    improve
```

and satisfies the RFP gate:

```text
CompositeQuality_treatment >= CompositeQuality_baseline * 1.15
hallucination_rate_treatment <= hallucination_rate_baseline * 0.80
p95_end_to_end_latency_treatment <= p95_end_to_end_latency_baseline * 1.10
successful_processing_rate >= 0.99
```

while preserving:

- cost threshold
- governance invariants
- residual honesty
- authority limits

## 16. M5-beta Preliminary Machine-Judge Lane

M5-beta is a small machine-assisted A/B assessment, not the full M5 proof.

For a query `q`:

```text
BaselineAnswers_beta(q) = {B_1}
TreatmentAnswers_beta(q) = {T_1}
```

Each answer is transformed through the same claim substrate:

```text
A_i
  -> ClaimAtoms(A_i)
  -> PredicatePNF(A_i)
  -> SupportComparison(A_i, C_i)
  -> PreliminaryScores(A_i)
```

The beta comparison object is:

```text
BetaPairScore(q) =
(
  grounding_delta,
  completeness_delta,
  hallucination_delta,
  citation_support_delta,
  residual_laundering_delta,
  judge_directional_usefulness,
  human_agreement,
  governance_violations
)
```

M5-beta can only justify proceeding to full M5 when:

```text
human_agreement = true
governance_violations = 0
```

and the machine judge is observed to catch unsupported or overclaimed answer
claims. It cannot establish:

```text
full_m5_proven
rfp_pass
answer_quality_lift_proven
promotion_authority
routing_authority
```

## 17. Answer Manifold Extension

The mature M5 scoring object is an answer manifold rather than a single best
answer:

```text
AnswerSet(q) =
  BaselineAnswers(q) or TreatmentAnswers(q)
```

Define:

```text
S_answer(AnswerSet) =
(
  grounding,
  coherence,
  residual_stability,
  support_overlap,
  axis_consistency,
  contradiction_pressure,
  citation_consistency,
  latency,
  cost
)
```

This asks whether an answer family remains stable, grounded, and residual-honest
under repeated runs. It does not ask whether any one answer can be promoted to
truth.

The important stability diagnostics are:

- intra-arm PNF coherence
- residual tensor stability
- receipt/span/surface support overlap
- candidate-axis consistency
- contradiction topology
- citation/support consistency

These diagnostics can explain full M5 outcomes, but they do not replace the RFP
gate metrics.

## 18. Governance Invariants

Hard fail if any are true:

```text
promotion_authority
routing
semantic_fact_emission
surface_ref_implies_truth
candidate_axis_support_implies_truth
answer_quality_implies_promotion
```

The mathematically closed tranche statement is therefore:

```text
M4 structural retrieval formalism is frozen.
M5 answer-quality protocol, M5-beta preliminary lane, and scoring algebra are frozen/ready.
Full M5 proof is pending live repeated A/B runs and scoring.
M6 alone may define promotion authority.
```
