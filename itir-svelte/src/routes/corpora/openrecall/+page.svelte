<script lang="ts">
  import DashboardShell from '$lib/sb-dashboard/components/DashboardShell.svelte';
  import Panel from '$lib/ui/Panel.svelte';
  import Section from '$lib/ui/Section.svelte';
  import { page } from '$app/stores';

  export let data: {
    importRunId: string | null;
    appName: string | null;
    date: string | null;
    q: string;
    runs: Array<any>;
    summary: any;
    captures: Array<any>;
  };

  let q = data.q ?? '';

  function submitSearch(): void {
    const u = new URL($page.url);
    if (q.trim()) u.searchParams.set('q', q.trim());
    else u.searchParams.delete('q');
    window.location.href = u.pathname + (u.searchParams.toString() ? `?${u.searchParams.toString()}` : '');
  }

  function hrefForRun(runId: string): string {
    const u = new URL($page.url);
    u.searchParams.set('importRunId', runId);
    return u.pathname + '?' + u.searchParams.toString();
  }
</script>

<DashboardShell title="OpenRecall Browser">
  <Section title="OpenRecall captures" subtitle="Browse imported app/window/OCR captures from the canonical ITIR DB.">
    <div slot="actions" class="flex items-center gap-2">
      <input class="rounded-lg bg-paper-100 ring-1 ring-ink-900/10 px-3 py-2 text-sm" placeholder="Filter OCR / title / app..." bind:value={q} on:keydown={(e) => e.key === 'Enter' && submitSearch()} />
      <button class="rounded-lg bg-ink-900 text-paper-50 px-3 py-2 text-xs uppercase tracking-widest" on:click={submitSearch}>Search</button>
    </div>
    <div class="text-xs text-ink-800/60">
      Active import run: <span class="font-mono">{data.importRunId ?? '(latest)'}</span>
    </div>
  </Section>

  <div class="grid gap-4 lg:grid-cols-[1fr,1.4fr]">
    <div class="space-y-4">
      <Panel>
        <div class="text-xs uppercase tracking-[0.28em] text-ink-800/60">Import runs</div>
        <div class="mt-3 space-y-2">
          {#each data.runs as run}
            <a class={`block rounded-xl px-3 py-3 ring-1 ${run.import_run_id === data.importRunId ? 'bg-amber-50 ring-amber-300' : 'bg-paper-100 ring-ink-900/10 hover:bg-paper-200/70'}`} href={hrefForRun(run.import_run_id)}>
              <div class="font-mono text-[11px] text-ink-800/70 break-all">{run.import_run_id}</div>
              <div class="mt-1 text-sm text-ink-950">{run.imported_capture_count.toLocaleString()} captures</div>
              <div class="mt-1 text-[11px] text-ink-800/65">{run.imported_at}</div>
            </a>
          {/each}
        </div>
      </Panel>

      {#if data.summary}
        <Panel>
          <div class="text-xs uppercase tracking-[0.28em] text-ink-800/60">Summary</div>
          <div class="mt-3 space-y-1 text-sm text-ink-950">
            <div>{data.summary.captureCount.toLocaleString()} captures</div>
            <div>{data.summary.uniqueAppCount.toLocaleString()} apps</div>
            <div>{data.summary.withScreenshotCount.toLocaleString()} with screenshot</div>
            <div>{data.summary.latestCapturedAt ?? '—'}</div>
          </div>
          {#if data.summary.apps?.length}
            <div class="mt-4 text-xs uppercase tracking-[0.24em] text-ink-800/60">Apps</div>
            <div class="mt-2 flex flex-wrap gap-2">
              {#each data.summary.apps as app}
                <span class="rounded-full bg-paper-100 px-2 py-1 text-[11px] text-ink-800 ring-1 ring-ink-900/10">{app.appName}: {app.count}</span>
              {/each}
            </div>
          {/if}
        </Panel>
      {/if}
    </div>

    <Panel>
      <div class="text-xs uppercase tracking-[0.28em] text-ink-800/60">Captures</div>
      {#if data.captures.length === 0}
        <div class="mt-3 text-sm text-ink-800/70">No OpenRecall captures matched the current selection.</div>
      {:else}
        <div class="mt-3 space-y-3 max-h-[72dvh] overflow-auto pr-1">
          {#each data.captures as capture}
            <div class="rounded-xl bg-paper-100 px-4 py-3 ring-1 ring-ink-900/10">
              <div class="flex flex-wrap gap-3 text-[11px] font-mono text-ink-800/65">
                <span>{capture.captured_at}</span>
                <span>{capture.app_name || '(app?)'}</span>
                <span>{capture.window_title || '(window untitled)'}</span>
              </div>
              <div class="mt-2 whitespace-pre-wrap text-sm text-ink-950">{capture.ocr_text}</div>
              <div class="mt-2 text-[11px] text-ink-800/65">
                screenshot={capture.screenshot_path ?? '(none)'}
              </div>
            </div>
          {/each}
        </div>
      {/if}
    </Panel>
  </div>
</DashboardShell>
