<script lang="ts">
  import Panel from '$lib/ui/Panel.svelte';

  export let data: {
    payload: any;
    error: string | null;
  };

  $: payload = data.payload ?? {};
  $: summary = payload.summary ?? {};
  $: triage = summary.pack_triage ?? {};
  $: articles = summary.articles ?? [];
  $: selectedArticle = articles.find((row: any) => row.article_id === payload.selected_article_id) ?? articles[0] ?? null;
  $: graph = payload.selected_graph ?? null;
  $: graphSummary = graph?.summary ?? selectedArticle?.contested_graph_summary ?? null;
  $: topArticles = triage.top_contested_graphs ?? [];
  $: topCycles = triage.top_contested_cycles ?? [];
  $: topRegions = triage.top_contested_regions ?? [];
  $: topPairs = triage.top_high_severity_pairs ?? [];
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

  <div class="grid gap-4 xl:grid-cols-[1.1fr_0.9fr]">
    <Panel>
      <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Run summary</div>
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
      <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Top graphs</div>
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
      </div>
    </Panel>
  </div>

  <div class="grid gap-4 xl:grid-cols-[0.9fr_1.1fr]">
    <Panel>
      <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Top cycles</div>
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
      </div>
    </Panel>

    <Panel>
      <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Top regions</div>
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
      </div>
    </Panel>
  </div>

  <div class="grid gap-4 xl:grid-cols-[1fr_1fr]">
    <Panel>
      <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Article detail</div>
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
              <div class="mt-2 flex flex-wrap gap-1">
                {#each pair.top_changed_sections.slice(0, 4) as section}
                  <span class="rounded bg-amber-50 px-2 py-0.5 text-[11px] text-ink-900">
                    {section.section} ({section.touched_bytes})
                  </span>
                {/each}
              </div>
            {/if}
          </div>
        {/each}
      </div>
    </Panel>

    <Panel>
      <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Graph detail</div>
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
        </div>
      {:else}
        <div class="mt-3 text-sm text-ink-800/70">No contested graph available for the selected article/run.</div>
      {/if}
    </Panel>
  </div>

  <Panel>
    <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">High-severity pairs</div>
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
    </div>
  </Panel>
</div>
