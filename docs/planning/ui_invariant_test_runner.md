# UI Invariant Test Runner Template

This template is a minimal checklist for manual or scripted UI verification.

## Pre-Run
- Load fixture: `docs/planning/context_envelope_fixtures.json`
- Ensure context envelope validation is enabled.
- Enable a "context-free render" attempt path for negative testing.

## Test Runs

### Run A: Context-Free Rendering
- Action: open artifact by deep link.
- Expected:
  - Context strip visible.
  - Warning if any envelope field is missing.
  - Render blocked if envelope absent.

### Run B: Context Removal Gate
- Action: attempt export without context.
- Expected:
  - Modal shown.
  - Default export includes full context.
  - Any context removal is logged.

### Run C: Epistemic Slider Integrity
- Action: drag slider between "Known Then" and "Known Now".
- Expected:
  - Later facts only appear in "Known Now".
  - "Known Then" view remains unchanged.

### Run D: Context Drift Warning
- Action: open artifact outside original venue.
- Expected:
  - Drift warning overlay displayed.
  - User acknowledgement required.

### Run E: Interpretation Optional Mode
- Action: disable interpretation overlays.
- Expected:
  - Only artifacts and relationships render.
  - No narrative summaries appear.
