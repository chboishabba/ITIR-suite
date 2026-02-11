<script lang="ts">
  export let width = 1200;
  export let height = 800;

  export let minScale = 0.2;
  export let maxScale = 6;

  let root: SVGSVGElement | null = null;
  let dragging = false;
  let lastX = 0;
  let lastY = 0;

  let tx = 0;
  let ty = 0;
  let scale = 1;

  function clamp(v: number, lo: number, hi: number): number {
    return Math.max(lo, Math.min(hi, v));
  }

  function onPointerDown(e: PointerEvent) {
    if (!root) return;
    dragging = true;
    lastX = e.clientX;
    lastY = e.clientY;
    (e.currentTarget as Element).setPointerCapture(e.pointerId);
  }

  function onPointerMove(e: PointerEvent) {
    if (!dragging) return;
    const dx = e.clientX - lastX;
    const dy = e.clientY - lastY;
    lastX = e.clientX;
    lastY = e.clientY;
    tx += dx;
    ty += dy;
  }

  function onPointerUp() {
    dragging = false;
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
</script>

<div class="relative w-full overflow-hidden rounded-xl border border-ink-950/10 bg-white">
  <svg
    bind:this={root}
    {width}
    {height}
    class="block h-auto w-full touch-none select-none"
    role="application"
    aria-label="Interactive graph viewport"
    onpointerdown={onPointerDown}
    onpointermove={onPointerMove}
    onpointerup={onPointerUp}
    onpointercancel={onPointerUp}
    onwheel={onWheel}
  >
    <g transform={`translate(${tx} ${ty}) scale(${scale})`}>
      <slot />
    </g>
  </svg>
</div>
