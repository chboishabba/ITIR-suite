# itir-ribbon Interface Contract (Intended)

## Intersections
- Shared timeline-ribbon contract across ITIR/SB/SL/LES/DASHI surfaces.
- Consumes context and conservation inputs from upstream systems.
- Drives UI rendering and invariant checks in `SensibLaw/` integrations.

## Interaction Model
1. Load lens DSL and phase-regime definitions.
2. Compute conserved-quantity allocation across ordered segments.
3. Enforce ribbon invariants (sum, ordering, partition completeness).
4. Emit UI-contract-conformant segment payloads and diagnostics.

## Exchange Channels
### Channel A: Lens/Phase Ingress
- Input: lens JSON-AST and phase regime packs.
- Source files: `lens_dsl.md`, `lens_packs/`, `phase_regimes/`.

### Channel B: Context Envelope Ingress
- Input: timeline/context payload required to compute rho(t) allocation.
- Constraint: no context-free rendering.

### Channel C: Ribbon Model Egress
- Output: ordered segments with widths, anchors, and conservation metadata.
- Consumer: UI layers and invariant test suites.

### Channel D: Validation Egress
- Output: invariant-check results and failure diagnostics.
- Consumer: `SensibLaw/` UI tests and cross-suite QA workflows.
