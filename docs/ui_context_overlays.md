# UI — Context Overlays (bands/strips/toggles)

Context overlays are read-only, non-authoritative bands shown alongside the SB
timeline. They align by time/place and must never imply causality, advice, or
priority.

## Components

- **Weather band**: thin background strip; hover reveals raw observations.
- **Market climate strip**: volatility/level shading; labelled “public market
  context (non-personal)”; no green/red profit framing.
- **Astronomy glyphs**: sunrise/sunset/moon/eclipses as small icons; optional
  day/night shading.
- **Symbolic overlay strip**: opt-in; icons/arcs only; labelled “symbolic /
  non-causal”.

## Controls

- Per-overlay toggles (default off for symbolic overlays).
- Context badge on summaries: “context included” or “context excluded”.
- Export dialog warns when dropping overlays; logs loss.

## Language guardrails

- Never emit causal terms (“caused, influenced, impacted”).
- No recommendations, alerts, or nudges from context overlays.
- Provenance shown: “This data did not come from you.”

## Layout

- Overlays sit behind/parallel to the main time axis; they do not reorder event
  importance.
- Small multiples for long horizons (seasons/years) instead of collapsing into
  one averaged band.

## Failure modes to avoid

- Blending overlays into summaries without disclosure.
- Auto-enabling symbolic overlays.
- Inferring behaviour or mood from context fields.
