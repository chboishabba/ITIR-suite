# GWB Cross-Document Event Braid

Date: 2026-07-05

## Purpose

Define the next substrate after event-lineage preservation:

`local source events -> cross-source event reconciliation -> partial-order timeline braid`

GWB is the current proving ground, but the capability is not GWB-owned.

The likely long-term generic owner is a shared cross-source event/timeline
adapter layer that later lane/profile wrappers can prefill.

## Problem

The current GWB stack can now preserve:

`source -> event -> relation -> review -> receipt`

for at least some broader-review rows.

What it does not yet do is reconcile event windows across documents into a
shared event substrate. Today the system is still too close to:

- one document family
- one local extraction pass
- one review-effective merged relation surface

rather than:

- many source documents
- many local event windows
- explicit cross-document overlap/reconciliation edges
- one source-backed partial-order event graph

## Target Shape

The intended shape is:

`document-local event extraction`
`-> event/source/span/citation anchors`
`-> cross-document event identity and overlap reconciliation`
`-> partial-order timeline braid`
`-> broader-review rows that preserve braid lineage`
`-> projected linkage case and receipt`

This is not a prose merge. It is a typed graph.

## Core Example

If one source gives:

`A -> B -> C -> D`

and another gives:

`C -> D -> E -> F`

the system should be able to preserve:

- document-local event rows for both chains
- explicit bridge evidence for `C` and `D`
- ordering edges `C -> D` and `D -> E` from local source windows
- a merged partial order in which `A -> B -> C -> D -> E -> F` is derivable

The merged graph may still branch or remain uncertain. It must not silently
linearize uncertainty away.

## Event Carrier Requirements

Each document-local event candidate should preserve enough structure to support
reconciliation later. Minimal fields:

- `event_id`
- `doc_id`
- `source_family`
- `source_path` or `source_url`
- `source_span` or snippet reference
- `citation_ref` or citation ids
- `actors`
- `action`
- `objects`
- `legal_refs`
- `time_anchor`
- `local_order_index`
- `confidence`

This is a lower-bound carrier. Lanes may add metadata, but the reconciliation
surface should stay generic.

## Cross-Document Edge Kinds

The braid layer should admit typed reconciliation/order edges such as:

- `same_event_as`
- `overlaps_event`
- `precedes`
- `follows`
- `same_actor_role_as`
- `same_legal_matter_as`
- `contradicts`
- `refines`

Not every edge implies promotion. Some are only candidate reconciliation edges.

## Inference Discipline

The system may derive a wider ordering only when it remains grounded in local
document event lineage.

Required rule:

`no global timeline edge promotes unless it is backed by local document event lineage`

or is explicitly marked as:

`inferred_from_source_backed_overlap`

The braid is therefore:

- source-backed
- typed
- partial-order
- challengeable

It is not a narrative summary.

## Review-Surface Preservation Rule

The current lineage tranche fixed:

`source -> event -> relation -> review`

The next tranche must preserve:

`source -> local_event -> cross_source_event_or_edge -> promoted_relation -> review -> receipt`

This especially matters for evidence/support rows such as:

- `event_relation_support`
- `merged_promoted_relation`

Summary rows may remain aggregate. Evidence rows must preserve upstream event
lineage.

## Receipt / Linkage Follow-On

After the braid exists, the linkage contract should be able to certify more
than queue-review depth.

Useful additional diagnostics:

- `event_lineage_depth`
- `cross_source_braid_depth`
- `ordering_edge_visibility`
- `candidate_vs_promoted_visibility`

That keeps the receipt honest about what depth was actually preserved.

## Immediate Implementation Order

1. Build document-local event windows across the local GWB corpus and public
   sources.
2. Reconcile overlapping events across documents using actor/action/object/time
   and legal-reference overlap.
3. Emit explicit cross-document edge records such as `same_event_as`,
   `overlaps_event`, and `precedes`.
4. Build a merged partial-order timeline braid.
5. Preserve `merged_event_id` and `ordering_edge_id` into broader-review rows
   and then into projected linkage/receipt surfaces.

## Non-Goals

- Do not pretend the braid is a fully historically anchored timeline yet.
- Do not flatten uncertain merges into one prose sentence.
- Do not let renderer concerns decide event identity or ordering semantics.
- Do not make this a GWB-only public API surface.

## Working Invariants

- Input envelopes select nothing.
- Adapters discover from content.
- Raw reports do not receive receipts.
- Only projected, typed, authority-bounded world models can carry receipts.
- Cross-document ordering is a typed partial order, not a prose summary.
- No merged timeline edge should survive without inspectable source-event
  lineage or an explicitly typed inferred-overlap basis.

