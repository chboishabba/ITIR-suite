<script lang="ts">
  import DashboardShell from '$lib/sb-dashboard/components/DashboardShell.svelte';
  import Section from '$lib/ui/Section.svelte';
  import Panel from '$lib/ui/Panel.svelte';
  import ChatBubble from '$lib/chat/ChatBubble.svelte';
  import type { ChatRole } from '$lib/chat/types';
  import { page } from '$app/stores';
  import { onDestroy, onMount, tick } from 'svelte';

  export let data: {
    threadId: string;
    title: string | null;
    total: number;
    tail: number;
    range: { start: string | null; end: string | null };
    notebookMetaSummary: {
      notebookIdHash: string | null;
      unscoped: boolean;
      eventCount: number;
      groupedMessageCount: number;
      sourceObservedCount: number;
      artifactObservedCount: number;
      sourceSummaryCount: number;
      uniqueNoteIdCount: number;
      firstTs: string | null;
      lastTs: string | null;
    } | null;
    notebookMetaSources: Array<{
      noteIdHash: string;
      sourceTitle: string | null;
      sourceType: string | null;
      sourceUrl: string | null;
      mentions: number;
    }> | null;
    messages: Array<{
      message_id: string;
      canonical_thread_id: string;
      ts: string;
      role: string;
      text: string;
      source_id: string | null;
      platform: string | null;
      account_id: string | null;
      source_message_id: string | null;
      source_thread_id: string | null;
    }>;
  };

  let collapsedLong = true;
  let q = '';
  let loadOlderHref = '';
  let backHref = '/';

  // Rendering a large thread tail in one shot creates a big DOM and slows down scroll.
  // We keep a tail-window mounted and progressively prepend within the already-loaded slice.
  const RENDER_STEP = 200;
  const INITIAL_RENDER = 250;
  let renderTailCount = INITIAL_RENDER;
  let listEl: HTMLDivElement | null = null;
  let topSentinelEl: HTMLDivElement | null = null;
  let io: IntersectionObserver | null = null;
  let didAutoScroll = false;
  let focusedMessageId: string | null = null;

  type SourceIndexRow = {
    hash: string;
    title: string;
    type: string;
    url: string;
    mentions: number;
  };

  function normalizeRole(r: string): ChatRole {
    const s = (r ?? '').toLowerCase().trim();
    if (s === 'user') return 'user';
    if (s === 'assistant') return 'assistant';
    if (s === 'tool') return 'tool';
    if (s === 'system') return 'system';
    return 'other';
  }

  function normalizeSourceType(v: string): string {
    const s = (v ?? '').trim();
    if (!s) return '';
    return s.replace(/^SourceType\./i, '').trim().toUpperCase();
  }

  function sourceTypeBadge(v: string): string {
    const s = normalizeSourceType(v);
    if (s === 'GOOGLE_DOCS' || s === 'GOOGLE_DOC') return 'GDoc';
    if (s === 'PASTED_TEXT' || s === 'TEXT') return 'Text';
    if (s === 'PDF') return 'PDF';
    if (s === 'WEB_PAGE' || s === 'WEB') return 'Web';
    if (s === 'YOUTUBE') return 'YT';
    if (!s) return 'Source';
    return s;
  }

  $: filtered = data.messages.filter((m) => {
    if (!q.trim()) return true;
    const needle = q.toLowerCase();
    return (m.text ?? '').toLowerCase().includes(needle) || (m.ts ?? '').toLowerCase().includes(needle);
  });

  $: rendered = filtered.slice(Math.max(0, filtered.length - renderTailCount));
  $: sourceIndex = (() => {
    const rowsRaw = data.notebookMetaSources ?? [];
    const rows: SourceIndexRow[] = rowsRaw.map((r) => ({
      hash: r.noteIdHash,
      title: (r.sourceTitle ?? '').trim() || '(untitled source)',
      type: normalizeSourceType(r.sourceType ?? ''),
      url: (r.sourceUrl ?? '').trim(),
      mentions: Math.max(1, Number(r.mentions ?? 1) || 1)
    }));
    const byHash: Record<string, number> = {};
    rows.forEach((r, i) => {
      byHash[r.hash] = i + 1;
    });
    return { rows, byHash };
  })();

  $: title = (data.title ?? '(untitled)').trim() || '(untitled)';
  $: focusTs = $page.url.searchParams.get('focus_ts');
  $: focusKey = focusTs ? focusTs.slice(0, 19) : null;
  $: focusMid = $page.url.searchParams.get('focus_mid');
  $: focusSourceMid = $page.url.searchParams.get('focus_source_message_id');

  $: {
    const u = new URL($page.url);
    const notebookMetaThread = Boolean(data.notebookMetaSummary);
    const tailStep = notebookMetaThread ? 100 : 400;
    const tailMax = notebookMetaThread ? 400 : 2000;
    u.searchParams.set('tail', String(Math.min(tailMax, (data.tail ?? tailStep) + tailStep)));
    loadOlderHref = u.pathname + '?' + u.searchParams.toString();

    const b = new URL($page.url);
    b.pathname = '/';
    if (data.range.start) b.searchParams.set('start', data.range.start);
    else b.searchParams.delete('start');
    if (data.range.end) b.searchParams.set('end', data.range.end);
    else b.searchParams.delete('end');
    // Keep other params out.
    backHref = b.pathname + (b.searchParams.toString() ? '?' + b.searchParams.toString() : '');
  }

  async function prependMoreWithinLoaded(): Promise<void> {
    if (!listEl) return;
    if (renderTailCount >= filtered.length) return;
    const prevScrollHeight = listEl.scrollHeight;
    const prevScrollTop = listEl.scrollTop;

    renderTailCount = Math.min(filtered.length, renderTailCount + RENDER_STEP);
    await tick();

    // Keep the viewport anchored when we prepend.
    const nextScrollHeight = listEl.scrollHeight;
    listEl.scrollTop = nextScrollHeight - prevScrollHeight + prevScrollTop;
  }

  // Reset progressive rendering when the data slice or filter changes.
  $: {
    // Filter changes should be responsive; keep the initial DOM smaller.
    renderTailCount = Math.min(filtered.length, INITIAL_RENDER);
  }

  onMount(() => {
    if (!listEl) return;
    if (!topSentinelEl) return;
    if (typeof IntersectionObserver === 'undefined') return;

    io = new IntersectionObserver(
      (entries) => {
        const e = entries[0];
        if (!e?.isIntersecting) return;
        void prependMoreWithinLoaded();
      },
      { root: listEl, threshold: 0.01 }
    );
    io.observe(topSentinelEl);

    void (async () => {
      await tick();
      if (!listEl) return;

      // If a focus timestamp is provided, try to locate and center that message
      // (even if it requires progressively prepending within the loaded slice).
      if (focusMid) {
        for (let tries = 0; tries < 24; tries++) {
          const hit = listEl.querySelector(`[data-message-id="${focusMid}"]`) as HTMLElement | null;
          if (hit) {
            focusedMessageId = hit.getAttribute('data-message-id');
            hit.scrollIntoView({ block: 'center' });
            didAutoScroll = true;
            return;
          }
          if (renderTailCount >= filtered.length) break;
          await prependMoreWithinLoaded();
        }
      }

      if (focusSourceMid) {
        for (let tries = 0; tries < 24; tries++) {
          const hit = listEl.querySelector(`[data-source-message-id="${focusSourceMid}"]`) as HTMLElement | null;
          if (hit) {
            focusedMessageId = hit.getAttribute('data-message-id');
            hit.scrollIntoView({ block: 'center' });
            didAutoScroll = true;
            return;
          }
          if (renderTailCount >= filtered.length) break;
          await prependMoreWithinLoaded();
        }
      }

      if (focusKey) {
        for (let tries = 0; tries < 24; tries++) {
          const hit = listEl.querySelector(`[data-ts="${focusKey}"]`) as HTMLElement | null;
          if (hit) {
            focusedMessageId = hit.getAttribute('data-message-id');
            hit.scrollIntoView({ block: 'center' });
            didAutoScroll = true;
            return;
          }
          if (renderTailCount >= filtered.length) break;
          await prependMoreWithinLoaded();
        }
        // Fall through to bottom if we couldn't find it.
      }

      if (didAutoScroll) return;
      listEl.scrollTop = listEl.scrollHeight;
      didAutoScroll = true;
    })();
  });

  onDestroy(() => io?.disconnect());
</script>

<DashboardShell title="Thread Viewer">
  <Section title={title} subtitle={`thread_id=${data.threadId}${data.range.start && data.range.end ? ` | range=${data.range.start}..${data.range.end}` : ''}`}>
    <div slot="actions" class="flex flex-wrap items-center gap-2">
      <input
        class="rounded-lg bg-paper-100 ring-1 ring-ink-900/10 px-3 py-2 text-sm"
        placeholder="Filter..."
        bind:value={q}
      />
      <label class="flex items-center gap-2 text-xs uppercase tracking-widest text-ink-800/60">
        <input type="checkbox" bind:checked={collapsedLong} />
        Collapse long
      </label>
      <a
        class="rounded-lg bg-paper-100 ring-1 ring-ink-900/10 px-3 py-2 text-xs uppercase tracking-widest"
        href={backHref}
      >
        Back
      </a>
      <a
        class="rounded-lg bg-ink-900 text-paper-50 px-3 py-2 text-xs uppercase tracking-widest"
        href={loadOlderHref}
      >
        Load older
      </a>
    </div>

    <div class="text-xs text-ink-800/60">
      Showing <span class="font-mono">{rendered.length.toLocaleString()}</span> of <span class="font-mono">{filtered.length.toLocaleString()}</span> loaded (total <span class="font-mono">{data.total.toLocaleString()}</span>, tail={data.tail}).
    </div>
  </Section>

  {#if data.notebookMetaSummary}
    <Panel>
      <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">NotebookLM Snapshot</div>
      <div class="mt-3 grid gap-2 sm:grid-cols-2 lg:grid-cols-5">
        <div class="rounded-lg bg-paper-100 ring-1 ring-ink-900/10 px-3 py-2">
          <div class="text-[10px] uppercase tracking-widest text-ink-800/60">Notebook</div>
          <div class="mt-1 font-mono text-xs text-ink-950 break-all">
            {#if data.notebookMetaSummary.unscoped}
              unscoped
            {:else}
              {data.notebookMetaSummary.notebookIdHash}
            {/if}
          </div>
        </div>
        <div class="rounded-lg bg-paper-100 ring-1 ring-ink-900/10 px-3 py-2">
          <div class="text-[10px] uppercase tracking-widest text-ink-800/60">Events</div>
          <div class="mt-1 font-mono text-sm text-ink-950">{data.notebookMetaSummary.eventCount.toLocaleString()}</div>
          <div class="text-[11px] text-ink-800/70">
            grouped messages: <span class="font-mono">{data.notebookMetaSummary.groupedMessageCount.toLocaleString()}</span>
          </div>
        </div>
        <div class="rounded-lg bg-paper-100 ring-1 ring-ink-900/10 px-3 py-2">
          <div class="text-[10px] uppercase tracking-widest text-ink-800/60">Sources Observed</div>
          <div class="mt-1 font-mono text-sm text-ink-950">{data.notebookMetaSummary.sourceObservedCount.toLocaleString()}</div>
          <div class="text-[11px] text-ink-800/70">
            unique source ids: <span class="font-mono">{data.notebookMetaSummary.uniqueNoteIdCount.toLocaleString()}</span>
          </div>
        </div>
        <div class="rounded-lg bg-paper-100 ring-1 ring-ink-900/10 px-3 py-2">
          <div class="text-[10px] uppercase tracking-widest text-ink-800/60">Artifacts / Snippets</div>
          <div class="mt-1 text-[11px] text-ink-800/80">
            artifact rows: <span class="font-mono">{data.notebookMetaSummary.artifactObservedCount.toLocaleString()}</span>
          </div>
          <div class="text-[11px] text-ink-800/80">
            source snippets: <span class="font-mono">{data.notebookMetaSummary.sourceSummaryCount.toLocaleString()}</span>
          </div>
        </div>
        <div class="rounded-lg bg-paper-100 ring-1 ring-ink-900/10 px-3 py-2">
          <div class="text-[10px] uppercase tracking-widest text-ink-800/60">Window</div>
          <div class="mt-1 text-[11px] text-ink-800/80">
            first: <span class="font-mono">{data.notebookMetaSummary.firstTs ?? '-'}</span>
          </div>
          <div class="text-[11px] text-ink-800/80">
            last: <span class="font-mono">{data.notebookMetaSummary.lastTs ?? '-'}</span>
          </div>
        </div>
      </div>
    </Panel>

    {#if sourceIndex.rows.length}
      <Panel>
        <div class="flex flex-wrap items-center justify-between gap-2">
          <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Source Index</div>
          <div class="font-mono text-[11px] text-ink-800/65">{sourceIndex.rows.length.toLocaleString()} source(s)</div>
        </div>
        <div class="mt-2 max-h-[280px] overflow-auto overscroll-contain rounded-xl bg-paper-50 ring-1 ring-ink-900/10">
          <div class="divide-y divide-ink-900/10">
            {#each sourceIndex.rows as s, i (s.hash)}
              <div class="px-3 py-2">
                <div class="flex flex-wrap items-center gap-2">
                  <span class="inline-flex items-center rounded-full bg-ink-900 text-paper-50 px-2 py-[2px] text-[10px] font-mono">{i + 1}</span>
                  <span class="inline-flex items-center rounded-full bg-paper-100 ring-1 ring-ink-900/10 px-2 py-[2px] text-[10px] font-mono">{sourceTypeBadge(s.type)}</span>
                  <span class="min-w-0 flex-1 truncate text-[12px] text-ink-950/90" title={s.title}>{s.title}</span>
                  <span class="font-mono text-[10px] text-ink-800/60">mentions={s.mentions}</span>
                </div>
                <div class="mt-1 flex flex-wrap items-center gap-x-3 gap-y-1 font-mono text-[10px] text-ink-800/60">
                  <span title={s.hash}>id={s.hash.replace(/^sha256:/i, '').slice(0, 12)}...</span>
                  {#if s.url}
                    <a href={s.url} target="_blank" rel="noreferrer" class="truncate max-w-full text-sky-900 underline decoration-sky-900/30 underline-offset-2">{s.url}</a>
                  {/if}
                </div>
              </div>
            {/each}
          </div>
        </div>
      </Panel>
    {/if}
  {/if}

  {#if !filtered.length}
    <Panel tone="warn">
      No messages loaded for this thread (or filter excluded all).
    </Panel>
  {:else}
    <div class="rounded-2xl ring-1 ring-ink-900/10 bg-paper-50 shadow-crisp">
      <div bind:this={listEl} class="max-h-[70dvh] overflow-auto overscroll-contain px-4 py-4 space-y-4">
        <div bind:this={topSentinelEl} class="h-px"></div>
        {#each rendered as m (m.message_id)}
          <ChatBubble
            messageId={m.message_id}
            sourceMessageId={m.source_message_id}
            notebookSourceIndex={sourceIndex.byHash}
            focused={focusedMessageId === m.message_id}
            role={normalizeRole(m.role)}
            ts={m.ts}
            source={m.source_id}
            text={m.text ?? ''}
            collapsed={collapsedLong}
          />
        {/each}
      </div>
    </div>
  {/if}
</DashboardShell>
