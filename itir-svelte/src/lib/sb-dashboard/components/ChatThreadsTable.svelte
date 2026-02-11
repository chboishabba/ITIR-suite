<script lang="ts">
  import Section from '$lib/ui/Section.svelte';
  import type { ThreadRow } from '../adapters/dashboard';

  export let rows: ThreadRow[];
  export let start: string | null = null;
  export let end: string | null = null;
  export let notebooklmMetaEvents: number = 0;

  const UNKNOWN_SOURCE = '(unknown)';
  const NOTEBOOKLM_META_SOURCE = 'notebooklm (meta-only)';

  type SortKey = 'share' | 'messageCount' | 'title';
  let sortKey: SortKey = 'share';
  let sourceEnabled: Record<string, boolean> = {};

  $: sorted = [...rows].sort((a, b) => {
    if (sortKey === 'title') return a.title.localeCompare(b.title);
    if (sortKey === 'messageCount') return b.messageCount - a.messageCount;
    return (b.share ?? 0) - (a.share ?? 0) || b.messageCount - a.messageCount;
  });
  $: availableSources = (() => {
    const set = new Set<string>(rows.flatMap((r) => rowSources(r)));
    if (notebooklmMetaEvents > 0) set.add(NOTEBOOKLM_META_SOURCE);
    return [...set].sort((a, b) => a.localeCompare(b));
  })();
  $: {
    const next: Record<string, boolean> = {};
    let changed = Object.keys(sourceEnabled).length !== availableSources.length;
    for (const src of availableSources) {
      const value = sourceEnabled[src] ?? true;
      next[src] = value;
      if (sourceEnabled[src] !== value) changed = true;
    }
    if (changed) sourceEnabled = next;
  }
  $: activeSourceCount = availableSources.filter((src) => sourceEnabled[src]).length;
  $: filtered = sorted.filter((r) => rowSources(r).some((src) => sourceEnabled[src]));

  function pct(v: number | undefined): string {
    if (v === undefined) return '';
    return `${(v * 100).toFixed(1)}%`;
  }

  function shortTs(ts?: string): string {
    if (!ts) return '';
    // Expect ISO like 2026-02-03T12:40:42Z -> 2026-02-03 12:40
    if (ts.length >= 16) return `${ts.slice(0, 10)} ${ts.slice(11, 16)}`;
    return ts;
  }

  async function copy(text: string) {
    try {
      await navigator.clipboard.writeText(text);
    } catch {
      // ignore
    }
  }

  function threadHref(threadId: string): string {
    const qs: string[] = [];
    if (start) qs.push(`start=${encodeURIComponent(start)}`);
    if (end) qs.push(`end=${encodeURIComponent(end)}`);
    return `/thread/${encodeURIComponent(threadId)}${qs.length ? `?${qs.join('&')}` : ''}`;
  }

  function isMetaRow(row: ThreadRow): boolean {
    return Boolean(row.metaOnly) || row.threadId.startsWith('meta:');
  }

  function rowSources(row: ThreadRow): string[] {
    const sources = (row.sources ?? [])
      .map((src) => String(src ?? '').trim())
      .filter(Boolean);
    if (sources.length) return sources;
    const fallback = String(row.origin ?? '').trim();
    return fallback ? [fallback] : [UNKNOWN_SOURCE];
  }

  function sourceLabel(row: ThreadRow): string {
    const sources = rowSources(row);
    if (sources.length <= 1) return sources[0] ?? '';
    return `${sources[0]} +${sources.length - 1}`;
  }

  function sourceTitle(row: ThreadRow): string {
    return rowSources(row).join(', ');
  }

  function sourceDescription(src: string): string {
    if (src === NOTEBOOKLM_META_SOURCE) {
      return `NotebookLM metadata events in range: ${Math.max(0, Math.trunc(notebooklmMetaEvents))}`;
    }
    return src;
  }

  function setAllSources(enabled: boolean) {
    const next: Record<string, boolean> = {};
    for (const src of availableSources) next[src] = enabled;
    sourceEnabled = next;
  }

  function toggleSource(src: string, enabled: boolean) {
    sourceEnabled = { ...sourceEnabled, [src]: enabled };
  }
</script>

<Section title="Chat Threads" subtitle="Thread list with color mapping (from chat_flow).">
  <div slot="actions" class="flex items-center gap-2">
    <label class="text-xs uppercase tracking-widest text-ink-800/60" for="sort">Sort</label>
    <select id="sort" class="rounded-lg bg-paper-100 ring-1 ring-ink-900/10 px-2 py-1 text-sm" bind:value={sortKey}>
      <option value="share">Share</option>
      <option value="messageCount">Messages</option>
      <option value="title">Title</option>
    </select>
    <details class="relative">
      <summary class="list-none cursor-pointer rounded-lg bg-paper-100 ring-1 ring-ink-900/10 px-2 py-1 text-sm text-ink-900/80 select-none">
        Sources {activeSourceCount}/{availableSources.length || 0}
      </summary>
      <div class="absolute right-0 mt-2 z-20 w-80 rounded-xl bg-paper-50 ring-1 ring-ink-900/15 shadow-crisp p-3">
        <div class="flex items-center justify-between gap-2 mb-2">
          <div class="text-xs uppercase tracking-widest text-ink-800/60">Source Filter</div>
          <div class="flex items-center gap-2">
            <button type="button" class="text-xs underline decoration-ink-900/20 hover:decoration-ink-900/50" on:click={() => setAllSources(true)}>All</button>
            <button type="button" class="text-xs underline decoration-ink-900/20 hover:decoration-ink-900/50" on:click={() => setAllSources(false)}>None</button>
          </div>
        </div>
        <div class="max-h-64 overflow-auto pr-1 space-y-1">
          {#if !availableSources.length}
            <div class="text-xs text-ink-800/70">No sources available.</div>
          {:else}
            {#each availableSources as src (src)}
              <label class="flex items-center gap-2 text-xs text-ink-900/85">
                <input
                  type="checkbox"
                  class="rounded border-ink-900/20"
                  checked={sourceEnabled[src]}
                  on:change={(e) => toggleSource(src, (e.currentTarget as HTMLInputElement).checked)}
                />
                <span class="font-mono truncate" title={sourceDescription(src)}>
                  {src}
                </span>
              </label>
            {/each}
          {/if}
        </div>
        {#if notebooklmMetaEvents > 0}
          <div class="mt-2 border-t border-ink-900/10 pt-2 text-[11px] text-ink-800/70">
            <span class="font-mono">{NOTEBOOKLM_META_SOURCE}</span> rows are grouped from NotebookLM notes metadata logs.
          </div>
        {/if}
      </div>
    </details>
  </div>

  <div class="max-h-[420px] overflow-auto overscroll-contain rounded-xl ring-1 ring-ink-900/10">
    <table class="min-w-[980px] w-full table-fixed border-separate border-spacing-0">
      <thead class="sticky top-0 bg-paper-100">
        <tr>
          <th class="w-[60%] text-left text-xs uppercase tracking-widest text-ink-800/60 px-3 py-2">Thread</th>
          <th class="w-[140px] text-left text-xs uppercase tracking-widest text-ink-800/60 px-3 py-2">First</th>
          <th class="w-[140px] text-left text-xs uppercase tracking-widest text-ink-800/60 px-3 py-2">Last</th>
          <th class="w-[90px] text-right text-xs uppercase tracking-widest text-ink-800/60 px-3 py-2">Share</th>
          <th class="w-[90px] text-right text-xs uppercase tracking-widest text-ink-800/60 px-3 py-2">Msgs</th>
          <th class="w-[140px] text-left text-xs uppercase tracking-widest text-ink-800/60 px-3 py-2">Origin</th>
        </tr>
      </thead>
      <tbody>
        {#if !filtered.length}
          <tr class="odd:bg-paper-50 even:bg-paper-100">
            <td class="px-3 py-3 text-sm text-ink-900/70" colspan="6">
              No threads match the selected source filters.
            </td>
          </tr>
        {:else}
          {#each filtered as r (r.threadId)}
            <tr class="group odd:bg-paper-50 even:bg-paper-100">
              <td class="px-3 py-1.5 relative">
                <div class="flex items-center gap-3 min-w-0">
                  <div class="h-3 w-3 rounded-sm ring-1 ring-ink-900/20 shrink-0" style={`background:${r.colorHex ?? '#ddd'}`}></div>
                  <div class="min-w-0">
                    <div class="flex items-center gap-2 min-w-0">
                      <a
                        class="text-sm text-ink-950 truncate underline decoration-ink-900/20 hover:decoration-ink-900/50"
                        title="Open thread viewer in new tab"
                        href={threadHref(r.threadId)}
                        target="_blank"
                        rel="noreferrer"
                      >
                        {r.title}
                      </a>
                      {#if isMetaRow(r)}
                        <span class="rounded-full bg-paper-100 ring-1 ring-ink-900/10 px-2 py-0.5 text-[10px] uppercase tracking-widest text-ink-800/70">meta</span>
                      {/if}
                    </div>
                  </div>
                </div>

                <div class="pointer-events-none opacity-0 group-hover:opacity-100 group-hover:pointer-events-auto transition-opacity absolute right-3 top-1/2 -translate-y-1/2 z-10">
                  <button
                    class="rounded-full bg-paper-50 shadow-crisp ring-1 ring-ink-900/15 px-3 py-1 font-mono text-[11px] text-ink-900/80 whitespace-nowrap max-w-[52rem] overflow-x-auto"
                    type="button"
                    title="Click to copy full thread ID"
                    on:click={() => copy(r.threadId)}
                  >
                    id={r.threadId}
                  </button>
                </div>
              </td>
              <td class="px-3 py-1.5 font-mono text-xs text-ink-900/70 whitespace-nowrap" title={r.firstTs ?? ''}>
                {shortTs(r.firstTs) || '-'}
              </td>
              <td class="px-3 py-1.5 font-mono text-xs text-ink-900/70 whitespace-nowrap" title={r.lastTs ?? ''}>
                {shortTs(r.lastTs) || '-'}
              </td>
              <td class="px-3 py-1.5 text-right font-mono text-xs text-ink-900/80">{pct(r.share)}</td>
              <td class="px-3 py-1.5 text-right font-mono text-xs text-ink-900/80">{r.messageCount.toLocaleString()}</td>
              <td class="px-3 py-1.5 font-mono text-xs text-ink-800/70 truncate" title={sourceTitle(r)}>{sourceLabel(r)}</td>
            </tr>
          {/each}
        {/if}
      </tbody>
    </table>
  </div>
</Section>
