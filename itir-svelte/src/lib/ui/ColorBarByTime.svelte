<script lang="ts">
  // 24-hour distribution bar (GitHub-style "heartbeat" cue).
  // Provide either:
  // - `hours`: list of hour indexes (0-23), or
  // - `bins`: explicit 24-length counts.

  export let hours: number[] | null = null;
  export let bins: number[] | null = null;
  export let markHours: number[] | null = null;
  export let heightPx = 10;
  export let gapPx = 1;
  export let className = '';

  function clampHour(h: number): number | null {
    if (!Number.isFinite(h)) return null;
    const n = Math.floor(h);
    if (n < 0 || n > 23) return null;
    return n;
  }

  $: counts = (() => {
    const out = Array.from({ length: 24 }, () => 0);
    if (Array.isArray(bins) && bins.length === 24) {
      for (let i = 0; i < 24; i++) out[i] = Number(bins[i] ?? 0) || 0;
      return out;
    }
    if (Array.isArray(hours)) {
      for (const h of hours) {
        const hh = clampHour(h);
        if (hh === null) continue;
        out[hh] = (out[hh] ?? 0) + 1;
      }
      return out;
    }
    return out;
  })();

  $: maxV = Math.max(1, ...counts);

  function alpha(v: number): number {
    if (v <= 0) return 0.08;
    const r = Math.max(0, Math.min(1, v / maxV));
    return 0.18 + 0.70 * r;
  }

  function tip(h: number): string {
    const v = counts[h] ?? 0;
    return `${String(h).padStart(2, '0')}:00 = ${v}`;
  }
</script>

<div
  class={className}
  style={`display:grid; grid-template-columns: repeat(24, minmax(0, 1fr)); gap:${gapPx}px; height:${heightPx}px; width:100%;`}
>
  {#each Array.from({ length: 24 }, (_, i) => i) as h (h)}
    {@const v = counts[h] ?? 0}
    {@const isMarked = Array.isArray(markHours) && markHours.includes(h)}
    <div
      class={`rounded-[2px] ring-1 ${isMarked ? 'ring-ink-900/60' : 'ring-ink-900/10'}`}
      style={`${v > 0 ? `background: rgba(194, 91, 42, ${alpha(v).toFixed(3)});` : 'background: rgba(16, 26, 51, 0.06);'}`}
      title={tip(h)}
    ></div>
  {/each}
</div>
