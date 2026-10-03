# GOV-1 exact-head verification ledger

Date: 2026-10-03

This ledger records the source-written max-cut. It does not promote any row to
compile/fixture/runtime/production evidence without an observed receipt.

| Repository | Branch / PR | GOV-1 source head | Service state | Evidence state | Observed GOV-1 verification |
|---|---|---:|---|---|---|
| SensibLaw | `agent/gov1-integrated-control-case` / PR #498 | `291f593fae4bc7fccef323fa3fcdd58a7007584d` | implemented | source_written | none yet |
| StatiBaker | `agent/gov1-execution-evidence` / PR #2 | `8ef6f63f5771e1d76f06554dec8b937fdcd1b6b0` | implemented | source_written | none yet |
| SLR | `agent/gov1-inv-control-packet` / PR #52 | `5e8d81c3b3092b0ed69f8f691bb1b5a85502be69` | implemented | source_written | none yet |
| itir-dioxus | `agent/m10-mixed-source-dual-lens` / PR #9 | `9de58188f05804389e379be6ea9a5f5c1e86913a` | implemented | source_written | none yet |
| dashi_agda | `agent/context-indexed-pnf-interlingua` / PR #1086 | `7bbc696aceea0d8fa9231ca9aeede95af732332a` | implemented | source_written | none yet |
| ITIR-suite control plan | `agent/itir-inv1-professional-investigator` / PR #18 | this ledger's commit successor | implemented | source_written | documentation only |
| ITIR-suite C4/PlantUML | `agent/gov1-control-case-uml` / PR #19 | `afcc432aeb9d03a3e449820e22edbe7465e34087` | implemented | source_written | diagram parse/render not rerun in this tranche |

## Prior receipts that remain valid but do not certify GOV-1

Before this GOV max-cut, the user reported and pushed focused certification:

- SLR REL/INV: Rust package tests passed (106 unit tests plus integration suites).
- Agda: focused REL boundary owners passed the parallel runner.
- Lean 4.28: five focused REL modules built/typechecked exit 0.
- Canonical heads were reported/pushed separately.

Those receipts establish confidence in their exact prior heads only. They do
not automatically cover the new GOV files in this ledger.

## Promotion commands / evidence to collect

### SensibLaw

```bash
pytest -q tests/policy/test_control_case.py \
  tests/policy/test_information_governance.py \
  tests/policy/test_nonconformance.py
pytest -q
```

### StatiBaker

```bash
pytest -q tests/test_statibaker_governance_evidence.py
pytest -q
```

### SLR

```bash
cargo test -p sensiblaw-pg-source-store investigation_acquisition
cargo test -p sensiblaw-pg-source-store governance_control_case
cargo test -p sensiblaw-pg-source-store
```

Then obtain a live PostgreSQL receipt only after a real persisted REL comparison/residual exists. Do not synthesize one for GOV-1.

### Agda

Kernel-check:

```text
DASHI/Core/ITIRInvestigationAcquisitionParetoExact.agda
DASHI/Core/ITIRInvestigationWorkbenchProjectionExact.agda
DASHI/Core/ITIRGovernanceControlCaseExact.agda
```

The >1000 direct-Pareto regression is part of the formal acceptance surface.

### Dioxus

At the final SLR pin:

```bash
cargo test --features production-data
cargo run --features production-data --example gov1_investigation_projection_receipt
```

Then perform desktop/HCD/GPU acceptance separately. The receipt executable must not be represented as a physical GPU receipt.

## Release gate

The suite may generate a GOV-1 control summary from these receipts only after
the exact tested heads are copied into this ledger. A green result for one
repository cannot promote another repository's evidence state.
