# Polity-Aware Follow/Ranking Control Snapshot

Date: 2026-04-07

## Purpose

Tie the new polity-aware scoring surface into bounded outputs, ensuring parent authorities (EU, RU), sub-jurisdiction implementers (member states, constitutional courts), and adjudication layers share a transparent ranking bias without collapsing levels.

## Guidance

- Weighted overlays now emit both the base follow priority and the polity-aware boost so downstream operator views can inspect macro vs. sub-level leverage cases.
- Penalties keep mixed international-domestic contexts visible and avoid sneaking preemption/policy overrides through the ranking layer.
- Ordered scenarios: EU→member-state, RU→constitutional court→national court, PIF→member-state; each step adds the weight from `polity_follow_control` and surfaces the score on the control artifact.

## Tests

- `SensibLaw/tests/test_polity_follow_control.py` validates the weighting for the EU/member-state pair, the constitutional/national boost, and regional-only cases.

## Residual Risks

- Without broader fixture coverage, the macro→sub-jurisdiction ladders still rely on consistent metadata; future work should expand the fixture set before generalizing further.
