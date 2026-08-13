<script lang="ts">
  import DashboardShell from '$lib/sb-dashboard/components/DashboardShell.svelte';
  import Panel from '$lib/ui/Panel.svelte';
  import Section from '$lib/ui/Section.svelte';
  import { page } from '$app/stores';

  export let data: {
    runId: string | null;
    conversationHash: string | null;
    q: string;
    runs: Array<any>;
    summary: any;
    activeRunId: string | null;
    messages: Array<any>;
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
    u.searchParams.set('runId', runId);
    u.searchParams.delete('conversation');
    return u.pathname + '?' + u.searchParams.toString();
  }

  function hrefForConversation(hash: string): string {
    const u = new URL($page.url);
    if (hash) u.searchParams.set('conversation', hash);
    else u.searchParams.delete('conversation');
    return u.pathname + '?' + u.searchParams.toString();
  }
</script>

<DashboardShell title="Messenger Browser">
  <Section title="Messenger test DB" subtitle="Browse the filtered Messenger ingest DB. This is a read-only view over the bounded message store, not the raw export JSON.">
    <div slot="actions" class="flex items-center gap-2">
      <input class="rounded-lg bg-paper-100 ring-1 ring-ink-900/10 px-3 py-2 text-sm" placeholder="Filter sender/text..." bind:value={q} on:keydown={(e) => e.key === 'Enter' && submitSearch()} />
      <button class="rounded-lg bg-ink-900 text-paper-50 px-3 py-2 text-xs uppercase tracking-widest" on:click={submitSearch}>Search</button>
    </div>
    <div class="text-xs text-ink-800/60">Active run: <span class="font-mono">{data.activeRunId ?? '(none)'}</span></div>
  </Section>

  <div class="grid gap-4 lg:grid-cols-[1fr,1.4fr]">
    <div class="space-y-4">
      <Panel>
        <div class="text-xs uppercase tracking-[0.28em] text-ink-800/60">Runs</div>
        <div class="mt-3 space-y-2">
          {#each data.runs as run}
            <a class={`block rounded-xl px-3 py-3 ring-1 ${run.run_id === (data.activeRunId ?? data.runId) ? 'bg-amber-50 ring-amber-300' : 'bg-paper-100 ring-ink-900/10 hover:bg-paper-200/70'}`} href={hrefForRun(run.run_id)}>
              <div class="font-mono text-[11px] text-ink-800/70 break-all">{run.run_id}</div>
              <div class="mt-1 text-sm text-ink-950">{run.message_count.toLocaleString()} msgs · {run.conversation_count.toLocaleString()} conversations</div>
              <div class="mt-1 text-[11px] text-ink-800/65">{run.created_at}</div>
            </a>
          {/each}
        </div>
      </Panel>

      {#if data.summary}
        <Panel>
          <div class="text-xs uppercase tracking-[0.28em] text-ink-800/60">Run summary</div>
          <div class="mt-3 space-y-1 text-sm text-ink-950">
            <div>{data.summary.message_count.toLocaleString()} kept messages</div>
            <div>{data.summary.conversation_count.toLocaleString()} conversations</div>
            <div>{data.summary.first_ts ?? '—'} to {data.summary.last_ts ?? '—'}</div>
          </div>
          <div class="mt-3 text-xs text-ink-800/65">
            retention=<span class="font-mono">{data.summary.retention_policy}</span> · redaction=<span class="font-mono">{data.summary.redaction_policy}</span>
          </div>
          {#if data.summary.top_conversations?.length}
            <div class="mt-4 text-xs uppercase tracking-[0.24em] text-ink-800/60">Top conversations</div>
            <div class="mt-2 space-y-2">
              {#each data.summary.top_conversations as convo}
                <a class={`block rounded-lg px-3 py-2 ring-1 ${convo.conversation_hash === data.conversationHash ? 'bg-sky-50 ring-sky-300' : 'bg-paper-100 ring-ink-900/10'}`} href={hrefForConversation(convo.conversation_hash)}>
                  <div class="font-mono text-[11px] text-ink-800/70">{convo.conversation_hash}</div>
                  <div class="mt-1 text-sm text-ink-950">{convo.message_count.toLocaleString()} msgs · {convo.conversation_type}</div>
                </a>
              {/each}
            </div>
          {/if}
        </Panel>
      {/if}
    </div>

    <Panel>
      <div class="flex items-center justify-between gap-3">
        <div class="text-xs uppercase tracking-[0.28em] text-ink-800/60">Messages</div>
        <div class="text-[11px] text-ink-800/65">
          {#if data.conversationHash}
            conversation=<span class="font-mono">{data.conversationHash}</span>
          {:else}
            latest across run
          {/if}
        </div>
      </div>
      {#if data.messages.length === 0}
        <div class="mt-3 text-sm text-ink-800/70">No Messenger rows matched the current selection.</div>
      {:else}
        <div class="mt-3 space-y-3 max-h-[72dvh] overflow-auto pr-1">
          {#each data.messages as msg}
            <div class="rounded-xl bg-paper-100 px-4 py-3 ring-1 ring-ink-900/10">
              <div class="flex flex-wrap gap-3 text-[11px] font-mono text-ink-800/65">
                <span>{msg.ts}</span>
                <span>{msg.sender}</span>
                <span>{msg.conversation_hash}</span>
              </div>
              <div class="mt-2 whitespace-pre-wrap text-sm text-ink-950">{msg.text}</div>
            </div>
          {/each}
        </div>
      {/if}
    </Panel>
  </div>
</DashboardShell>
