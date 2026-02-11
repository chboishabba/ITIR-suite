<script lang="ts" context="module">
  export type GraphNode = {
    id: string;
    label: string;
    weight?: number;
    color?: string;
    tooltip?: string;
  };

  export type GraphEdge = {
    from: string;
    to: string;
    weight?: number;
  };
</script>

<script lang="ts">
  import GraphViewport from '$lib/ui/GraphViewport.svelte';

  export let left: GraphNode[] = [];
  export let right: GraphNode[] = [];
  export let edges: GraphEdge[] = [];

  export let width = 1200;
  export let height = 800;

  export let leftX = 120;
  export let rightX = 1080;

  export let nodeW = 220;
  export let nodeH = 18;
  export let padY = 8;
  export let fontSize = 10;

  function clamp(v: number, lo: number, hi: number): number {
    return Math.max(lo, Math.min(hi, v));
  }

  type Pt = { x: number; y: number };
  function layout(nodes: GraphNode[], x: number, topY: number): Map<string, Pt> {
    const m = new Map<string, Pt>();
    const usableH = height - topY * 2;
    const step = Math.max(nodeH + padY, usableH / Math.max(1, nodes.length));
    nodes.forEach((n, i) => {
      m.set(n.id, { x, y: topY + i * step });
    });
    return m;
  }

  $: leftPos = layout(left, leftX, 60);
  $: rightPos = layout(right, rightX - nodeW, 60);

  function edgePath(a: Pt, b: Pt): string {
    const x1 = a.x + nodeW;
    const y1 = a.y + nodeH / 2;
    const x2 = b.x;
    const y2 = b.y + nodeH / 2;
    const dx = Math.max(40, (x2 - x1) * 0.5);
    return `M ${x1} ${y1} C ${x1 + dx} ${y1}, ${x2 - dx} ${y2}, ${x2} ${y2}`;
  }
</script>

<GraphViewport {width} {height}>
  <g>
    {#each edges as e (e.from + '->' + e.to)}
      {@const a = leftPos.get(e.from)}
      {@const b = rightPos.get(e.to)}
      {#if a && b}
        {@const w = clamp(Number(e.weight ?? 1), 1, 12)}
        <path
          d={edgePath(a, b)}
          fill="none"
          stroke="rgba(10,10,10,0.18)"
          stroke-width={0.6 + 0.2 * w}
        />
      {/if}
    {/each}
  </g>

  <g>
    {#each left as n (n.id)}
      {@const p = leftPos.get(n.id)}
      {#if p}
        <rect x={p.x} y={p.y} width={nodeW} height={nodeH} rx="4" fill={n.color ?? '#e8f4ff'} stroke="rgba(0,0,0,0.12)" />
        <title>{n.tooltip ?? n.label}</title>
        <text x={p.x + 8} y={p.y + 12} font-size={fontSize} fill="rgba(0,0,0,0.88)">{n.label}</text>
      {/if}
    {/each}
  </g>

  <g>
    {#each right as n (n.id)}
      {@const p = rightPos.get(n.id)}
      {#if p}
        <rect x={p.x} y={p.y} width={nodeW} height={nodeH} rx="4" fill={n.color ?? '#f6f6f6'} stroke="rgba(0,0,0,0.12)" />
        <title>{n.tooltip ?? n.label}</title>
        <text x={p.x + 8} y={p.y + 12} font-size={fontSize} fill="rgba(0,0,0,0.88)">{n.label}</text>
      {/if}
    {/each}
  </g>
</GraphViewport>
