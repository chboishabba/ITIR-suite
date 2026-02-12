# Evidence Promotion Contract v1 (Deterministic, Truth/View Split)

Date: 2026-02-12  
Status: Active draft for AAO/HCA/GWB graph surfaces  
Origin (provenance only, no fetch in this step): `698bdf6e-43f8-839c-9089-34ee3d3338dd`

## Purpose
Define how evidence/sourcing signals are attached to extracted AAO propositions without polluting actor/action/object truth lanes.

## Core boundary
- Truth layer:
  - `subjects`, `action`, `entity_objects`, `modifier_objects`, `modifiers`, `chains`.
  - Sentence-local and frame-scoped only.
- Evidence layer:
  - `citations[]`, `sl_references[]`, optional evidence/support links between frames.
  - Never rewrites truth roles.
- View layer:
  - May render evidence as a separate lane/edge family (`kind=evidence`).
  - May hide/show evidence edges without changing truth payloads.

## Deterministic triggers
- Evidence signals are read from structured fields:
  - `citations[].text`
  - `sl_references[].text` (or authority/ref fallback)
- No semantic regex for actor/action inference.
- Regex remains acceptable for citation token parsing and text hygiene only.

## Edge families
- `role`: subject/requester to action, action to object.
- `sequence`: time chain and/or step progression.
- `evidence`: action to citation/sl-reference evidence nodes.

## Invariants
- Evidence edges are overlay-only:
  - do not affect layout ordering semantics,
  - do not affect node->fact scope validation,
  - do not add subjects/objects to a frame.
- Every rendered evidence node must be traceable to event-local `citations[]` or `sl_references[]`.
- Frame scope must remain explicit (`event_id`/`fact_id` lineage).

## UI contract (AAO-all initial slice)
- Add optional evidence lane in AAO-all graph:
  - Evidence nodes sourced from event `citations[]` + `sl_references[]`.
  - Edges from `act:<event_id>` to evidence nodes with `kind=evidence`.
- Add toggle: show/hide evidence edges.
- Keep default graph stable with evidence hidden by default.

## Follow-up (not in this patch)
- Add explicit evidence frame types (`EVIDENCE`, `ASSERTION`, `REASONING`) in payload generation.
- Add cross-frame evidence links (`SUPPORTS`, `ATTRIBUTED_TO`, `CITES_SAME_RECORD`) with basis metadata.
- Add UI distinction for edge subtypes inside evidence family.
