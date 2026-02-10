<script lang="ts">
  import {
    ArtifactLinks,
    ChatFlowWaterfall,
    ChatThreadsTable,
    DashboardHeader,
    DashboardShell,
    FrequencyBars,
    SummaryCards,
    TimelinePanel,
    ToolUseSummary
  } from '$lib/sb-dashboard';

  import { buildThreadRows, buildWaterfallSegments } from '$lib/sb-dashboard/adapters/dashboard';
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
  };

  export let form: any;

  $: payload = data.payload;
  $: threadRows = buildThreadRows(payload);
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
    buildError={form?.error ?? null}
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

  <WhenYouWorkHeatmap heatmaps={data.heatmaps} />

  <FrequencyBars frequencyByHour={payload.frequency_by_hour} />
  <ArtifactLinks links={payload.artifact_links} />

  <ChatThreadsTable rows={threadRows} />
  <ChatFlowWaterfall {segments} />
  <ToolUseSummary toolUse={payload.tool_use_summary} />
  <TimelineRibbonLite events={payload.timeline} />
  <TimelinePanel events={payload.timeline} />

  <div class="text-xs text-ink-800/60">
    Source: <span class="font-mono">{data.source}</span>
  </div>
</DashboardShell>
