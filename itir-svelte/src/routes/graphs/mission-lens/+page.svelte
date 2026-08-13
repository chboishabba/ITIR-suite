<script lang="ts">
  import BipartiteGraph from '$lib/ui/BipartiteGraph.svelte';
  import LayeredGraph from '$lib/ui/LayeredGraph.svelte';

  export let form:
    | {
        ok?: boolean;
        error?: string;
      }
    | undefined;

  export let data: {
    date: string;
    runId: string;
    report: any;
    error: string | null;
  };

  const report = data.report ?? {};
  const summary = report.summary ?? {};
  const missionObserver = report.mission_observer ?? {};
  const planningGraph = report.planning_graph ?? { nodes: [], edges: [] };
  const actualAllocation = report.actual_allocation ?? { left: [], right: [], edges: [] };
  const layeredGraph = report.layered_graph ?? { layers: [], edges: [] };
  const deadlineSummary = report.deadline_summary ?? [];
  const driftSummary = report.drift_summary ?? [];
  const activityRows = report.activity_rows ?? [];
  const actualMappingSummary = report.actual_mapping_summary ?? {};
  const effectiveActualMappings = report.effective_actual_mappings ?? [];
  const reviewedActualMappings = report.reviewed_actual_mappings ?? [];
  let selectedPlanNodeId = '';
  let selectedActivityRefId = '';

  function certaintyTone(kind: string): string {
    if (kind === 'exact_time') return 'bg-rose-100 text-rose-900';
    if (kind === 'day_bound') return 'bg-amber-100 text-amber-900';
    if (kind === 'range_bound') return 'bg-sky-100 text-sky-900';
    if (kind === 'horizon_bound') return 'bg-zinc-100 text-zinc-800';
    return 'bg-zinc-100 text-zinc-600';
  }

  function urgencyTone(level: string): string {
    if (level === 'high') return 'bg-rose-100 text-rose-900';
    if (level === 'low') return 'bg-emerald-100 text-emerald-900';
    return 'bg-amber-100 text-amber-900';
  }

  function driftTone(status: string): string {
    if (status === 'over') return 'text-emerald-700';
    if (status === 'under') return 'text-rose-700';
    return 'text-zinc-600';
  }

  function mappingTone(kind: string): string {
    if (kind === 'reviewed') return 'bg-emerald-100 text-emerald-900';
    if (kind === 'lexical') return 'bg-sky-100 text-sky-900';
    return 'bg-amber-100 text-amber-900';
  }

  function mappingStatusTone(status: string): string {
    if (status === 'linked' || status === 'reassigned') return 'bg-emerald-100 text-emerald-900';
    if (status === 'abstained') return 'bg-amber-100 text-amber-900';
    if (status === 'unlinked') return 'bg-zinc-200 text-zinc-900';
    if (status === 'unmapped') return 'bg-zinc-100 text-zinc-700';
    return 'bg-sky-100 text-sky-900';
  }

  function recommendationTone(action: string): string {
    if (action === 'auto_link_safe') return 'bg-emerald-100 text-emerald-900';
    if (action === 'review_primary_vs_alternative') return 'bg-sky-100 text-sky-900';
    if (action === 'abstain_recommended') return 'bg-amber-100 text-amber-900';
    return 'bg-zinc-100 text-zinc-700';
  }

  $: selectedPlanNode =
    planningGraph.nodes?.find((row: any) => row.planNodeId === selectedPlanNodeId) ??
    planningGraph.nodes?.[0] ??
    null;
  $: selectedActivity =
    activityRows.find((row: any) => row.activityRefId === selectedActivityRefId) ??
    activityRows?.[0] ??
    null;
  $: selectedActivityCurrent =
    effectiveActualMappings.find((row: any) => row.activityRefId === selectedActivityRefId) ??
    null;
  $: if (!selectedActivityRefId) {
    const firstUnmapped = activityRows.find((row: any) => row.mappingSource === 'unmapped');
    selectedActivityRefId = firstUnmapped?.activityRefId ?? activityRows?.[0]?.activityRefId ?? '';
  }
  $: selectedActivityHistory = reviewedActualMappings.filter((row: any) => row.activityRefId === selectedActivityRefId) ?? [];
</script>

<svelte:head>
  <title>Mission Lens</title>
</svelte:head>

<div class="space-y-8">
  <section class="rounded-3xl border border-ink-950/10 bg-white/90 p-6 shadow-sm">
    <div class="flex flex-wrap items-end justify-between gap-4">
      <div class="space-y-2">
        <p class="text-xs uppercase tracking-[0.25em] text-ink-950/45">Mission Lens</p>
        <h1 class="text-3xl font-semibold tracking-tight text-ink-950">Actual vs Should</h1>
        <p class="max-w-3xl text-sm leading-6 text-ink-950/70">
          Fused ITIR-owned mission lens rendered against SB’s actual daily process surface. The left side shows where observed activity landed; the right side shows mission and planning nodes with deadlines, drift, and authored structure.
        </p>
      </div>
      <form method="GET" class="flex flex-wrap items-end gap-3">
        <label class="space-y-1 text-sm text-ink-950/70">
          <span>Date</span>
          <input class="rounded-xl border border-ink-950/15 px-3 py-2" type="date" name="date" value={data.date} />
        </label>
        <label class="space-y-1 text-sm text-ink-950/70">
          <span>Run ID</span>
          <input class="w-72 rounded-xl border border-ink-950/15 px-3 py-2" type="text" name="runId" value={report?.run_id ?? data.runId ?? ''} placeholder="Latest run by default" aria-label="Mission lens run id" />
        </label>
        <button class="rounded-full bg-ink-950 px-4 py-2 text-sm font-medium text-white" type="submit">Load lens</button>
      </form>
    </div>
    {#if data.error}
      <p class="mt-4 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800">{data.error}</p>
    {/if}
  </section>

  {#if report}
    <section class="grid gap-4 md:grid-cols-5">
      <article class="rounded-3xl border border-ink-950/10 bg-white/90 p-5 shadow-sm">
        <p class="text-xs uppercase tracking-[0.22em] text-ink-950/45">Planning Nodes</p>
        <p class="mt-2 text-3xl font-semibold text-ink-950">{summary.planning_node_count ?? 0}</p>
      </article>
      <article class="rounded-3xl border border-ink-950/10 bg-white/90 p-5 shadow-sm">
        <p class="text-xs uppercase tracking-[0.22em] text-ink-950/45">Deadlines</p>
        <p class="mt-2 text-3xl font-semibold text-ink-950">{summary.deadline_count ?? 0}</p>
      </article>
      <article class="rounded-3xl border border-ink-950/10 bg-white/90 p-5 shadow-sm">
        <p class="text-xs uppercase tracking-[0.22em] text-ink-950/45">Mapped Flows</p>
        <p class="mt-2 text-3xl font-semibold text-ink-950">{summary.mapped_actual_edge_count ?? 0}</p>
      </article>
      <article class="rounded-3xl border border-ink-950/10 bg-white/90 p-5 shadow-sm">
        <p class="text-xs uppercase tracking-[0.22em] text-ink-950/45">Reviewed Links</p>
        <p class="mt-2 text-3xl font-semibold text-ink-950">{summary.reviewed_actual_mapping_count ?? 0}</p>
      </article>
      <article class="rounded-3xl border border-ink-950/10 bg-white/90 p-5 shadow-sm">
        <p class="text-xs uppercase tracking-[0.22em] text-ink-950/45">Observer Missions</p>
        <p class="mt-2 text-3xl font-semibold text-ink-950">{missionObserver?.summary?.mission_count ?? 0}</p>
      </article>
      <article class="rounded-3xl border border-ink-950/10 bg-white/90 p-5 shadow-sm">
        <p class="text-xs uppercase tracking-[0.22em] text-ink-950/45">Safe Recs</p>
        <p class="mt-2 text-3xl font-semibold text-ink-950">{actualMappingSummary.recommended_safe ?? 0}</p>
      </article>
      <article class="rounded-3xl border border-ink-950/10 bg-white/90 p-5 shadow-sm">
        <p class="text-xs uppercase tracking-[0.22em] text-ink-950/45">Review Needed</p>
        <p class="mt-2 text-3xl font-semibold text-ink-950">{actualMappingSummary.recommended_review ?? 0}</p>
      </article>
      <article class="rounded-3xl border border-ink-950/10 bg-white/90 p-5 shadow-sm md:col-span-2">
        <p class="text-xs uppercase tracking-[0.22em] text-ink-950/45">Dashboard Scope</p>
        <p class="mt-2 text-lg font-semibold text-ink-950">{report?.sb_dashboard_source?.scope ?? 'n/a'}</p>
      </article>
    </section>

    <section class="rounded-3xl border border-ink-950/10 bg-white/90 p-6 shadow-sm">
      <div class="mb-4 flex items-center justify-between gap-4">
        <div>
          <h2 class="text-xl font-semibold text-ink-950">Fused Mission Flow</h2>
          <p class="text-sm text-ink-950/65">
            Bipartite flow between observed activity and mission/planning nodes. This is the current fused actual-vs-should surface.
          </p>
        </div>
      </div>
      <BipartiteGraph
        left={actualAllocation.left ?? []}
        right={actualAllocation.right ?? []}
        edges={actualAllocation.edges ?? []}
        height={Math.max(640, 90 * Math.max((actualAllocation.left ?? []).length, (actualAllocation.right ?? []).length))}
        on:nodeSelect={(event) => {
          const nodeId = String(event.detail.nodeId || '');
          if (nodeId.startsWith('plan:')) selectedPlanNodeId = nodeId.slice('plan:'.length);
        }}
      />
    </section>

    <section class="grid gap-6 xl:grid-cols-[1.7fr,1fr]">
      <article class="rounded-3xl border border-ink-950/10 bg-white/90 p-6 shadow-sm">
        <div class="mb-4">
          <h2 class="text-xl font-semibold text-ink-950">Mission / Phase / Task Graph</h2>
          <p class="text-sm text-ink-950/65">
            Hierarchy and containment graph seeded from observer missions and extended through authored planning nodes.
          </p>
        </div>
        <LayeredGraph layers={layeredGraph.layers ?? []} edges={layeredGraph.edges ?? []} />
      </article>

      <article class="space-y-6">
        <div class="rounded-3xl border border-ink-950/10 bg-white/90 p-6 shadow-sm">
          <h2 class="text-xl font-semibold text-ink-950">Selected Planning Node</h2>
          {#if selectedPlanNode}
            <div class="mt-4 space-y-3 text-sm text-ink-950/80">
              <p><strong>{selectedPlanNode.title}</strong> · {selectedPlanNode.nodeKind}</p>
              <p>Status: {selectedPlanNode.status}</p>
              <p>Source: {selectedPlanNode.sourceKind}</p>
              <p>Target weight: {selectedPlanNode.targetWeight}</p>
              {#if selectedPlanNode.receipts?.length}
                <div class="space-y-1">
                  <p class="text-xs uppercase tracking-[0.2em] text-ink-950/45">Receipts</p>
                  <div class="flex flex-wrap gap-2">
                    {#each selectedPlanNode.receipts as receipt}
                      <span class="rounded-full bg-zinc-100 px-3 py-1 text-xs text-zinc-800">{receipt.kind}: {receipt.value}</span>
                    {/each}
                  </div>
                </div>
              {/if}
              {#if selectedPlanNode.deadline?.rawPhrase}
                <p>Deadline phrase: {selectedPlanNode.deadline.rawPhrase}</p>
              {/if}
              <div class="flex flex-wrap gap-2">
                <span class={`rounded-full px-3 py-1 text-xs font-medium ${certaintyTone(selectedPlanNode.deadline?.certaintyKind ?? 'ambiguous')}`}>
                  {selectedPlanNode.deadline?.certaintyKind ?? 'ambiguous'}
                </span>
                <span class={`rounded-full px-3 py-1 text-xs font-medium ${urgencyTone(selectedPlanNode.deadline?.urgencyLevel ?? 'medium')}`}>
                  {selectedPlanNode.deadline?.urgencyLevel ?? 'medium'}
                </span>
                <span class="rounded-full bg-zinc-100 px-3 py-1 text-xs font-medium text-zinc-800">
                  {selectedPlanNode.deadline?.flexibilityLevel ?? 'flexible'}
                </span>
              </div>
            </div>
          {:else}
            <p class="mt-3 text-sm text-ink-950/65">No planning node is available yet.</p>
          {/if}
        </div>

        <div class="rounded-3xl border border-ink-950/10 bg-white/90 p-6 shadow-sm">
          <h2 class="text-xl font-semibold text-ink-950">Add Planning Node</h2>
          <form method="POST" action="?/addPlanNode" class="mt-4 grid gap-3">
            <input type="hidden" name="runId" value={report.run_id ?? ''} />
            <input type="hidden" name="date" value={data.date} />
            <label class="space-y-1 text-sm text-ink-950/70">
              <span>Title</span>
              <input class="w-full rounded-xl border border-ink-950/15 px-3 py-2" type="text" name="title" placeholder="Finish mission lens contract" aria-label="Mission title" />
            </label>
            <div class="grid gap-3 md:grid-cols-2">
              <label class="space-y-1 text-sm text-ink-950/70">
                <span>Node kind</span>
                <select class="w-full rounded-xl border border-ink-950/15 px-3 py-2" name="nodeKind">
                  <option value="mission">mission</option>
                  <option value="phase">phase</option>
                  <option value="task" selected>task</option>
                  <option value="subtask">subtask</option>
                  <option value="set">set</option>
                </select>
              </label>
              <label class="space-y-1 text-sm text-ink-950/70">
                <span>Parent plan node</span>
                <select class="w-full rounded-xl border border-ink-950/15 px-3 py-2" name="parentPlanNodeId">
                  <option value="">none</option>
                  {#each planningGraph.nodes ?? [] as node}
                    <option value={node.planNodeId}>{node.title}</option>
                  {/each}
                </select>
              </label>
            </div>
            <div class="grid gap-3 md:grid-cols-2">
              <label class="space-y-1 text-sm text-ink-950/70">
                <span>Target weight</span>
                <input class="w-full rounded-xl border border-ink-950/15 px-3 py-2" type="number" step="0.5" min="0" name="targetWeight" value="1" />
              </label>
              <label class="space-y-1 text-sm text-ink-950/70">
                <span>Status</span>
                <select class="w-full rounded-xl border border-ink-950/15 px-3 py-2" name="status">
                  <option value="active" selected>active</option>
                  <option value="blocked">blocked</option>
                  <option value="done">done</option>
                  <option value="obsolete">obsolete</option>
                </select>
              </label>
            </div>
            <label class="space-y-1 text-sm text-ink-950/70">
              <span>Raw deadline phrase</span>
              <input class="w-full rounded-xl border border-ink-950/15 px-3 py-2" type="text" name="rawDeadline" placeholder="close of business Friday / 2026-03-12 / sometime next week" aria-label="Deadline" />
            </label>
            <div class="grid gap-3 md:grid-cols-3">
              <label class="space-y-1 text-sm text-ink-950/70">
                <span>Due start</span>
                <input class="w-full rounded-xl border border-ink-950/15 px-3 py-2" type="text" name="dueStart" placeholder="2026-03-12 or 2026-03-12T17:00:00Z" aria-label="Start window" />
              </label>
              <label class="space-y-1 text-sm text-ink-950/70">
                <span>Certainty</span>
                <select class="w-full rounded-xl border border-ink-950/15 px-3 py-2" name="certaintyKind">
                  <option value="">infer</option>
                  <option value="exact_time">exact_time</option>
                  <option value="day_bound">day_bound</option>
                  <option value="range_bound">range_bound</option>
                  <option value="horizon_bound">horizon_bound</option>
                  <option value="ambiguous">ambiguous</option>
                </select>
              </label>
              <label class="space-y-1 text-sm text-ink-950/70">
                <span>Urgency</span>
                <select class="w-full rounded-xl border border-ink-950/15 px-3 py-2" name="urgencyLevel">
                  <option value="">infer</option>
                  <option value="high">high</option>
                  <option value="medium">medium</option>
                  <option value="low">low</option>
                </select>
              </label>
            </div>
            <button class="mt-2 rounded-full bg-ink-950 px-4 py-2 text-sm font-medium text-white" type="submit">Create planning node</button>
            {#if form?.error}
              <p class="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800">{form.error}</p>
            {/if}
          </form>
        </div>

        <div class="rounded-3xl border border-ink-950/10 bg-white/90 p-6 shadow-sm">
          <h2 class="text-xl font-semibold text-ink-950">Review Actual Mapping</h2>
          <p class="mt-2 text-sm text-ink-950/65">
            Reviewed actions override lexical fallback in mission drift/accounting. Link, reassign, unlink, or explicitly abstain from mapping the selected activity.
          </p>
          {#if selectedActivity}
            <div class="mt-4 space-y-4">
              <label class="space-y-1 text-sm text-ink-950/70">
                <span>Observed activity</span>
                <select class="w-full rounded-xl border border-ink-950/15 px-3 py-2" name="activityRefId" bind:value={selectedActivityRefId}>
                  {#each activityRows as row}
                    <option value={row.activityRefId}>
                      {row.ts || 'no-ts'} · {row.kind} · {(row.detail || row.sourcePath || row.activityRefId).slice(0, 88)}
                    </option>
                  {/each}
                </select>
              </label>
              <div class="rounded-2xl border border-ink-950/10 px-4 py-3">
                <div class="flex flex-wrap items-center justify-between gap-3">
                  <p class="font-medium text-ink-950">{selectedActivity.kind} · {selectedActivity.ts || 'no timestamp'}</p>
                  <div class="flex flex-wrap gap-2">
                    <span class={`rounded-full px-3 py-1 text-xs font-medium ${mappingTone(selectedActivity.mappingSource)}`}>{selectedActivity.mappingSource}</span>
                    <span class={`rounded-full px-3 py-1 text-xs font-medium ${mappingStatusTone(selectedActivity.mappingStatus)}`}>{selectedActivity.mappingStatus}</span>
                    {#if selectedActivity.recommendedAction && selectedActivity.recommendedAction !== 'none'}
                      <span class={`rounded-full px-3 py-1 text-xs font-medium ${recommendationTone(selectedActivity.recommendedAction)}`}>
                        recommended: {selectedActivity.recommendedAction}
                      </span>
                    {/if}
                  </div>
                </div>
                <p class="mt-2 text-sm text-ink-950/75">{selectedActivity.detail || selectedActivity.sourcePath || selectedActivity.activityRefId}</p>
                {#if selectedActivity.effectivePlanNodeId}
                  <p class="mt-2 text-xs text-ink-950/55">Effective plan node: {selectedActivity.effectivePlanNodeId}</p>
                {/if}
                {#if selectedActivityCurrent}
                  <div class="mt-3 rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3">
                    <p class="text-xs uppercase tracking-[0.2em] text-emerald-900/55">Effective Provenance</p>
                    <p class="mt-2 text-sm text-emerald-950">
                      {selectedActivityCurrent.mappingKind} · {selectedActivityCurrent.status} · {selectedActivityCurrent.updatedAt}
                    </p>
                    {#if selectedActivityCurrent.receipts?.length}
                      <div class="mt-3 flex flex-wrap gap-2">
                        {#each selectedActivityCurrent.receipts as receipt}
                          {#if receipt.kind !== 'activity_ref_id'}
                            <span class="rounded-full bg-white/80 px-3 py-1 text-xs font-medium text-emerald-950">
                              {receipt.kind}: {receipt.value}
                            </span>
                          {/if}
                        {/each}
                      </div>
                    {/if}
                  </div>
                {/if}
                {#if selectedActivity.recommendedAction && selectedActivity.recommendedAction !== 'none'}
                  <p class="mt-2 text-xs text-ink-950/60">
                    {selectedActivity.recommendationReason} · confidence {selectedActivity.recommendationConfidence}
                  </p>
                {/if}
                {#if selectedActivity.lexicalExplanation}
                  <div class="mt-3 rounded-2xl border border-sky-200 bg-sky-50 px-4 py-3">
                    <p class="text-xs uppercase tracking-[0.2em] text-sky-900/55">Lexical Explanation</p>
                    <p class="mt-2 text-sm text-sky-950">
                      Matched <strong>{selectedActivity.lexicalExplanation.matchedTitle}</strong> via {selectedActivity.lexicalExplanation.matchedFields.join(', ')}.
                    </p>
                    {#if selectedActivity.lexicalExplanation.snippets?.length}
                      {#each selectedActivity.lexicalExplanation.snippets as snippet}
                        <p class="mt-1 text-xs text-sky-900/80">{snippet.field}: {snippet.snippet}</p>
                      {/each}
                    {/if}
                    {#if selectedActivity.lexicalExplanation.topAlternative}
                      <div class="mt-3 rounded-xl border border-sky-300/60 bg-white/80 px-3 py-2">
                        <p class="text-xs uppercase tracking-[0.18em] text-sky-900/55">Top Alternative</p>
                        <p class="mt-1 text-sm text-sky-950">
                          {selectedActivity.lexicalExplanation.topAlternative.matchedTitle} via {selectedActivity.lexicalExplanation.topAlternative.matchedFields.join(', ')}
                        </p>
                        <form method="POST" action="?/addActualMapping" class="mt-3">
                          <input type="hidden" name="runId" value={report.run_id ?? ''} />
                          <input type="hidden" name="date" value={data.date} />
                          <input type="hidden" name="planNodeId" value={selectedActivity.lexicalExplanation.topAlternative.planNodeId} />
                          <input type="hidden" name="activityRefId" value={selectedActivity.activityRefId} />
                          <input type="hidden" name="authoring" value="mission_lens_lexical_top_alternative" />
                          <input type="hidden" name="recommendationKind" value="accepted_top_alternative" />
                          <input type="hidden" name="recommendationReason" value={selectedActivity.recommendationReason ?? 'accepted top lexical alternative'} />
                          <input type="hidden" name="note" value="Accepted top alternative from lexical explanation" />
                          <button class="rounded-full bg-sky-700 px-3 py-2 text-xs font-medium text-white" type="submit">
                            Link to top alternative
                          </button>
                        </form>
                      </div>
                    {/if}
                    <form method="POST" action="?/addActualMapping" class="mt-3">
                      <input type="hidden" name="runId" value={report.run_id ?? ''} />
                      <input type="hidden" name="date" value={data.date} />
                      <input type="hidden" name="planNodeId" value={selectedActivity.lexicalExplanation.planNodeId} />
                      <input type="hidden" name="activityRefId" value={selectedActivity.activityRefId} />
                      <input type="hidden" name="authoring" value="mission_lens_lexical_primary" />
                      <input type="hidden" name="recommendationKind" value="accepted_primary_lexical_match" />
                      <input type="hidden" name="recommendationReason" value={selectedActivity.recommendationReason ?? 'accepted primary lexical match'} />
                      <input type="hidden" name="note" value="Accepted primary lexical match" />
                      <button class="rounded-full bg-emerald-700 px-3 py-2 text-xs font-medium text-white" type="submit">
                        Keep primary lexical match
                      </button>
                    </form>
                  </div>
                {/if}
              </div>
              <div class="grid gap-3">
                <form method="POST" action="?/addActualMapping" class="grid gap-2 rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3">
                  <input type="hidden" name="runId" value={report.run_id ?? ''} />
                  <input type="hidden" name="date" value={data.date} />
                  <input type="hidden" name="planNodeId" value={selectedPlanNode?.planNodeId ?? ''} />
                  <input type="hidden" name="activityRefId" value={selectedActivity.activityRefId} />
                  <input type="hidden" name="authoring" value="mission_lens_manual_link" />
                  <input class="w-full rounded-xl border border-emerald-300/70 px-3 py-2 text-sm" type="text" name="note" placeholder="Reviewed link from mission lens" aria-label="Note for review link" />
                  <button class="rounded-full bg-emerald-700 px-4 py-2 text-sm font-medium text-white" type="submit" disabled={!selectedPlanNode}>
                    Link to selected node
                  </button>
                </form>
                <form method="POST" action="?/reassignActualMapping" class="grid gap-2 rounded-2xl border border-sky-200 bg-sky-50 px-4 py-3">
                  <input type="hidden" name="runId" value={report.run_id ?? ''} />
                  <input type="hidden" name="date" value={data.date} />
                  <input type="hidden" name="planNodeId" value={selectedPlanNode?.planNodeId ?? ''} />
                  <input type="hidden" name="activityRefId" value={selectedActivity.activityRefId} />
                  <input class="w-full rounded-xl border border-sky-300/70 px-3 py-2 text-sm" type="text" name="note" placeholder="Reassign this activity to the selected node" aria-label="Note for reassign activity" />
                  <button class="rounded-full bg-sky-700 px-4 py-2 text-sm font-medium text-white" type="submit" disabled={!selectedPlanNode}>
                    Reassign to selected node
                  </button>
                </form>
                <div class="grid gap-3 md:grid-cols-2">
                  <form method="POST" action="?/unlinkActualMapping" class="grid gap-2 rounded-2xl border border-zinc-200 bg-zinc-50 px-4 py-3">
                    <input type="hidden" name="runId" value={report.run_id ?? ''} />
                    <input type="hidden" name="date" value={data.date} />
                    <input type="hidden" name="activityRefId" value={selectedActivity.activityRefId} />
                    <input class="w-full rounded-xl border border-zinc-300/70 px-3 py-2 text-sm" type="text" name="note" placeholder="Explicitly unlink this activity" aria-label="Note for unlink activity" />
                    <button class="rounded-full bg-zinc-700 px-4 py-2 text-sm font-medium text-white" type="submit">
                      Unlink
                    </button>
                  </form>
                  <form method="POST" action="?/abstainActualMapping" class="grid gap-2 rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3">
                    <input type="hidden" name="runId" value={report.run_id ?? ''} />
                    <input type="hidden" name="date" value={data.date} />
                    <input type="hidden" name="activityRefId" value={selectedActivity.activityRefId} />
                    <input class="w-full rounded-xl border border-amber-300/70 px-3 py-2 text-sm" type="text" name="note" placeholder="Reviewed but left unresolved" aria-label="Note for unresolved activity" />
                    <button class="rounded-full bg-amber-700 px-4 py-2 text-sm font-medium text-white" type="submit">
                      Abstain / leave unresolved
                    </button>
                  </form>
                </div>
              </div>
            </div>
          {:else}
            <p class="mt-4 text-sm text-ink-950/65">No activity rows are available to review for this date.</p>
          {/if}
        </div>
      </article>
    </section>

    <section class="grid gap-6 xl:grid-cols-[1.15fr,1fr]">
      <article class="rounded-3xl border border-ink-950/10 bg-white/90 p-6 shadow-sm">
        <div class="flex items-center justify-between gap-4">
          <div>
            <h2 class="text-xl font-semibold text-ink-950">Observed Activity Rows</h2>
            <p class="text-sm text-ink-950/65">
              Concrete daily activity rows with current mapping status.
            </p>
          </div>
          <div class="flex flex-col items-end gap-3">
            {#if (actualMappingSummary.recommended_safe ?? 0) > 0}
              <form method="POST" action="?/applySafeRecommendations">
                <input type="hidden" name="runId" value={report.run_id ?? ''} />
                <input type="hidden" name="date" value={data.date} />
                <button class="rounded-full bg-emerald-700 px-4 py-2 text-sm font-medium text-white" type="submit">
                  Apply Safe Recommendations
                </button>
              </form>
            {/if}
            <div class="flex flex-wrap justify-end gap-2 text-xs">
              <span class={`rounded-full px-3 py-1 font-medium ${mappingTone('reviewed')}`}>reviewed {actualMappingSummary.reviewed_linked ?? 0}</span>
              <span class={`rounded-full px-3 py-1 font-medium ${mappingTone('reviewed')}`}>reassigned {actualMappingSummary.reviewed_reassigned ?? 0}</span>
              <span class={`rounded-full px-3 py-1 font-medium ${mappingStatusTone('abstained')}`}>abstained {actualMappingSummary.reviewed_abstained ?? 0}</span>
              <span class={`rounded-full px-3 py-1 font-medium ${mappingStatusTone('unlinked')}`}>unlinked {actualMappingSummary.reviewed_unlinked ?? 0}</span>
              <span class={`rounded-full px-3 py-1 font-medium ${mappingTone('lexical')}`}>lexical {actualMappingSummary.lexical_linked ?? 0}</span>
              <span class={`rounded-full px-3 py-1 font-medium ${mappingTone('lexical')}`}>lexical ambiguous {actualMappingSummary.lexical_ambiguous ?? 0}</span>
              <span class={`rounded-full px-3 py-1 font-medium ${recommendationTone('auto_link_safe')}`}>safe recs {actualMappingSummary.recommended_safe ?? 0}</span>
              <span class={`rounded-full px-3 py-1 font-medium ${recommendationTone('review_primary_vs_alternative')}`}>review recs {actualMappingSummary.recommended_review ?? 0}</span>
              <span class={`rounded-full px-3 py-1 font-medium ${recommendationTone('abstain_recommended')}`}>abstain recs {actualMappingSummary.recommended_abstain ?? 0}</span>
              <span class={`rounded-full px-3 py-1 font-medium ${mappingTone('unmapped')}`}>unmapped {actualMappingSummary.unmapped ?? 0}</span>
            </div>
          </div>
        </div>
        <div class="mt-4 space-y-3">
          {#if activityRows.length}
            {#each activityRows.slice(0, 24) as row}
              <button
                class={`w-full rounded-2xl border px-4 py-3 text-left ${selectedActivityRefId === row.activityRefId ? 'border-ink-950/35 bg-zinc-50' : 'border-ink-950/10 bg-white'}`}
                type="button"
                on:click={() => {
                  selectedActivityRefId = row.activityRefId;
                  if (row.matchedPlanNodeIds?.[0]) selectedPlanNodeId = row.matchedPlanNodeIds[0];
                }}
              >
                <div class="flex flex-wrap items-center justify-between gap-3">
                  <p class="font-medium text-ink-950">{row.kind} · {row.ts || 'no timestamp'}</p>
                  <div class="flex flex-wrap gap-2">
                    <span class={`rounded-full px-3 py-1 text-xs font-medium ${mappingTone(row.mappingSource)}`}>{row.mappingSource}</span>
                    <span class={`rounded-full px-3 py-1 text-xs font-medium ${mappingStatusTone(row.mappingStatus)}`}>{row.mappingStatus}</span>
                    {#if row.recommendedAction && row.recommendedAction !== 'none'}
                      <span class={`rounded-full px-3 py-1 text-xs font-medium ${recommendationTone(row.recommendedAction)}`}>{row.recommendedAction}</span>
                    {/if}
                  </div>
                </div>
                <p class="mt-2 text-sm text-ink-950/75">{row.detail || row.sourcePath || row.activityRefId}</p>
                {#if row.matchedPlanNodeIds?.length}
                  <p class="mt-2 text-xs text-ink-950/55">Linked plan nodes: {row.matchedPlanNodeIds.join(', ')}</p>
                {/if}
                {#if row.lexicalExplanation}
                  <p class="mt-2 text-xs text-sky-800">Lexical match: {row.lexicalExplanation.matchedTitle} via {row.lexicalExplanation.matchedFields.join(', ')}</p>
                {/if}
                {#if row.recommendedAction && row.recommendedAction !== 'none'}
                  <p class="mt-2 text-xs text-ink-950/55">{row.recommendationReason}</p>
                {/if}
              </button>
            {/each}
          {:else}
            <p class="text-sm text-ink-950/65">No observed activity rows were available for this date.</p>
          {/if}
        </div>
      </article>

      <article class="rounded-3xl border border-ink-950/10 bg-white/90 p-6 shadow-sm">
        <h2 class="text-xl font-semibold text-ink-950">Deadline Semantics</h2>
        <div class="mt-4 space-y-3">
          {#if deadlineSummary.length}
            {#each deadlineSummary as row}
              <div class="rounded-2xl border border-ink-950/10 px-4 py-3">
                <div class="flex flex-wrap items-center justify-between gap-3">
                  <p class="font-medium text-ink-950">{row.title}</p>
                  <div class="flex flex-wrap gap-2">
                    <span class={`rounded-full px-3 py-1 text-xs font-medium ${certaintyTone(row.certaintyKind ?? 'ambiguous')}`}>{row.certaintyKind ?? 'ambiguous'}</span>
                    <span class={`rounded-full px-3 py-1 text-xs font-medium ${urgencyTone(row.urgencyLevel ?? 'medium')}`}>{row.urgencyLevel ?? 'medium'}</span>
                    <span class="rounded-full bg-zinc-100 px-3 py-1 text-xs font-medium text-zinc-800">{row.flexibilityLevel ?? 'flexible'}</span>
                  </div>
                </div>
                {#if row.rawPhrase}
                  <p class="mt-2 text-sm text-ink-950/70">Phrase: {row.rawPhrase}</p>
                {/if}
                {#if row.dueStart || row.dueEnd}
                  <p class="mt-1 text-sm text-ink-950/70">Normalized: {row.dueStart ?? 'n/a'}{row.dueEnd && row.dueEnd !== row.dueStart ? ` → ${row.dueEnd}` : ''}</p>
                {/if}
              </div>
            {/each}
          {:else}
            <p class="text-sm text-ink-950/65">No mission deadlines are available yet.</p>
          {/if}
        </div>
      </article>

      <article class="rounded-3xl border border-ink-950/10 bg-white/90 p-6 shadow-sm">
        <h2 class="text-xl font-semibold text-ink-950">Drift Summary</h2>
        <div class="mt-4 space-y-3">
          {#if driftSummary.length}
            {#each driftSummary.slice(0, 16) as row}
              <div class="flex items-center justify-between gap-4 rounded-2xl border border-ink-950/10 px-4 py-3">
                <div>
                  <p class="font-medium text-ink-950">{row.title}</p>
                  <p class="text-xs text-ink-950/55">Actual {row.actualWeight.toFixed(0)} · Target {row.targetWeight.toFixed(0)}</p>
                </div>
                <p class={`text-sm font-semibold ${driftTone(row.status)}`}>
                  {row.drift > 0 ? '+' : ''}{row.drift.toFixed(1)}
                </p>
              </div>
            {/each}
          {:else}
            <p class="text-sm text-ink-950/65">No drift rows are available yet.</p>
          {/if}
        </div>
      </article>
    </section>

    <section class="rounded-3xl border border-ink-950/10 bg-white/90 p-6 shadow-sm">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <h2 class="text-xl font-semibold text-ink-950">Reviewed Mapping History</h2>
        <span class="rounded-full bg-zinc-100 px-3 py-1 text-xs font-medium text-zinc-800">effective {effectiveActualMappings.length}</span>
      </div>
      <div class="mt-4 space-y-3">
        {#if selectedActivityHistory.length}
          {#each selectedActivityHistory as mapping}
            <div class="rounded-2xl border border-ink-950/10 px-4 py-3">
              <div class="flex flex-wrap items-center justify-between gap-3">
                <p class="font-medium text-ink-950">
                  {mapping.activityRefId}{mapping.planNodeId ? ` → ${mapping.planNodeId}` : ''}
                </p>
                <div class="flex flex-wrap gap-2">
                  <span class="rounded-full bg-emerald-100 px-3 py-1 text-xs font-medium text-emerald-900">{mapping.mappingKind}</span>
                  <span class={`rounded-full px-3 py-1 text-xs font-medium ${mappingStatusTone(mapping.status)}`}>{mapping.status}</span>
                  <span class="rounded-full bg-zinc-100 px-3 py-1 text-xs font-medium text-zinc-800">{mapping.confidenceTier}</span>
                </div>
              </div>
              <p class="mt-1 text-xs text-ink-950/55">{mapping.createdAt}</p>
              {#if mapping.note}
                <p class="mt-2 text-sm text-ink-950/70">{mapping.note}</p>
              {/if}
              {#if mapping.receipts?.length}
                <div class="mt-3 flex flex-wrap gap-2">
                  {#each mapping.receipts as receipt}
                    {#if receipt.kind !== 'activity_ref_id'}
                      <span class="rounded-full bg-zinc-100 px-3 py-1 text-xs font-medium text-zinc-800">
                        {receipt.kind}: {receipt.value}
                      </span>
                    {/if}
                  {/each}
                </div>
              {/if}
            </div>
          {/each}
        {:else}
          <p class="text-sm text-ink-950/65">No reviewed mapping history exists for the selected activity yet.</p>
        {/if}
      </div>
    </section>
  {/if}
</div>
