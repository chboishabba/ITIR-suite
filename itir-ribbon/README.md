# ITIR Ribbon Module

This module defines the timeline ribbon contract, lens DSL, and phase-regime
lens packs shared across ITIR/SB/SL/LES/DASHI. It is an accounting surface: the
ribbon conserves an explicitly named quantity under the active lens and does
not encode narrative meaning.

## Contents

- `ui_contract.md`: required UI selectors and conservation checks.
- `lens_dsl.md`: JSON-AST lens DSL for defining rho(t).
- `phase_regimes.md`: shared phase vocabulary and lens packs.
- `lens_packs/`: lens definitions as JSON.
- `phase_regimes/`: phase regime packs per subsystem.

## Invariants

- Segment widths sum to 100% of the conserved quantity under the active lens.
- Segments form a complete, ordered partition of the ribbon domain.
- Lens switching reallocates width but preserves order and anchors.
- Threads do not affect width unless explicitly included by the lens.

## Related docs

- `SensibLaw/docs/timeline_ribbon.md`
- `SensibLaw/schemas/timeline.ribbon.v1.schema.json`
