export function resolveFactReviewSourceRows(workbench, sources) {
  const recentSources = workbench?.reopen_navigation?.recent_sources;
  if (Array.isArray(recentSources) && recentSources.length > 0) {
    return recentSources;
  }
  return Array.isArray(sources) ? sources : [];
}

export function buildFactReviewHrefForSource(source, params) {
  const searchParams = new URLSearchParams();
  const workflowKind = source?.latest_workflow_link?.workflow_kind ?? source?.workflow_kind ?? params.workflowKind;
  const workflowRunId = source?.latest_workflow_link?.workflow_run_id ?? source?.workflow_run_id ?? null;
  searchParams.set('workflow', workflowKind);
  if (workflowRunId) searchParams.set('workflowRunId', workflowRunId);
  if (source?.source_label) searchParams.set('sourceLabel', source.source_label);
  if (params.wave) searchParams.set('wave', params.wave);
  searchParams.set('view', params.view);
  return `/graphs/fact-review?${searchParams.toString()}`;
}

export function resolveFactReviewAvailableIssueFilters(workbench, view) {
  if (view !== 'intake_triage') {
    return ['all'];
  }
  const filters = workbench?.issue_filters?.available_filters;
  return Array.isArray(filters) && filters.length > 0 ? filters : ['all'];
}

export function resolveFactReviewFilteredItems(workbench, view, selectedIssueFilter) {
  const selectedView = workbench?.operator_views?.[view];
  const issueGroups = selectedView?.groups ?? {};
  if (view === 'intake_triage' && selectedIssueFilter !== 'all') {
    return Array.isArray(issueGroups?.[selectedIssueFilter]) ? issueGroups[selectedIssueFilter] : [];
  }
  return Array.isArray(selectedView?.items) ? selectedView.items : [];
}

export function resolveSelectedFact(workbench, selectedFactId) {
  const facts = Array.isArray(workbench?.facts) ? workbench.facts : [];
  return facts.find((row) => row?.fact_id === selectedFactId) ?? facts[0] ?? null;
}

export function resolveInspectorClassification(workbench, selectedFact) {
  return (
    selectedFact?.inspector_classification ??
    workbench?.inspector_classification?.facts?.[selectedFact?.fact_id ?? ''] ??
    null
  );
}

export function resolveChronologyBuckets(workbench) {
  const groups = workbench?.chronology_groups ?? {};
  const dated = Array.isArray(groups.dated_events) ? groups.dated_events : [];
  const approximate = Array.isArray(groups.approximate_events) ? groups.approximate_events : [];
  const undated = Array.isArray(groups.undated_events) ? groups.undated_events : [];
  const contested = Array.isArray(groups.contested_chronology_items) ? groups.contested_chronology_items : [];
  return {
    dated,
    approximate,
    undated,
    contested,
    undatedOrContested: [...undated, ...contested],
  };
}
