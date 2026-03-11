# Profile Contracts

Status: ratified for implementation slice v1 (2026-03-10).

Profile contracts define **admissibility boundaries** for a shared compression
engine. Profiles may only accept/reject overlays; they must not alter the
canonical token stream or span anchoring.

Profiles:
- `SL`: legal/norm admissibility boundaries
- `SB`: state/lifecycle/adapter admissibility boundaries
- `infra`: systems/ops admissibility boundaries

References:
- `docs/planning/compression_engine.md`
- `docs/planning/cross_profile_safety_tests.md`

## Invariants (All Profiles)
1. Canonical text is immutable.
2. Tokenization is deterministic and profile-independent.
3. Spans are identical across profiles for a given input.
4. Profiles may only filter overlays/groups/axes.

## Admissibility Scope (High-Level)
Profiles may define:
- Allowed group IDs
- Allowed axis IDs + values
- Allowed overlay IDs and labels
- Lint rules for rejections or warnings

Profiles may not define:
- Alternative tokenization rules
- Alternative span anchoring
- Profile-specific overlay generation that is not span-anchored

## Profile Rule Sets (v1)

### `sl_profile`
- Allowed groups:
  - `statute_ref`, `case_ref`, `principle_ref`, `actor_role`
- Allowed axes:
  - `jurisdiction`, `authority_level`, `modality`
- Allowed overlays:
  - `citation`, `holding`, `norm_constraint`, `actor_role`
- Explicitly forbidden:
  - groups: `system_component`, `pipeline_step`, `signal_ref`
  - axes: `hosting`, `deployment_scope`
  - overlays: `ops_label`, `incident_marker`, `metric_annotation`

### `sb_profile`
- Allowed groups:
  - `task_ref`, `actor_role`, `state_transition`, `evidence_ref`
- Allowed axes:
  - `state_phase`, `adapter_source`, `confidence_tier`
- Allowed overlays:
  - `activity_label`, `transition_label`, `evidence_link`, `receipt`
- Explicitly forbidden:
  - groups: `system_component`, `pipeline_step`, `signal_ref`
  - overlays: `ops_label`, `incident_marker`, `metric_annotation`

### `infra_profile`
- Allowed groups:
  - `system_component`, `service_ref`, `pipeline_step`, `signal_ref`
- Allowed axes:
  - `deployment_scope`, `hosting`, `severity`
- Allowed overlays:
  - `ops_label`, `incident_marker`, `metric_annotation`
- Explicitly forbidden:
  - groups: `statute_ref`, `case_ref`, `principle_ref`
  - overlays: `citation`, `holding`, `norm_constraint`

## Shared lint severities
- `error`:
  - span or payload invariants violated
  - forbidden or unknown group/axis/overlay for profile
- `warn`:
  - profile-adjacent but non-canonical metadata that can be dropped safely
