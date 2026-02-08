# ITIR Assumption Stress Test (2026-02-08)

## Purpose
Capture high-risk architectural assumptions as explicit failure modes with
controls, test hooks, and decision linkage.

This document is a hardening artifact for refactor coordination, focused on
anti-enshittification and boundary integrity.

## Method
- Treat each assumption as falsifiable.
- Define concrete failure signals.
- Attach controls to existing decision IDs where possible.
- Convert unresolved assumptions into executable TODO/test gates.

## Stress register

| AID | Assumption under stress | Failure mode if false | Decision linkage | Control / test gate |
| --- | --- | --- | --- | --- |
| A1 | 3D axes can simultaneously carry contact and account-layer semantics without overload. | Visual ambiguity, lane collisions, unreadable timeline ("spaghetti"). | `Q1` | Freeze axis hierarchy policy before advanced 3D expansion. Require deterministic 2D fallback and lane collision tests. |
| A2 | SB temporal folding is neutral because SB is non-agentic. | Hidden prioritization and intent substitution through fold/loss policy. | `Q2` | Store "mechanical should" as machine flags + explicit loss profile declarations. Add fold-policy receipts and red-team tests for hidden nudging. |
| A3 | Receipt-backed claims are sufficient protection against fabricated causal narratives. | "Reproducible hallucinations" where citations are valid but causal glue is invented. | `Q6` and Three-Locks quality gates | Require claim-link metadata (`link_type`, `confidence`, `counter_hypothesis_ref`) for public outputs. Fail artifact build on missing causal-link provenance. |
| A4 | Universal slot grammar can represent plural legal traditions without epistemic loss. | Cultural flattening and forced normalization of non-separable legal subjects. | `Q7` | Add non-reduction path: allow parallel authority models with explicit `needs_reconciliation` and unmapped-preservation nodes. Ban silent coercion into dominant schema. |
| A5 | Local-first encrypted architecture can maintain high-fidelity 3D performance at target scale. | Performance collapse, fatigue amplification, pressure to centralize/decrypt. | New perf/privacy gate | Define benchmark budget and degradation contract (level-of-detail, query windows, precomputed local indexes). Fail perf gate if limits exceeded. |
| A6 | `needs_reconciliation` is sufficient terminal state for contradictions during urgent action contexts. | User blocked in crisis; system preserves ambiguity but fails actionable support. | `Q6` plus action policy | Add contradiction action protocol: branch-specific action bundles with explicit uncertainty labels and no forced semantic collapse. |
| A7 | Canonical reducer quality remains stable without explicit lexical-noise guardrails. | False anchors and semantic drift from stopwords/number-heavy spans, cross-page artifacts, and citation boilerplate flooding. | `Q11` + shared reducer guard policy | Add deterministic lexical guard suite and fixtures for noisy spans; fail conformance if guard outputs regress. |
| A8 | Safety controls can remain optional until fully implemented. | Fail-open governance: boundary-affecting changes merge without active enforcement. | Refactor merge/gate policy | Require fail-closed CI stub tests for every `OPEN` AID/Qx control; merge blocked unless passing or explicitly waived with receipt. |
| A9 | Multi-stage compression remains truthful without explicit anti-recursive-summary rules. | Summary-of-summary decay and review inversion (harder to verify output than to regenerate). | Expansion Invariant policy | Ban summaries as canonical inputs to downstream summarizers unless expanded to raw IDs first; add lineage checks and decay tests. |
| A10 | Loss profiles remain comparable and auditable without schema-level constraints. | Inconsistent or vague loss declarations hide compression harm and prevent cross-surface audit. | Expansion contract + schema freeze | Define machine-readable `loss_profile` schema and enforce required fields for every fold/sitrep/receipt surface. |

## Immediate control policy
- Do not treat unresolved assumptions as harmless.
- Any feature depending on a stressed assumption must:
  - declare dependency on the relevant AID,
  - include at least one failure test,
  - include rollback behavior if the assumption fails at runtime.
- Every `OPEN` control must have a fail-closed CI stub (or explicit waiver
  receipt) so safeguards cannot silently remain optional.

## Sprint 10 impact
### Blocking for Sprint 10
- `A2` (`Q2`): SB fold output semantics and anti-nudge boundary.
- `A3` (causal-link provenance minimum): required for claims entering public
  artifact surfaces.
- `A8`: fail-closed test gate discipline for unresolved controls.
- `A9`: no summary-of-summary canonical pipeline paths.

### Tracked, non-blocking for Sprint 10 thin slice
- `A1` (`Q1`), `A4` (`Q7`), `A5` (perf/privacy gate), `A6` (contradiction
  action protocol), `A7` (lexical-noise guardrails), `A10` (loss-profile schema
  enforcement).

These remain mandatory before broad production rollout.

## Test additions required
- Axis hierarchy collision fixture tests (`A1`).
- SB fold-policy red-team tests for implicit prioritization (`A2`).
- Receipt-to-claim link integrity tests (`A3`).
- Plural-law non-reduction preservation fixtures (`A4`).
- Performance budget benchmarks under encryption/load (`A5`).
- Contradiction action branching tests (`A6`).
- Lexical-noise deterministic guard fixtures (stopword/number-heavy spans,
  cross-page artifacts, citation boilerplate flooding) (`A7`).
- Fail-closed CI stub tests for unresolved AIDs/Qx controls (`A8`).
- Summary-lineage tests preventing recursive summary ingestion without expansion
  to raw IDs (`A9`).
- Loss-profile schema validation tests across SB/receipts surfaces (`A10`).

## Acceptance statement
The architecture is considered hardened only when each AID has:
- explicit policy text,
- corresponding tests,
- and merge gates preventing silent regression.
