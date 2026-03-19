<script lang="ts">
  export let data: {
    workflowKind: string;
    workflowRunId?: string | null;
    sourceLabel?: string | null;
    view: string;
    wave: string;
    workbench: any;
    acceptance: any;
    sources: any[];
    error: string | null;
  };

  const views = [
    { key: 'intake_triage', label: 'Intake triage' },
    { key: 'chronology_prep', label: 'Chronology prep' },
    { key: 'procedural_posture', label: 'Procedural posture' },
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

  $: selectedView = data.workbench?.operator_views?.[data.view] ?? null;
  $: issueGroups = selectedView?.groups ?? {};
  $: canonicalIssueFilters = data.workbench?.issue_filters?.available_filters ?? ['all'];
  $: availableIssueFilters = data.view === 'intake_triage' ? canonicalIssueFilters : ['all'];
  $: filteredItems =
    data.view === 'intake_triage' && selectedIssueFilter !== 'all'
      ? issueGroups?.[selectedIssueFilter] ?? []
      : selectedView?.items ?? [];
  $: reopenNavigation = data.workbench?.reopen_navigation ?? null;
  $: selectedFact =
    (data.workbench?.facts ?? []).find((row: any) => row.fact_id === selectedFactId) ??
    (data.workbench?.facts ?? [])[0] ??
    null;
  $: selectedClassification =
    (selectedFact?.inspector_classification as any) ??
    data.workbench?.inspector_classification?.facts?.[selectedFact?.fact_id ?? ''] ??
    null;
  $: selectedStatements = (data.workbench?.statements ?? []).filter((row: any) =>
    selectedFact?.statement_ids?.includes(row.statement_id)
  );
  $: selectedExcerpts = (data.workbench?.excerpts ?? []).filter((row: any) =>
    selectedFact?.excerpt_ids?.includes(row.excerpt_id)
  );
  $: selectedEvents = (data.workbench?.events ?? []).filter((row: any) =>
    selectedFact?.event_ids?.includes(row.event_id)
  );

  function hrefForView(key: string): string {
    const params = new URLSearchParams();
    params.set('workflow', data.workflowKind);
    if (data.workflowRunId) params.set('workflowRunId', data.workflowRunId);
    if (data.sourceLabel) params.set('sourceLabel', data.sourceLabel);
    if (data.wave) params.set('wave', data.wave);
    params.set('view', key);
    return `/graphs/fact-review?${params.toString()}`;
  }

  function hrefForSource(source: any): string {
    const params = new URLSearchParams();
    const workflowKind = source?.latest_workflow_link?.workflow_kind ?? source?.workflow_kind ?? data.workflowKind;
    const workflowRunId = source?.latest_workflow_link?.workflow_run_id ?? source?.workflow_run_id ?? null;
    params.set('workflow', workflowKind);
    if (workflowRunId) params.set('workflowRunId', workflowRunId);
    if (source?.source_label) params.set('sourceLabel', source.source_label);
    if (data.wave) params.set('wave', data.wave);
    params.set('view', data.view);
    return `/graphs/fact-review?${params.toString()}`;
  }

  function clickFact(factId: string): void {
    selectedFactId = factId;
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
    <div class="rounded border border-red-300 bg-red-50 px-4 py-3 text-sm text-red-800">{data.error}</div>
  {:else if data.workbench}
    <div class="mb-6 grid gap-4 lg:grid-cols-4">
      <div class="rounded border border-zinc-200 bg-white p-4">
        <div class="text-xs uppercase tracking-[0.24em] text-zinc-500">Run</div>
        <div class="mt-2 font-mono text-xs text-zinc-700">{data.workbench.run.run_id}</div>
        <div class="mt-2 text-sm text-zinc-900">Review queue: {data.workbench.summary.review_queue_count}</div>
        <div class="text-sm text-zinc-900">Contested: {data.workbench.summary.contested_item_count}</div>
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
        <div class="mt-2 text-sm text-zinc-900">Read-only, provenance-first, no reasoning overlay</div>
        <div class="mt-2 text-xs text-zinc-600">
          {reopenNavigation?.current?.source_label ?? data.sourceLabel ?? 'latest linked source'}
        </div>
      </div>
    </div>

    <section class="mb-6 rounded border border-zinc-200 bg-white p-4">
      <div class="mb-4">
        <div class="text-xs uppercase tracking-[0.24em] text-zinc-500">Recent / source-centric reopen</div>
        <div class="mt-3 flex flex-wrap gap-2">
          {#each reopenNavigation?.recent_sources ?? data.sources ?? [] as source}
            <a class={`rounded border px-3 py-1 text-sm ${data.sourceLabel === source.source_label ? 'border-amber-300 bg-amber-50 text-amber-950' : 'border-zinc-200 bg-zinc-50 text-zinc-700'}`} href={hrefForSource(source)}>
              {source.source_label}
            </a>
          {/each}
        </div>
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
                {#each data.workbench.chronology_groups.dated_events as row}
                  <button class="mt-2 block w-full rounded border border-zinc-200 bg-white px-3 py-2 text-left text-sm" on:click={() => clickFact(row.fact_id)}>
                    <div class="font-medium">{row.event_type}</div>
                    <div class="text-xs text-zinc-600">{row.time_start} · {row.primary_actor ?? 'unknown actor'}</div>
                  </button>
                {/each}
              </div>
              <div class="rounded border border-zinc-200 bg-zinc-50 p-3">
                <div class="text-xs uppercase tracking-[0.18em] text-zinc-500">Approximate chronology</div>
                {#each data.workbench.chronology_groups.approximate_events as row}
                  <div class="mt-2 rounded border border-zinc-200 bg-white px-3 py-2 text-sm">
                    <div class="font-medium">{row.label ?? row.event_type}</div>
                    <div class="text-xs text-zinc-600">{row.time_start ?? 'approximate'}</div>
                  </div>
                {/each}
              </div>
              <div class="rounded border border-zinc-200 bg-zinc-50 p-3">
                <div class="text-xs uppercase tracking-[0.18em] text-zinc-500">Undated / contested chronology</div>
                {#each [...data.workbench.chronology_groups.undated_events, ...data.workbench.chronology_groups.contested_chronology_items] as row}
                  <div class="mt-2 rounded border border-zinc-200 bg-white px-3 py-2 text-sm">
                    <div class="font-medium">{row.label ?? row.event_type}</div>
                    <div class="text-xs text-zinc-600">{row.time_start ?? 'undated'}</div>
                  </div>
                {/each}
              </div>
            </div>
          {:else}
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
              </button>
            {/each}
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
            {#if selectedFact.latest_review_note}
              <div class="mt-2 rounded border border-zinc-200 bg-white px-3 py-2 text-sm text-zinc-800">
                Latest review note: {selectedFact.latest_review_note}
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
      <div class="mt-3 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        {#each data.acceptance?.stories ?? [] as story}
          <div class="rounded border border-zinc-200 bg-zinc-50 p-3">
            <div class="flex items-center justify-between gap-3">
              <div class="font-medium text-zinc-950">{story.story_id}</div>
              <div class={`rounded px-2 py-1 text-xs ${story.status === 'pass' ? 'bg-emerald-100 text-emerald-900' : story.status === 'partial' ? 'bg-amber-100 text-amber-900' : 'bg-rose-100 text-rose-900'}`}>
                {story.status}
              </div>
            </div>
            <div class="mt-1 text-sm text-zinc-700">{story.label}</div>
            <div class="mt-2 text-xs text-zinc-600">{story.passed_check_count}/{story.check_count} checks passed</div>
          </div>
        {/each}
      </div>
    </section>
  {/if}
</div>
