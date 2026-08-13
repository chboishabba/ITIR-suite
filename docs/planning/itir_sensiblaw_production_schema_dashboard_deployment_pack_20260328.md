# ITIR x SensibLaw Production Schema, Dashboard, and Deployment Pack (2026-03-28)

## Purpose
Define the next production-facing contract layer for ITIR/SensibLaw:
- core runtime entities
- dashboard and monitoring surfaces
- local-first deployment topology

This note is still docs-first.
It does not introduce runtime behavior yet.

## Design Principles
The production shape should satisfy seven constraints:
- every user-visible claim is traceable to evidence
- the system distinguishes candidate, promoted, disputed, and abstained states
- external facts are separated from internal state
- obligations are first-class
- all schemas support local-first storage with optional later sync
- every mutation is auditable
- trust-sensitive fields support restricted visibility because misuse of
  structured truth can itself be harmful

## Core Entity Set
The first production entity inventory is:
- `Case`
- `Party`
- `EvidenceItem`
- `SourceAnchor`
- `ExtractedAtom`
- `IdentitySignal`
- `TrustBoundary`
- `GraphNode`
- `GraphEdge`
- `AlignmentGap`
- `Obligation`
- `OutputArtifact`
- `ReviewDecision`
- `AuditEvent`
- `UserPreference`
- `AccessGrant`
- `ModeState`

## 1. Core Schemas
### 1.1 `Case`
Purpose:
container for one user situation, whether everyday or high-risk.

Fields:
- `case_id`
- `tenant_id`
- `case_type`
- `mode`
- `status`
- `severity`
- `created_at`
- `updated_at`
- `owner_user_id`
- `assigned_reviewer_id`
- `summary`
- `primary_need`
- `desired_outcome`
- `jurisdiction`
- `due_date`
- `retention_policy`
- `encryption_profile`

Enumerations:
- `case_type`:
  tenancy, abuse, medical, welfare, workplace, communication, planning, custom
- `mode`:
  light, hybrid, strict
- `status`:
  intake, structuring, alignment, action_ready, monitoring, escalated, closed
- `severity`:
  low, medium, high, critical

### 1.2 `Party`
Purpose:
represents any actor involved.

Fields:
- `party_id`
- `case_id`
- `role`
- `display_name`
- `legal_name`
- `organization_name`
- `contact_methods`
- `trust_level`
- `adverse_flag`
- `notes`
- `visibility_scope`

Enumerations:
- `role`:
  user, advocate, lawyer, clinician, landlord, institution, provider,
  witness, reviewer, unknown

### 1.3 `EvidenceItem`
Purpose:
canonical record for uploaded or captured material.

Fields:
- `evidence_id`
- `case_id`
- `evidence_type`
- `source_uri`
- `local_blob_ref`
- `content_hash`
- `capture_time`
- `author_party_id`
- `device_metadata`
- `transcript_status`
- `redaction_status`
- `sensitivity`
- `chain_of_custody`
- `summary`
- `extracted_text_ref`

Enumerations:
- `evidence_type`:
  audio, transcript, email, pdf, image, note, message, form, medical_record,
  timeline_entry
- `transcript_status`:
  none, pending, complete, verified
- `redaction_status`:
  none, suggested, applied, reviewed
- `sensitivity`:
  ordinary, confidential, trauma_sensitive, legally_sensitive,
  medical_sensitive

### 1.4 `SourceAnchor`
Purpose:
precise provenance for any structured claim.

Fields:
- `anchor_id`
- `evidence_id`
- `locator_type`
- `start_offset`
- `end_offset`
- `page`
- `line_start`
- `line_end`
- `timestamp_start`
- `timestamp_end`
- `quote_excerpt`
- `confidence`

### 1.5 `ExtractedAtom`
Purpose:
smallest structured unit from the external compiler.

Fields:
- `atom_id`
- `case_id`
- `atom_type`
- `subject_party_id`
- `predicate`
- `object_value`
- `object_party_id`
- `normalized_value`
- `time_ref`
- `location_ref`
- `source_anchor_ids`
- `confidence`
- `truth_status`
- `rule_refs`
- `review_state`

Enumerations:
- `atom_type`:
  event, notice, obligation, breach, statement, diagnosis, symptom, payment,
  threat, request, refusal, appointment, timeline_marker
- `truth_status`:
  candidate, promoted, disputed, abstained, withdrawn
- `review_state`:
  auto_only, pending_human, reviewed, locked

### 1.6 `IdentitySignal`
Purpose:
smallest structured unit from the internal compiler.

Fields:
- `signal_id`
- `case_id`
- `signal_type`
- `subject_party_id`
- `description`
- `source_anchor_ids`
- `confidence`
- `stability`
- `sensitivity`
- `review_state`

Enumerations:
- `signal_type`:
  friction, overload, freeze_response, avoidance, confidence_drop, trust_loss,
  dissociation_risk, moralization_trigger, restatement_burden, goal,
  coping_pattern
- `stability`:
  transient, recurring, persistent, unknown

### 1.7 `TrustBoundary`
Purpose:
captures what makes output acceptable or rejectable.

Fields:
- `boundary_id`
- `case_id`
- `party_id`
- `boundary_type`
- `rule`
- `severity`
- `source_anchor_ids`
- `active_flag`

Enumerations:
- `boundary_type`:
  tone, privacy, bias, diagnosis, ideology, surveillance, sharing, overreach,
  certainty
- `severity`:
  soft, medium, hard

### 1.8 `GraphNode` and `GraphEdge`
`GraphNode` fields:
- `node_id`
- `case_id`
- `node_type`
- `label`
- `canonical_ref`
- `payload_ref`
- `truth_status`
- `visibility_scope`

`GraphEdge` fields:
- `edge_id`
- `case_id`
- `edge_type`
- `from_node_id`
- `to_node_id`
- `direction`
- `source_anchor_ids`
- `confidence`
- `truth_status`

Node types:
- fact, person, organization, obligation, need, event, issue, diagnosis,
  provider, legal_rule, trust_factor

Edge types:
- caused_by, stated_by, linked_to, breaches, satisfies, escalates_to,
  disputes, supports, contradicts, assigned_to, due_by

### 1.9 `AlignmentGap`
Purpose:
represents the gap function in computable form.

Fields:
- `gap_id`
- `case_id`
- `gap_type`
- `related_node_ids`
- `severity`
- `explanation`
- `suggested_resolution`
- `source_anchor_ids`
- `status`

Enumerations:
- `gap_type`:
  fact_to_rule, rule_to_action, truth_to_trust, continuity, evidence_missing,
  actor_unassigned, deadline_missing, conflict_unresolved

### 1.10 `Obligation`
Purpose:
the execution primitive.

Fields:
- `obligation_id`
- `case_id`
- `need_node_id`
- `responsible_party_id`
- `fallback_party_id`
- `required_action`
- `deadline_at`
- `sla_class`
- `status`
- `trigger_reason`
- `evidence_basis`
- `escalation_policy_id`
- `completion_notes`
- `completed_at`
- `breached_at`

Enumerations:
- `sla_class`:
  informational, routine, urgent, critical
- `status`:
  proposed, active, in_progress, completed, breached, waived, disputed

### 1.11 `OutputArtifact`
Purpose:
anything shown or exported to users.

Fields:
- `artifact_id`
- `case_id`
- `artifact_type`
- `mode`
- `title`
- `summary`
- `payload_ref`
- `generated_from_refs`
- `trust_safety_profile`
- `approval_state`
- `shared_with`
- `created_at`

Artifact types:
- next_steps, timeline, message_draft, complaint_packet, duty_matrix,
  unmet_need_map, contradiction_matrix, escalation_notice

### 1.12 `ReviewDecision`
Purpose:
human review and correction loop.

Fields:
- `review_id`
- `case_id`
- `target_type`
- `target_id`
- `reviewer_party_id`
- `decision`
- `rationale`
- `changes_applied`
- `created_at`

Decisions:
- approve, reject, amend, abstain, escalate

### 1.13 `AuditEvent`
Purpose:
traceability and accountability.

Fields:
- `event_id`
- `tenant_id`
- `case_id`
- `actor_id`
- `action_type`
- `target_type`
- `target_id`
- `old_value_ref`
- `new_value_ref`
- `mode_at_time`
- `created_at`
- `signature_ref`

### 1.14 `AccessGrant`
Purpose:
selective sharing without breaking sovereignty.

Fields:
- `grant_id`
- `case_id`
- `grantee_party_id`
- `scope`
- `object_refs`
- `expires_at`
- `granted_by`
- `revoked_at`

### 1.15 `ModeState`
Purpose:
stores why the system is in light, hybrid, or strict mode.

Fields:
- `mode_state_id`
- `case_id`
- `selected_mode`
- `risk_score`
- `time_pressure_score`
- `conflict_score`
- `evidence_completeness_score`
- `user_state_score`
- `override_by_user`
- `override_reason`
- `effective_from`
- `effective_to`

## 2. Dashboard and Monitoring UI
### 2.1 Dashboard architecture
Use three layers:
- user dashboard
- review and operations dashboard
- quality and governance dashboard

### 2.2 User dashboard
Light-first by default.

Home panel:
- what this looks like
- what matters
- what to do next
- current mode
- urgent deadlines

Case panel:
- case summary
- timeline
- evidence count
- unresolved questions
- trust notes
- obligations if in hybrid or strict

Next-step panel:
- one to three recommended actions
- effort level
- expected outcome
- deadline if applicable

Evidence panel:
- documents
- transcripts
- anchors
- redaction state

Privacy panel:
- local only
- shared with lawyer
- shared with clinician
- revoke access

### 2.3 Operations dashboard
Audience:
reviewers, advocates, service operators

Widgets:
- active cases by type
- mode distribution
- cases breaching SLA
- unassigned needs
- review queue
- disputes and abstentions
- evidence processing failures
- mode override frequency

### 2.4 Governance dashboard
Audience:
quality, compliance, service owners

Widgets:
- traceability coverage
- nonconformance count
- unsafe inference rate
- trust rejection rate
- breach-to-escalation lag
- correction turnaround
- local-only compliance rate
- export and sharing events

### 2.5 KPI cards
Recommended KPI cards:
- time to first actionable output
- first-pass acceptance rate
- traceable-claim coverage
- obligation assignment rate
- SLA breach rate
- escalation success rate
- retraumatization flag rate
- story restatement count
- output usefulness score

### 2.6 UX guidance
For normal users:
- default to light mode
- no graph first

For advanced users:
- allow structured views:
  timeline, rule map, obligation table, provenance table

For high-risk users:
- strict mode should emphasize:
  actor, deadline, fallback, escalation

## 3. Local-First Deployment Mapping
### 3.1 Deployment goals
The production posture should preserve:
- local sovereignty
- strong privacy for sensitive trauma, legal, and medical material
- graceful progression from ordinary guidance to strict, auditable case
  management

### 3.2 Recommended topology
#### Tier 1: local device runtime
Runs on the user machine by default.

Components:
- input interface
- mode controller
- processing engine
- identity engine
- local graph engine
- local output engine
- local encrypted store

Use for:
- all ordinary cases
- all sensitive preprocessing

#### Tier 2: optional trusted sync node
Only if explicitly enabled.

Components:
- encrypted backup
- key-split recovery option
- multi-device sync
- reviewer exchange envelope

Use for:
- continuity, not default analysis

#### Tier 3: restricted collaboration node
Separate deployment profile for advocates or teams.

Components:
- reviewed artifact exchange
- obligation tracking
- shared audit log for approved items only

Use for:
- lawyer, clinician, caseworker collaboration after explicit grant

### 3.3 Storage model
Local storage:
- encrypted relational store for entities and metadata
- encrypted blob store for evidence
- local search index
- local graph store

Practical starting stack:
- SQLite or single-user Postgres mode for relational entities
- local object/blob store
- relational edges first rather than a heavy graph platform
- append-only audit log

### 3.4 Encryption model
At rest:
- per-case encryption key
- per-user master key
- hardware-backed storage where available

In motion:
- all sync end-to-end encrypted
- server never sees plaintext case content
- only artifact-specific sharing grants expose selected items

Key model:
- master key held locally
- optional user-controlled recovery splits
- no default third-party escrow

### 3.5 Processing model
Default:
- extraction and alignment run locally

Optional:
- only de-identified or user-approved artifacts may leave the device

Model execution:
- local transcription, extraction, summarization where possible
- remote inference only on explicit opt-in and after redaction-policy check

### 3.6 Deployment environments
- personal desktop:
  full local pipeline, good for power users and advocates
- laptop-only:
  lightweight inference, defer heavy jobs
- family/caregiving:
  separate case spaces, strict access grants, visible sharing audit
- professional workstation:
  reviewed artifact sharing, obligation tracking, governance dashboard

### 3.7 Operational controls
ITIL-aligned:
- incident queue for urgent harm or deadline cases
- problem queue for recurring extraction or trust failures
- change control for rule and prompt updates
- knowledge articles from reviewed patterns

ISO-aligned:
- document control for schemas and rule packs
- nonconformance log
- CAPA workflow
- periodic acceptance review

Six Sigma-aligned:
- defect logging by class
- control charts for acceptance, breach, correction, rejection
- root-cause tagging:
  tone, evidence gap, mapping error, privacy issue, delay

### 3.8 Deployment phases
Phase 1:
- local-first single-user desktop
- cases, evidence, atoms, outputs, manual review
- no sync by default

Phase 2:
- local-first multi-device encrypted sync
- access grants
- reviewed artifact sharing
- dashboard and monitoring

Phase 3:
- professional collaboration
- obligation workflows
- SLA tracking
- escalation routing
- governance dashboard

## 4. Practical Default Stack
Frontend:
- desktop-first app with a web-style shell

Local services:
- processing worker
- identity worker
- graph/alignment worker
- obligation service
- audit service

Storage:
- SQLite plus encrypted blobs plus edge tables

Search:
- local full-text index

Models:
- local transcription
- local extraction and summarization
- strict opt-in for remote fallback

Observability:
- local metrics store
- export-only governance logs
- no default third-party telemetry

## 5. Final Recommendation
Do not start with the full collaboration platform.

Start with:
- local-first single-user case engine
- truth-status states
- obligation object
- dashboard with:
  next steps, timelines, evidence, obligations, trust controls

That validates the hardest requirement first:
whether the system can convert lived material into usable, trusted action
without becoming another hostile system.
