# Provenance Packet Geometry

## Purpose

Normalize the small receipt/header shape that repeats across narrative
comparison, handoff artifacts, and nearby packet-style surfaces.

## Scope

- `SensibLaw/src/policy/provenance_packet_geometry.py`
- first adopters:
  - `SensibLaw/src/reporting/narrative_compare.py`
  - `SensibLaw/src/fact_intake/handoff_artifacts.py`

## Boundary

- in scope:
  - receipt kind/value rows
  - packet header normalization
  - lightweight receipt-kinds validation
- out of scope:
  - lane-specific classifier policy
  - SQL schema ownership
  - UI/report rendering

## Acceptance

- existing narrative comparison receipt shape stays stable
- handoff artifact payloads keep their current meaning
- helper tests prove deterministic geometry helpers

