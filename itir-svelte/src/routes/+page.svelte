<script lang="ts">
  import {
    ArtifactLinks,
    ChatFlowWaterfall,
    ChatThreadsTable,
    DashboardHeader,
    DashboardShell,
    FrequencyBars,
    NotebookLMLifecycle,
    SummaryCards,
    TimelinePanel,
    ToolUseSummary
  } from '$lib/sb-dashboard';

  import { buildThreadRows, buildWaterfallSegments, type ThreadRow } from '$lib/sb-dashboard/adapters/dashboard';
  import type { DashboardPayload } from '$lib/sb-dashboard/contracts/dashboard';
  import DateRangeSelector from '$lib/ui/DateRangeSelector.svelte';
  import MissingRunsPanel from '$lib/ui/MissingRunsPanel.svelte';
  import Panel from '$lib/ui/Panel.svelte';
  import WhenYouWorkHeatmap from '$lib/sb-dashboard/components/WhenYouWorkHeatmap.svelte';
  import TimelineRibbonLite from '$lib/sb-dashboard/components/TimelineRibbonLite.svelte';

  export let data: {
    payload: DashboardPayload;
    source: string;
    parseError: string | null;
    availableDates: string[];
    selected: { start: string; end: string };
    missingDates: string[];
    heatmaps: any;
    runsRoot: string;
    buildSummary: { built: number; failed: number } | null;
    buildError?: string | null;
    autoBuildEnabled?: boolean;
    runsRootWritable?: boolean;
    notebookMetaRows?: ThreadRow[];
  };

  export let form: any;

  $: payload = data.payload;
  $: notebooklmMetaEvents = (() => {
    const summary = (payload as any)?.notes_meta_summary ?? (payload as any)?.notes_meta_totals;
    const raw = summary?.notebooklm_events;
    const n = typeof raw === 'number' && Number.isFinite(raw) ? raw : Number(String(raw ?? ''));
    return Number.isFinite(n) ? Math.max(0, Math.trunc(n)) : 0;
  })();
  $: baseThreadRows = buildThreadRows(payload);
  $: threadRows = (() => {
    const extras = (data.notebookMetaRows ?? []).filter((r) => !baseThreadRows.some((b) => b.threadId === r.threadId));
    return extras.length ? [...baseThreadRows, ...extras] : baseThreadRows;
  })();
  $: segments = buildWaterfallSegments(payload);
</script>

<DashboardShell title="itir-svelte">
  <DateRangeSelector availableDates={data.availableDates} start={data.selected.start || payload.date} end={data.selected.end || payload.date} />
  <MissingRunsPanel
    missingDates={data.missingDates}
    start={data.selected.start || payload.date}
    end={data.selected.end || payload.date}
    runsRoot={data.runsRoot}
    buildSummary={data.buildSummary}
    buildError={form?.error ?? data.buildError ?? null}
    autoBuildEnabled={Boolean(data.autoBuildEnabled)}
  />

  {#if data.parseError}
    <Panel tone="danger">
      <div class="text-xs uppercase tracking-[0.28em] text-red-800/80">Load error</div>
      <pre class="mt-3 whitespace-pre-wrap font-mono text-xs text-ink-950">{data.parseError}</pre>
      <div class="mt-3 text-xs text-ink-800/60">
        Source: <span class="font-mono">{data.source}</span>
      </div>
    </Panel>
  {/if}

  <DashboardHeader {payload} />

  <SummaryCards summary={payload.summary} frequencyByHour={payload.frequency_by_hour} />

  <NotebookLMLifecycle {payload} />

  <WhenYouWorkHeatmap
    heatmaps={data.heatmaps}
    start={data.selected.start || payload.date}
    end={data.selected.end || payload.date}
    missingDates={data.missingDates}
  />

  <FrequencyBars frequencyByHour={payload.frequency_by_hour} />
  <ArtifactLinks links={payload.artifact_links} />

  <ChatThreadsTable
    rows={threadRows}
    start={data.selected.start || payload.date}
    end={data.selected.end || payload.date}
    notebooklmMetaEvents={notebooklmMetaEvents}
  />
  <ChatFlowWaterfall {segments} />
  <ToolUseSummary toolUse={payload.tool_use_summary} />
  <TimelineRibbonLite events={payload.timeline} />
  <TimelinePanel events={payload.timeline} />

  <Panel>
    <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Graphs</div>
    <div class="mt-2 text-sm text-ink-950">
      <a class="underline decoration-ink-950/20 underline-offset-4 hover:decoration-ink-950/50" href="/graphs/wiki-candidates"
        >Wiki candidates (GWB)</a
      >
      <span class="ml-2 text-xs text-ink-800/60 font-mono">SensibLaw/.cache_local/wiki_candidates_gwb.json</span>
    </div>
    <div class="mt-2 text-sm text-ink-950">
      <a class="underline decoration-ink-950/20 underline-offset-4 hover:decoration-ink-950/50" href="/graphs/wiki-timeline"
        >Wiki timeline (GWB)</a
      >
      <span class="ml-2 text-xs text-ink-800/60 font-mono">SensibLaw/.cache_local/wiki_timeline_gwb.json</span>
    </div>
    <div class="mt-2 text-sm text-ink-950">
      <a
        class="underline decoration-ink-950/20 underline-offset-4 hover:decoration-ink-950/50"
        href="/graphs/wiki-timeline-aoo"
        >Wiki timeline AAO (GWB)</a
      >
      <span class="ml-2 text-xs text-ink-800/60 font-mono">SensibLaw/.cache_local/wiki_timeline_gwb_aoo.json</span>
    </div>
    <div class="mt-2 text-sm text-ink-950">
      <a
        class="underline decoration-ink-950/20 underline-offset-4 hover:decoration-ink-950/50"
        href="/graphs/wiki-timeline-aoo?view=step-ribbon"
        >Wiki timeline Step-Ribbon (GWB)</a
      >
      <span class="ml-2 text-xs text-ink-800/60 font-mono">view=step-ribbon</span>
    </div>
    <div class="mt-2 text-sm text-ink-950">
      <a
        class="underline decoration-ink-950/20 underline-offset-4 hover:decoration-ink-950/50"
        href="/graphs/wiki-timeline-aoo-all"
        >Wiki timeline AAO combined (GWB)</a
      >
      <span class="ml-2 text-xs text-ink-800/60 font-mono">SensibLaw/.cache_local/wiki_timeline_gwb_aoo.json</span>
    </div>
    <div class="mt-2 text-sm text-ink-950">
      <a
        class="underline decoration-ink-950/20 underline-offset-4 hover:decoration-ink-950/50"
        href="/graphs/wiki-timeline-aoo?source=hca"
        >Case timeline AAO (HCA S94/2025)</a
      >
      <span class="ml-2 text-xs text-ink-800/60 font-mono">SensibLaw/.cache_local/wiki_timeline_hca_s942025_aoo.json</span>
    </div>
    <div class="mt-2 text-sm text-ink-950">
      <a
        class="underline decoration-ink-950/20 underline-offset-4 hover:decoration-ink-950/50"
        href="/graphs/wiki-timeline-aoo?source=hca&view=step-ribbon"
        >Case timeline Step-Ribbon (HCA S94/2025)</a
      >
      <span class="ml-2 text-xs text-ink-800/60 font-mono">view=step-ribbon</span>
    </div>
    <div class="mt-2 text-sm text-ink-950">
      <a
        class="underline decoration-ink-950/20 underline-offset-4 hover:decoration-ink-950/50"
        href="/graphs/wiki-timeline-aoo-all?source=hca"
        >Case timeline AAO combined (HCA S94/2025)</a
      >
      <span class="ml-2 text-xs text-ink-800/60 font-mono">SensibLaw/.cache_local/wiki_timeline_hca_s942025_aoo.json</span>
    </div>
    <div class="mt-2 text-xs text-ink-800/60">
      Visualizes the pre-graph extraction substrate (page -&gt; candidate evidence edges).
    </div>
  </Panel>

  <Panel>
    <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Archive</div>
    <div class="mt-2 text-sm text-ink-950">
      <a class="underline decoration-ink-950/20 underline-offset-4 hover:decoration-ink-950/50" href="/threads">Browse threads</a>
      <span class="ml-2 text-xs text-ink-800/60 font-mono">~/.chat_archive.sqlite or ~/chat_archive.sqlite</span>
    </div>
  </Panel>

  <Panel>
    <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Viewers</div>
    <div class="mt-2 text-sm text-ink-950">
      <a class="underline decoration-ink-950/20 underline-offset-4 hover:decoration-ink-950/50" href="/viewers/hca-case"
        >HCA transcript + document viewer workbench</a
      >
      <span class="ml-2 text-xs text-ink-800/60 font-mono">reusable transcript/document/folder components</span>
    </div>
  </Panel>

  <Panel>
    <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Mission Lens</div>
    <div class="mt-2 text-sm text-ink-950">
      <a class="underline decoration-ink-950/20 underline-offset-4 hover:decoration-ink-950/50" href="/graphs/mission-lens"
        >Actual vs should mission workbench</a
      >
      <span class="ml-2 text-xs text-ink-800/60 font-mono">ITIR-owned planning lens rendered against SB dashboard data</span>
    </div>
  </Panel>

  <div class="text-xs text-ink-800/60">
    Source: <span class="font-mono">{data.source}</span>
  </div>
</DashboardShell>
