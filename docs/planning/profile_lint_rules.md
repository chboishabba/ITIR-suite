# Profile Lint Rules

Status: draft (2026-03-04).

Lint rules enforce profile boundaries without changing compression semantics.

References:
- `docs/planning/profile_contracts.md`
- `docs/planning/compression_engine.md`

## Global Lint Rules (All Profiles)
1. **Unanchored overlays**: error.
2. **Out-of-bounds spans**: error.
3. **Overlay introduces new characters**: error.
4. **Empty span overlays**: error.

## Profile Lint Rules (To Be Filled)
Each profile must define:
- Forbidden group IDs
- Forbidden axis IDs or values
- Forbidden overlay IDs or labels
- Warning-level rule set for advisory-only issues

## Severity Guidance
- `error`: reject overlay or payload
- `warn`: accept payload but emit lint warning
