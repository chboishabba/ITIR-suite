# GOV-1 Integrated Control Case Design

Date: 2026-10-03
Status: approved design distilled from the attached GUI/governance formalism

## Goal

Add one suite-wide engineering-governance control plane over StatiBaker, SensibLaw, ITIR/REL/INV, operator UIs, and DASHI formal owners without creating a second semantic authority or implying standards certification.

The canonical trace is:

```text
User story
-> requirement
-> risk
-> control
-> implementation
-> evidence
-> residual / CAPA
-> release state
```

Standards are engineering-control provenance and design lenses, not certification claims.

## Authority allocation

- **SensibLaw** owns the canonical control-profile, control-case and compliance-evaluation runtime.
- **StatiBaker** supplies execution/service evidence and retains its sequence-first, non-semantic authority boundary.
- **SLR** binds REL/INV runtime objects to governance/control evidence, without becoming the suite compliance authority.
- **Dioxus/Svelte** expose governed projections only. Selection, sorting, filtering and display order do not create preference, evidence, authority or truth.
- **DASHI Agda/Lean** prove the authority, projection, Pareto and non-promotion firewalls that are mathematical.
- **ITIR-suite** owns cross-repository roadmap/user-story/C4 documentation and acceptance matrices.

## Control case

Canonical conceptual carrier:

```text
ControlCase = (
  obligation/control,
  scope/context,
  accountable owner,
  risk addressed,
  implementation/control mechanism,
  evidence/receipt,
  nonconformance/residual
)
```

Control cases distinguish at minimum:

- `satisfied`
- `partial`
- `failed`
- `insufficient_evidence`
- `not_applicable`

A passing test is evidence for a named control; it is not itself a certification or a universal conformance claim.

## Portable control families

The shared profile extends the existing SensibLaw control machinery with these families:

- authority and provenance — ISO 9001 / ISO/IEC 42001
- requirements and acceptance — ISO 9001 / Six Sigma
- AI intended use and lifecycle — ISO/IEC 42001
- AI risk — ISO/IEC 23894 / NIST AI RMF
- information security — ISO/IEC 27001
- privacy information management — ISO/IEC 27701
- access and scope — ISO/IEC 27001 / 27701
- human oversight — ISO/IEC 42001 / NIST AI RMF
- uncertainty/non-promotion — ISO/IEC 42001 / 23894 / NIST AI RMF
- service configuration/change/release/incident/problem — ITIL
- CAPA/defect reduction — ISO 9001 / Six Sigma
- usability/HCD/UI semantics/accessibility — ISO 9241-110, 9241-161, 9241-210, 9241-171, ISO 24552, ISO 24505-1/-2, ISO 22727
- deployment/display/environment context — ISO 9241-306 / ISO 16817
- architecture traceability — C4 / PlantUML

## Service and evidence state

Implementation state and evidence strength remain orthogonal.

```text
ServiceChangeState =
  proposed | implemented | verified | validated | released | observed | incident | rolled_back

EvidenceState =
  source_written | compile_checked | fixture_checked | runtime_observed | production_observed
```

No state may silently promote another.

## Security/privacy lifecycle

MatterContext remains the visibility decision owner. It is supplemented, not replaced, by explicit information-processing metadata:

```text
InformationAsset:
  asset_ref
  data_class
  contains_pii
  sensitivity
  accountable_role
  purpose_ref
  matter_ref
  access_basis_ref
  allowed_consumer_refs
  storage_ref
  external_provider_refs
  retention_class_ref
  revocation_or_deletion_state
  audit_refs

ProcessingActivity:
  activity_ref
  purpose_ref
  input_asset_refs
  output_asset_refs
  processor_role_ref
  external_provider_refs
  control_refs
  evidence_refs
```

## INV-1 proving case

Every acquisition route retains the existing non-scalar merit vector `(I,D,C,N,L)` and gains a separate governance envelope. Governance is never folded into a priority score.

```text
AcquisitionGovernance = (
  purpose,
  authorization/access,
  privacy,
  security,
  AI-risk/intended-use,
  service/evidence state,
  control/evidence refs
)
```

A route can be Pareto admissible while operationally non-executable.

## GUI projection contract

The investigation GUI is a proof-preserving Matter-scoped projection.

Required firewalls:

- visible route implies a real persisted route;
- hidden/filtered route does not imply absent/false;
- selected does not imply preferred;
- first/rendered-first does not imply best;
- sorting by an axis does not alter the Pareto frontier;
- blocked does not imply dominated;
- executable does not imply Pareto-admissible;
- frontier membership does not grant authorization;
- potential reopening does not equal actual reopening;
- UI navigation/actions cannot create source evidence or semantic authority.

The default interaction is obligation-first:

```text
unresolved question / residual
-> why unresolved
-> useful next evidence
-> Pareto trade-off explanation
-> access/provenance/genealogy
-> potential reopening cone
-> optional exact graph/provenance inspection
```

The GUI separates:

1. **Investigate** — human explanation of unresolved coordinate, frontier trade-offs, access state and potential reopening.
2. **Inspect** — exact source revisions, residual refs, receipts, genealogy and dependency path.
3. **Graph** — optional power view; never the default semantic authority.

Frontier and executable-frontier are distinct types. Dominated alternatives remain inspectable but are not rendered as inferior evidence.

## Pareto formalism correction

The current Agda `1000 ∸ gain` encoding can saturate for gain values above 1000. GOV-1 must not claim UI/formal frontier equality while that hidden bound exists.

The formal owner must either:

- prove a declared upper bound before using the loss embedding, or
- use direct mixed-orientation dominance matching the Rust runtime.

The preferred long-term owner is direct mixed-orientation dominance.

## Six Sigma / CAPA

Use DMAIC only as a precise engineering loop:

```text
Define  -> consumer-visible defect / requirement
Measure -> exact residual / evidence vector
Analyse -> dependency/root-cause trace
Improve -> bounded repair/change
Control -> regression/no-regression evidence
```

Typed nonconformities include semantic mismatch, provenance loss, authority leak, scope leak, privacy exposure, security-boundary violation, UI ambiguity, replay nondeterminism, performance regression and hidden-work amplification.

## NIST AI RMF mapping

- Govern: authority, acquisition policy, security/privacy, accountable humans.
- Map: user, matter, consumer, affected persons/context, provenance.
- Measure: residuals, unsupported premises, source dependence, false joins, abstention/calibration, UI misunderstandings.
- Manage: block, qualify, request evidence, selectively reopen, rollback, incident/problem/CAPA.

## C4 / PlantUML

One authoritative suite architecture view should include:

- source acquisition
- canonical evidence
- parser/PNF
- REL
- INV
- S29 review
- S30 MatterContext
- GOV-1 control case
- Dioxus/Svelte read projections
- StatiBaker execution memory
- formal verification

Trust/control annotations should identify at least semantic authority, review authority, read projection, PII boundary and external provider boundary.

## Non-goals

- No claim of ISO/ITIL/NIST certification.
- No weighted governance score.
- No second semantic compiler, review authority or compliance engine.
- No UI-created evidence, source truth, acquisition authority or claim truth.
- No automatic PII inference beyond explicitly supplied/validated metadata.
- No broad two-way synchronization merely to make governance dashboards look complete.
