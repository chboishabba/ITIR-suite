# Reviewer Packet Geometry

## Purpose

Normalize the small queue-item shape used for reviewer/operator packets so
control-plane style surfaces stop duplicating title/subtitle/detail-row/chip
normalization.

## Scope

- `SensibLaw/src/review_geometry/reviewer_packets.py`
- first adopters:
  - `SensibLaw/src/fact_intake/control_plane.py`
  - `SensibLaw/src/fact_intake/operator_views.py`

## Boundary

- in scope:
  - packet title/subtitle/description normalization
  - chips normalization
  - detail-row normalization
  - queue summary counting
- out of scope:
  - lane-specific route-target logic
  - lane-specific resolution-status policy
  - UI rendering

## Acceptance

- existing fact-intake control-plane payloads keep their meaning
- helper tests show the geometry helpers are deterministic
- control-plane summary counts still match current behavior

