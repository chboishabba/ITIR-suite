<script lang="ts">
  import Section from '$lib/ui/Section.svelte';

  type Heatmaps = {
    weekday_names: string[];
    weekday_day_counts: number[]; // len 7
    lanes: string[];
    lane_labels: Record<string, string>;
    lane_totals: Record<string, number>;
    default_selected: string[];
    series: Record<string, number[][]>; // lane -> 7x24 totals
  };

  export let heatmaps: Heatmaps | null;

  let normalize = true;
  let selected = new Set<string>();

  $: if (heatmaps) {
    // Initialize selection once per new heatmaps object.
    // Keep user selection stable if possible, but fall back to defaults when empty.
    if (selected.size === 0) {
      const defaults = heatmaps.default_selected?.length ? heatmaps.default_selected : heatmaps.lanes;
      selected = new Set(defaults.filter((l) => (heatmaps.lane_totals?.[l] ?? 0) > 0));
    }
  }

  const INTENT_SET = ['git', 'shell', 'chat', 'pr', 'git_branch', 'input', 'calendar', 'activity'];

  function laneAvailable(lane: string): boolean {
    return (heatmaps?.lane_totals?.[lane] ?? 0) > 0;
  }

  function toggle(lane: string) {
    const next = new Set(selected);
    if (next.has(lane)) next.delete(lane);
    else next.add(lane);
    selected = next;
  }

  function selectAll() {
    if (!heatmaps) return;
    selected = new Set(heatmaps.lanes.filter(laneAvailable));
  }
  function selectNone() {
    selected = new Set();
  }
  function selectIntent() {
    if (!heatmaps) return;
    selected = new Set(INTENT_SET.filter((l) => heatmaps.lanes.includes(l) && laneAvailable(l)));
  }

  function denomForDow(dow: number): number {
    const v = heatmaps?.weekday_day_counts?.[dow] ?? 0;
    return Math.max(1, v);
  }

  function cellAvgPerDay(lane: string, dow: number, hour: number): number {
    const m = heatmaps?.series?.[lane];
    const total = m?.[dow]?.[hour] ?? 0;
    return total / denomForDow(dow);
  }

  function laneMax(lane: string): number {
    let mx = 0;
    for (let dow = 0; dow < 7; dow++) {
      for (let h = 0; h < 24; h++) {
        mx = Math.max(mx, cellAvgPerDay(lane, dow, h));
      }
    }
    return mx;
  }

  $: selectedLanes = heatmaps ? heatmaps.lanes.filter((l) => selected.has(l) && laneAvailable(l)) : [];
  $: laneMaxes = new Map<string, number>(selectedLanes.map((l) => [l, laneMax(l)]));

  function combinedScore(dow: number, hour: number): number {
    if (!selectedLanes.length) return 0;
    if (!normalize) {
      let sum = 0;
      for (const lane of selectedLanes) sum += cellAvgPerDay(lane, dow, hour);
      return sum;
    }
    let sum = 0;
    for (const lane of selectedLanes) {
      const mx = laneMaxes.get(lane) ?? 0;
      const v = cellAvgPerDay(lane, dow, hour);
      sum += mx > 0 ? v / mx : 0;
    }
    return sum / selectedLanes.length;
  }

  $: maxScore = (() => {
    let mx = 0;
    for (let dow = 0; dow < 7; dow++) for (let h = 0; h < 24; h++) mx = Math.max(mx, combinedScore(dow, h));
    return mx;
  })();

  function level(v: number): number {
    if (v <= 0 || maxScore <= 0) return 0;
    const r = Math.max(0, Math.min(1, v / maxScore));
    if (r <= 0.2) return 1;
    if (r <= 0.4) return 2;
    if (r <= 0.65) return 3;
    return 4;
  }

  function tooltip(dow: number, hour: number): string {
    if (!heatmaps) return '';
    const day = heatmaps.weekday_names?.[dow] ?? String(dow);
    const days = heatmaps.weekday_day_counts?.[dow] ?? 0;
    const parts: string[] = [];
    for (const lane of selectedLanes) {
      const label = heatmaps.lane_labels?.[lane] ?? lane;
      const avg = cellAvgPerDay(lane, dow, hour);
      parts.push(`${label} avg/day=${avg.toFixed(2)}`);
    }
    const score = combinedScore(dow, hour);
    return `${day} ${String(hour).padStart(2, '0')}:00 (days=${days}) | score=${normalize ? score.toFixed(2) : score.toFixed(2)}${parts.length ? ' | ' + parts.join(' | ') : ''}`;
  }
</script>

<Section title="When You Work (Weekday x Hour)" subtitle="Design cue: GitHub contribution calendar. Toggle signals; normalization avoids one lane swamping others.">
  <div slot="actions" class="flex flex-wrap items-center gap-2">
    <label class="flex items-center gap-2 text-xs uppercase tracking-widest text-ink-800/60">
      <input type="checkbox" bind:checked={normalize} />
      Normalize
    </label>
    <button class="rounded-lg bg-paper-100 ring-1 ring-ink-900/10 px-3 py-2 text-xs uppercase tracking-widest" type="button" on:click={selectAll}>
      All
    </button>
    <button class="rounded-lg bg-paper-100 ring-1 ring-ink-900/10 px-3 py-2 text-xs uppercase tracking-widest" type="button" on:click={selectNone}>
      None
    </button>
    <button class="rounded-lg bg-paper-100 ring-1 ring-ink-900/10 px-3 py-2 text-xs uppercase tracking-widest" type="button" on:click={selectIntent}>
      Intent set
    </button>
  </div>

  {#if !heatmaps}
    <div class="text-sm text-ink-800/70">No heatmap data.</div>
  {:else}
    <div class="grid gap-4 lg:grid-cols-[18rem,1fr]">
      <div class="rounded-xl bg-paper-100 ring-1 ring-ink-900/10 px-4 py-3">
        <div class="text-xs uppercase tracking-widest text-ink-800/60">Signals</div>
        <div class="mt-2 grid gap-2">
          {#each heatmaps.lanes as lane (lane)}
            <label class="flex items-center justify-between gap-3 text-sm">
              <span class="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={selected.has(lane)}
                  disabled={!laneAvailable(lane)}
                  on:change={() => toggle(lane)}
                />
                <span class={!laneAvailable(lane) ? 'text-ink-800/40' : 'text-ink-950'}>
                  {heatmaps.lane_labels?.[lane] ?? lane}
                </span>
              </span>
              <span class="font-mono text-xs text-ink-800/60">{(heatmaps.lane_totals?.[lane] ?? 0).toLocaleString()}</span>
            </label>
          {/each}
        </div>
      </div>

      <div class="overflow-auto rounded-xl ring-1 ring-ink-900/10 bg-paper-50 p-3">
        <div class="grid gap-[3px]" style="grid-template-columns: 40px repeat(24, minmax(12px, 1fr));">
          <div></div>
          {#each Array.from({ length: 24 }, (_, i) => i) as h (h)}
            <div class="text-[10px] font-mono text-ink-800/50 text-center">{h % 3 === 0 ? String(h).padStart(2, '0') : ''}</div>
          {/each}

          {#each Array.from({ length: 7 }, (_, i) => i) as dow (dow)}
            <div class="text-[11px] font-mono text-ink-800/60 pr-1 text-right">{heatmaps.weekday_names?.[dow] ?? dow}</div>
            {#each Array.from({ length: 24 }, (_, i) => i) as h2 (dow + ':' + h2)}
              {@const s = combinedScore(dow, h2)}
              {@const l = level(s)}
              <div
                class={`w-full rounded-[3px] ring-1 ring-ink-900/10 ${l === 0 ? 'bg-paper-100' : l === 1 ? 'bg-accent-600/20' : l === 2 ? 'bg-accent-600/35' : l === 3 ? 'bg-accent-600/55' : 'bg-accent-600/80'}`}
                title={tooltip(dow, h2)}
                style="aspect-ratio: 1 / 1"
              ></div>
            {/each}
          {/each}
        </div>
      </div>
    </div>
  {/if}
</Section>
