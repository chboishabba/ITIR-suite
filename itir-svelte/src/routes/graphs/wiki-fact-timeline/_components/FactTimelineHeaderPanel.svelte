<script lang="ts">
  import Panel from '$lib/ui/Panel.svelte';
  import { type ImportanceProfileId } from '$lib/importanceProfiles';

  type TimeGranularity = 'year' | 'month' | 'day';

  export let relPath: string;
  export let source: string | undefined;
  export let diagnostics:
    | {
        event_count: number;
        fact_row_source: string;
        raw_fact_rows: number;
        output_fact_rows: number;
      }
    | undefined;
  export let granularity: TimeGranularity;
  export let maxFacts: number;
  export let factsAllLength: number;
  export let importanceProfile: ImportanceProfileId;
  export let scopeValidation: {
    ok: boolean;
    leakCount: number;
    sample: string[];
  };
</script>

<Panel>
  <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Fact timeline</div>
  <div class="mt-2 text-sm text-ink-950">
    Source: <span class="font-mono text-xs">{relPath}</span>
  </div>
  <div class="mt-2 text-xs text-ink-800/60">
    Linearized fact rows from sentence-local extraction. Non-causal. Non-authoritative.
  </div>
  {#if diagnostics}
    <div class="mt-2 font-mono text-[10px] text-ink-800/70">
      events={diagnostics.event_count}
      rows_raw={diagnostics.raw_fact_rows}
      rows_out={diagnostics.output_fact_rows}
      source={diagnostics.fact_row_source}
    </div>
  {/if}

  <div class="mt-4 flex flex-wrap items-center gap-3 text-sm">
    <label class="flex items-center gap-2">
      <span class="text-ink-800/70">Dataset</span>
      <select
        class="rounded-md border border-ink-950/15 bg-white px-2 py-1 text-sm"
        value={source ?? 'hca'}
        on:change={(e) => {
          const v = (e.currentTarget as HTMLSelectElement).value;
          window.location.href = `/graphs/wiki-fact-timeline?source=${encodeURIComponent(v)}`;
        }}
      >
        <option value="hca">hca</option>
        <option value="gwb">gwb</option>
        <option value="legal">legal</option>
        <option value="legal_follow">legal_follow</option>
      </select>
    </label>
    <label class="flex items-center gap-2">
      <span class="text-ink-800/70">Time</span>
      <select bind:value={granularity} class="rounded-md border border-ink-950/15 bg-white px-2 py-1 text-sm">
        <option value="year">Year</option>
        <option value="month">Month</option>
        <option value="day">Day</option>
      </select>
    </label>
    <label class="flex items-center gap-2">
      <span class="text-ink-800/70">Facts</span>
      <input
        type="number"
        min="20"
        max={factsAllLength}
        step="10"
        bind:value={maxFacts}
        class="w-24 rounded-md border border-ink-950/15 px-2 py-1 font-mono text-xs"
        aria-label="Max facts"
      />
    </label>
    <label class="flex items-center gap-2">
      <span class="text-ink-800/70">Importance</span>
      <select bind:value={importanceProfile} class="rounded-md border border-ink-950/15 bg-white px-2 py-1 text-sm">
        <option value="entropy_role_section_v1">entropy_role_section_v1</option>
        <option value="none">none</option>
      </select>
    </label>
    <a
      class="rounded-md border border-ink-950/15 px-2 py-1 text-xs text-ink-950 hover:border-ink-950/30 hover:bg-ink-950/[0.03]"
      href={`/graphs/wiki-timeline-aoo-all?source=${encodeURIComponent(source ?? 'hca')}`}
    >
      Open AAO-all
    </a>
  </div>
  <div class="mt-2 font-mono text-[10px] text-ink-800/70">
    scope_validator={scopeValidation.ok ? 'ok' : 'leak'}
    leaks={scopeValidation.leakCount}
    profile={importanceProfile}
  </div>
  {#if !scopeValidation.ok}
    <div class="mt-1 rounded border border-red-300/60 bg-red-50 px-2 py-1 font-mono text-[10px] text-red-800">
      {scopeValidation.sample.join(' | ')}
    </div>
  {/if}
</Panel>
