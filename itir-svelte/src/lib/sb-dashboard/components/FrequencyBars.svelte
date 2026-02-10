<script lang="ts">
  import Section from '$lib/ui/Section.svelte';

  export let frequencyByHour: Record<string, number[]> | undefined;

  function isHourBins(v: unknown): v is number[] {
    return Array.isArray(v) && v.length === 24 && v.every((x) => typeof x === 'number' && Number.isFinite(x));
  }

  function lanes(): string[] {
    const keys = Object.keys(frequencyByHour ?? {})
      .filter((k) => isHourBins((frequencyByHour as any)?.[k]))
      .sort();
    return keys.length ? ['all', ...keys] : [];
  }

  let lane = '';

  $: available = lanes();
  $: lane = lane || available[0] || '';

  function max(xs: number[]): number {
    let m = 0;
    for (const x of xs) if (x > m) m = x;
    return m;
  }

  function sumAll(): number[] {
    const out = Array.from({ length: 24 }, () => 0);
    for (const [k, bins] of Object.entries(frequencyByHour ?? {})) {
      if (!isHourBins(bins)) continue;
      // Ignore "all" if it ever appears as a real key.
      if (k === 'all') continue;
      for (let i = 0; i < 24; i++) out[i] = (out[i] ?? 0) + (bins[i] ?? 0);
    }
    return out;
  }
</script>

<Section title="Frequency By Hour" subtitle="Select a lane, or view `all` (sum across lanes).">
  <div slot="actions" class="flex items-center gap-2">
    <label class="text-xs uppercase tracking-widest text-ink-800/60" for="lane">Lane</label>
    <select
      id="lane"
      class="rounded-lg bg-paper-100 ring-1 ring-ink-900/10 px-2 py-1 text-sm"
      bind:value={lane}
      disabled={!available.length}
    >
      {#each available as k}
        <option value={k}>{k === 'all' ? 'all (sum)' : k}</option>
      {/each}
    </select>
  </div>

  {#if lane && (lane === 'all' || frequencyByHour?.[lane])}
    {@const values = lane === 'all' ? sumAll() : (frequencyByHour?.[lane] ?? [])}
    {@const m = max(values)}

    <div class="grid gap-1" style="grid-template-columns: repeat(24, minmax(0, 1fr));">
      {#each values as v, h (h)}
        <div class="flex flex-col items-center gap-1">
          <div
            class="w-full rounded bg-ink-900/10"
            style={`height: 60px; position: relative; overflow: hidden;`}
            title={`${h}:00 = ${v}`}
          >
            <div
              class="absolute bottom-0 left-0 right-0 rounded bg-accent-600/70"
              style={`height: ${m ? Math.max(2, Math.round((v / m) * 60)) : 2}px`}
            ></div>
          </div>
          <div class="font-mono text-[10px] text-ink-800/60">{h}</div>
        </div>
      {/each}
    </div>
  {:else}
    <div class="text-sm text-ink-800/70">No frequency data.</div>
  {/if}
</Section>
