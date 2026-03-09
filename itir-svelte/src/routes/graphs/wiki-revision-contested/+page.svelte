<script lang="ts">
  import LayeredGraph, { type LayerNode, type LayeredEdge } from '$lib/ui/LayeredGraph.svelte';
  import Panel from '$lib/ui/Panel.svelte';

  type PageState =
    | 'load_error'
    | 'producer_error'
    | 'graph_not_enabled'
    | 'missing_graph_payload'
    | 'graph_ready'
    | 'no_graph';
  type PanelTone = 'neutral' | 'warn';

  export let data: {
    payload: any;
    error: string | null;
  };

  $: payload = data.payload ?? {};
  $: summary = payload.summary ?? {};
  $: selectedPack = (payload.packs ?? []).find((row: any) => row.pack_id === payload.selected_pack_id) ?? null;
  $: packGraphEnabled = Boolean(selectedPack?.graph_enabled);
  $: triage = summary.pack_triage ?? {};
  $: articles = summary.articles ?? [];
  $: selectedArticle = articles.find((row: any) => row.article_id === payload.selected_article_id) ?? articles[0] ?? null;
  $: graph = payload.selected_graph ?? null;
  $: graphSummary = graph?.summary ?? selectedArticle?.contested_graph_summary ?? null;
  $: topArticles = triage.top_contested_graphs ?? [];
  $: topCycles = triage.top_contested_cycles ?? [];
  $: topRegions = triage.top_contested_regions ?? [];
  $: topPairs = triage.top_high_severity_pairs ?? [];
  $: selectedArticleStatus = String(selectedArticle?.status ?? '').toLowerCase();
  $: selectedArticleError = selectedArticle?.error ?? null;
  $: hasGraphPayload = Boolean(graphSummary);
  $: hasGraphCounts = Boolean(summary.contested_graph_counts);
  let selectedGraphNodeId: string | null = null;
  $: pageState = (data.error
    ? 'load_error'
    : selectedArticleStatus === 'error'
      ? 'producer_error'
      : selectedArticle && !packGraphEnabled
        ? 'graph_not_enabled'
      : selectedArticle && selectedArticle.contested_graph_available && !hasGraphPayload
        ? 'missing_graph_payload'
        : selectedArticle && hasGraphPayload
          ? 'graph_ready'
          : 'no_graph') as PageState;
  $: pageStateTone = (pageState === 'producer_error' || pageState === 'missing_graph_payload' ? 'warn' : 'neutral') as PanelTone;
  $: cycleRegionIds = new Set((graph?.cycles ?? []).map((row: any) => String(row.region_id ?? '')).filter(Boolean));
  $: graphPairNodes = (graph?.selected_pairs ?? []).map((pair: any) => ({
    id: String(pair.pair_id ?? ''),
    label: `${pair.pair_kind} ${pair.top_severity ?? 'none'}`,
    fullLabel: `${pair.pair_kind} | ${pair.older_revid} → ${pair.newer_revid} | score=${pair.candidate_score}`,
    tooltip: `${pair.pair_id}\n${pair.older_revid} → ${pair.newer_revid}\nseverity=${pair.top_severity ?? 'none'}`,
    color:
      pair.top_severity === 'high'
        ? '#fee2e2'
        : pair.top_severity === 'medium'
          ? '#fef3c7'
          : '#e5e7eb',
    scale: 1
  })) as LayerNode[];
  $: graphRegionNodes = (graph?.regions ?? []).map((region: any) => ({
    id: String(region.region_id ?? ''),
    label: `${region.title} (${region.touch_count ?? 0})`,
    fullLabel: `${region.title} | touches=${region.touch_count ?? 0} | bytes=${region.total_touched_bytes ?? 0} | heat=${region.graph_heat ?? 0}`,
    tooltip: `${region.title}\nseverity=${region.highest_severity ?? 'none'}\ntouches=${region.touch_count ?? 0}\ncycle=${cycleRegionIds.has(String(region.region_id ?? '')) ? 'yes' : 'no'}`,
    color: cycleRegionIds.has(String(region.region_id ?? ''))
      ? '#fecaca'
      : region.highest_severity === 'high'
        ? '#fde68a'
        : region.highest_severity === 'medium'
          ? '#fef3c7'
          : '#dbeafe',
    scale: Math.max(0.9, Math.min(1.9, 0.9 + Number(region.touch_count ?? 0) * 0.18))
  })) as LayerNode[];
  $: graphEventNodes = (graph?.events ?? []).slice(0, 16).map((event: any) => ({
    id: String(event.event_id ?? ''),
    label: String(event.event_id ?? ''),
    tooltip: `event ${event.event_id}`,
    color: '#e9d5ff',
    scale: 0.9
  })) as LayerNode[];
  $: graphEpistemicNodes = (graph?.epistemic_surfaces ?? []).slice(0, 12).map((epi: any) => ({
    id: String(epi.epistemic_id ?? ''),
    label: String(epi.event_id ?? epi.epistemic_id ?? ''),
    fullLabel: `${epi.epistemic_id} | event=${epi.event_id ?? ''}`,
    tooltip: `${epi.epistemic_id}\nevent=${epi.event_id ?? ''}`,
    color: '#c7d2fe',
    scale: 0.9
  })) as LayerNode[];
  $: graphLayers = [
    { id: 'pairs', title: 'Pairs', nodes: graphPairNodes },
    { id: 'regions', title: 'Regions', nodes: graphRegionNodes },
    { id: 'events', title: 'Events', nodes: graphEventNodes },
    { id: 'epistemic', title: 'Epistemic', nodes: graphEpistemicNodes }
  ].filter((layer) => layer.nodes.length);
  $: graphNodeIds = new Set(graphLayers.flatMap((layer) => layer.nodes.map((node) => node.id)));
  $: graphEdges = (graph?.edges ?? [])
    .filter((edge: any) => graphNodeIds.has(String(edge.source_id ?? '')) && graphNodeIds.has(String(edge.target_id ?? '')))
    .map((edge: any) => ({
      id: String(edge.edge_id ?? `${edge.source_id ?? ''}:${edge.target_id ?? ''}:${edge.edge_kind ?? ''}`),
      from: String(edge.source_id ?? ''),
      to: String(edge.target_id ?? ''),
      label:
        edge.edge_kind === 'touches_region'
          ? undefined
          : edge.edge_kind === 'co_occurs_in_region'
            ? 'co'
            : edge.edge_kind === 'returns_to_region'
              ? 'cycle'
              : edge.edge_kind === 'changes_attribution'
                ? 'attr'
                : edge.edge_kind === 'changes_event'
                  ? 'event'
                  : edge.edge_kind === 'revises_after'
                    ? 'next'
                    : edge.edge_kind === 'escalates_region'
                      ? 'sev'
                      : undefined,
      kind:
        edge.edge_kind === 'revises_after'
          ? 'sequence'
          : edge.edge_kind === 'changes_attribution' || edge.edge_kind === 'changes_event'
            ? 'evidence'
            : edge.edge_kind === 'co_occurs_in_region' || edge.edge_kind === 'returns_to_region' || edge.edge_kind === 'escalates_region'
              ? 'context'
              : 'role'
    })) as LayeredEdge[];
  $: graphNodeLookup = new Map(
    graphLayers.flatMap((layer) => layer.nodes.map((node) => [node.id, { ...node, layerTitle: layer.title }]))
  );
  $: selectedGraphNode = selectedGraphNodeId ? graphNodeLookup.get(selectedGraphNodeId) ?? null : null;
</script>

<div class="space-y-4 p-6">
  <Panel>
    <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Contested region graphs</div>
    <div class="mt-2 text-sm text-ink-950">
      Hybrid revision-churn + extraction/epistemic graph over bounded contested Wikipedia history windows.
    </div>
    <div class="mt-3 grid gap-3 md:grid-cols-3">
      <label class="text-sm">
        <div class="mb-1 text-xs uppercase tracking-[0.2em] text-ink-800/60">Pack</div>
        <select
          class="w-full rounded-md border border-ink-950/15 bg-white px-2 py-1.5 text-sm"
          value={payload.selected_pack_id ?? ''}
          on:change={(e) => {
            const next = (e.currentTarget as HTMLSelectElement).value;
            window.location.href = `/graphs/wiki-revision-contested?pack=${encodeURIComponent(next)}`;
          }}
        >
          {#each payload.packs ?? [] as pack}
            <option value={pack.pack_id}>{pack.pack_id}</option>
          {/each}
        </select>
      </label>
      <label class="text-sm">
        <div class="mb-1 text-xs uppercase tracking-[0.2em] text-ink-800/60">Run</div>
        <select
          class="w-full rounded-md border border-ink-950/15 bg-white px-2 py-1.5 text-sm"
          value={payload.selected_run_id ?? ''}
          on:change={(e) => {
            const next = (e.currentTarget as HTMLSelectElement).value;
            window.location.href = `/graphs/wiki-revision-contested?pack=${encodeURIComponent(payload.selected_pack_id ?? '')}&run=${encodeURIComponent(next)}`;
          }}
        >
          {#each payload.runs ?? [] as run}
            <option value={run.run_id}>{run.run_id}</option>
          {/each}
        </select>
      </label>
      <label class="text-sm">
        <div class="mb-1 text-xs uppercase tracking-[0.2em] text-ink-800/60">Article</div>
        <select
          class="w-full rounded-md border border-ink-950/15 bg-white px-2 py-1.5 text-sm"
          value={payload.selected_article_id ?? ''}
          on:change={(e) => {
            const next = (e.currentTarget as HTMLSelectElement).value;
            window.location.href = `/graphs/wiki-revision-contested?pack=${encodeURIComponent(payload.selected_pack_id ?? '')}&run=${encodeURIComponent(payload.selected_run_id ?? '')}&article=${encodeURIComponent(next)}`;
          }}
        >
          {#each articles as article}
            <option value={article.article_id}>{article.article_id}</option>
          {/each}
        </select>
      </label>
    </div>
    <div class="mt-3 text-xs text-ink-800/60">
      DB: <span class="font-mono">{payload.db_path}</span>
    </div>
  </Panel>

  {#if data.error}
    <Panel tone="danger">
      <div class="text-xs uppercase tracking-[0.28em] text-red-800/80">Load error</div>
      <pre class="mt-3 whitespace-pre-wrap font-mono text-xs text-ink-950">{data.error}</pre>
    </Panel>
  {/if}

  {#if !data.error && selectedArticle}
    <Panel tone={pageStateTone}>
      <div class="flex flex-wrap items-center gap-2">
        <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Selected article status</div>
        <span class="rounded bg-white/80 px-2 py-0.5 font-mono text-[11px] text-ink-950">{pageState}</span>
      </div>
      {#if pageState === 'producer_error'}
        <div class="mt-2 text-sm text-ink-950">
          This article row is a producer-run error, so contested graph detail is unavailable for this run.
        </div>
        {#if selectedArticleError}
          <pre class="mt-3 whitespace-pre-wrap rounded-lg border border-ink-950/10 bg-white p-3 font-mono text-xs text-ink-950">{selectedArticleError}</pre>
        {/if}
      {:else if pageState === 'missing_graph_payload'}
        <div class="mt-2 text-sm text-ink-950">
          The run marked a contested graph as available, but the selected graph payload did not hydrate. This is a contract/read-path problem rather than a producer error row.
        </div>
        {#if selectedArticle.contested_graph_path}
          <div class="mt-3 text-xs text-ink-800/70">
            expected graph artifact: <span class="font-mono">{selectedArticle.contested_graph_path}</span>
          </div>
        {/if}
      {:else if pageState === 'graph_not_enabled'}
        <div class="mt-2 text-sm text-ink-950">
          This pack does not have contested-region graph generation enabled. Pair reports and article diffs may exist, but graph detail is not expected for this run.
        </div>
      {:else if pageState === 'graph_ready'}
        <div class="mt-2 text-sm text-ink-950">
          Graph-backed contested detail is available for this article and run.
        </div>
      {:else}
        <div class="mt-2 text-sm text-ink-950">
          No contested graph is available for the selected article in this run.
        </div>
      {/if}
      <div class="mt-3 flex flex-wrap gap-2 text-[11px] text-ink-800/70">
        <span class="rounded bg-white/80 px-2 py-0.5 font-mono">article_status={selectedArticleStatus || 'none'}</span>
        <span class="rounded bg-white/80 px-2 py-0.5 font-mono">pack_graph_enabled={packGraphEnabled ? 'true' : 'false'}</span>
        <span class="rounded bg-white/80 px-2 py-0.5 font-mono">graph_available={selectedArticle.contested_graph_available ? 'true' : 'false'}</span>
        <span class="rounded bg-white/80 px-2 py-0.5 font-mono">graph_payload={hasGraphPayload ? 'true' : 'false'}</span>
        <span class="rounded bg-white/80 px-2 py-0.5 font-mono">graph_counts={hasGraphCounts ? 'true' : 'false'}</span>
      </div>
    </Panel>
  {/if}

  <div class="grid gap-4 xl:grid-cols-[1.1fr_0.9fr]">
    <Panel>
      <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Run summary</div>
      <div class="mt-1 text-xs text-ink-800/60">Pack-level totals for the selected run across all monitored articles.</div>
      <div class="mt-3 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <div class="rounded-lg border border-ink-950/10 bg-white p-3">
          <div class="text-[11px] uppercase tracking-[0.2em] text-ink-800/60">Changed</div>
          <div class="mt-1 text-2xl font-semibold text-ink-950">{summary.counts?.changed ?? 0}</div>
        </div>
        <div class="rounded-lg border border-ink-950/10 bg-white p-3">
          <div class="text-[11px] uppercase tracking-[0.2em] text-ink-800/60">Pairs</div>
          <div class="mt-1 text-2xl font-semibold text-ink-950">{summary.candidate_pair_counts?.reported ?? 0}</div>
        </div>
        <div class="rounded-lg border border-ink-950/10 bg-white p-3">
          <div class="text-[11px] uppercase tracking-[0.2em] text-ink-800/60">Regions</div>
          <div class="mt-1 text-2xl font-semibold text-ink-950">{summary.contested_graph_counts?.regions_detected ?? 0}</div>
        </div>
        <div class="rounded-lg border border-ink-950/10 bg-white p-3">
          <div class="text-[11px] uppercase tracking-[0.2em] text-ink-800/60">Cycles</div>
          <div class="mt-1 text-2xl font-semibold text-ink-950">{summary.contested_graph_counts?.cycles_detected ?? 0}</div>
        </div>
      </div>
      <div class="mt-3 text-sm text-ink-800/80">
        highest severity:
        <span class="ml-1 rounded bg-amber-100 px-2 py-0.5 font-mono text-xs">{summary.highest_severity ?? 'none'}</span>
      </div>
    </Panel>

    <Panel>
      <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Pack triage: top graphs</div>
      <div class="mt-1 text-xs text-ink-800/60">These rankings are run-wide, not specific to the selected article.</div>
      <div class="mt-3 space-y-2">
        {#each topArticles as row}
          <a
            class="block rounded-lg border border-ink-950/10 bg-white p-3 hover:border-ink-950/20"
            href={`/graphs/wiki-revision-contested?pack=${encodeURIComponent(payload.selected_pack_id ?? '')}&run=${encodeURIComponent(payload.selected_run_id ?? '')}&article=${encodeURIComponent(row.article_id)}`}
          >
            <div class="flex items-center justify-between gap-3">
              <div class="font-medium text-ink-950">{row.title ?? row.article_id}</div>
              <div class="font-mono text-[11px] text-ink-800/60">{row.top_severity}</div>
            </div>
            <div class="mt-1 text-xs text-ink-800/70">
              heat={row.graph_heat ?? 0} regions={row.region_count ?? 0} cycles={row.cycle_count ?? 0}
            </div>
          </a>
        {/each}
        {#if !topArticles.length}
          <div class="rounded-lg border border-dashed border-ink-950/15 bg-white p-3 text-sm text-ink-800/70">
            No contested graph summaries are available for the selected run.
          </div>
        {/if}
      </div>
    </Panel>
  </div>

  <div class="grid gap-4 xl:grid-cols-[0.9fr_1.1fr]">
    <Panel>
      <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Pack triage: top cycles</div>
      <div class="mt-1 text-xs text-ink-800/60">Run-wide contested-region revisitation patterns across the whole pack.</div>
      <div class="mt-3 space-y-2">
        {#each topCycles as cycle}
          <div class="rounded-lg border border-ink-950/10 bg-white p-3">
            <div class="flex items-center justify-between gap-3">
              <div class="font-medium text-ink-950">{cycle.region_title}</div>
              <div class="font-mono text-[11px] text-ink-800/60">{cycle.highest_severity}</div>
            </div>
            <div class="mt-1 text-xs text-ink-800/70">
              {cycle.article_id} | touches={cycle.touch_count ?? 0} | {cycle.reason}
            </div>
          </div>
        {/each}
        {#if !topCycles.length}
          <div class="rounded-lg border border-dashed border-ink-950/15 bg-white p-3 text-sm text-ink-800/70">
            No contested cycles were detected for the selected run.
          </div>
        {/if}
      </div>
    </Panel>

    <Panel>
      <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Pack triage: top regions</div>
      <div class="mt-1 text-xs text-ink-800/60">Largest or hottest contested regions across all articles in the selected run.</div>
      <div class="mt-3 space-y-2">
        {#each topRegions as region}
          <div class="rounded-lg border border-ink-950/10 bg-white p-3">
            <div class="flex items-center justify-between gap-3">
              <div class="font-medium text-ink-950">{region.region_title}</div>
              <div class="font-mono text-[11px] text-ink-800/60">{region.highest_severity}</div>
            </div>
            <div class="mt-1 text-xs text-ink-800/70">
              {region.article_id} | touches={region.touch_count ?? 0} | touched_bytes={region.total_touched_bytes ?? 0}
            </div>
          </div>
        {/each}
        {#if !topRegions.length}
          <div class="rounded-lg border border-dashed border-ink-950/15 bg-white p-3 text-sm text-ink-800/70">
            No contested regions were detected for the selected run.
          </div>
        {/if}
      </div>
    </Panel>
  </div>

  <div class="grid gap-4 xl:grid-cols-[1fr_1fr]">
    <Panel>
      <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Selected article detail</div>
      <div class="mt-1 text-xs text-ink-800/60">This section is scoped to the article selected above.</div>
      {#if selectedArticle}
        <div class="mt-3 text-lg font-semibold text-ink-950">{selectedArticle.title}</div>
        <div class="mt-1 flex flex-wrap gap-2 text-[11px] text-ink-800/70">
          <span class="rounded bg-slate-100 px-2 py-0.5 font-mono">{selectedArticle.article_id}</span>
          <span class="rounded bg-slate-100 px-2 py-0.5 font-mono">{selectedArticle.top_severity}</span>
          <span class="rounded bg-slate-100 px-2 py-0.5 font-mono">{selectedArticle.selected_primary_pair_kind ?? 'none'}</span>
        </div>
        <div class="mt-3 grid gap-2 sm:grid-cols-2">
          <div class="rounded-lg border border-ink-950/10 bg-white p-3">
            <div class="text-[11px] uppercase tracking-[0.2em] text-ink-800/60">Primary pair</div>
            <div class="mt-1 font-mono text-xs text-ink-950">{selectedArticle.selected_primary_pair_id ?? 'none'}</div>
          </div>
          <div class="rounded-lg border border-ink-950/10 bg-white p-3">
            <div class="text-[11px] uppercase tracking-[0.2em] text-ink-800/60">Graph</div>
            <div class="mt-1 font-mono text-xs text-ink-950">{selectedArticle.contested_graph_available ? 'available' : 'none'}</div>
          </div>
        </div>
        {#if selectedArticle.report_path}
          <div class="mt-3 text-xs text-ink-800/70">
            pair report: <span class="font-mono">{selectedArticle.report_path}</span>
          </div>
        {/if}
        {#if selectedArticle.contested_graph_path}
          <div class="mt-1 text-xs text-ink-800/70">
            contested graph: <span class="font-mono">{selectedArticle.contested_graph_path}</span>
          </div>
        {/if}
      {/if}

      <div class="mt-4 text-xs uppercase tracking-[0.28em] text-ink-800/70">Selected pairs</div>
      <div class="mt-3 space-y-2">
        {#each selectedArticle?.pair_reports ?? [] as pair}
          <div class="rounded-lg border border-ink-950/10 bg-white p-3">
            <div class="flex items-center justify-between gap-3">
              <div class="font-medium text-ink-950">{pair.pair_kind}</div>
              <div class="font-mono text-[11px] text-ink-800/60">{pair.top_severity}</div>
            </div>
            <div class="mt-1 text-xs text-ink-800/70">
              {pair.older_revid} → {pair.newer_revid} | score={pair.candidate_score}
            </div>
            {#if pair.top_changed_sections?.length}
              <div class="mt-2">
                <div class="text-[11px] uppercase tracking-[0.18em] text-ink-800/55">Top changed sections</div>
                <div class="mt-2 space-y-1">
                {#each pair.top_changed_sections.slice(0, 4) as section}
                  <div class="rounded bg-amber-50 px-2 py-1 text-[11px] text-ink-900">
                    <span class="font-medium">{section.section}</span>
                    <span class="ml-2 font-mono text-ink-800/70">{section.touched_bytes}</span>
                  </div>
                {/each}
                </div>
              </div>
            {/if}
          </div>
        {/each}
        {#if !(selectedArticle?.pair_reports?.length)}
          <div class="rounded-lg border border-dashed border-ink-950/15 bg-white p-3 text-sm text-ink-800/70">
            No candidate pair reports were persisted for the selected article.
          </div>
        {/if}
      </div>
    </Panel>

    <Panel>
      <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Selected article graph</div>
      <div class="mt-1 text-xs text-ink-800/60">Contested-region graph detail for the selected article only.</div>
      {#if graphSummary}
        <div class="mt-3 grid gap-3 sm:grid-cols-2">
          <div class="rounded-lg border border-ink-950/10 bg-white p-3">
            <div class="text-[11px] uppercase tracking-[0.2em] text-ink-800/60">Hottest region</div>
            <div class="mt-1 text-sm font-medium text-ink-950">{graphSummary.hottest_region?.title ?? 'none'}</div>
          </div>
          <div class="rounded-lg border border-ink-950/10 bg-white p-3">
            <div class="text-[11px] uppercase tracking-[0.2em] text-ink-800/60">Graph heat</div>
            <div class="mt-1 font-mono text-sm text-ink-950">{graphSummary.graph_heat ?? 0}</div>
          </div>
        </div>
        <div class="mt-4 text-xs uppercase tracking-[0.28em] text-ink-800/70">Network view</div>
        <div class="mt-1 text-xs text-ink-800/60">
          Pairs feed regions; regions connect to changed events and epistemic surfaces. Red regions participate in detected cycles.
        </div>
        {#if graphLayers.length >= 2}
          <div class="mt-3">
            <LayeredGraph
              layers={graphLayers}
              edges={graphEdges}
              width={1500}
              height={640}
              fitToWidth={true}
              scrollWhenOverflow={true}
              colGap={240}
              nodeW={180}
              expandedNodeW={360}
              on:nodeSelect={(e) => (selectedGraphNodeId = (e as CustomEvent<{ nodeId: string }>).detail.nodeId)}
            />
          </div>
          <div class="mt-3 rounded-lg border border-ink-950/10 bg-white p-3">
            <div class="text-[11px] uppercase tracking-[0.2em] text-ink-800/60">Selected graph node</div>
            {#if selectedGraphNode}
              <div class="mt-1 text-sm font-medium text-ink-950">{selectedGraphNode.layerTitle}: {selectedGraphNode.label}</div>
              {#if selectedGraphNode.fullLabel}
                <div class="mt-1 text-xs text-ink-800/70">{selectedGraphNode.fullLabel}</div>
              {/if}
              {#if selectedGraphNode.tooltip}
                <pre class="mt-2 whitespace-pre-wrap font-mono text-[11px] text-ink-800/70">{selectedGraphNode.tooltip}</pre>
              {/if}
            {:else}
              <div class="mt-1 text-sm text-ink-800/70">Click a node in the graph to inspect it here.</div>
            {/if}
          </div>
        {:else}
          <div class="mt-3 rounded-lg border border-dashed border-ink-950/15 bg-white p-3 text-sm text-ink-800/70">
            Not enough graph layers were hydrated to render a node/edge view.
          </div>
        {/if}
        <div class="mt-4 text-xs uppercase tracking-[0.28em] text-ink-800/70">Regions</div>
        <div class="mt-3 space-y-2">
          {#each graph?.regions ?? [] as region}
            <div class="rounded-lg border border-ink-950/10 bg-white p-3">
              <div class="flex items-center justify-between gap-3">
                <div class="font-medium text-ink-950">{region.title}</div>
                <div class="font-mono text-[11px] text-ink-800/60">{region.highest_severity}</div>
              </div>
              <div class="mt-1 text-xs text-ink-800/70">
                touches={region.touch_count} | touched_bytes={region.total_touched_bytes} | heat={region.graph_heat}
              </div>
              {#if region.pair_kinds?.length}
                <div class="mt-2 flex flex-wrap gap-1">
                  {#each region.pair_kinds as kind}
                    <span class="rounded bg-slate-100 px-2 py-0.5 text-[11px] text-ink-900">{kind}</span>
                  {/each}
                </div>
              {/if}
            </div>
          {/each}
          {#if !(graph?.regions?.length)}
            <div class="rounded-lg border border-dashed border-ink-950/15 bg-white p-3 text-sm text-ink-800/70">
              Graph summary exists, but no region rows were included in the hydrated payload.
            </div>
          {/if}
        </div>
        <div class="mt-4 text-xs uppercase tracking-[0.28em] text-ink-800/70">Cycles</div>
        <div class="mt-3 space-y-2">
          {#each graph?.cycles ?? [] as cycle}
            <div class="rounded-lg border border-ink-950/10 bg-white p-3">
              <div class="flex items-center justify-between gap-3">
                <div class="font-medium text-ink-950">{cycle.region_title}</div>
                <div class="font-mono text-[11px] text-ink-800/60">{cycle.highest_severity}</div>
              </div>
              <div class="mt-1 text-xs text-ink-800/70">
                touches={cycle.touch_count} | {cycle.reason}
              </div>
            </div>
          {/each}
          {#if !(graph?.cycles?.length)}
            <div class="rounded-lg border border-dashed border-ink-950/15 bg-white p-3 text-sm text-ink-800/70">
              No contested cycles were emitted for this selected graph.
            </div>
          {/if}
        </div>
      {:else}
        {#if pageState === 'producer_error'}
          <div class="mt-3 text-sm text-ink-800/70">
            Producer error: the selected article did not complete revision processing, so graph detail is unavailable.
          </div>
        {:else if pageState === 'graph_not_enabled'}
          <div class="mt-3 text-sm text-ink-800/70">
            Graph not enabled: this pack only persisted pair-level revision analysis, not contested-region graphs.
          </div>
        {:else if pageState === 'missing_graph_payload'}
          <div class="mt-3 text-sm text-ink-800/70">
            Missing graph payload: the run indicates a graph artifact, but the hydrated payload is empty.
          </div>
        {:else}
          <div class="mt-3 text-sm text-ink-800/70">No contested graph available for the selected article/run.</div>
        {/if}
      {/if}
    </Panel>
  </div>

  <Panel>
    <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Pack triage: high-severity pairs</div>
    <div class="mt-1 text-xs text-ink-800/60">Run-wide pair ranking across all articles in the selected pack/run.</div>
    <div class="mt-3 space-y-2">
      {#each topPairs as pair}
        <div class="rounded-lg border border-ink-950/10 bg-white p-3">
          <div class="flex items-center justify-between gap-3">
            <div class="font-medium text-ink-950">{pair.article_id}</div>
            <div class="font-mono text-[11px] text-ink-800/60">{pair.top_severity}</div>
          </div>
          <div class="mt-1 text-xs text-ink-800/70">
            {pair.pair_kind} | {pair.older_revid} → {pair.newer_revid} | score={pair.candidate_score}
          </div>
        </div>
      {/each}
      {#if !topPairs.length}
        <div class="rounded-lg border border-dashed border-ink-950/15 bg-white p-3 text-sm text-ink-800/70">
          No high-severity pairs were recorded for the selected run.
        </div>
      {/if}
    </div>
  </Panel>
</div>
