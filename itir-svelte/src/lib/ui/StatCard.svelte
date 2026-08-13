<script lang="ts">
  export let label: string;
  export let value: string;
  export let hint: string | null = null;
</script>

<div class="rounded-xl bg-paper-100 ring-1 ring-ink-900/10 px-4 py-3">
  <div class="grid grid-cols-[1fr_auto] items-start gap-3">
    <div>
      <div class="text-xs uppercase tracking-widest text-ink-800/70">{label}</div>
      <div class="mt-1 font-display text-2xl leading-none text-ink-950">{value}</div>
      {#if hint}
        <div class="mt-2 text-xs text-ink-800/60">{hint}</div>
      {/if}
    </div>
    <div class="self-center">
      <slot name="spark" />
    </div>
  </div>
</div>
