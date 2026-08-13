# Profile Lint Rules

Status: ratified for implementation slice v1 (2026-03-10).

Lint rules enforce profile boundaries without changing compression semantics.

References:
- `docs/planning/profile_contracts.md`
- `docs/planning/compression_engine.md`

## Global Lint Rules (All Profiles)
1. **Unanchored overlays**: error.
2. **Out-of-bounds spans**: error.
3. **Overlay introduces new characters**: error.
4. **Empty span overlays**: error.

## Profile Lint Rules (v1)

### `sl_profile` lint rules
- `error` on:
  - infrastructure-only group ids (`system_component`, `pipeline_step`, `signal_ref`)
  - infrastructure-only axes (`hosting`, `deployment_scope`)
  - infrastructure-only overlays (`ops_label`, `incident_marker`, `metric_annotation`)

### `sb_profile` lint rules
- `error` on:
  - infrastructure-only group ids (`system_component`, `pipeline_step`, `signal_ref`)
  - infrastructure-only overlays (`ops_label`, `incident_marker`, `metric_annotation`)
- `warn` on:
  - legal-only overlays (`citation`, `holding`, `norm_constraint`) when encountered in mixed imports

### `infra_profile` lint rules
- `error` on:
  - legal-only group ids (`statute_ref`, `case_ref`, `principle_ref`)
  - legal-only overlays (`citation`, `holding`, `norm_constraint`)
- `warn` on:
  - SB lifecycle overlays not mapped to infra state contracts

## Severity Guidance
- `error`: reject overlay or payload
- `warn`: accept payload but emit lint warning
