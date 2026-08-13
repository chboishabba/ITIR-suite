# ITIR x SensibLaw PostgreSQL Schema and Deployment Bundle (2026-03-28)

## Purpose
Refine the production pack into a more execution-oriented reference bundle:
- PostgreSQL-first schema specification
- dashboard-facing operational views
- deployment topology and default stack guidance

This remains a docs-first artifact.
It does not mean the schema has been migrated or applied in the repo.

## Main Decision
Use PostgreSQL as the reference production schema, while keeping the first
runtime target local-first and single-user.

SQLite adaptation remains valid for initial single-user deployment, but the
reference production pack should be explicit enough to support later migration,
shared review surfaces, and governance dashboards.

## 1. Schema Scope
The reference schema should cover:
- tenancy and identity tables
- cases
- parties
- evidence and anchors
- extracted atoms
- identity signals and trust boundaries
- graph nodes and edges
- alignment gaps
- obligations
- output artifacts
- review decisions
- audit events
- preferences, access grants, and mode state

## 2. Production Schema Principles
- one tenant may hold many users and many cases
- every case may contain evidence, atoms, identity signals, graph records,
  obligations, outputs, and audit events
- truth state must be explicit
- mode state must be explicit
- access and sharing must be explicit
- important objects must be auditable
- sensitive content should be stored by reference where possible rather than
  duplicated throughout derived tables

## 3. PostgreSQL Reference Surface
The reference schema should include:
- extension setup:
  `pgcrypto`, `uuid-ossp`
- enumerated types for:
  case type, mode, case status, severity, party role, evidence type,
  transcript/redaction/sensitivity states, locator type, atom type,
  truth/review state, signal/stability type, trust-boundary type/severity,
  node/edge type, gap type/status, SLA class, obligation status,
  artifact/approval type, review decision, action type, access scope
- normalized core tables with foreign-key linkage and bounded indexes
- `updated_at` trigger helper for mutable tables

This should be treated as the reference logical schema, not yet as an applied
migration contract.

### 3.1 Reference SQL Pack Shape
The bounded SQL reference pack should be explicit about:
- extension setup
- enumerated types
- core table creation in dependency order
- join tables for source anchors and graph/gap/artifact linkage
- `updated_at` trigger helper plus per-table triggers
- dashboard-facing operational views

This keeps the production schema concrete enough to migrate later without
claiming that the repo has already adopted PostgreSQL as the first runtime.

### 3.2 Migration Ordering
If a first executable SQL artifact is emitted, the order should stay:
1. extensions
2. enums
3. tenancy / user tables
4. cases and parties
5. evidence and anchors
6. extracted atoms and atom-anchor joins
7. identity signals, trust boundaries, and their anchor joins
8. graph nodes/edges and edge-anchor joins
9. alignment gaps and related joins
10. obligations
11. output artifacts and artifact references
12. review / audit / preferences / access / mode state
13. `updated_at` triggers
14. dashboard-facing operational views

The first migration-ready SQL file should be ordered top-to-bottom with no
manual fix-up steps.

## 4. Core Production Tables
Reference table families:
- `tenants`
- `users`
- `cases`
- `parties`
- `evidence_items`
- `source_anchors`
- `extracted_atoms`
- `atom_source_anchors`
- `identity_signals`
- `signal_source_anchors`
- `trust_boundaries`
- `trust_boundary_source_anchors`
- `graph_nodes`
- `graph_edges`
- `edge_source_anchors`
- `alignment_gaps`
- `alignment_gap_nodes`
- `gap_source_anchors`
- `obligations`
- `output_artifacts`
- `artifact_references`
- `review_decisions`
- `audit_events`
- `user_preferences`
- `access_grants`
- `mode_states`

## 5. Operational Views
The first reference operational views should be:
- `vw_active_obligations`
- `vw_sla_breaches`
- `vw_traceability_coverage`
- `vw_open_gaps`

These are intended as dashboard and review surfaces over the same canonical
tables, not as parallel authority stores.

The minimum view intent should stay explicit:
- `vw_active_obligations`:
  current execution load by case/mode/actor
- `vw_sla_breaches`:
  obligation deadlines missed but not resolved/waived
- `vw_traceability_coverage`:
  anchored-atom coverage over current case facts
- `vw_open_gaps`:
  unresolved fact-to-rule / rule-to-action / truth-to-trust gaps

## 6. Dashboard Bundle
The production dashboard split remains:
- user dashboard
- operations dashboard
- governance dashboard

Recommended cards/widgets:
- time to first actionable output
- first-pass acceptance rate
- traceable-claim coverage
- obligation assignment rate
- SLA breach rate
- escalation success rate
- retraumatization flag rate
- story restatement count
- output usefulness score

The first dashboard bundle should remain role-bounded:
- user dashboard:
  home, next steps, case summary, evidence, privacy, strict-mode panel
- operations dashboard:
  active cases, obligations, SLA breaches, review queue, processing failures
- governance dashboard:
  traceability, unsafe inference, nonconformance, sharing/export, CAPA/audit

## 7. Deployment Bundle
### Tier 1: local device runtime
Default starting point.

Contains:
- local app shell
- mode controller
- processing / identity / graph / alignment workers
- obligation service
- output engine
- local encrypted DB/blob storage
- audit logger

### Tier 2: optional trusted sync node
Only with explicit user enablement.

Contains:
- encrypted sync store
- backup / continuity path
- artifact exchange envelope

### Tier 3: restricted collaboration node
Later profile only.

Contains:
- reviewed artifact exchange
- obligation tracking
- governance / operations dashboards for approved items

The PlantUML deployment bundle should mirror the same three-tier story:
- user device with full local runtime and encrypted evidence storage
- optional trusted sync node for encrypted continuity only
- optional reviewer workspace for approved/shared artifacts only

## 8. Storage and Security Posture
Default storage posture:
- relational tables first
- encrypted blob store for evidence
- append-only audit log
- local search index
- relational edges before heavy graph infrastructure

Default security posture:
- per-case encryption
- user-held master key
- end-to-end encrypted sync when enabled
- no default third-party escrow
- remote inference only on explicit opt-in after policy checks

## 9. Practical Default Stack
Frontend:
- desktop-first app with a web-style shell

Local services:
- processing worker
- identity worker
- graph / alignment worker
- obligation service
- audit service

Storage:
- SQLite or PostgreSQL local mode plus encrypted blobs plus edge tables

Search:
- local full-text index

Models:
- local transcription
- local extraction / summarization
- strict opt-in remote fallback only

Observability:
- local metrics store
- export-only governance logs
- no default third-party telemetry

## 10. Implementation Guidance
Do not start with the full collaboration platform.

Start with:
- local-first single-user case engine
- truth-status states
- obligation object
- dashboard surfaces for next steps, timelines, evidence, obligations,
  trust controls

That is the smallest production slice that tests whether the suite can turn
lived material into usable, trusted action without becoming another hostile
system.

## 11. Recommended Build Order
Keep the production path bounded:
1. core schema reference plus local encrypted blob store
2. case intake, evidence ingestion, extracted atoms, identity signals,
   output artifacts
3. graph nodes/edges plus alignment gaps
4. obligations plus dashboard-facing operational views
5. audit events and access grants
6. optional trusted sync and reviewer workspace

If a concrete implementation step is taken next, prefer:
- a migration-ready SQL file in execution order, or
- a local service/API spec over the same entity set

Do not widen into full collaboration workflows before the local-first
single-user slice proves usable.

## 12. Service API Surface
If an interface layer is emitted next, it should be split into:
- external REST API under `/api/v1`
- local runtime service API for on-device workers

### 12.1 REST API
The bounded REST surface should cover:
- cases:
  `POST /cases`, `GET /cases`, `GET /cases/{case_id}`
- evidence:
  `POST /cases/{case_id}/evidence`,
  `GET /cases/{case_id}/evidence`
- extraction:
  `POST /cases/{case_id}/extract`,
  `GET /cases/{case_id}/atoms`,
  `GET /cases/{case_id}/signals`
- graph/alignment:
  `GET /cases/{case_id}/graph`,
  `POST /cases/{case_id}/align`,
  `GET /cases/{case_id}/gaps`
- obligations:
  `POST /cases/{case_id}/obligations`,
  `GET /cases/{case_id}/obligations`,
  `PATCH /obligations/{id}`
- outputs:
  `GET /cases/{case_id}/next-steps`,
  `GET /cases/{case_id}/timeline`,
  `POST /cases/{case_id}/generate-document`
- mode and audit:
  `GET /cases/{case_id}/mode`,
  `POST /cases/{case_id}/mode`,
  `GET /cases/{case_id}/audit`

The REST surface should remain production-shaped but still subordinate to the
local-first runtime target.

### 12.2 Local Service API
The local runtime split should stay explicit:
- processing service:
  `ingest`, `tokenize`, `extract_atoms`
- identity service:
  `extract_signals`, `detect_trust_boundaries`
- graph service:
  `build_graph`, `query_graph`
- alignment service:
  `compute_gaps`, `detect_conflicts`
- mode controller:
  `evaluate_signals`, `select_mode`
- obligation service:
  `create_obligation`, `check_deadlines`, `escalate`
- output service:
  `generate_summary`, `generate_actions`, `generate_documents`
- governance service:
  `log_event`, `enforce_policy`, `validate_output`

The immediate next implementation artifact should still stay narrow:
either one migration-ready SQL file or one local service/API spec, not both
plus infrastructure/platform rollout at once.

## Relationship To Existing Notes
This note refines:
- `docs/planning/itir_sensiblaw_production_schema_dashboard_deployment_pack_20260328.md`
- `docs/planning/itir_sensiblaw_mode_switching_ui_and_templates_20260328.md`
- `docs/planning/itir_sensiblaw_service_architecture_plantuml_20260328.puml`

The production layer now reads as:
- service/product architecture
- mode and obligation control
- case-library and KPI model
- production schema/dashboard/deployment reference pack

The linked PlantUML bundle is the visual service map for that stack: one
context/container pack plus the compact flow and case-library variants that
show the same architecture from different operator angles.
