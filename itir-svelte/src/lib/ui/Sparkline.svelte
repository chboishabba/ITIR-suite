<script lang="ts">
  // Simple sparkline/heartbeat inspired by GitHub contributions.
  // Renders an area + stroke in an SVG that stretches to its container.

  export let series: number[] = [];
  export let padY = 0.08; // 0..0.3 relative vertical padding
  export let strokeClass = 'stroke-emerald-600';
  export let fillClass = 'fill-emerald-600/15';
  export let backgroundClass = 'fill-transparent';
  export let ariaLabel: string | null = null;

  const W = 100;
  const H = 28;

  function finite(n: unknown): number | null {
    if (typeof n === 'number' && Number.isFinite(n)) return n;
    return null;
  }

  $: values = (series ?? []).map((v) => finite(v) ?? 0);
  $: minV = values.length ? Math.min(...values) : 0;
  $: maxV = values.length ? Math.max(...values) : 0;
  $: span = Math.max(1e-9, maxV - minV);
  $: innerPad = Math.max(0, Math.min(0.3, padY));

  function yFor(v: number): number {
    // map to [pad, H-pad], inverted (top is 0)
    const t = (v - minV) / span;
    const y0 = H * innerPad;
    const y1 = H * (1 - innerPad);
    return y1 - t * (y1 - y0);
  }

  $: points = (() => {
    const n = values.length;
    if (n <= 0) return [];
    if (n === 1) return [{ x: 0, y: yFor(values[0] ?? 0) }];
    return values.map((v, i) => ({ x: (i / (n - 1)) * W, y: yFor(v) }));
  })();

  function pathLine(): string {
    if (!points.length) return '';
    const [p0, ...rest] = points;
    let d = `M ${p0!.x.toFixed(2)} ${p0!.y.toFixed(2)}`;
    for (const p of rest) d += ` L ${p.x.toFixed(2)} ${p.y.toFixed(2)}`;
    return d;
  }

  function pathArea(): string {
    if (!points.length) return '';
    const line = pathLine();
    const last = points[points.length - 1]!;
    return `${line} L ${last.x.toFixed(2)} ${H.toFixed(2)} L 0 ${H.toFixed(2)} Z`;
  }

  $: lineD = pathLine();
  $: areaD = pathArea();
</script>

<svg
  class="block h-full w-full"
  viewBox={`0 0 ${W} ${H}`}
  preserveAspectRatio="none"
  role={ariaLabel ? 'img' : 'presentation'}
  aria-label={ariaLabel ?? undefined}
>
  <rect x="0" y="0" width={W} height={H} class={backgroundClass} />
  {#if points.length >= 2}
    <path d={areaD} class={fillClass} />
    <path d={lineD} class={`fill-none ${strokeClass}`} stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
  {:else if points.length === 1}
    <circle cx={points[0]!.x} cy={points[0]!.y} r="2.5" class={strokeClass} />
  {/if}
</svg>

