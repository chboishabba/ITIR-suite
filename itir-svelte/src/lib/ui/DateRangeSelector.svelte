<script lang="ts">
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';

  export let availableDates: string[] = [];
  export let start: string;
  export let end: string;

  const isDate = (v: string) => /^\d{4}-\d{2}-\d{2}$/.test(v);

  $: min = availableDates.length ? availableDates[0] : undefined;
  $: max = availableDates.length ? availableDates[availableDates.length - 1] : undefined;

  async function apply(nextStart: string, nextEnd: string) {
    if (!isDate(nextStart) || !isDate(nextEnd)) return;
    const s = nextStart;
    const e = nextEnd;
    const startFinal = s <= e ? s : e;
    const endFinal = s <= e ? e : s;

    const url = new URL($page.url);
    url.searchParams.set('start', startFinal);
    url.searchParams.set('end', endFinal);
    await goto(url.pathname + url.search, { replaceState: true, keepFocus: true, noScroll: true });
  }
</script>

<div class="rounded-2xl bg-paper-50 shadow-crisp ring-1 ring-ink-900/10 px-5 py-4">
  <div class="flex flex-wrap items-end justify-between gap-4">
    <div>
      <div class="text-xs uppercase tracking-[0.28em] text-ink-800/60">Date range</div>
      <div class="mt-2 font-display text-xl tracking-tight text-ink-950">{start} → {end}</div>
      {#if min && max}
        <div class="mt-2 text-xs text-ink-800/60">
          Available: <span class="font-mono">{min}</span> .. <span class="font-mono">{max}</span>
        </div>
      {/if}
    </div>

    <div class="flex flex-wrap items-end gap-3">
      <div class="grid gap-1">
        <label class="text-xs uppercase tracking-widest text-ink-800/60" for="start">Start</label>
        <input
          id="start"
          type="date"
          class="rounded-lg bg-paper-100 ring-1 ring-ink-900/10 px-3 py-2 text-sm"
          value={start}
          on:change={(e) => apply((e.currentTarget as HTMLInputElement).value, end)}
        />
      </div>
      <div class="grid gap-1">
        <label class="text-xs uppercase tracking-widest text-ink-800/60" for="end">End</label>
        <input
          id="end"
          type="date"
          class="rounded-lg bg-paper-100 ring-1 ring-ink-900/10 px-3 py-2 text-sm"
          value={end}
          on:change={(e) => apply(start, (e.currentTarget as HTMLInputElement).value)}
        />
      </div>
      <button
        class="rounded-lg bg-paper-100 ring-1 ring-ink-900/10 px-3 py-2 text-xs uppercase tracking-widest"
        type="button"
        on:click={() => apply(end, end)}
      >
        Single day
      </button>
    </div>
  </div>
</div>
