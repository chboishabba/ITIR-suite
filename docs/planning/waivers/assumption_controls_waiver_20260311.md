# Assumption Control Waiver Receipt (2026-03-11)

Scope: `A1`, `A3`, `A4`, `A5`, `A6`, `A9`, `A10`.

Reason:
- These controls remain open implementation tracks and are explicitly tracked in
  top-level `TODO.md`.
- CI must fail closed if any unresolved control is removed from this receipt or
  loses registry linkage.

Expiry/Review:
- This waiver must be reviewed whenever any listed control changes from
  `waived` to `implemented` in
  `docs/planning/assumption_controls_registry.json`.

Trace:
- Source stress register:
  `docs/planning/assumption_stress_test_20260208.md`
- Registry:
  `docs/planning/assumption_controls_registry.json`
