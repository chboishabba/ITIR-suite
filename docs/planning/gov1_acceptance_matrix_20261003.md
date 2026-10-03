# GOV-1 acceptance matrix

Date: 2026-10-03

This matrix is an engineering acceptance map, not an ISO/ITIL/NIST certification statement.

| Requirement | Risk | Control | Implementation owner | Required evidence | Current state for new GOV tranche | Open residual / CAPA |
|---|---|---|---|---|---|---|
| one control plane, no second semantic authority | governance subsystem silently becomes truth owner | non-promotion flags + existing evaluator ownership | SensibLaw / DASHI | focused tests + formal owner | source_written | exact-head tests/kernel |
| service state distinct from evidence strength | implemented presented as validated | orthogonal enums/state carrier | SensibLaw / StatiBaker / DASHI | state-transition regressions | source_written | focused/full tests |
| standards are design provenance only | false certification implication | `source_standards`; `certification_claim=false` | SensibLaw | profile/control-case rendering tests | source_written | focused/full tests |
| PII/purpose lifecycle explicit | Matter visibility mistaken for processing purpose | InformationAsset / ProcessingActivity | SensibLaw | asset/activity tests + scoped fixture | source_written | fixture + privacy review |
| GOV does not alter INV merit vector | access/privacy state becomes hidden ranking axis | governance sidecar outside `(I,D,C,N,L)` | SLR / DASHI | before/after frontier equality regression | source_written | Rust compile/test |
| mixed-orientation Pareto has no hidden 1000 bound | formal/UI/runtime frontier mismatch | direct orientation inequalities | SLR / DASHI | >1000 regression + Agda kernel | source_written | exact-head Rust/Agda receipt |
| Pareto result is explainable | `frontier=true` becomes opaque authority | concrete dominance witness | SLR | dominated/nondominated fixture | source_written | Rust fixture receipt |
| blocked frontier != dominated | authorization constraint visually interpreted as poor evidence | separate frontier-access disposition | SLR / Dioxus / DASHI | blocked-nondominated fixture | source_written | Dioxus compile/UI fixture |
| render/sort/selection do not rank | UI creates recommendation by order | stable ID order + view-only sort + no preferred/winner field | Dioxus / DASHI | projection tests | source_written | exact-head Dioxus test |
| hidden != absent | Matter/filter omission interpreted as false | world/visible/hidden counts + projection proof | Dioxus / DASHI | Matter projection fixture | source_written | scope denial fixture |
| potential reopening != actual reopening | counterfactual shown as changed assessment | PotentialReopeningCone has no mutation authority | SLR / Dioxus / DASHI | two-hop dependency fixture | source_written | actual PG update/reopen receipt |
| acquisition result cannot create source | UI/operator result manufactures evidence | source must pre-exist canonical store | SLR | live PG present-update fixture | existing INV runtime compiled; live receipt blocked by missing REL row | persist real REL/INV fixture |
| execution evidence does not decide compliance | observer data becomes control verdict | one-way StatiBaker projection | StatiBaker / SensibLaw | implemented != validated + incident tests | source_written | focused/full tests |
| CAPA cannot erase original residual | repair produces clean historical rewrite | immutable original residual/evidence refs | SensibLaw / DASHI | CAPA regression | source_written | focused/kernel receipt |
| GUI is proof-preserving read projection | Dioxus becomes mutation/authority surface | Investigate/Inspect/Graph typed projection | Dioxus / DASHI | projection + component + GPU acceptance | source_written typed model | component integration + desktop/GPU receipt |

## Verification states

Use only these evidence-state labels for GOV-1 implementation receipts:

```text
source_written
compile_checked
fixture_checked
runtime_observed
production_observed
```

And separately:

```text
proposed
implemented
verified
validated
released
observed
incident
rolled_back
```

No matrix entry may infer one axis from the other.

## Exact-head promotion checklist

- [ ] SensibLaw GOV-1 focused tests pass.
- [ ] SensibLaw full suite passes.
- [ ] StatiBaker governance evidence focused/full tests pass.
- [ ] SLR governance packet + explainable Pareto tests pass.
- [ ] SLR PG packet exact persist/reopen fixture passes.
- [ ] Agda direct-Pareto >1000, workbench projection and GOV owners kernel-check.
- [ ] Dioxus typed projection tests pass at the final SLR pin.
- [ ] Dioxus Investigate/Inspect/Graph human-facing regression passes without color-only semantics or hidden ranking.
- [ ] MatterContext denial prevents out-of-scope control/acquisition packet disclosure.
- [ ] Live INV queue/update receipt exists over a real persisted REL residual.
- [ ] REL-1C remains visibly open until independently sourced three-domain corpus acceptance actually runs.
