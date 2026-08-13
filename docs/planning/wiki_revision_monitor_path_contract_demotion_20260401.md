# Wiki Revision Monitor Path Contract Demotion 2026-04-01

## Purpose

Tighten the post-contraction revision-monitor contract so default SQLite-backed
query payloads stop advertising export-path fields as if they were operational
runtime state.

## Current state

- Query-time JSON fallback is already gone.
- DB blob fallback is already gone.
- The remaining residue is contract-shaped:
  some default read-model and query payloads still expose path fields such as
  `report_path`, `pair_report_path`, `contested_graph_path`, and `graph_path`.
- Summary payloads no longer include `out_dir`; run-level directories remain an external provenance artifact rather than canonical query state.

These fields are no longer suitable as ordinary runtime contract because the
lane is being pushed toward SQLite-canonical behavior.

The sharper provenance reading is:

- local path fields are not semantic identity
- local path fields are not enough for hosted/shareable provenance
- if a field survives, it should survive only as provenance-only or transient
  implementation metadata

## First safe slice

Do not change storage or execution flow again in this pass.

Instead:

- keep path-bearing columns in SQLite for now
- keep runner writes unchanged for this slice
- remove those path fields from default read-model/query payloads

Target default payloads:

- changed article rows
- selected pair rows
- selected contested graph payload
- summary top-article rows

## Governance

- ITIL:
  this is a low-risk contract cleanup after the earlier storage/runtime
  corrections.
- ISO 9000:
  default consumer payloads should reflect the canonical state model, not
  transitional export metadata.
- Six Sigma:
  path-shaped optional metadata should not vary across consumers as if it were
  canonical truth.
- C4:
  keep export-path details outside the default operational query surface.

## Acceptance gate

- default revision-monitor query payloads no longer expose those export paths
  as ordinary runtime fields
- SQLite remains the canonical query surface
- no behavior regresses in summary, changed-article ordering, selected-pair
  ordering, or selected-graph reconstruction
