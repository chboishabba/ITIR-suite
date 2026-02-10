<script lang="ts">
  import Section from '$lib/ui/Section.svelte';

  export let missingDates: string[] = [];
  export let start: string;
  export let end: string;
  export let runsRoot: string | null = null;
  export let buildSummary: { built: number; failed: number } | null = null;
  export let buildError: string | null = null;
</script>

{#if missingDates.length || buildSummary || buildError}
  <Section title="Missing Runs" subtitle="Dates in the selected range that have no dashboard output on disk.">
    {#if runsRoot}
      <div class="text-xs text-ink-800/60">
        SB_RUNS_ROOT (resolved): <span class="font-mono break-all">{runsRoot}</span>
      </div>
    {/if}

    {#if buildSummary}
      <div class="mt-2 text-sm text-ink-900/80">
        Build result: built <span class="font-mono">{buildSummary.built}</span>, failed <span class="font-mono">{buildSummary.failed}</span>.
      </div>
    {/if}

    {#if buildError}
      <div class="mt-2 rounded-xl bg-paper-100 ring-1 ring-red-700/30 px-4 py-3 text-sm text-red-900/80 whitespace-pre-wrap">
        {buildError}
      </div>
    {/if}

    <div class="text-sm text-ink-900/80">
      Missing {missingDates.length} day{missingDates.length === 1 ? '' : 's'}.
    </div>
    <div class="mt-3 flex flex-wrap gap-2">
      {#each missingDates as d (d)}
        <span class="rounded-full bg-paper-100 ring-1 ring-ink-900/10 px-3 py-1 font-mono text-xs text-ink-800/70">{d}</span>
      {/each}
    </div>

    <form method="POST" action="?/buildMissing" class="mt-4">
      <input type="hidden" name="start" value={start} />
      <input type="hidden" name="end" value={end} />
      <button
        class="rounded-lg bg-ink-900 text-paper-50 px-4 py-2 text-xs uppercase tracking-widest"
        type="submit"
      >
        Build Missing Days
      </button>
      <div class="mt-2 text-xs text-ink-800/60">
        Runs `StatiBaker/scripts/build_dashboard.py` for missing dates (writes dashboards into `SB_RUNS_ROOT`).
      </div>
    </form>
  </Section>
{/if}
