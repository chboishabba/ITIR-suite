# Docstore and Obsidian MCP Tools

## Role

The docstore tools expose read-only status and open-question projections through
the existing `itir-mcp` contract. They do not create a new authority surface.

## Tools

- `itir.docstore.status`
  - returns artifact, producer, authority, unresolved-pressure, and question
    summary counts
  - reuses suite normalized artifact joins when artifacts are available
- `itir.docstore.open_questions`
  - aggregates typed SB/SL fields, TODO pressure, review-packet uncertainty,
    structured Markdown hints, and optional Obsidian observer hints
- `itir.obsidian.vault_scan`
  - reads an explicit vault path or plugin-exported bundle
  - emits observer-class note hashes and candidate hints only
- `itir.docstore.proposal_receipt`
  - turns `structured_hint` or `candidate_hint` records into non-authoritative
    review receipts
  - requires reviewer identity, action, timestamp, and decision reason
- `itir.markdown.render_projection`
  - renders MCP responses as replaceable Markdown blocks/pages
- `itir.markdown.write_projection`
  - writes generated projections under an explicit output root
  - refuses to overwrite human pages without generated markers
- `itir.docstore.config_plan`
  - validates allowlisted roots, scan limits, include flags, and cache metadata
    without scanning producer content

## Promotion Levels

- `typed_source`: producer-owned structured fields such as SB `open_questions`,
  normalized artifact `follow_obligation`, and SL review-packet uncertainty
- `structured_hint`: explicit Markdown sections such as open questions,
  blockers, gaps, or assumptions
- `candidate_hint`: query-intent lines such as `:itir-query:` or `:sl-query:`

Hints are review inputs. They are not promoted facts.

Proposal receipts remain below canonical truth. A `mark_promotable` receipt is
held unless a downstream promotion authority is present in the review payload.

## Obsidian Boundary

Allowed:

- Obsidian queries ITIR through MCP.
- ITIR scans explicitly configured vault or bundle inputs.
- Generated Markdown projections are replaceable.
- Note and vault identity use hashes by default.

Forbidden:

- note titles, tags, backlinks, or paths becoming canonical IDs
- Obsidian edits mutating promoted ITIR/SL/SB records
- generated projections becoming permanent copied evidence
- full note bodies being stored as authority

## Producer Adapters

`itir.docstore.open_questions` also accepts explicit producer adapter paths:

- `sensiblaw_fact_review_paths`
- `sensiblaw_operator_view_paths`
- `statibaker_dashboard_paths`
- `statibaker_codex_trace_paths`
- `generated_artifact_paths`

These adapters read structured JSON fields only. They do not walk the suite by
default and do not infer legal or semantic truth from prose.

## Generated Projections

Markdown projections are generated output only. The Python exporter writes below
`_ITIR/generated/...` relative to the explicit output root, and the Obsidian
plugin writes replaceable pages below its configured generated folder. Both are
projection surfaces, not evidence stores.
