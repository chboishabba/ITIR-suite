## Wiki Revision Monitor Path Residue Cut

Date: 2026-04-02

Decision:
- finish the last small revision-monitor contract cut by removing
  `timeline_path` and `aoo_path` from article-state and article-result
  storage
- keep `snapshot_path` as the only remaining article-local provenance field in
  this lane for now
- keep `out_dir` out of scope for this slice; it remains transitional
  run-level provenance rather than truth

Reason:
- the runner already stopped persisting timeline/AOO continuity as canonical
  state
- those columns are now dead residue from the earlier JSON-to-SQLite
  migration path
- this is the last small schema cleanup worth landing before the user-story
  sweep

Acceptance:
- fresh schema and old-DB rebuilds drop `timeline_path` and `aoo_path` from
  `wiki_revision_monitor_article_state`
- fresh schema and old-DB rebuilds drop `timeline_path` and `aoo_path` from
  `wiki_revision_monitor_article_results`
- focused revision-monitor tests stay green
