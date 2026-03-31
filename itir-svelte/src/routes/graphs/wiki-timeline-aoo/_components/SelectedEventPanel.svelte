<script lang="ts">
  import Panel from '$lib/ui/Panel.svelte';

  export let selected: any;
  export let source = 'gwb';
  export let layoutMode: 'roles' | 'step_ribbon';
  export let timeGranularity: 'auto' | 'year' | 'month' | 'day';
  export let hrefFor: (source: string, viewType: string) => string;
  export let onSetTimeGranularity: (value: 'auto' | 'year' | 'month' | 'day') => void;
</script>

<Panel>
  <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Selected</div>
  <div class="mt-2 text-sm text-ink-950">{selected.text}</div>
  <div class="mt-2 text-xs text-ink-800/60">
    {selected.anchor.text} | section: <span class="font-mono">{selected.section}</span>
  </div>
  {#if selected.chains?.length}
    <div class="mt-2 font-mono text-xs text-ink-800/60">
      chains:
      {#each selected.chains as c, i (i)}
        <span class="ml-2">{c.kind}({c.from_step ?? '-'}-&gt;{c.to_step ?? c.to ?? '-'})</span>
      {/each}
    </div>
  {/if}
  <div class="mt-4 flex flex-wrap items-center gap-2 text-xs text-ink-950">
    <div class="font-mono text-[10px] uppercase tracking-[0.20em] text-ink-800/70">Layout</div>
    <button
      class="rounded-md border px-2 py-1 font-mono text-[11px] {layoutMode==='step_ribbon' ? 'border-ink-950/40 bg-ink-950/[0.04]' : 'border-ink-950/10 bg-white hover:border-ink-950/25 hover:bg-ink-950/[0.02]'}"
      on:click={() => {
        window.location.href = hrefFor(source, 'step-ribbon');
      }}
    >
      step-ribbon
    </button>
    <button
      class="rounded-md border px-2 py-1 font-mono text-[11px] {layoutMode==='roles' ? 'border-ink-950/40 bg-ink-950/[0.04]' : 'border-ink-950/10 bg-white hover:border-ink-950/25 hover:bg-ink-950/[0.02]'}"
      on:click={() => {
        window.location.href = hrefFor(source, 'roles');
      }}
    >
      roles
    </button>
  </div>
  <div class="mt-2 text-[11px] text-ink-800/65">
    `step-ribbon` preserves sentence order (S1 -&gt; S2 ...) with explicit `then` edges; it is linearization only, not causality.
  </div>
  <div class="mt-4 flex flex-wrap items-center gap-2 text-xs text-ink-950">
    <div class="font-mono text-[10px] uppercase tracking-[0.20em] text-ink-800/70">Time view</div>
    <button
      class="rounded-md border px-2 py-1 font-mono text-[11px] {timeGranularity==='auto' ? 'border-ink-950/40 bg-ink-950/[0.04]' : 'border-ink-950/10 bg-white hover:border-ink-950/25 hover:bg-ink-950/[0.02]'}"
      on:click={() => onSetTimeGranularity('auto')}
    >
      auto
    </button>
    <button
      class="rounded-md border px-2 py-1 font-mono text-[11px] {timeGranularity==='year' ? 'border-ink-950/40 bg-ink-950/[0.04]' : 'border-ink-950/10 bg-white hover:border-ink-950/25 hover:bg-ink-950/[0.02]'}"
      on:click={() => onSetTimeGranularity('year')}
    >
      year
    </button>
    <button
      class="rounded-md border px-2 py-1 font-mono text-[11px] {timeGranularity==='month' ? 'border-ink-950/40 bg-ink-950/[0.04]' : 'border-ink-950/10 bg-white hover:border-ink-950/25 hover:bg-ink-950/[0.02]'}"
      on:click={() => onSetTimeGranularity('month')}
    >
      month
    </button>
    <button
      class="rounded-md border px-2 py-1 font-mono text-[11px] {timeGranularity==='day' ? 'border-ink-950/40 bg-ink-950/[0.04]' : 'border-ink-950/10 bg-white hover:border-ink-950/25 hover:bg-ink-950/[0.02]'}"
      on:click={() => onSetTimeGranularity('day')}
    >
      day
    </button>
  </div>
</Panel>
