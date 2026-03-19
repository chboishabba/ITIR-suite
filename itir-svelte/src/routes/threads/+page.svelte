<script lang="ts">
  import DashboardShell from '$lib/sb-dashboard/components/DashboardShell.svelte';
  import Section from '$lib/ui/Section.svelte';
  import Panel from '$lib/ui/Panel.svelte';
  import { page } from '$app/stores';

  export let data: {
    threads: Array<{
      canonical_thread_id: string;
      title: string;
      message_count: number;
      empty_text_count: number;
      latest_ts: string;
      source_id: string | null;
      platform: string | null;
      account_id: string | null;
      any_source_thread_id: string | null;
    }>;
    q: string;
    limit: number;
    offset: number;
  };

  let q = data.q ?? '';

  function submitSearch(): void {
    const u = new URL($page.url);
    if (q.trim()) u.searchParams.set('q', q.trim());
    else u.searchParams.delete('q');
    u.searchParams.delete('offset');
    window.location.href = u.pathname + (u.searchParams.toString() ? `?${u.searchParams.toString()}` : '');
  }

  function shortId(id: string): string {
    const s = (id ?? '').trim();
    if (s.length <= 12) return s;
    return s.slice(0, 10) + '…';
  }

  function fmtTs(ts: string): string {
    const s = (ts ?? '').trim();
    // 2026-02-04T22:03:27+00:00 -> 2026-02-04 22:03
    if (s.length >= 16) return `${s.slice(0, 10)} ${s.slice(11, 16)}`;
    return s;
  }
</script>

  <DashboardShell title="Threads">
  <Section title="Threads" subtitle="Browse/search the local chat archive. Query matches title, canonical thread id, source ids.">
    <div slot="actions" class="flex flex-wrap items-center gap-2">
      <label class="sr-only" for="threads-search">Search threads</label>
      <input
        id="threads-search"
        class="rounded-lg bg-paper-100 ring-1 ring-ink-900/10 px-3 py-2 text-sm min-w-[18rem]"
        placeholder="Search title / id / source..."
        bind:value={q}
        on:keydown={(e) => e.key === 'Enter' && submitSearch()}
        aria-label="Search threads"
      />
      <button
        type="button"
        class="rounded-lg bg-ink-900 text-paper-50 px-3 py-2 text-xs uppercase tracking-widest"
        on:click={submitSearch}
      >
        Search
      </button>
      <a class="rounded-lg bg-paper-100 ring-1 ring-ink-900/10 px-3 py-2 text-xs uppercase tracking-widest" href="/">Back</a>
    </div>
    <div class="text-xs text-ink-800/60">
      Showing up to <span class="font-mono">{data.limit}</span> threads (offset <span class="font-mono">{data.offset}</span>).
    </div>
  </Section>

  {#if !data.threads?.length}
    <Panel tone="warn">
      No threads found (try a different query).
    </Panel>
  {:else}
    <div class="rounded-2xl ring-1 ring-ink-900/10 bg-paper-50 shadow-crisp overflow-hidden">
      <div class="overflow-auto overscroll-contain max-h-[70dvh]">
        <table class="min-w-[920px] w-full table-fixed">
          <thead class="sticky top-0 bg-paper-50 ring-1 ring-ink-900/10">
            <tr class="text-left text-[10px] font-mono uppercase tracking-widest text-ink-800/60">
              <th class="px-3 py-2 w-[42%]">Title</th>
              <th class="px-3 py-2 w-[14%]">Latest</th>
              <th class="px-3 py-2 w-[10%] text-right">Msgs</th>
              <th class="px-3 py-2 w-[10%] text-right">Empty</th>
              <th class="px-3 py-2 w-[24%]">IDs</th>
            </tr>
          </thead>
          <tbody>
            {#each data.threads as t (t.canonical_thread_id)}
              <tr class="border-t border-ink-900/10 hover:bg-paper-100">
                <td class="px-3 py-2">
                  <a
                    class="text-sm text-ink-950 hover:underline"
                    href={`/thread/${t.canonical_thread_id}${$page.url.searchParams.get('start') || $page.url.searchParams.get('end') ? `?${$page.url.searchParams.toString()}` : ''}`}
                    target="_blank"
                    rel="noreferrer"
                    title="Open thread viewer (new tab)"
                  >
                    <span class="truncate block">{t.title}</span>
                  </a>
                </td>
                <td class="px-3 py-2 font-mono text-xs text-ink-800/70" title={t.latest_ts}>{fmtTs(t.latest_ts)}</td>
                <td class="px-3 py-2 font-mono text-xs text-ink-800/70 text-right">{t.message_count.toLocaleString()}</td>
                <td class="px-3 py-2 font-mono text-xs text-ink-800/70 text-right">{t.empty_text_count.toLocaleString()}</td>
                <td class="px-3 py-2">
                  <div class="font-mono text-[11px] text-ink-800/70 truncate" title={t.canonical_thread_id}>
                    canon={shortId(t.canonical_thread_id)}
                  </div>
                  <div class="font-mono text-[11px] text-ink-800/60 truncate" title={t.any_source_thread_id ?? ''}>
                    {t.any_source_thread_id ? `source_thread=${shortId(t.any_source_thread_id)}` : 'source_thread=(none)'}
                  </div>
                  <div class="font-mono text-[11px] text-ink-800/60 truncate" title={t.source_id ?? ''}>
                    {t.source_id ? `source=${t.source_id}` : ''}
                  </div>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    </div>
  {/if}
</DashboardShell>
