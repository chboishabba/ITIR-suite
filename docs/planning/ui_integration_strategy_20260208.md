# Cross-Project UI Integration Strategy (2026-02-08)

## Problem statement
The suite now has multiple renderer styles (Streamlit, Gradio, static HTML, and
planned Svelte). Team iteration cost is rising because interface ownership and
integration depth are not explicit.

## Goals
- Make every current interface discoverable from one registry.
- Let users jump directly to each native UI (including WhisperX Gradio).
- Prevent accidental authority leakage across SL/TiRC/SB/Ribbon boundaries.
- Keep frontend migration velocity high for SB componentization.

## Non-goals
- No forced single UI rewrite across all components in Sprint 10.
- No cross-component state mutation from a visual shell.
- No replacement of component-native APIs/CLIs.

## Decisions (current)
### D1: Link-hub first (ratified)
- Adopt a registry + launcher model before any deep UI federation.
- Native interfaces remain source surfaces.

### D2: SB frontend target (working)
- Use `SvelteKit + Tailwind` as working migration target for SB UI
  componentization.
- Keep React as explicit fallback only.

### D3: Federation is optional and read-only by default
- If a shared shell is added, it aggregates links/status and read-only views.
- Any authority-crossing write stays receipt-gated outside the shell.

## Phased execution
### Phase 0: Registry lockdown (now)
- Publish UI registry and machine-readable manifest.
- Wire docs index entries and TODO ownership.

### Phase 1: Launcher surface (next)
- Implement a minimal launcher page that reads
  `docs/planning/ui_surface_manifest.json`.
- Show:
  - component name
  - launch command
  - local access link/path
  - authority lane

### Phase 2: Thin federation (optional)
- Add read-only deep links from SB/SL surfaces into each other where useful.
- Keep same-tab replacement optional; default to opening native interfaces.

### Phase 3: Unified shell evaluation gate
- Only proceed if:
  - SB Svelte migration reaches parity gates.
  - UI launcher adoption is stable.
  - No authority-boundary regressions observed.

## Interaction contract for any shared shell
1. Navigation-only default:
   shell routes to native surfaces; no silent data writes.
2. Explicit source badges:
   each view labels origin (`SL`, `SB`, `TiRC`, `observer`).
3. Promotion discipline:
   shell cannot "upgrade" observer data to canonical state.
4. Replay/expandability:
   any summarized card must link back to raw IDs/artifacts.

## Sprint alignment with SB monolith split
Use `StatiBaker/docs/svelte_migration_sprint.md` as the SB-specific migration
plan and execute in parallel with link-hub rollout:

- Sprint 0/1: payload contract freeze + Svelte bootstrap + daily view parity.
- Sprint 2/3: interactive panels + weekly/lifetime routes.
- Sprint 4: backend decoupling (`dashboard.py` split) while keeping JSON as
  source contract.

## Risks and controls
- Risk: integration pressure creates hidden canonical writes.
  - Control: explicit authority lane tagging and promotion-receipt gates.
- Risk: portal becomes stale as commands/ports drift.
  - Control: manifest is versioned in repo and reviewed in refactor checklist.
- Risk: federation blocks SB migration velocity.
  - Control: keep launcher independent from SB component internals.

## Acceptance criteria
1. Registry includes all core project interface surfaces (or explicitly marks
   CLI/API-only status).
2. WhisperX Gradio URL/launch path is documented and reachable.
3. SB migration target and fallback are explicitly documented.
4. Refactor coordination + TODO entries track UI linking/integration as a
   first-class workstream.
