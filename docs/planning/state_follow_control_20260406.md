# State-Aware Follow and Ranking Control

Date: 2026-04-06

## Purpose

Capture the bounded control surface that tells the follow/search selection layers how to weight state/local statutes, regulations, and cases versus federal ones under domain-specific contexts such as tort/compliance. This surface keeps the ruling narrow: state sources gain priority only where they explicitly apply, federal/state separation remains visible, and preemption signals are preserved.

## Rule

- When a follow obligation attaches to multiple levels (state, local, federal), boost the priority for state/local signals using a minimal additive weight (e.g., +0.8 for state, +0.6 for local). Federal references still contribute a base score so historically dominant preemption remains inspectable.
- If both federal and state are present in the same follow decision, apply a small penalty (e.g., reduce 0.1) to keep separation of sources explicit and avoid blending levels that could mask preemption requirements.
- Keep the weights deterministic so automated ranking decisions remain reproducible and traceable.

## Constraints and Preconditions

- Source annotations must plainly flag the level (state/local/federal) before the ranking layer applies this surface.
- Domain contexts such as tort/compliance must explicitly declare when they depend first on state or local authority; otherwise default to federal priority.

## Jurisdiction Fit Extension

- The same control surface now relies on the jurisdiction-fit weighting helper so international, regional, national, and domestic overlays explicitly affect the bounded outputs while maintaining inspectable separations; mixed-level contexts continue to carry a small penalty to highlight preemption sensitivities.

## Postconditions and Residual Risk

- Follow/search ranking outputs surface both the raw score and the state-aware boost, allowing downstream operators to inspect how state sensitivity affected the recommendation.
- Residual risk: without richer metadata, some mixed-level contexts still fall back to federal reasoning; future focus should collect stronger level signals before expanding the control surface.
