<script lang="ts">
  import Panel from '$lib/ui/Panel.svelte';

  export let objectHintRows: Array<{
    title: string;
    source: string;
    hints: Array<{ lane: string; kind: string; title: string; score: number }>;
  }> = [];
</script>

<Panel>
  <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Object resolver hints</div>
  {#if objectHintRows.length}
    <div class="mt-3 max-h-[260px] space-y-2 overflow-auto">
      {#each objectHintRows as r (r.title + ':' + r.source)}
        <div class="rounded border border-ink-950/10 bg-white px-2 py-2">
          <div class="font-mono text-[11px] text-ink-950">
            [{r.source}] {r.title}
          </div>
          {#if r.hints.length}
            <div class="mt-1 flex flex-wrap gap-2 text-[10px]">
              {#each r.hints as h, i (r.title + ':' + i)}
                <span class="rounded bg-slate-100 px-1.5 py-0.5 font-mono text-ink-900">
                  {h.kind}@{h.lane}: {h.title} ({Number(h.score).toFixed(2)})
                </span>
              {/each}
            </div>
          {:else}
            <div class="mt-1 text-[11px] text-ink-800/70">no resolver hints</div>
          {/if}
        </div>
      {/each}
    </div>
  {:else}
    <div class="mt-3 text-xs text-ink-800/70">No objects available for hinting in this event.</div>
  {/if}
</Panel>
