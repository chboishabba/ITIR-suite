# SL Observation/Claim Contracts (2026-03-27)

## Source
- Derived from `docs/planning/sl_whitepaper_followthrough_20260314.md`.
- Canonical thread: `eab13fe32136bc69aebdb9a21888b76215faab11`

## Purpose
Ratify explicit contracts for SL-facing `Observation`, `Claim`, and evidence-link
surfaces before implementation so future work does not collapse source truth into
canonical facts.

## Data objects

### 1) Observation
- Identifier: `observation_id`
- `source_unit_id`: citation-ready stable source fragment id
- `source_quote`: normalized quote text
- `source_span`: `{ start_char, end_char, start_token?, end_token? }`
- `speaker_id` + `speaker_role` (if available)
- `jurisdiction`, `certainty` (`string | null`)
- `observed_at` (`ISO-8601 | null`)
- `asserted_at` (`ISO-8601`)
- `evidence_refs`: list of deterministic source pointers
- `status`: `active | revised | withdrawn | disputed`
- `canonicality`: `raw | verified | adjudicated`
- `payload_version`: semantic contract version string
- `hash`: deterministic digest over canonicalized payload

#### Mandatory invariants
- `source_unit_id`, `source_quote`, and at least one `evidence_ref` are required
  for any `Observation` in canonical contracts.
- `status` is required and cannot be inferred from missing fields.
- `payload_version` and `hash` are required for deterministic replay.

### 2) Claim
- Identifier: `claim_id`
- `observation_id`: pointer to parent `Observation`
- `predicate`: canonical predicate key
- `subject_id` + `object_id`
- `subject_type`, `object_type`
- `norm_id` (jurisdiction-aware law or rule reference)
- `posture`: `asserted | denied | abstained`
- `evidence_quality`: `low | medium | high`
- `confidence`: numeric score (`0.0` to `1.0`) or `null`
- `claim_created_at`
- `claim_updated_at`
- `source_conflict_refs`: optional list of competing claim ids
- `evidence_links`: list of claim-level evidence link ids
- `hash`: deterministic digest over canonicalized payload

#### Mandatory invariants
- Every `Claim` must reference an existing `observation_id`.
- `predicate`, `subject_id`, and `object_id` are mandatory.
- `posture` and one of `evidence_links` / `evidence_conflicts` is required.

### 3) Evidence link
- Identifier: `link_id`
- `claim_id`
- `observation_id` or `source_unit_id`
- `link_kind`: `supporting | contradicting | neutral`
- `span_ref` (optional deterministic sub-fragment)
- `trace_refs`: receipts/notes that justify the link
- `link_hash`

#### Mandatory invariants
- `claim_id` is required.
- At least one of `observation_id` or `source_unit_id` is required.
- `link_kind` is required.

## Contracts across layers

### Canonical lane
- `Observation` and `Claim` objects are canonical data model outputs.
- `evidence_links` do not replace raw observations; they annotate evidence
  relationships deterministically.
- Any rewrite of canonical ids must preserve deterministic idempotency receipts.

### Projection lane (RDF/Wikidata)
- Projections must retain:
  - original `observation_id`
  - `source_unit_id`
  - `norm_id`
  - `jurisdiction`
  - status + provenance pointers
- Projection may be lossy on graph shape but must not lose provenance.
- For an explicit machine-readable boundary in this milestone, emit:
  - `projection_records` as evidence-preserving, reified triple rows
  - `provenance` pointers to at least `source_unit_id`, `observation status`,
    and `jurisdiction`
  - `evidence_refs` from canonical observation evidence plus deterministic
    claim links
- Boundary schema:
  - `SensibLaw/schemas/sl.observation_claim.wikidata_projection.v1.schema.yaml`
- Recommended converter:
  - `src/sl_projection_boundary.py` (`build_wikidata_projection_report`)

## Transition receipts (future slice)
- A legal reasoning transition receives:
  - `current_state`
  - one or more `Observation` ids
  - deterministic rule identifier (`rule_id`)
  - optional guard set
- Output must include:
  - `next_state`
  - `deltas`
- Both `current_state` and `next_state` references and a `transition_receipt_id`
  are mandatory.
- Transition receipts now explicitly carry:
  - `rule_version` for policy/compiler lineage
  - `jurisdiction` scope used by transition application
  - `legal_version` for law-text / rule-version tracking
  - `effective_from` and optional `effective_to` timestamps for bounded temporal
    applicability

## Acceptance criteria for Milestone R
- A shared contract document exists and is linked from
  `docs/planning/sl_whitepaper_followthrough_20260314.md`.
- `Observation` and `Claim` payloads are defined with mandatory fields and
  invariants.
- Evidence linkage is explicit and deterministic.
- Projection direction and loss constraints are specified.
- Machine-readable contract is now defined in:
  - `SensibLaw/schemas/sl.observation_claim.contract.v1.schema.yaml`
- `R.2 Contract definition` is now complete after adding a bounded,
  versioned schema artifact in the active runtime schema surface.

## Generalization target (2026-03-28 refresh)
- The current `Observation` / `Claim` seam remains the canonical near-term
  contract.
- The next broadening target is an all-sources reconciliation bundle over
  promoted observations/claims rather than a Wikidata-specific fact grammar.
- Use
  `docs/planning/all_sources_factbundle_reconciliation_boundary_20260328.md`
  as the boundary note for that future generalization.
