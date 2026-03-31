<script lang="ts">
  import Panel from '$lib/ui/Panel.svelte';

  export let selected: any;
  export let selectedNodeId: string | null;
  export let selectedContext: { needle: string; summary: string[] } | null;
  export let selectedContextDetails: {
    requesters: string[];
    subjects: string[];
    actions: string[];
    objects: string[];
    numerics: string[];
    citations: string[];
    slRefs: string[];
    factRows: string[];
    warnings: string[];
  };
  export let expandContextDetails = false;
  export let onToggleDetails: () => void;
  export let fmtTime: (anchor: { year: number; month: number | null; day: number | null; precision: string }) => string;
  export let highlightParts: (text: string, needle: string) => Array<{ s: string; hit: boolean }>;
</script>

<Panel>
  <div class="flex flex-wrap items-center justify-between gap-3">
    <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Context</div>
    <div class="text-[11px] font-mono text-ink-800/60">
      {#if selected}
        selected: {selected.event_id}{#if selectedNodeId} ({selectedNodeId}){/if}
        <button
          class="ml-2 rounded border border-ink-950/10 bg-white px-2 py-0.5 text-[10px] hover:border-ink-950/25"
          on:click={onToggleDetails}
        >
          {expandContextDetails ? 'collapse details' : 'expand details'}
        </button>
      {:else}
        click a node to inspect context
      {/if}
    </div>
  </div>
  {#if selected && selectedContext}
    <div class="mt-3 rounded-lg border border-ink-950/10 bg-white p-3">
      <div class="flex flex-wrap items-center justify-between gap-2">
        <div class="font-mono text-[10px] text-ink-800/60">{fmtTime(selected.anchor)} {selected.event_id}</div>
        <div class="font-mono text-[10px] text-ink-800/60">section={selected.section}</div>
      </div>
      <div class="mt-2 text-sm leading-relaxed text-ink-950">
        {#each highlightParts(selected.text, selectedContext.needle) as p, i (i)}
          {#if p.hit}
            <mark class="rounded bg-amber-100 px-0.5">{p.s}</mark>
          {:else}
            <span>{p.s}</span>
          {/if}
        {/each}
      </div>
      <div class="mt-2 font-mono text-[11px] text-ink-800/65">
        connected {selectedContext.summary.join(' ')}
      </div>
      {#if expandContextDetails}
        <div class="mt-3 max-h-[280px] overflow-auto rounded border border-ink-950/10 bg-slate-50 p-2 text-[11px]">
          {#if selectedContextDetails.requesters.length}
            <div class="mb-1">
              <span class="font-mono text-ink-800/60">requesters</span>
              {#each selectedContextDetails.requesters as x (selected.event_id + ':req:' + x)}
                <span class="ml-1 inline-block rounded bg-purple-100 px-1.5 py-0.5 font-mono">[{x}]</span>
              {/each}
            </div>
          {/if}
          {#if selectedContextDetails.subjects.length}
            <div class="mb-1">
              <span class="font-mono text-ink-800/60">subjects</span>
              {#each selectedContextDetails.subjects as x (selected.event_id + ':sub:' + x)}
                <span class="ml-1 inline-block rounded bg-emerald-100 px-1.5 py-0.5 font-mono">[{x}]</span>
              {/each}
            </div>
          {/if}
          {#if selectedContextDetails.actions.length}
            <div class="mb-1">
              <span class="font-mono text-ink-800/60">actions</span>
              {#each selectedContextDetails.actions as x (selected.event_id + ':act:' + x)}
                <span class="ml-1 inline-block rounded bg-amber-100 px-1.5 py-0.5 font-mono">[{x}]</span>
              {/each}
            </div>
          {/if}
          {#if selectedContextDetails.objects.length}
            <div class="mb-1">
              <span class="font-mono text-ink-800/60">objects</span>
              {#each selectedContextDetails.objects as x (selected.event_id + ':obj:' + x)}
                <span class="ml-1 inline-block rounded bg-slate-100 px-1.5 py-0.5 font-mono">[{x}]</span>
              {/each}
            </div>
          {/if}
          {#if selectedContextDetails.numerics.length}
            <div class="mb-1">
              <span class="font-mono text-ink-800/60">numeric</span>
              {#each selectedContextDetails.numerics as x (selected.event_id + ':num:' + x)}
                <span class="ml-1 inline-block rounded bg-rose-100 px-1.5 py-0.5 font-mono">[{x}]</span>
              {/each}
            </div>
          {/if}
          {#if selectedContextDetails.factRows.length}
            <div class="mb-1">
              <span class="font-mono text-ink-800/60">timeline_facts</span>
              {#each selectedContextDetails.factRows.slice(0, 6) as x (selected.event_id + ':fact:' + x)}
                <span class="ml-1 mt-1 inline-block rounded bg-lime-50 px-1.5 py-0.5 font-mono text-ink-900">{x}</span>
              {/each}
            </div>
          {/if}
          {#if selectedContextDetails.citations.length}
            <div class="mb-1">
              <span class="font-mono text-ink-800/60">citations</span>
              {#each selectedContextDetails.citations.slice(0, 8) as x (selected.event_id + ':cit:' + x)}
                <span class="ml-1 inline-block rounded bg-amber-50 px-1.5 py-0.5 font-mono text-ink-900">{x}</span>
              {/each}
            </div>
          {/if}
          {#if selectedContextDetails.slRefs.length}
            <div class="mb-1">
              <span class="font-mono text-ink-800/60">sl_refs</span>
              {#each selectedContextDetails.slRefs.slice(0, 8) as x (selected.event_id + ':sl:' + x)}
                <span class="ml-1 inline-block rounded bg-blue-50 px-1.5 py-0.5 font-mono text-ink-900">{x}</span>
              {/each}
            </div>
          {/if}
          {#if selectedContextDetails.warnings.length}
            <div>
              <span class="font-mono text-ink-800/60">warnings</span>
              {#each selectedContextDetails.warnings as x (selected.event_id + ':warn:' + x)}
                <span class="ml-1 inline-block rounded bg-rose-50 px-1.5 py-0.5 font-mono text-ink-900">{x}</span>
              {/each}
            </div>
          {/if}
        </div>
      {/if}
    </div>
  {/if}
</Panel>
