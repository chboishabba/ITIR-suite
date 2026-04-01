# Wiki Revision Monitor Dead Path Schema Drop 2026-04-01

## Purpose

Remove dead revision-monitor path columns that no longer carry operational
meaning after the SQLite-first and no-routine-JSON-report cuts.

## Scope

Core runner tables:

- `wiki_revision_monitor_article_state.report_path`
- `wiki_revision_monitor_article_results.report_path`
- `wiki_revision_monitor_candidate_pairs.pair_report_path`
- `wiki_revision_monitor_contested_graphs.graph_path`

Read-model tables:

- `wiki_revision_monitor_changed_articles.report_path`
- `wiki_revision_monitor_changed_articles.contested_graph_path`
- `wiki_revision_monitor_selected_pairs.pair_report_path`

## Decision

These fields are now dead compatibility residue:

- the default runner path no longer writes pair-report JSON
- the default runner path no longer writes contested-graph JSON
- query/read-model payloads no longer expose those paths as routine state
- the remaining operational meaning is already represented in SQLite-owned
  scalar fields and normalized rows

Therefore they should be removed from fresh schema creation and rebuilt out of
old DBs in place.

## Governance

- ITIL:
  controlled standard change on a narrowed schema surface
- ISO 9000:
  eliminate obsolete contract fields once the replacement surface is proven
- Six Sigma:
  remove dead representational variance from storage
- C4:
  keep the canonical store lean and semantically relevant
