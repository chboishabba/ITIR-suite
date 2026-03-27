<script lang="ts">
  import DashboardShell from '$lib/sb-dashboard/components/DashboardShell.svelte';
  import Section from '$lib/ui/Section.svelte';
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
  };

  function fmtTs(ts: string): string {
    const s = (ts ?? '').trim();
    if (s.length >= 16) return `${s.slice(0, 10)} ${s.slice(11, 16)}`;
    return s;
  }
</script>

<DashboardShell title="Chat Archive">
  <Section title="Chat archive threads" subtitle="Canonical thread index over the local chat archive. Open a thread to read the full conversation and tool/event rows.">
    <div class="text-sm">
      <a class="underline decoration-ink-950/20 underline-offset-4 hover:decoration-ink-950/50" href="/threads">Open existing thread search page</a>
    </div>
  </Section>

  <div class="rounded-2xl ring-1 ring-ink-900/10 bg-paper-50 shadow-crisp overflow-hidden">
    <div class="overflow-auto overscroll-contain max-h-[75dvh]">
      <table class="min-w-[980px] w-full table-fixed">
        <thead class="sticky top-0 bg-paper-50 ring-1 ring-ink-900/10">
          <tr class="text-left text-[10px] font-mono uppercase tracking-widest text-ink-800/60">
            <th class="px-3 py-2 w-[38%]">Title</th>
            <th class="px-3 py-2 w-[14%]">Latest</th>
            <th class="px-3 py-2 w-[10%] text-right">Msgs</th>
            <th class="px-3 py-2 w-[10%] text-right">Empty</th>
            <th class="px-3 py-2 w-[28%]">Source</th>
          </tr>
        </thead>
        <tbody>
          {#each data.threads as t (t.canonical_thread_id)}
            <tr class="border-t border-ink-900/10 hover:bg-paper-100">
              <td class="px-3 py-2">
                <a class="text-sm text-ink-950 hover:underline" href={`/thread/${t.canonical_thread_id}`}>{t.title}</a>
                <div class="mt-1 font-mono text-[11px] text-ink-800/65">{t.canonical_thread_id}</div>
              </td>
              <td class="px-3 py-2 font-mono text-xs text-ink-800/70">{fmtTs(t.latest_ts)}</td>
              <td class="px-3 py-2 text-right font-mono text-xs text-ink-800/70">{t.message_count.toLocaleString()}</td>
              <td class="px-3 py-2 text-right font-mono text-xs text-ink-800/70">{t.empty_text_count.toLocaleString()}</td>
              <td class="px-3 py-2">
                <div class="font-mono text-[11px] text-ink-800/70 break-all">{t.source_id ?? '(none)'}</div>
                <div class="mt-1 font-mono text-[11px] text-ink-800/60 break-all">{t.any_source_thread_id ?? '(no source thread id)'}</div>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  </div>
</DashboardShell>
