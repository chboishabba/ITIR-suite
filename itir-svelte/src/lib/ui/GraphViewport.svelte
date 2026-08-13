<script lang="ts">
  export let width = 1200;
  export let height = 800;
  export let fitToWidth = true;
  export let scrollWhenOverflow = false;
  export let resetKey: string | number = '';

  export let minScale = 0.2;
  export let maxScale = 6;

  let root: SVGSVGElement | null = null;
  let dragging = false;
  let panning = false;
  let lastX = 0;
  let lastY = 0;
  let downX = 0;
  let downY = 0;

  let tx = 0;
  let ty = 0;
  let scale = 1;
  let lastResetKey: string | number = '';

  function clamp(v: number, lo: number, hi: number): number {
    return Math.max(lo, Math.min(hi, v));
  }

  function onPointerDown(e: PointerEvent) {
    if (!root) return;
    dragging = true;
    panning = false;
    lastX = e.clientX;
    lastY = e.clientY;
    downX = e.clientX;
    downY = e.clientY;
  }

  function onPointerMove(e: PointerEvent) {
    if (!dragging) return;
    const dx0 = e.clientX - downX;
    const dy0 = e.clientY - downY;
    if (!panning) {
      // Only capture and pan after a small threshold, so simple clicks on nodes
      // don't get retargeted and break click handlers.
      if (Math.hypot(dx0, dy0) < 2.5) return;
      panning = true;
      // Some synthetic events (tests) and some embedded browser contexts can throw here.
      try {
        (e.currentTarget as Element).setPointerCapture(e.pointerId);
      } catch {
        // no-op
      }
    }
    const dx = e.clientX - lastX;
    const dy = e.clientY - lastY;
    lastX = e.clientX;
    lastY = e.clientY;
    tx += dx;
    ty += dy;
  }

  function onPointerUp() {
    dragging = false;
    panning = false;
  }

  function onWheel(e: WheelEvent) {
    if (!root) return;
    e.preventDefault();

    const rect = root.getBoundingClientRect();
    const cx = e.clientX - rect.left;
    const cy = e.clientY - rect.top;

    const delta = -e.deltaY;
    const factor = delta > 0 ? 1.12 : 1 / 1.12;
    const next = clamp(scale * factor, minScale, maxScale);

    // Zoom towards cursor.
    const k = next / scale;
    tx = cx - k * (cx - tx);
    ty = cy - k * (cy - ty);
    scale = next;
  }

  export function reset() {
    tx = 0;
    ty = 0;
    scale = 1;
  }

  $: if (resetKey !== lastResetKey) {
    reset();
    lastResetKey = resetKey;
  }
</script>

<div class="relative w-full rounded-xl border border-ink-950/10 bg-white {scrollWhenOverflow ? 'overflow-auto' : 'overflow-hidden'}">
  <svg
    bind:this={root}
    {width}
    {height}
    class="block touch-none select-none"
    style={
      fitToWidth
        ? `width:100%; height:${height}px; max-width:100%;`
        : `width:${width}px; height:${height}px; max-width:none;`
    }
    role="application"
    aria-label="Interactive graph viewport"
    on:pointerdown|capture={onPointerDown}
    on:pointermove|capture={onPointerMove}
    on:pointerup|capture={onPointerUp}
    on:pointercancel|capture={onPointerUp}
    on:wheel={onWheel}
  >
    <g transform={`translate(${tx} ${ty}) scale(${scale})`}>
      <slot />
    </g>
  </svg>
</div>
