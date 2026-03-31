<script lang="ts">
  import Panel from '$lib/ui/Panel.svelte';

  export let parserModel: string | null = null;
  export let hasSpanCandidates = false;
  export let showAllSpans = false;
  export let spanShown: Array<{
    span_id: string;
    text: string;
    span_type: string;
    recurrence?: { seen_events?: number };
    hygiene?: { view_score?: number; token_count?: number };
  }> = [];
  export let totalSpanCount = 0;
  export let onToggleShowAll: () => void;
</script>

<Panel>
  <div class="flex flex-wrap items-center justify-between gap-2">
    <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Span candidates</div>
    <div class="font-mono text-[10px] text-ink-800/60">
      {#if parserModel}
        parser={parserModel}
      {:else}
        parser=(none)
      {/if}
    </div>
  </div>
  {#if hasSpanCandidates}
    <div class="mt-3 flex flex-wrap items-center gap-3 text-xs text-ink-950">
      <label class="flex items-center gap-2">
        <input type="checkbox" checked={showAllSpans} on:change={onToggleShowAll} />
        <span class="text-ink-800/70">show all</span>
      </label>
      <div class="font-mono text-[10px] text-ink-800/60">
        showing {spanShown.length} / {totalSpanCount}
      </div>
    </div>
    <div class="mt-3 flex flex-wrap gap-2 text-[11px]">
      {#each spanShown as s (s.span_id)}
        <span class="rounded border border-ink-950/10 bg-white px-2 py-1 font-mono text-ink-950">
          <span class="text-ink-800/70">{s.span_type}</span>
          <span class="ml-2">{s.text}</span>
          {#if s.hygiene?.view_score !== undefined}
            <span class="ml-2 text-ink-800/60">score={Number(s.hygiene.view_score).toFixed(2)}</span>
          {/if}
          {#if s.recurrence?.seen_events}
            <span class="ml-2 text-ink-800/60">seen={s.recurrence.seen_events}</span>
          {/if}
        </span>
      {/each}
    </div>
  {:else}
    <div class="mt-3 text-xs text-ink-800/60">No span candidates for this event.</div>
  {/if}
</Panel>
