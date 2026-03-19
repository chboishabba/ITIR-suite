<script lang="ts">
  import { createEventDispatcher } from 'svelte';

  type FolderEntry = {
    id: string;
    name: string;
    relPath: string;
    kind: 'file' | 'dir';
    bytes?: number | null;
  };

  export let title = 'Folder';
  export let entries: FolderEntry[] = [];
  export let selectedId: string | null = null;
  export let showSearch = true;
  export let maxHeightPx = 420;

  const dispatch = createEventDispatcher<{ select: FolderEntry }>();

  let query = '';

  function fmtSize(n: number | null | undefined): string {
    if (!Number.isFinite(Number(n))) return '';
    const value = Number(n);
    if (value < 1024) return `${value} B`;
    if (value < 1024 * 1024) return `${(value / 1024).toFixed(1)} KB`;
    return `${(value / (1024 * 1024)).toFixed(1)} MB`;
  }

  $: filtered = (() => {
    const q = query.trim().toLowerCase();
    if (!q) return entries;
    return entries.filter((e) => `${e.name} ${e.relPath}`.toLowerCase().includes(q));
  })();
</script>

<div class="rounded-2xl bg-paper-50 shadow-crisp ring-1 ring-ink-900/10">
  <div class="flex items-center justify-between gap-3 border-b border-ink-900/10 px-4 py-3">
    <div class="font-display text-sm tracking-tight text-ink-950">{title}</div>
    <div class="font-mono text-[10px] text-ink-800/70">entries={entries.length}</div>
  </div>

{#if showSearch}
    <div class="border-b border-ink-900/10 px-4 py-2">
      <label class="sr-only">Filter transcript and document files</label>
      <input
        class="w-full rounded-lg bg-paper-100 px-3 py-2 text-sm ring-1 ring-ink-900/10"
        bind:value={query}
        placeholder="Filter files/folders..."
        aria-label="Filter files and folders"
      />
    </div>
  {/if}

  <div class="overflow-auto px-2 py-2" style={`max-height:${Math.max(160, Math.floor(maxHeightPx))}px`}>
    {#if !filtered.length}
      <div class="px-3 py-2 text-xs text-ink-800/70">No entries match the current filter.</div>
    {:else}
      <div class="space-y-1">
        {#each filtered as entry (entry.id)}
          <button
            type="button"
            aria-label={`${entry.kind} ${entry.name}`}
            aria-current={selectedId === entry.id ? 'true' : undefined}
            class={`grid w-full grid-cols-[auto_1fr_auto] items-center gap-2 rounded-md px-3 py-2 text-left ring-1 ring-ink-900/10 hover:bg-ink-950/[0.03] ${
              selectedId === entry.id ? 'bg-sky-50 ring-sky-300/50' : 'bg-white'
            }`}
            on:click={() => dispatch('select', entry)}
          >
            <span class="font-mono text-[10px] uppercase tracking-wider text-ink-800/70">{entry.kind}</span>
            <span class="min-w-0 truncate font-mono text-[12px] text-ink-950" title={entry.relPath}>{entry.name}</span>
            <span class="font-mono text-[10px] text-ink-800/60">{fmtSize(entry.bytes)}</span>
          </button>
        {/each}
      </div>
    {/if}
  </div>
</div>
