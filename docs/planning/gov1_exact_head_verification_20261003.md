# GOV-1 / INV exact-head verification ledger

Date: 2026-10-03

This ledger separates already-observed receipts from newer source-written
acceptance work. A green receipt for an older exact head never promotes a newer
branch automatically.

## Observed executable heads

| Repository | Exact head | Service state | Evidence state | Observed verification |
|---|---:|---|---|---|
| SLR `main` | `2dd32c2d2047720dc3c382191ba6164cf44d7992` | verified | fixture_checked | GOV packet 2/2; INV/Pareto 8/8 including >1000 mixed-axis and blocked-frontier; full `sensiblaw-pg-source-store` passed except explicitly ignored live-DB tests |
| StatiBaker `main` | `9d275e9bd20f4642e2704f564b27eff501e5d357` | verified | fixture_checked | GOV evidence 3/3; full suite still has two unrelated baseline failures: bundle replay drift and existing `fold_policy` allowlist guardrail |
| itir-dioxus `main` | `23323c1cfe55eb782649166c8828e9c67a8b29b4` | verified | compile_checked | production-data library compile passed at preceding GOV merge; GOV projection receipt compiled; interactive default workbench shell subsequently landed with clickable stage/coordinate selection |

These receipts do not establish a live PostgreSQL INV/GOV round-trip because
the reachable database did not contain a persisted REL comparison/residual and
no synthetic case was inserted simply to make that receipt green.

## Current source-written acceptance heads

| Repository | Branch / PR | Exact source head | Service state | Evidence state | Remaining promotion gate |
|---|---|---:|---|---|---|
| SLR | `agent/inv-case-persisted-rel-gov` / PR #53 | `413b46862e7760b9020ec0bb2027eb5bc81169bf` | implemented | source_written | compile/tests, then run against a real persisted REL residual; graph binding additionally requires an existing persisted legal-follow projection |
| itir-dioxus | `agent/inv-workbench-visible-projection` / PR #10 | `7636bc550d1b61f995fe907d9f752a77b2160575` | implemented | source_written | regenerate Cargo lock against SLR PR #53; production-data compile/tests; visible desktop acceptance; bound-graph receipt only when real graph data exists |
| dashi_agda | `agent/context-indexed-pnf-interlingua` / PR #1086 | `7bbc696aceea0d8fa9231ca9aeede95af732332a` | implemented | source_written | exact-head kernel check for direct mixed Pareto, >1000 specimen, GUI and GOV firewalls |
| SensibLaw | `agent/gov1-integrated-control-case` / PR #498 | `291f593fae4bc7fccef323fa3fcdd58a7007584d` | implemented | source_written | focused/full policy tests on its current exact head |
| ITIR-suite C4 | `agent/gov1-control-case-uml` / PR #19 | `afcc432aeb9d03a3e449820e22edbe7465e34087` | implemented | source_written | render/lint if promotion requires a diagram receipt |

## What PR #53 adds without fabricating data

`itir_inv1_governed_case` starts only from an already-persisted REL comparison
and a residual already owned by that comparison. It derives the exact parent
source revisions from the durable REL record, persists/reopens the INV queue and
GOV packet, and can optionally record a separately completed acquisition result
only after the acquired source was already ingested through its native adapter.

`InvestigationGraphBinding` is an immutable lower-authority binding from one
persisted INV obligation to one already-persisted `legal_follow` projection.
Persistence verifies the existing graph contract:

```text
projection_kind = legal_follow
authority_ceiling = derived_only_challengeable
promotion_allowed = false
execution_allowed = false
```

The binding creates no nodes, edges, semantic authority, access authority or
acquisition state. `itir_inv1_bind_graph` only persists/reopens that binding.

## What PR #10 adds without synthesising a graph

The visible acquisition route now consumes the typed Investigate / Inspect /
Graph projection. The generic workbench remains the no-data fallback.

Graph mode has two honest states:

1. no persisted binding -> explicit "no graph bound" view; counterfactual
   reopening refs may still be inspected but are labelled **not a graph**;
2. persisted binding -> SLR reopens the existing legal-follow projection,
   Dioxus re-checks all graph source refs through the current MatterContext,
   then projects exactly those persisted nodes/edges into `GraphIr`.

`GraphIr` geometry is presentation-only. Selection reopens existing
source/provenance refs and cannot change review, truth, access or acquisition
state.

## Exact next receipts

### SLR PR #53

```bash
cargo test -p sensiblaw-pg-source-store investigation_graph_binding
cargo test -p sensiblaw-pg-source-store investigation_acquisition
cargo test -p sensiblaw-pg-source-store governance_control_case
cargo test -p sensiblaw-pg-source-store
cargo run -p sensiblaw-pg-source-store --example itir_inv1_governed_case -- <real-case.json>
```

Only after a real graph already exists:

```bash
cargo run -p sensiblaw-pg-source-store --example itir_inv1_bind_graph -- <real-binding.json>
```

### Dioxus PR #10

First regenerate the lock from the exact SLR PR #53 pin; do not hand-edit git
package hashes.

```bash
cargo test --features production-data --test investigation_projection_modes
cargo test --features production-data investigation_graph
cargo check --features production-data --lib
cargo run --features production-data --example gov1_investigation_projection_receipt
```

Only when an actual graph binding exists:

```bash
cargo run --features production-data --example inv1_graph_projection_receipt
```

Desktop/HCD and physical GPU acceptance remain separate evidence dimensions.
A GraphIr receipt is not a GPU receipt.

### Agda PR #1086

Kernel-check:

```text
DASHI/Core/ITIRInvestigationAcquisitionParetoExact.agda
DASHI/Core/ITIRInvestigationWorkbenchProjectionExact.agda
DASHI/Core/ITIRGovernanceControlCaseExact.agda
```

## Release gate

The next meaningful promotion is not another architecture document. It is one
real persisted case producing the chain:

```text
SourceRevision
-> RelationalComparison
-> Residual
-> AcquisitionObligation
-> GovernancePacket
-> separately acquired canonical SourceRevision
-> SelectiveReopening
-> persisted proof/dependency graph
-> InvestigationGraphBinding
-> Matter-authorised GraphIr projection
```

No link in that chain may be inferred merely because the next product surface
would look more complete.
