<script lang="ts">
  import Section from '$lib/ui/Section.svelte';
  import type { DashboardPayload } from '../contracts/dashboard';

  export let payload: DashboardPayload;

  type LifecycleBucket = { created?: number; modified?: number; moved?: number; deleted?: number; seen?: number; other?: number };
  type NotesMetaTotals = {
    total_events?: number;
    notebooklm_events?: number;
    lifecycle?: Record<string, LifecycleBucket>;
  };

  function n(v: unknown): number {
    const x = typeof v === 'number' && Number.isFinite(v) ? v : Number(String(v));
    return Number.isFinite(x) ? x : 0;
  }

  function fmtLifecycle(b: LifecycleBucket | null): string {
    const bb = b ?? {};
    return `${n(bb.created)}/${n(bb.modified)}/${n(bb.moved)}/${n(bb.deleted)}/${n(bb.seen)}`;
  }

  $: totals = ((payload as any).notes_meta_summary as NotesMetaTotals | undefined) ?? ((payload as any).notes_meta_totals as NotesMetaTotals | undefined);

  // Weekly payloads include `notes_meta_averages_per_day`; range payloads may compute their own.
  $: avg = (payload as any).notes_meta_averages_per_day as { total_events?: number; notebooklm_events?: number } | undefined;

  $: lifecycleFromTotals = totals?.lifecycle ?? undefined;
  $: lifecycleFromWeekly = (payload as any).notebooklm_lifecycle_totals as Record<string, LifecycleBucket> | undefined;
  $: lifecycle = lifecycleFromTotals ?? lifecycleFromWeekly ?? undefined;

  $: notebook = lifecycle?.notebook ?? null;
  $: file = lifecycle?.file ?? null;

  $: notesMetaEvents = totals ? n(totals.total_events) : 0;
  $: notebooklmEvents = totals ? n(totals.notebooklm_events) : 0;

  $: show = Boolean(totals || lifecycleFromWeekly);
</script>

<Section title="NotebookLM Lifecycle (Metadata)" subtitle="Read-only observer counts (created/modified/moved/deleted/seen).">
  {#if show}
    <div class="grid gap-3 md:grid-cols-2 lg:grid-cols-4">
      <div class="rounded-xl bg-paper-50 ring-1 ring-ink-900/10 px-4 py-3">
        <div class="text-xs uppercase tracking-widest text-ink-800/60">Notes meta events</div>
        <div class="mt-1 font-mono text-2xl text-ink-950">{notesMetaEvents.toLocaleString()}</div>
        {#if avg && (avg.total_events ?? 0) > 0}
          <div class="mt-1 text-xs text-ink-800/60">avg/day: <span class="font-mono">{n(avg.total_events).toFixed(2)}</span></div>
        {/if}
      </div>

      <div class="rounded-xl bg-paper-50 ring-1 ring-ink-900/10 px-4 py-3">
        <div class="text-xs uppercase tracking-widest text-ink-800/60">NotebookLM meta events</div>
        <div class="mt-1 font-mono text-2xl text-ink-950">{notebooklmEvents.toLocaleString()}</div>
        {#if avg && (avg.notebooklm_events ?? 0) > 0}
          <div class="mt-1 text-xs text-ink-800/60">avg/day: <span class="font-mono">{n(avg.notebooklm_events).toFixed(2)}</span></div>
        {/if}
      </div>

      <div class="rounded-xl bg-paper-50 ring-1 ring-ink-900/10 px-4 py-3">
        <div class="text-xs uppercase tracking-widest text-ink-800/60">Notebooks (c/m/mv/d/seen)</div>
        <div class="mt-1 font-mono text-xl text-ink-950">{fmtLifecycle(notebook)}</div>
      </div>

      <div class="rounded-xl bg-paper-50 ring-1 ring-ink-900/10 px-4 py-3">
        <div class="text-xs uppercase tracking-widest text-ink-800/60">Files (c/m/mv/d/seen)</div>
        <div class="mt-1 font-mono text-xl text-ink-950">{fmtLifecycle(file)}</div>
      </div>
    </div>
  {:else}
    <div class="text-sm text-ink-800/60">No NotebookLM metadata in this payload.</div>
  {/if}
</Section>
