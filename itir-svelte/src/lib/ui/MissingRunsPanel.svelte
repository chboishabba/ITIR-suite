<script lang="ts">
  import Section from '$lib/ui/Section.svelte';
  import { onDestroy, onMount } from 'svelte';

  export let missingDates: string[] = [];
  export let start: string;
  export let end: string;
  export let runsRoot: string | null = null;
  export let buildSummary: { built: number; failed: number } | null = null;
  export let buildError: string | null = null;
  export let autoBuildEnabled: boolean = false;

  type Job = {
    jobId: string;
    stage: string;
    percent: number;
    message: string;
    missingTotal: number;
    built: number;
    failed: number;
    errors: string[];
    done: boolean;
  };

  let jobId: string | null = null;
  let job: Job | null = null;
  let jobError: string | null = null;
  let polling: any = null;
  let lastAutoKey = '';

  async function startJob(): Promise<void> {
    jobError = null;
    try {
      const resp = await fetch('/api/build-missing/start', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ start, end })
      });
      const data = await resp.json().catch(() => null);
      if (!resp.ok || !data?.ok) throw new Error(String(data?.error ?? resp.statusText));
      jobId = String(data.jobId);
      await pollOnce();
      startPolling();
    } catch (err) {
      jobError = err instanceof Error ? err.message : String(err);
    }
  }

  async function pollOnce(): Promise<void> {
    if (!jobId) return;
    const resp = await fetch(`/api/build-missing/status?jobId=${encodeURIComponent(jobId)}`);
    const data = await resp.json().catch(() => null);
    if (!resp.ok || !data?.ok) {
      jobError = String(data?.error ?? resp.statusText);
      return;
    }
    job = data.job as Job;
    if (job?.done) stopPolling();
  }

  function startPolling(): void {
    if (polling) return;
    polling = setInterval(() => void pollOnce(), 600);
  }

  function stopPolling(): void {
    if (polling) clearInterval(polling);
    polling = null;
  }

  onDestroy(() => stopPolling());

  onMount(() => {
    const key = `${start}..${end}|${missingDates.join(',')}`;
    if (!autoBuildEnabled) return;
    if (!missingDates.length) return;
    if (key === lastAutoKey) return;
    lastAutoKey = key;
    void startJob();
  });
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

    {#if jobError}
      <div class="mt-2 rounded-xl bg-paper-100 ring-1 ring-red-700/30 px-4 py-3 text-sm text-red-900/80 whitespace-pre-wrap">
        {jobError}
      </div>
    {/if}

    {#if job && !job.done}
      <div class="mt-3 flex items-center gap-3">
        <div
          class="h-4 w-4 rounded-full border-2 border-ink-900/30 border-t-ink-900 animate-spin"
          aria-label="building"
        ></div>
        <div class="text-sm text-ink-900/80">
          {job.message}
          <span class="ml-2 font-mono text-xs text-ink-900/70">{Math.max(0, Math.min(100, Math.trunc(job.percent)))}%</span>
        </div>
      </div>
      <div class="mt-2 h-2 rounded-full bg-paper-100 ring-1 ring-ink-900/10 overflow-hidden">
        <div class="h-2 bg-ink-900/70" style={`width: ${Math.max(0, Math.min(100, Math.trunc(job.percent)))}%`}></div>
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

    <div class="mt-4 flex flex-wrap items-center gap-3">
      <button
        class="rounded-lg bg-ink-900 text-paper-50 px-4 py-2 text-xs uppercase tracking-widest disabled:opacity-50"
        type="button"
        on:click={() => startJob()}
        disabled={Boolean(jobId && job && !job.done)}
      >
        Build Missing Days
      </button>
      <div class="text-xs text-ink-800/60">
        Ingestes Codex chats (best-effort) then runs `StatiBaker/scripts/build_dashboard.py` for missing dates.
      </div>
    </div>
  </Section>
{/if}
