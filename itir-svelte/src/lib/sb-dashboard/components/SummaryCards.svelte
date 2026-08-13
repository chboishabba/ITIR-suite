<script lang="ts">
  import StatCard from '$lib/ui/StatCard.svelte';
  import Sparkline from '$lib/ui/Sparkline.svelte';

  export let summary: Record<string, unknown> | undefined;
  export let frequencyByHour: Record<string, number[]> | undefined;

  function num(v: unknown): number | null {
    if (typeof v === 'number' && Number.isFinite(v)) return v;
    return null;
  }

  function fmtInt(v: unknown): string {
    const n = num(v);
    if (n === null) return 'n/a';
    return Math.round(n).toLocaleString();
  }

  function fmtPct(v: unknown): string {
    const n = num(v);
    if (n === null) return 'n/a';
    return `${(n * 100).toFixed(1)}%`;
  }

  function lane(laneKey: string): number[] | null {
    const xs = (frequencyByHour as any)?.[laneKey];
    if (!Array.isArray(xs) || xs.length !== 24) return null;
    return xs.map((v) => (typeof v === 'number' && Number.isFinite(v) ? v : 0));
  }

  const cards = [
    { label: 'Chat messages', key: 'chat_messages', fmt: fmtInt },
    { label: 'Chat threads', key: 'chat_threads', fmt: fmtInt },
    { label: 'Switch rate', key: 'chat_switch_rate', fmt: fmtPct },
    { label: 'Shell commands', key: 'shell_commands', fmt: fmtInt },
    { label: 'Git commits', key: 'git_commits', fmt: fmtInt },
    { label: 'Media events', key: 'media_events', fmt: fmtInt }
  ] as const;

  const sparklines: Record<string, { lane: string; stroke: string; fill: string; aria: string }> = {
    chat_messages: { lane: 'chat', stroke: 'stroke-emerald-600', fill: 'fill-emerald-600/15', aria: 'Chat messages by hour' },
    shell_commands: { lane: 'shell', stroke: 'stroke-sky-600', fill: 'fill-sky-600/15', aria: 'Shell commands by hour' },
    git_commits: { lane: 'git', stroke: 'stroke-violet-600', fill: 'fill-violet-600/15', aria: 'Git commits by hour' },
    media_events: { lane: 'media', stroke: 'stroke-rose-600', fill: 'fill-rose-600/15', aria: 'Media events by hour' }
  };
</script>

<div class="grid grid-cols-2 gap-3 md:grid-cols-3 lg:grid-cols-6">
  {#each cards as c (c.key)}
    <StatCard label={c.label} value={c.fmt(summary?.[c.key])}>
      <svelte:fragment slot="spark">
        {#if sparklines[c.key] && lane(sparklines[c.key]!.lane)}
          <div class="h-8 w-24">
            <Sparkline
              series={lane(sparklines[c.key]!.lane) ?? []}
              strokeClass={sparklines[c.key]!.stroke}
              fillClass={sparklines[c.key]!.fill}
              ariaLabel={sparklines[c.key]!.aria}
            />
          </div>
        {/if}
      </svelte:fragment>
    </StatCard>
  {/each}
</div>
