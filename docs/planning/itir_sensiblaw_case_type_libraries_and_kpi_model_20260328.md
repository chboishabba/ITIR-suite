# ITIR x SensibLaw Case-Type Libraries and KPI Model (2026-03-28)

## Purpose
Define the next layer above the standard service application model:
fixed-shape case libraries plus a shared KPI model.

These libraries are not topic folders.
They are repeatable service libraries that keep the same operational shape
while varying domain rules, sensitivities, obligation patterns, and outputs.

## Main Decision
Case handling should be organized around a small set of service libraries with
one fixed shape:
- input profile
- state profile
- rule sources
- identity/trust sensitivities
- obligation patterns
- outputs
- KPIs
- escalation rules

The first four libraries supported by the current corpus are:
- tenancy
- abuse and institutional accountability
- medical and trauma-informed care
- welfare and support services

## 1. Tenancy Library
### Service purpose
Convert housing conflict into enforceable, time-bound next actions without
escalating user stress unnecessarily.

### Typical inputs
- lease or rooming status
- entry notices
- landlord or agent messages
- photos, recordings, maintenance evidence
- breach notices, tribunal forms, timelines

### State profile
- external:
  notice, access, safety defects, bond, eviction, informal tenancy status
- internal:
  fear, freeze response, shakiness, defeat, delay before replying

### Rule sources
- residential tenancy legislation
- entry and notice requirements
- repair and safety obligations
- bond and eviction pathways
- tribunal procedure

### Identity/trust sensitivities
- do not restate technical disadvantage as if it ends the matter
- do not collapse lived unfairness into formal status only
- account for coercion and selective enforcement, not just formal rights

### Core obligation patterns
- shelter security
- lawful notice
- safety remediation
- retaliatory-risk mitigation
- evidence preservation

### Standard outputs
- timeline of events
- entry-compliance check
- safety defect register
- action ladder:
  document, notify, breach, tribunal, emergency escalation

### Key failure modes
- formally right but practically unusable
- user too distressed to act
- landlord exploits ambiguity of status
- selective enforcement disappears from the formal graph

## 2. Abuse and Institutional Accountability Library
### Service purpose
Transform fragmented abuse history and cover-up evidence into
continuity-preserving legal and advocacy structure.

### Typical inputs
- personal narrative
- historical correspondence
- institutional letters
- medical and therapy records
- witness statements
- media, notes, timelines, transcripts

### State profile
- external:
  institutional actors, incidents, concealment patterns, procedural barriers
- internal:
  dissociation, shame, mistrust, retraumatization risk, memory fragmentation

### Rule sources
- civil liability
- duty of care
- vicarious liability
- obstruction and interference concepts
- compensation/redress pathways
- human-rights and convention references

### Identity/trust sensitivities
- do not force diagnosis-shaped summaries
- support tell-it-once, keep-adding continuity
- validate narrative integrity without overstating certainty

### Core obligation patterns
- secure evidence continuity
- institution-specific accountability mapping
- retraumatization-safe disclosure
- counsel-ready factual bundles
- conflict-safe chronology

### Standard outputs
- master event timeline
- institution actor graph
- duty and breach matrix
- evidence packet with provenance
- issue map for counsel or advocate

### Key failure modes
- fragmentation mistaken for unreliability
- graph becomes too tangled to use
- institutional exemptions swallow practical action
- the system becomes another invalidating voice

## 3. Medical and Trauma-Informed Care Library
### Service purpose
Bridge clinical reality, lived trauma reality, and legal-administrative
consequences.

### Typical inputs
- clinical notes
- assessment records
- medication history
- care plans
- incident records
- capacity-related documents
- patient narrative and recordings

### State profile
- external:
  diagnoses, care providers, service eligibility, capacity determinations
- internal:
  dissociation, mistrust of clinicians, prior gaslighting,
  fluctuating functioning

### Rule sources
- health service policies
- capacity and consent law
- guardianship or powers frameworks
- complaint and review mechanisms
- trauma-informed practice standards

### Identity/trust sensitivities
- avoid fixative, institution-shaped interpretation
- prefer causative, trauma-aware handling

### Core obligation patterns
- accurate trauma-aware interpretation
- continuity across providers
- non-harmful documentation
- review when misdiagnosis risk appears
- rights-preserving capacity handling

### Standard outputs
- clinical contradiction matrix
- capacity-risk note
- provider continuity map
- trauma trigger handling note
- escalation packet for complaint or advocacy

### Key failure modes
- misdiagnosis becomes canonical
- provider language is over-trusted
- passing one simple test is treated as global wellness
- records become another coercive instrument

## 4. Welfare and Support Services Library
### Service purpose
Prevent drop-to-zero-care by binding unmet needs to actors, time, and fallback
paths.

### Typical inputs
- benefit records
- housing or emergency support interactions
- caseworker notes
- intake outcomes
- messages, referrals, denials
- chronology of requests and missed handoffs

### State profile
- external:
  unmet need, provider network, handoff sequence, denial or non-response
- internal:
  collapse of trust, resignation, confusion, survival stress

### Rule sources
- welfare eligibility frameworks
- emergency support policies
- service obligations
- referral and coordination procedures
- funding and provider agreements

### Identity/trust sensitivities
- show handoff failure graphs rather than moralizing the person
- avoid ideological summaries when the real failure is coordination and
  accountability

### Core obligation patterns
- shelter
- heat or food
- continuity across providers
- fallback if one provider fails
- public/auditable accountability

### Standard outputs
- unmet need map
- provider responsibility chain
- missed handoff log
- escalation ladder
- care obligation tracker

### Key failure modes
- everyone is vaguely responsible so no one acts
- no SLA exists
- no fallback actor exists
- narrative becomes ideological instead of operational

## Shared KPI Model
The KPI model should work across all four libraries with additional
library-specific measures where needed.

### A. Service KPIs
#### Intake quality
- case completeness at first pass
- evidence source coverage
- risk classification accuracy

#### Throughput
- time from intake to structured case
- time from structured case to first actionable output
- time from first output to obligation assignment

#### User acceptance
- first-pass acceptance rate
- trust-preserving output rate
- rework due to tone or framing

### B. Quality KPIs
#### Traceability
- percentage of output claims with source provenance
- percentage of promoted facts with confidence and status
- percentage of outputs containing explicit uncertainty where needed

#### Correctness
- fact-to-rule precision
- fact omission rate
- conflict detection rate
- correction rate after review

#### Safety
- retraumatization trigger rate
- escalation to human review rate
- unsafe inference rate

### C. Obligation KPIs
#### Assignment
- percentage of unmet needs mapped to a responsible actor
- percentage of obligations with deadline
- percentage of obligations with fallback path

#### Execution
- obligation completion rate
- SLA breach rate
- escalation success rate
- silent drop rate

### D. Trust and Usability KPIs
#### Cognitive load
- user-reported effort reduction
- average number of times the story must be restated
- time saved in evidence assembly

#### Confidence
- user confidence before and after output
- rate of:
  this helps me decide what to do next
- rate of:
  this feels like another system talking at me

### E. Library-Specific KPIs
#### Tenancy
- notice compliance detection rate
- repair and safety issue capture rate
- tribunal-ready packet completion rate

#### Abuse
- chronology completeness rate
- institution actor mapping completeness
- evidence continuity retention

#### Medical
- contradiction detection rate
- capacity disagreement capture rate
- provider continuity gap detection

#### Welfare
- unmet need assignment rate
- cross-provider handoff success
- emergency need time-to-action

## Relationship To Existing Notes
This note extends:
- `docs/planning/itir_sensiblaw_standard_service_application_model_20260328.md`
- `docs/planning/itir_sensiblaw_operational_readiness_overlay_20260328.md`
- `docs/planning/itir_sensiblaw_identity_trust_alignment_layer_20260328.md`

Together they now say:
- one standard service flow
- multiple fixed-shape case libraries
- one shared KPI/control language across those libraries

## Best Next Milestone Refinement
The next bounded prototype should define:
- one selected case library
- its fixed-shape input/state/rule/obligation/output surface
- one minimal KPI slice from each shared KPI family
- one library-specific KPI slice

That is the smallest step that proves the service model can become comparable
across case families rather than only reusable in prose.
