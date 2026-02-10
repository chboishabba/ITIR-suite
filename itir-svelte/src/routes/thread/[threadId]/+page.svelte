<script lang="ts">
  import DashboardShell from '$lib/sb-dashboard/components/DashboardShell.svelte';
  import Section from '$lib/ui/Section.svelte';
  import Panel from '$lib/ui/Panel.svelte';
  import ChatBubble, { type ChatRole } from '$lib/chat/ChatBubble.svelte';
  import { page } from '$app/stores';

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

  $: title = (data.title ?? '(untitled)').trim() || '(untitled)';

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
      Showing <span class="font-mono">{filtered.length.toLocaleString()}</span> of <span class="font-mono">{data.total.toLocaleString()}</span> messages (tail={data.tail}).
    </div>
  </Section>

  {#if !filtered.length}
    <Panel tone="warn">
      No messages loaded for this thread (or filter excluded all).
    </Panel>
  {:else}
    <div class="rounded-2xl ring-1 ring-ink-900/10 bg-paper-50 shadow-crisp">
      <div class="max-h-[70dvh] overflow-auto overscroll-contain px-4 py-4 space-y-4">
        {#each filtered as m (m.message_id)}
          <ChatBubble role={normalizeRole(m.role)} ts={m.ts} source={m.source_id} text={m.text ?? ''} collapsed={collapsedLong} />
        {/each}
      </div>
    </div>
  {/if}
</DashboardShell>
