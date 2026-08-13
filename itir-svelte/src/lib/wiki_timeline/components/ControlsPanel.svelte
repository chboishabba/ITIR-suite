<script lang="ts">
  import Panel from '$lib/ui/Panel.svelte';

  export let data: any;
  export let eventsAllLength = 0;
  export let timeGranularity: 'year' | 'month' | 'day';
  export let limitEvents: number;
  export let maxSubjects: number;
  export let maxObjects: number;
  export let maxNumbers: number;
  export let maxSources: number;
  export let maxLenses: number;
  export let maxEvidence: number;
  export let includeSources: boolean;
  export let includeLenses: boolean;
  export let includeRequesters: boolean;
  export let includePurpose: boolean;
  export let includeEvidence: boolean;
  export let orderByFactDate: boolean;
</script>

<Panel>
  <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Wiki timeline AAO: whole-article combined</div>
  <div class="mt-2 text-sm text-ink-950">
    Timeline input: <span class="font-mono text-xs">{data.relPath}</span>
  </div>
  <div class="mt-2 text-xs text-ink-800/60">
    DB run: <span class="font-mono break-all">{data.payload.run_id ?? '(unknown)'}</span>
    <span class="mx-2">|</span>
    stored timeline_path: <span class="font-mono break-all">{(data.payload.source_timeline as any)?.path ?? '(unknown)'}</span>
    <span class="mx-2">|</span>
    loaded_from_db: <span class="font-mono">{data.payload.__loaded_from_db ? 'true' : 'false'}</span>
  </div>
  <div class="mt-2 text-xs text-ink-800/60">
    Union graph over many sentence-local AAO extractions. Non-causal. Non-authoritative.
  </div>

  <div class="mt-4 flex flex-wrap items-center gap-3 text-sm">
    <label class="flex items-center gap-2">
      <span class="text-ink-800/70">Dataset</span>
      <select
        class="rounded-md border border-ink-950/15 bg-white px-2 py-1 text-sm"
        value={data.source ?? 'gwb'}
        aria-label="Dataset source"
        on:change={(e) => {
          const v = (e.currentTarget as HTMLSelectElement).value;
          window.location.href = `/graphs/wiki-timeline-aoo-all?source=${encodeURIComponent(v)}`;
        }}
      >
        <option value="gwb">gwb</option>
        <option value="gwb_public_bios_v1">gwb_public_bios_v1</option>
        <option value="gwb_corpus_v1">gwb_corpus_v1</option>
        <option value="hca">hca</option>
        <option value="legal">legal</option>
        <option value="legal_follow">legal_follow</option>
      </select>
    </label>
    <label class="flex items-center gap-2">
      <span class="text-ink-800/70">Time</span>
      <select bind:value={timeGranularity} class="rounded-md border border-ink-950/15 bg-white px-2 py-1 text-sm" aria-label="Time granularity">
        <option value="year">Year</option>
        <option value="month">Month</option>
        <option value="day">Day</option>
      </select>
    </label>
    <label class="flex items-center gap-2">
      <span class="text-ink-800/70">Events</span>
      <input
        type="number"
        min="10"
        max={eventsAllLength}
        step="5"
        bind:value={limitEvents}
        class="w-24 rounded-md border border-ink-950/15 px-2 py-1 font-mono text-xs"
        aria-label="Max events"
      />
    </label>
    <label class="flex items-center gap-2">
      <span class="text-ink-800/70">Max subjects</span>
      <input type="number" min="10" max="400" step="10" bind:value={maxSubjects} class="w-24 rounded-md border border-ink-950/15 px-2 py-1 font-mono text-xs" aria-label="Max subjects" />
    </label>
    <label class="flex items-center gap-2">
      <span class="text-ink-800/70">Max objects</span>
      <input type="number" min="10" max="600" step="10" bind:value={maxObjects} class="w-24 rounded-md border border-ink-950/15 px-2 py-1 font-mono text-xs" aria-label="Max objects" />
    </label>
    <label class="flex items-center gap-2">
      <span class="text-ink-800/70">Max numeric</span>
      <input type="number" min="10" max="600" step="10" bind:value={maxNumbers} class="w-24 rounded-md border border-ink-950/15 px-2 py-1 font-mono text-xs" aria-label="Max numeric values" />
    </label>
    <label class="flex items-center gap-2">
      <input type="checkbox" bind:checked={includeSources} aria-label="Show source lane" />
      <span class="text-ink-800/70">Source lane</span>
    </label>
    {#if includeSources}
      <label class="flex items-center gap-2">
        <span class="text-ink-800/70">Max sources</span>
        <input type="number" min="10" max="400" step="10" bind:value={maxSources} class="w-24 rounded-md border border-ink-950/15 px-2 py-1 font-mono text-xs" aria-label="Max sources" />
      </label>
    {/if}
    <label class="flex items-center gap-2">
      <input type="checkbox" bind:checked={includeLenses} aria-label="Show lens lane" />
      <span class="text-ink-800/70">Lens lane</span>
    </label>
    {#if includeLenses}
      <label class="flex items-center gap-2">
        <span class="text-ink-800/70">Max lenses</span>
        <input type="number" min="10" max="500" step="10" bind:value={maxLenses} class="w-24 rounded-md border border-ink-950/15 px-2 py-1 font-mono text-xs" aria-label="Max lenses" />
      </label>
    {/if}
    <label class="flex items-center gap-2">
      <input type="checkbox" bind:checked={includeEvidence} aria-label="Show evidence lane" />
      <span class="text-ink-800/70">Evidence lane</span>
    </label>
    {#if includeEvidence}
      <label class="flex items-center gap-2">
        <span class="text-ink-800/70">Max evidence</span>
        <input type="number" min="10" max="400" step="10" bind:value={maxEvidence} class="w-24 rounded-md border border-ink-950/15 px-2 py-1 font-mono text-xs" aria-label="Max evidence" />
      </label>
    {/if}
    <label class="flex items-center gap-2">
      <input type="checkbox" bind:checked={includeRequesters} aria-label="Show requesters" />
      <span class="text-ink-800/70">Requesters</span>
    </label>
    <label class="flex items-center gap-2">
      <input type="checkbox" bind:checked={includePurpose} aria-label="Show purpose" />
      <span class="text-ink-800/70">Purpose</span>
    </label>
    <label class="flex items-center gap-2">
      <input type="checkbox" bind:checked={orderByFactDate} />
      <span class="text-ink-800/70">Fact-date order</span>
    </label>
    <a
      class="rounded-md border border-ink-950/15 px-2 py-1 text-xs text-ink-950 hover:border-ink-950/30 hover:bg-ink-950/[0.03]"
      href={`/graphs/wiki-timeline?source=${encodeURIComponent(data.source ?? 'gwb')}`}
    >
      Open Timeline
    </a>
    <a
      class="rounded-md border border-ink-950/15 px-2 py-1 text-xs text-ink-950 hover:border-ink-950/30 hover:bg-ink-950/[0.03]"
      href={`/graphs/wiki-timeline-aoo?source=${encodeURIComponent(data.source ?? 'gwb')}`}
    >
      Open AAO
    </a>
    <a
      class="rounded-md border border-ink-950/15 px-2 py-1 text-xs text-ink-950 hover:border-ink-950/30 hover:bg-ink-950/[0.03]"
      href={`/graphs/wiki-timeline-aoo?source=${encodeURIComponent(data.source ?? 'gwb')}&view=step-ribbon`}
    >
      Open Step-Ribbon
    </a>
    <a
      class="rounded-md border border-ink-950/15 px-2 py-1 text-xs text-ink-950 hover:border-ink-950/30 hover:bg-ink-950/[0.03]"
      href={`/graphs/wiki-fact-timeline?source=${encodeURIComponent(data.source ?? 'gwb')}`}
    >
      Open Fact Timeline
    </a>
  </div>
</Panel>
