<script lang="ts">
  import DashboardShell from '$lib/sb-dashboard/components/DashboardShell.svelte';
  import Panel from '$lib/ui/Panel.svelte';
  import Section from '$lib/ui/Section.svelte';
  export let data: {
    cards: Array<{
      key: string;
      label: string;
      description: string;
      href: string;
      status: 'available' | 'missing';
      detail: string;
    }>;
    recentThreads: Array<{
      canonical_thread_id: string;
      title: string;
      latest_ts: string;
      message_count: number;
    }>;
    messengerSummary: { message_count: number; conversation_count: number; created_at: string } | null;
    openrecallSummary: { captureCount: number; uniqueAppCount: number; latestCapturedAt: string | null } | null;
  };

  function fmtTs(ts: string | null | undefined): string {
    const s = (ts ?? '').trim();
    if (!s) return '—';
    if (s.length >= 16) return `${s.slice(0, 10)} ${s.slice(11, 16)}`;
    return s;
  }
</script>

<DashboardShell title="Corpus Browser">
  <Section
    title="Corpus Browser"
    subtitle="Read-only browsing over the main local corpora: chat archive threads, Messenger ingest DB, and OpenRecall captures."
  >
    <div class="text-sm text-ink-800/75">
      This is the quickest way to inspect what ITIR has actually ingested, plus jump into the processed semantic/report outputs, without jumping between raw SQLite files.
    </div>
  </Section>

  <div class="grid gap-4 lg:grid-cols-3">
    {#each data.cards as card}
      <Panel>
        <div class="flex items-start justify-between gap-3">
          <div>
            <div class="text-xs uppercase tracking-[0.28em] text-ink-800/60">{card.label}</div>
            <div class="mt-2 text-sm text-ink-950">{card.description}</div>
          </div>
          <div class={`rounded-full px-2 py-1 text-[10px] uppercase tracking-widest ${card.status === 'available' ? 'bg-emerald-100 text-emerald-900' : 'bg-amber-100 text-amber-900'}`}>
            {card.status}
          </div>
        </div>
        <div class="mt-3 font-mono text-[11px] text-ink-800/65 break-all">{card.detail}</div>
        <div class="mt-4">
          <a class="text-sm underline decoration-ink-950/20 underline-offset-4 hover:decoration-ink-950/50" href={card.href}>
            Open {card.label}
          </a>
        </div>
      </Panel>
    {/each}
  </div>

  <div class="grid gap-4 lg:grid-cols-[1.3fr,1fr]">
    <Panel>
      <div class="text-xs uppercase tracking-[0.28em] text-ink-800/60">Recent chat threads</div>
      {#if data.recentThreads.length === 0}
        <div class="mt-3 text-sm text-ink-800/70">No chat archive threads were found.</div>
      {:else}
        <div class="mt-3 space-y-2">
          {#each data.recentThreads as thread}
            <a class="block rounded-xl bg-paper-100 px-3 py-3 ring-1 ring-ink-900/10 hover:bg-paper-200/70" href={`/thread/${thread.canonical_thread_id}`}>
              <div class="text-sm text-ink-950">{thread.title}</div>
              <div class="mt-1 flex flex-wrap gap-3 font-mono text-[11px] text-ink-800/65">
                <span>{fmtTs(thread.latest_ts)}</span>
                <span>{thread.message_count.toLocaleString()} msgs</span>
                <span>{thread.canonical_thread_id.slice(0, 12)}…</span>
              </div>
            </a>
          {/each}
        </div>
      {/if}
      <div class="mt-4 text-sm">
        <a class="underline decoration-ink-950/20 underline-offset-4 hover:decoration-ink-950/50" href="/corpora/chat-archive">
          Browse full chat archive thread index
        </a>
      </div>
    </Panel>

    <div class="space-y-4">
      <Panel>
        <div class="text-xs uppercase tracking-[0.28em] text-ink-800/60">Messenger snapshot</div>
        {#if data.messengerSummary}
          <div class="mt-3 space-y-1 text-sm text-ink-950">
            <div>{data.messengerSummary.message_count.toLocaleString()} kept messages</div>
            <div>{data.messengerSummary.conversation_count.toLocaleString()} conversations</div>
            <div class="font-mono text-[11px] text-ink-800/65">{fmtTs(data.messengerSummary.created_at)}</div>
          </div>
        {:else}
          <div class="mt-3 text-sm text-ink-800/70">Messenger test DB not available.</div>
        {/if}
        <div class="mt-4 text-sm">
          <a class="underline decoration-ink-950/20 underline-offset-4 hover:decoration-ink-950/50" href="/corpora/messenger">
            Open Messenger browser
          </a>
        </div>
      </Panel>

      <Panel>
        <div class="text-xs uppercase tracking-[0.28em] text-ink-800/60">OpenRecall snapshot</div>
        {#if data.openrecallSummary}
          <div class="mt-3 space-y-1 text-sm text-ink-950">
            <div>{data.openrecallSummary.captureCount.toLocaleString()} captures</div>
            <div>{data.openrecallSummary.uniqueAppCount.toLocaleString()} apps</div>
            <div class="font-mono text-[11px] text-ink-800/65">{fmtTs(data.openrecallSummary.latestCapturedAt)}</div>
          </div>
        {:else}
          <div class="mt-3 text-sm text-ink-800/70">No OpenRecall captures found in the current ITIR DB.</div>
        {/if}
        <div class="mt-4 text-sm">
          <a class="underline decoration-ink-950/20 underline-offset-4 hover:decoration-ink-950/50" href="/corpora/openrecall">
            Open OpenRecall browser
          </a>
        </div>
      </Panel>
    </div>
  </div>
</DashboardShell>
