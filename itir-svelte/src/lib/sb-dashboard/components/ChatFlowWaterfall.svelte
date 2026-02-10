<script lang="ts">
  import Section from '$lib/ui/Section.svelte';
  import type { WaterfallSegment } from '../adapters/dashboard';
  import { createWaterfallPrefs, hydrateWaterfallPrefs, colorFor, type WaterfallAlgoName, type WaterfallPaletteName } from '../hooks/waterfallColors';
  import { onMount } from 'svelte';

  // Initial, intentionally simple visualization:
  // consecutive segments grouped by hour+thread rendered as a striped bar,
  // with palette/algo settings persisted to the same localStorage keys as the legacy HTML.
  export let segments: WaterfallSegment[];

  const prefs = createWaterfallPrefs();

  const paletteOptions: WaterfallPaletteName[] = ['viridis', 'magma', 'plasma', 'inferno', 'custom'];
  const algoOptions: WaterfallAlgoName[] = ['thread', 'hour', 'role', 'switch'];

  type WidthMode = 'time' | 'messages';
  let widthMode: WidthMode = 'time';
  let hover: { hour: number; title: string; threadId: string; messageCount: number; durationSeconds: number } | null = null;

  let byHour: WaterfallSegment[][] = Array.from({ length: 24 }, () => []);
  let totals: number[] = Array.from({ length: 24 }, () => 0); // messages
  let maxTotal = 0;

  $: {
    byHour = Array.from({ length: 24 }, () => []);
    totals = Array.from({ length: 24 }, () => 0);
    for (const s of segments ?? []) {
      if (typeof s.hour !== 'number' || s.hour < 0 || s.hour > 23) continue;
      byHour[s.hour]!.push(s);
      totals[s.hour] = (totals[s.hour] ?? 0) + (s.messageCount ?? 0);
    }
    maxTotal = Math.max(0, ...totals);
  }

  function weight(s: WaterfallSegment): number {
    if (widthMode === 'messages') return Math.max(1, s.messageCount ?? 0);
    return Math.max(1, Math.round(s.durationSeconds ?? 0));
  }

  function fmtDur(s: number): string {
    const v = Math.max(0, Math.round(s));
    if (v >= 3600) return `${(v / 3600).toFixed(1)}h`;
    if (v >= 60) return `${Math.round(v / 60)}m`;
    return `${v}s`;
  }

  let custom = '';
  onMount(() => {
    // Avoid SSR/CSR hydration mismatch: apply stored prefs after mount.
    hydrateWaterfallPrefs(prefs, $prefs);
    custom = $prefs.custom;
  });

  function setPalette(palette: WaterfallPaletteName) {
    prefs.update((v) => ({ ...v, palette }));
  }
  function setAlgo(algo: WaterfallAlgoName) {
    prefs.update((v) => ({ ...v, algo }));
  }
  function applyCustom() {
    prefs.update((v) => ({ ...v, palette: 'custom', custom }));
  }
  function resetCustom() {
    custom = '';
    prefs.update((v) => ({ ...v, palette: 'viridis', custom: '' }));
  }
</script>

<Section title="Chat Flow Waterfall" subtitle="Grouped by hour+thread. Hour strip always fills width; per-hour volume shown separately.">
  <div slot="actions" class="flex flex-wrap items-center gap-2">
    <label class="text-xs uppercase tracking-widest text-ink-800/60" for="wf-palette">Palette</label>
    <select
      id="wf-palette"
      class="rounded-lg bg-paper-100 ring-1 ring-ink-900/10 px-2 py-1 text-sm"
      on:change={(e) => setPalette((e.currentTarget as HTMLSelectElement).value as WaterfallPaletteName)}
      value={$prefs.palette}
    >
      {#each paletteOptions as p}
        <option value={p}>{p}</option>
      {/each}
    </select>

    <label class="text-xs uppercase tracking-widest text-ink-800/60" for="wf-algo">Algo</label>
    <select
      id="wf-algo"
      class="rounded-lg bg-paper-100 ring-1 ring-ink-900/10 px-2 py-1 text-sm"
      on:change={(e) => setAlgo((e.currentTarget as HTMLSelectElement).value as WaterfallAlgoName)}
      value={$prefs.algo}
    >
      {#each algoOptions as a}
        <option value={a}>{a}</option>
      {/each}
    </select>

    <input
      class="min-w-[14rem] rounded-lg bg-paper-100 ring-1 ring-ink-900/10 px-3 py-1 text-sm font-mono"
      placeholder="custom colors: #111,#222,..."
      bind:value={custom}
    />
    <button class="rounded-lg bg-ink-900 text-paper-50 px-3 py-1 text-xs uppercase tracking-widest" type="button" on:click={applyCustom}>
      Apply
    </button>
    <button class="rounded-lg bg-paper-100 ring-1 ring-ink-900/10 px-3 py-1 text-xs uppercase tracking-widest" type="button" on:click={resetCustom}>
      Reset
    </button>
  </div>

  {#if hover}
    <div class="mb-3 rounded-xl bg-paper-100 ring-1 ring-ink-900/10 px-4 py-3">
      <div class="text-xs uppercase tracking-widest text-ink-800/60">Hover</div>
      <div class="mt-1 text-sm text-ink-950 whitespace-pre-wrap">{hover.title}{'\n'}{hover.threadId}</div>
      <div class="mt-2 font-mono text-xs text-ink-800/70">
        hour={hover.hour} msgs={hover.messageCount.toLocaleString()} span={fmtDur(hover.durationSeconds)}
      </div>
    </div>
  {/if}

  <div class="space-y-2">
    {#each Array.from({ length: 24 }, (_, i) => i) as h}
      {@const hourSegs = byHour[h] ?? []}
      {@const total = totals[h] ?? 0}
      <div class="flex items-center gap-3">
        <div class="w-10 text-right font-mono text-xs text-ink-800/60">{h}</div>
        <div class="w-24 shrink-0">
          <div
            class="h-2 w-full rounded bg-ink-900/10 overflow-hidden"
            title={`hour=${h} total=${total}`}
          >
            <div
              class="h-2 rounded bg-ink-900/40"
              style={`width:${maxTotal ? Math.round((total / maxTotal) * 100) : 0}%`}
            ></div>
          </div>
        </div>
        <div class="flex-1 overflow-hidden rounded-lg bg-paper-100 ring-1 ring-ink-900/10">
          <div class="flex h-6 w-full">
            {#each hourSegs as s, idx (h + ':' + idx)}
              <button
                type="button"
                class="h-full p-0 m-0 border-0"
                style={`background:${colorFor({ hour: s.hour, role: s.role, switch: s.switch, threadIndex: s.threadIndex, threadStartHour: s.threadStartHour, defaultColor: s.colorHex }, $prefs)}; flex:${weight(s)} 0 0`}
                title={`${s.threadTitle ?? '(no title)'}\n${s.threadId}\nmsgs=${s.messageCount} span_s=${Math.round(s.durationSeconds)} (hour=${h})`}
                aria-label={`${(s.threadTitle ?? '(no title)').trim() || '(no title)'} ${s.threadId} msgs ${s.messageCount} span_s ${Math.round(s.durationSeconds)}`}
                on:mouseenter={() =>
                  (hover = {
                    hour: h,
                    title: (s.threadTitle ?? '(no title)').trim() || '(no title)',
                    threadId: s.threadId,
                    messageCount: s.messageCount,
                    durationSeconds: s.durationSeconds
                  })}
                on:mouseleave={() => (hover = null)}
                on:focus={() =>
                  (hover = {
                    hour: h,
                    title: (s.threadTitle ?? '(no title)').trim() || '(no title)',
                    threadId: s.threadId,
                    messageCount: s.messageCount,
                    durationSeconds: s.durationSeconds
                  })}
                on:blur={() => (hover = null)}
              ></button>
            {/each}
          </div>
        </div>
      </div>
    {/each}
  </div>

  <div class="mt-3 flex flex-wrap items-center gap-2 text-xs text-ink-800/60">
    <span class="font-mono">width:</span>
    <button
      class={`rounded-lg px-3 py-1 uppercase tracking-widest ring-1 ${widthMode === 'time' ? 'bg-ink-900 text-paper-50 ring-ink-900/10' : 'bg-paper-100 text-ink-900 ring-ink-900/10'}`}
      type="button"
      on:click={() => (widthMode = 'time')}
    >
      time
    </button>
    <button
      class={`rounded-lg px-3 py-1 uppercase tracking-widest ring-1 ${widthMode === 'messages' ? 'bg-ink-900 text-paper-50 ring-ink-900/10' : 'bg-paper-100 text-ink-900 ring-ink-900/10'}`}
      type="button"
      on:click={() => (widthMode = 'messages')}
    >
      messages
    </button>
    <span>Order is chronological within each hour; time mode uses gap-to-next-message (or hour boundary) as span weight.</span>
  </div>
</Section>
