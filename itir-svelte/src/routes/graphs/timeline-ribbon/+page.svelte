<script lang="ts">
  import TimelineRibbonLite from '$lib/sb-dashboard/components/TimelineRibbonLite.svelte';

  export let data: {
    availableDates: string[];
    selected: { start: string; end: string };
    payload: { timeline?: any[]; period_start?: string; period_end?: string; days?: number; date: string };
    source: string;
    error: string | null;
  };

  $: timelineCount = data.payload.timeline?.length ?? 0;
</script>

<svelte:head>
  <title>Timeline Ribbon</title>
</svelte:head>

<div class="space-y-8 p-6">
  <section class="rounded-3xl border border-ink-950/10 bg-white/90 p-6 shadow-sm">
    <div class="flex flex-wrap items-end justify-between gap-4">
      <div class="space-y-2">
        <div class="text-xs uppercase tracking-[0.25em] text-ink-950/45">Timeline Ribbon</div>
        <h1 class="text-3xl font-semibold tracking-tight text-ink-950">Timeline Ribbon Workbench</h1>
        <p class="max-w-3xl text-sm leading-6 text-ink-950/70">
          Read-only ribbon workbench over the SB dashboard timeline payload. This keeps conserved-allocation ribbon behavior separate from AAO step-ribbon graph placement.
        </p>
      </div>

      <form method="GET" class="flex flex-wrap items-end gap-3">
        <label class="space-y-1 text-sm text-ink-950/70">
          <span>Start</span>
          <input class="rounded-xl border border-ink-950/15 px-3 py-2" type="date" name="start" value={data.selected.start} list="timeline-ribbon-dates" />
        </label>
        <label class="space-y-1 text-sm text-ink-950/70">
          <span>End</span>
          <input class="rounded-xl border border-ink-950/15 px-3 py-2" type="date" name="end" value={data.selected.end} list="timeline-ribbon-dates" />
        </label>
        <button class="rounded-full bg-ink-950 px-4 py-2 text-sm font-medium text-white" type="submit">Load ribbon</button>
      </form>
    </div>

    <datalist id="timeline-ribbon-dates">
      {#each data.availableDates as date}
        <option value={date}></option>
      {/each}
    </datalist>

    <div class="mt-4 flex flex-wrap gap-3 text-xs text-ink-800/65">
      <div>
        Range:
        <span class="font-mono">{data.selected.start}</span>
        <span class="mx-1">-></span>
        <span class="font-mono">{data.selected.end}</span>
      </div>
      <div>Timeline rows: <span class="font-mono">{timelineCount}</span></div>
      <div>Source: <span class="font-mono break-all">{data.source || 'n/a'}</span></div>
    </div>

    {#if data.error}
      <div class="mt-4 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800">{data.error}</div>
    {/if}
  </section>

  <TimelineRibbonLite
    events={data.payload.timeline}
    mode="workbench"
    title="Timeline Ribbon Workbench"
    subtitle="Ordered hourly segments conserve the active lens across the selected dashboard range."
  />
</div>
