<script lang="ts">
  import type { PageData } from './$types';
  import type {
    FactReviewControlPlaneQueueItem,
    FactReviewEvent,
    FactReviewExcerpt,
    FactReviewFact,
    FactReviewInspectorClassification,
    FactReviewRecentSource,
    FactReviewSource,
    FactReviewStatement,
    FactReviewViewItem
  } from '$lib/server/factReview';
  import {
    buildFactReviewCurrentHref,
    buildFactReviewHrefForSource,
    resolveChronologyBuckets,
    resolveFactReviewAvailableIssueFilters,
    resolveFactReviewFilteredItems,
    resolveFactReviewSourceRows,
    resolveInspectorClassification,
    resolveInspectorStatusRows,
    resolveSelectedFact
  } from '$lib/workbench/factReview.js';

  type FactReviewSourceRow = FactReviewSource | FactReviewRecentSource;

  export let data: PageData;

  const views = [
    { key: 'intake_triage', label: 'Intake triage' },
    { key: 'chronology_prep', label: 'Chronology prep' },
    { key: 'procedural_posture', label: 'Procedural posture' },
    { key: 'authority_follow', label: 'Authority follow' },
    { key: 'contested_items', label: 'Contested items' },
    { key: 'trauma_handoff', label: 'Trauma handoff' },
    { key: 'professional_handoff', label: 'Professional handoff' },
    { key: 'false_coherence_review', label: 'False-coherence review' },
    { key: 'public_claim_review', label: 'Public claim review' },
    { key: 'wiki_fidelity', label: 'Wiki fidelity' },
    { key: 'claim_alignment', label: 'Claim alignment' }
  ];

  let selectedFactId = data.workbench?.inspector_defaults?.selected_fact_id ?? null;
  let selectedIssueFilter = 'all';

  $: selectedView =
    data.demoBundle?.workbench?.operator_views?.[data.view] ??
    data.workbench?.operator_views?.[data.view] ??
    null;
  $: issueGroups = selectedView?.groups ?? {};
  $: availableIssueFilters = resolveFactReviewAvailableIssueFilters(data.workbench, data.view);
  $: filteredItems =
    data.view === 'authority_follow'
      ? []
      : (resolveFactReviewFilteredItems(data.workbench, data.view, selectedIssueFilter) as FactReviewViewItem[]);
  $: controlPlaneQueueRaw =
    selectedView?.control_plane?.version && Array.isArray(selectedView?.queue)
      ? (selectedView.queue as FactReviewControlPlaneQueueItem[])
      : [];
  $: authorityFollowQueue =
    data.view === 'intake_triage' && selectedIssueFilter !== 'all'
      ? controlPlaneQueueRaw.filter((row) =>
          Array.isArray(row.reason_codes) ? row.reason_codes.includes(selectedIssueFilter) : false
        )
      : controlPlaneQueueRaw;
  $: authorityFollowRouteCounts =
    selectedView?.control_plane?.version && selectedView?.summary?.route_target_counts
      ? Object.entries(selectedView.summary.route_target_counts as Record<string, number>)
      : [];
  $: authorityFollowResolutionCounts =
    selectedView?.control_plane?.version && selectedView?.summary?.resolution_status_counts
      ? Object.entries(selectedView.summary.resolution_status_counts as Record<string, number>)
      : [];
  $: reopenNavigation = data.workbench?.reopen_navigation ?? null;
  $: reopenSourceRows = resolveFactReviewSourceRows(data.workbench, data.sources) as FactReviewSourceRow[];
  $: currentRunHref = buildFactReviewCurrentHref(data.workbench, {
    workflowKind: data.workflowKind,
    wave: data.wave,
    view: data.view
  });
  $: chronologyBuckets = resolveChronologyBuckets(data.workbench);
  $: selectedFact = resolveSelectedFact(data.workbench, selectedFactId) as FactReviewFact | null;
  $: selectedClassification = resolveInspectorClassification(
    data.workbench,
    selectedFact
  ) as FactReviewInspectorClassification | null;
  $: inspectorStatuses = resolveInspectorStatusRows(selectedClassification);
  $: selectedStatements = (data.workbench?.statements ?? []).filter((row) =>
    selectedFact?.statement_ids?.includes(row.statement_id)
  ) as FactReviewStatement[];
  $: selectedExcerpts = (data.workbench?.excerpts ?? []).filter((row) =>
    selectedFact?.excerpt_ids?.includes(row.excerpt_id)
  ) as FactReviewExcerpt[];
  $: selectedEvents = (data.workbench?.events ?? []).filter((row) =>
    selectedFact?.event_ids?.includes(row.event_id)
  ) as FactReviewEvent[];

  function hrefForView(key: string): string {
    const params = new URLSearchParams();
    params.set('workflow', data.workflowKind);
    if (data.workflowRunId) params.set('workflowRunId', data.workflowRunId);
    if (data.sourceLabel) params.set('sourceLabel', data.sourceLabel);
    if (data.wave) params.set('wave', data.wave);
    params.set('view', key);
    return `/graphs/fact-review?${params.toString()}`;
  }

  function hrefForSource(source: FactReviewSourceRow): string {
    return buildFactReviewHrefForSource(source, {
      workflowKind: data.workflowKind,
      wave: data.wave,
      view: data.view
    });
  }

  function clickFact(factId: string): void {
    selectedFactId = factId;
  }

  function storyFamily(storyId: string): 'mary' | 'itir' | 'other' {
    if (storyId.startsWith('SL-US-')) return 'mary';
    if (storyId.startsWith('ITIR-US-')) return 'itir';
    return 'other';
  }

  function storyFamilyLabel(storyId: string): string {
    const family = storyFamily(storyId);
    return family === 'mary' ? 'Mary operator' : family === 'itir' ? 'ITIR operator' : 'Operator story';
  }

  function storyFamilyTone(storyId: string): string {
    const family = storyFamily(storyId);
    if (family === 'mary') return 'border-amber-200 bg-amber-50 text-amber-900';
    if (family === 'itir') return 'border-sky-200 bg-sky-50 text-sky-900';
    return 'border-zinc-200 bg-zinc-50 text-zinc-700';
  }
</script>

<svelte:head>
  <title>Fact Review Workbench</title>
</svelte:head>

<div class="mx-auto max-w-7xl px-6 py-8">
  <div class="mb-6 flex flex-wrap items-start justify-between gap-4">
    <div>
      <h1 class="text-3xl font-semibold tracking-tight">Fact Review Workbench</h1>
      <p class="mt-1 text-sm text-zinc-600">
        Read-only Mary-parity inspection over persisted fact-review runs.
      </p>
    </div>
    <div class="rounded border border-zinc-200 bg-zinc-50 px-4 py-3 text-xs text-zinc-700">
      <div class="font-mono">{data.workflowKind}</div>
      <div>{data.sourceLabel ?? 'latest linked source'}</div>
      <div class="mt-1 uppercase tracking-[0.2em] text-zinc-500">{data.wave}</div>
    </div>
  </div>

  {#if data.error}
    <div class="rounded border border-red-300 bg-red-50 px-4 py-3 text-sm text-red-800">
      <div class="font-medium">{data.errorTitle ?? 'Fact review load error'}</div>
      <div class="mt-1">{data.error}</div>
    </div>
  {:else if data.workbench}
    <div class="mb-6 grid gap-4 lg:grid-cols-4">
      <div class="rounded border border-zinc-200 bg-white p-4">
        <div class="text-xs uppercase tracking-[0.24em] text-zinc-500">Run</div>
        <div class="mt-2 font-mono text-xs text-zinc-700">{data.workbench.run.run_id}</div>
        <div class="mt-2 text-sm text-zinc-900">Review queue: {data.workbench.summary.review_queue_count}</div>
        <div class="text-sm text-zinc-900">Contested: {data.workbench.summary.contested_item_count}</div>
        <div class="text-sm text-zinc-900">Abstained / bounded context: {data.workbench.summary.abstained_fact_count ?? 0}</div>
      </div>
      <div class="rounded border border-zinc-200 bg-white p-4">
        <div class="text-xs uppercase tracking-[0.24em] text-zinc-500">Chronology</div>
        <div class="mt-2 text-sm text-zinc-900">Dated events: {data.workbench.chronology_summary.dated_event_count}</div>
        <div class="text-sm text-zinc-900">Undated events: {data.workbench.chronology_summary.undated_event_count}</div>
        <div class="text-sm text-zinc-900">No-event facts: {data.workbench.chronology_summary.no_event_fact_count}</div>
      </div>
      <div class="rounded border border-zinc-200 bg-white p-4">
        <div class="text-xs uppercase tracking-[0.24em] text-zinc-500">Acceptance</div>
        <div class="mt-2 text-sm text-zinc-900">Pass: {data.acceptance?.summary?.pass_count ?? 0}</div>
        <div class="text-sm text-zinc-900">Partial: {data.acceptance?.summary?.partial_count ?? 0}</div>
        <div class="text-sm text-zinc-900">Fail: {data.acceptance?.summary?.fail_count ?? 0}</div>
      </div>
      <div class="rounded border border-zinc-200 bg-white p-4">
        <div class="text-xs uppercase tracking-[0.24em] text-zinc-500">Reopen</div>
        <div class="mt-2 font-mono text-xs text-zinc-700">{reopenNavigation?.current?.workflow_run_id ?? data.workbench.run.workflow_link?.workflow_run_id}</div>
        <div class="mt-2 text-sm text-zinc-900">Read-only operator review over persisted evidence. Provenance-first, no reasoning overlay.</div>
        <div class="mt-2 text-xs text-zinc-600">
          {reopenNavigation?.current?.source_label ?? data.sourceLabel ?? 'latest linked source'}
        </div>
      </div>
    </div>

    <section class="mb-6 rounded border border-zinc-200 bg-white p-4">
      <div class="mb-4">
        <div class="flex flex-wrap items-center justify-between gap-3">
          <div class="text-xs uppercase tracking-[0.24em] text-zinc-500">Recent / source-centric reopen</div>
          <a class="rounded border border-zinc-200 bg-zinc-50 px-3 py-1 text-xs text-zinc-700" href={currentRunHref}>
            Open current persisted run
          </a>
        </div>
        {#if reopenSourceRows.length > 0}
          <div class="mt-3 flex flex-wrap gap-2">
            {#each reopenSourceRows as source}
              <a class={`rounded border px-3 py-1 text-sm ${data.sourceLabel === source.source_label ? 'border-amber-300 bg-amber-50 text-amber-950' : 'border-zinc-200 bg-zinc-50 text-zinc-700'}`} href={hrefForSource(source)}>
                {source.source_label}
              </a>
            {/each}
          </div>
        {:else}
          <div class="mt-3 rounded border border-dashed border-zinc-300 bg-zinc-50 px-3 py-2 text-sm text-zinc-600">
            No reopen sources are available for this workflow yet.
          </div>
        {/if}
      </div>
      <div class="mb-3 flex flex-wrap items-center gap-3">
        <div class="text-xs uppercase tracking-[0.24em] text-zinc-500">Operator views</div>
        {#each views as view}
          <a
            class={`rounded px-3 py-1 text-sm ${data.view === view.key ? 'bg-amber-100 text-amber-950' : 'bg-zinc-100 text-zinc-700'}`}
            href={hrefForView(view.key)}
          >
            {view.label}
          </a>
        {/each}
      </div>
      <div class="grid gap-4 lg:grid-cols-[1.2fr,1fr]">
        <div>
          <div class="mb-2 text-sm font-semibold text-zinc-900">{selectedView?.title ?? 'Operator view'}</div>
          {#if data.view === 'intake_triage' && availableIssueFilters.length > 1}
            <div class="mb-3 flex flex-wrap gap-2">
              {#each availableIssueFilters as filterKey}
                <button
                  class={`rounded px-3 py-1 text-xs ${selectedIssueFilter === filterKey ? 'bg-amber-100 text-amber-950' : 'bg-zinc-100 text-zinc-700'}`}
                  on:click={() => (selectedIssueFilter = filterKey)}
                >
                  {filterKey === 'all' ? 'all' : filterKey.replaceAll('_', ' ')}
                </button>
              {/each}
            </div>
          {/if}
          {#if data.view === 'chronology_prep'}
            <div class="grid gap-3 md:grid-cols-3">
              <div class="rounded border border-zinc-200 bg-zinc-50 p-3">
                <div class="text-xs uppercase tracking-[0.18em] text-zinc-500">Dated events</div>
                {#each chronologyBuckets.dated as row}
                  <button
                    class="mt-2 block w-full rounded border border-zinc-200 bg-white px-3 py-2 text-left text-sm"
                    disabled={!row.fact_id}
                    on:click={() => {
                      if (row.fact_id) clickFact(row.fact_id);
                    }}
                  >
                    <div class="font-medium">{row.event_type}</div>
                    <div class="text-xs text-zinc-600">{row.time_start} · {row.primary_actor ?? 'unknown actor'}</div>
                  </button>
                {/each}
              </div>
              <div class="rounded border border-zinc-200 bg-zinc-50 p-3">
                <div class="text-xs uppercase tracking-[0.18em] text-zinc-500">Approximate chronology</div>
                {#each chronologyBuckets.approximate as row}
                  <div class="mt-2 rounded border border-zinc-200 bg-white px-3 py-2 text-sm">
                    <div class="font-medium">{row.label ?? row.event_type}</div>
                    <div class="text-xs text-zinc-600">{row.time_start ?? 'approximate'}</div>
                  </div>
                {/each}
              </div>
              <div class="rounded border border-zinc-200 bg-zinc-50 p-3">
                <div class="text-xs uppercase tracking-[0.18em] text-zinc-500">Undated / contested chronology</div>
                {#each chronologyBuckets.undatedOrContested as row}
                  <div class="mt-2 rounded border border-zinc-200 bg-white px-3 py-2 text-sm">
                    <div class="font-medium">{row.label ?? row.event_type}</div>
                    <div class="text-xs text-zinc-600">{row.time_start ?? 'undated'}</div>
                  </div>
                {/each}
              </div>
            </div>
          {:else if selectedView?.control_plane?.version && authorityFollowQueue.length >= 0}
            <div class="grid gap-3 md:grid-cols-[18rem,1fr]">
              <div class="rounded border border-zinc-200 bg-zinc-50 p-3">
                <div class="text-xs uppercase tracking-[0.18em] text-zinc-500">Control-plane summary</div>
                <div class="mt-2 text-sm text-zinc-900">Family: {selectedView?.control_plane?.source_family ?? 'unknown'}</div>
                <div class="text-sm text-zinc-900">Hint: {selectedView?.control_plane?.hint_kind ?? 'unknown'}</div>
                <div class="text-sm text-zinc-900">Receipt: {selectedView?.control_plane?.receipt_kind ?? 'unknown'}</div>
                <div class="text-sm text-zinc-900">Substrate: {selectedView?.control_plane?.substrate_kind ?? 'unknown'}</div>
                <div class="mt-2 text-sm text-zinc-900">Available: {selectedView?.available ? 'yes' : 'no'}</div>
                {#if selectedView?.summary?.authority_receipt_count != null}
                  <div class="text-sm text-zinc-900">Receipts: {selectedView?.summary?.authority_receipt_count ?? 0}</div>
                {/if}
                {#if selectedView?.summary?.follow_needed_event_count != null}
                  <div class="text-sm text-zinc-900">Follow-needed events: {selectedView?.summary?.follow_needed_event_count ?? 0}</div>
                {/if}
                <div class="text-sm text-zinc-900">Queue items: {selectedView?.summary?.queue_count ?? authorityFollowQueue.length}</div>
                {#if selectedView?.summary?.conjecture_count != null}
                  <div class="text-sm text-zinc-900">Conjectures: {selectedView?.summary?.conjecture_count ?? 0}</div>
                {/if}
                {#if authorityFollowRouteCounts.length > 0}
                  <div class="mt-3 text-xs uppercase tracking-[0.18em] text-zinc-500">Route targets</div>
                  {#each authorityFollowRouteCounts as [routeTarget, count]}
                    <div class="mt-1 flex items-center justify-between rounded border border-zinc-200 bg-white px-2 py-1 text-xs text-zinc-700">
                      <span>{routeTarget}</span>
                      <span>{count}</span>
                    </div>
                  {/each}
                {/if}
                {#if authorityFollowResolutionCounts.length > 0}
                  <div class="mt-3 text-xs uppercase tracking-[0.18em] text-zinc-500">Resolution statuses</div>
                  {#each authorityFollowResolutionCounts as [resolutionStatus, count]}
                    <div class="mt-1 flex items-center justify-between rounded border border-zinc-200 bg-white px-2 py-1 text-xs text-zinc-700">
                      <span>{resolutionStatus}</span>
                      <span>{count}</span>
                    </div>
                  {/each}
                {/if}
              </div>
              <div class="rounded border border-zinc-200 bg-zinc-50 p-3">
                <div class="text-xs uppercase tracking-[0.18em] text-zinc-500">{selectedView?.control_plane?.conjecture_kind ?? 'queue'} queue</div>
                {#if authorityFollowQueue.length > 0}
                  {#each authorityFollowQueue as row}
                    <div class="mt-2 rounded border border-zinc-200 bg-white px-3 py-3 text-sm">
                      <div class="flex flex-wrap items-center justify-between gap-2">
                        <div class="font-medium text-zinc-900">{row.title ?? row.event_section ?? 'Follow item'}</div>
                        <div class="flex flex-wrap gap-2">
                          <div class="rounded bg-amber-100 px-2 py-0.5 text-[11px] text-amber-950">{row.route_target ?? 'manual_review'}</div>
                          <div class="rounded bg-zinc-200 px-2 py-0.5 text-[11px] text-zinc-800">{row.resolution_status ?? 'open'}</div>
                        </div>
                      </div>
                      <div class="mt-1 text-xs text-zinc-600">{row.subtitle ?? row.conjecture_kind ?? ''}</div>
                      <div class="mt-2 text-sm text-zinc-800">{row.description ?? row.event_text ?? ''}</div>
                      {#if Array.isArray(row.chips) && row.chips.length > 0}
                        <div class="mt-2 flex flex-wrap gap-2">
                          {#each row.chips as chip}
                            <span class="rounded bg-sky-50 px-2 py-0.5 text-[11px] text-sky-900">{chip}</span>
                          {/each}
                        </div>
                      {/if}
                      {#if Array.isArray(row.detail_rows) && row.detail_rows.length > 0}
                        <div class="mt-2 space-y-1">
                          {#each row.detail_rows as detail}
                            <div class="text-xs text-zinc-600">{detail.label}: {detail.value}</div>
                          {/each}
                        </div>
                      {/if}
                    </div>
                  {/each}
                {:else}
                  <div class="mt-2 rounded border border-dashed border-zinc-300 bg-white px-3 py-3 text-sm text-zinc-600">
                    No control-plane queue is available for this selector.
                  </div>
                {/if}
              </div>
            </div>
          {:else}
            {#if filteredItems.length > 0}
              {#each filteredItems as row}
                <button class="mt-2 block w-full rounded border border-zinc-200 bg-zinc-50 px-3 py-3 text-left" on:click={() => clickFact(row.fact_id)}>
                  <div class="flex flex-wrap items-center justify-between gap-2">
                    <div class="font-medium text-zinc-900">{row.label}</div>
                    <div class="text-xs text-zinc-500">{row.latest_review_status ?? row.candidate_status ?? ''}</div>
                  </div>
                  <div class="mt-2 text-xs text-zinc-600">
                    {(row.reason_labels ?? []).join(' · ') || `${row.contestation_count ?? 0} contested`}
                  </div>
                  {#if row.primary_contested_reason_text}
                    <div class="mt-2 text-sm text-zinc-800">{row.primary_contested_reason_text}</div>
                  {/if}
                  {#if row.signal_classes?.length}
                    <div class="mt-2 text-xs text-zinc-600">
                      Observation signals: {(row.signal_classes ?? []).join(' · ')}
                    </div>
                  {/if}
                  {#if row.source_signal_classes?.length}
                    <div class="mt-1 text-xs text-zinc-600">
                      Source provenance: {(row.source_signal_classes ?? []).join(' · ')}
                    </div>
                  {/if}
                  {#if row.policy_outcomes?.length}
                    <div class="mt-1 text-xs text-zinc-600">
                      Operator constraints: {(row.policy_outcomes ?? []).join(' · ')}
                    </div>
                  {/if}
                </button>
              {/each}
            {:else}
              <div class="rounded border border-dashed border-zinc-300 bg-zinc-50 px-3 py-3 text-sm text-zinc-600">
                No items are available for this operator view and filter yet.
              </div>
            {/if}
          {/if}
        </div>
        <div class="rounded border border-zinc-200 bg-zinc-50 p-4">
          <div class="text-xs uppercase tracking-[0.24em] text-zinc-500">Inspector</div>
          {#if selectedFact}
            <div class="mt-2 text-lg font-semibold text-zinc-950">{selectedFact.canonical_label ?? selectedFact.fact_text}</div>
            <div class="mt-2 text-sm text-zinc-700">Status: {selectedFact.candidate_status}</div>
            <div class="mt-2 text-sm text-zinc-700">Event links: {selectedFact.event_ids?.length ?? 0}</div>
            {#if selectedClassification}
              <div class="mt-4 text-xs uppercase tracking-[0.18em] text-zinc-500">Inspector classification</div>
              <div class="mt-2 flex flex-wrap gap-2">
                {#each selectedClassification.display_labels ?? [] as label}
                  <div class="rounded border border-zinc-200 bg-white px-3 py-1 text-xs text-zinc-800">{label}</div>
                {/each}
              </div>
              <div class="mt-3 grid gap-2 md:grid-cols-3">
                {#each inspectorStatuses as status}
                  <div class={`rounded border px-3 py-2 text-sm ${status.active ? 'border-amber-300 bg-amber-50 text-amber-950' : 'border-zinc-200 bg-white text-zinc-500'}`}>
                    <div class="text-[11px] uppercase tracking-[0.16em]">{status.label}</div>
                    <div class="mt-1 font-medium">{status.active ? 'present' : 'not present'}</div>
                  </div>
                {/each}
              </div>
            {/if}
            {#if selectedFact.signal_classes?.length}
              <div class="mt-2 text-sm text-zinc-700">
                Observation signals: {(selectedFact.signal_classes ?? []).join(' · ')}
              </div>
            {/if}
            {#if selectedFact.source_signal_classes?.length}
              <div class="mt-1 text-sm text-zinc-700">
                Source provenance: {(selectedFact.source_signal_classes ?? []).join(' · ')}
              </div>
            {/if}
            {#if selectedFact.policy_outcomes?.length}
              <div class="mt-1 text-sm text-zinc-700">
                Operator constraints: {(selectedFact.policy_outcomes ?? []).join(' · ')}
              </div>
            {/if}
            {#if selectedFact.latest_review_note}
              <div class="mt-2 rounded border border-zinc-200 bg-white px-3 py-2 text-sm text-zinc-800">
                Latest review note: {selectedFact.latest_review_note}
              </div>
            {/if}
            {#if selectedFact.policy_outcomes?.includes('bounded_context_required')}
              <div class="mt-2 rounded border border-sky-200 bg-sky-50 px-3 py-2 text-sm text-sky-900">
                This item remains bounded-context material. Keep source boundaries explicit and do not collapse it into a stronger narrative.
              </div>
            {/if}
            <div class="mt-4 text-xs uppercase tracking-[0.18em] text-zinc-500">Observations</div>
            {#each selectedFact.observations ?? [] as observation}
              <div class="mt-2 rounded border border-zinc-200 bg-white px-3 py-2 text-sm">
                <div class="font-medium text-zinc-900">{observation.predicate_key}</div>
                <div class="text-zinc-700">{observation.object_text}</div>
              </div>
            {/each}
            <div class="mt-4 text-xs uppercase tracking-[0.18em] text-zinc-500">Source types / roles</div>
            <div class="mt-2 rounded border border-zinc-200 bg-white px-3 py-2 text-sm text-zinc-800">
              {(selectedFact.source_types ?? []).join(' · ') || 'No source types'}
              {#if selectedFact.statement_roles?.length}
                <div class="mt-1 text-xs text-zinc-600">{selectedFact.statement_roles.join(' · ')}</div>
              {/if}
            </div>
            <div class="mt-4 text-xs uppercase tracking-[0.18em] text-zinc-500">Source statements</div>
            {#each selectedStatements as statement}
              <div class="mt-2 rounded border border-zinc-200 bg-white px-3 py-2 text-sm text-zinc-800">{statement.statement_text}</div>
            {/each}
            <div class="mt-4 text-xs uppercase tracking-[0.18em] text-zinc-500">Excerpts</div>
            {#each selectedExcerpts as excerpt}
              <div class="mt-2 rounded border border-zinc-200 bg-white px-3 py-2 text-sm text-zinc-800">{excerpt.excerpt_text}</div>
            {/each}
            <div class="mt-4 text-xs uppercase tracking-[0.18em] text-zinc-500">Derived events</div>
            {#each selectedEvents as event}
              <div class="mt-2 rounded border border-zinc-200 bg-white px-3 py-2 text-sm">
                <div class="font-medium text-zinc-900">{event.event_type}</div>
                <div class="text-zinc-700">{event.primary_actor ?? 'unknown actor'} · {event.time_start ?? 'undated'}</div>
              </div>
            {/each}
          {:else}
            <div class="mt-3 text-sm text-zinc-600">No fact selected.</div>
          {/if}
        </div>
      </div>
    </section>

    <section class="rounded border border-zinc-200 bg-white p-4">
      <div class="text-xs uppercase tracking-[0.24em] text-zinc-500">Story acceptance</div>
      <div class="mt-2 text-sm text-zinc-600">
        These story cards are operator-facing acceptance cues only. They summarize what this persisted run already proves; they do not add new adjudication.
      </div>
      {#if (data.acceptance?.stories ?? []).length > 0}
        <div class="mt-3 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {#each data.acceptance?.stories ?? [] as story}
            <div class="rounded border border-zinc-200 bg-zinc-50 p-3">
              <div class="flex items-center justify-between gap-3">
                <div class="font-medium text-zinc-950">{story.story_id}</div>
                <div class={`rounded px-2 py-1 text-xs ${story.status === 'pass' ? 'bg-emerald-100 text-emerald-900' : story.status === 'partial' ? 'bg-amber-100 text-amber-900' : 'bg-rose-100 text-rose-900'}`}>
                  {story.status}
                </div>
              </div>
              <div class={`mt-2 inline-flex rounded border px-2 py-1 text-[11px] uppercase tracking-[0.16em] ${storyFamilyTone(story.story_id)}`}>
                {storyFamilyLabel(story.story_id)}
              </div>
              <div class="mt-1 text-sm text-zinc-700">{story.label}</div>
              <div class="mt-2 text-xs text-zinc-600">{story.passed_check_count}/{story.check_count} checks passed</div>
            </div>
          {/each}
        </div>
      {:else}
        <div class="mt-3 rounded border border-dashed border-zinc-300 bg-zinc-50 px-3 py-3 text-sm text-zinc-600">
          No acceptance stories were recorded for this selector.
        </div>
      {/if}
    </section>
  {:else}
    <div class="rounded border border-zinc-200 bg-zinc-50 px-4 py-3 text-sm text-zinc-700">
      No persisted fact-review payload is available for this selector.
    </div>
  {/if}
</div>
