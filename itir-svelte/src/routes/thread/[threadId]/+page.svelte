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
    messages: Array<{
      message_id: string;
      canonical_thread_id: string;
      ts: string;
      role: string;
      text: string;
      source_id: string | null;
      platform: string | null;
      account_id: string | null;
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

  function normalizeRole(r: string): ChatRole {
    const s = (r ?? '').toLowerCase().trim();
    if (s === 'user') return 'user';
    if (s === 'assistant') return 'assistant';
    if (s === 'tool') return 'tool';
    if (s === 'system') return 'system';
    return 'other';
  }

  $: filtered = data.messages.filter((m) => {
    if (!q.trim()) return true;
    const needle = q.toLowerCase();
    return (m.text ?? '').toLowerCase().includes(needle) || (m.ts ?? '').toLowerCase().includes(needle);
  });

  $: rendered = filtered.slice(Math.max(0, filtered.length - renderTailCount));

  $: title = (data.title ?? '(untitled)').trim() || '(untitled)';
  $: focusTs = $page.url.searchParams.get('focus_ts');
  $: focusKey = focusTs ? focusTs.slice(0, 19) : null;

  $: {
    const u = new URL($page.url);
    u.searchParams.set('tail', String(Math.min(2000, (data.tail ?? 400) + 400)));
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
