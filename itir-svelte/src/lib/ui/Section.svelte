<script lang="ts">
  export let title: string;
  export let subtitle: string | null = null;
</script>

<section class="rounded-2xl bg-paper-50 shadow-crisp ring-1 ring-ink-900/10">
  <header class="flex items-start justify-between gap-6 border-b border-ink-900/10 px-5 py-4">
    <div>
      <h2 class="font-display text-lg tracking-tight text-ink-950">{title}</h2>
      {#if subtitle}
        <p class="mt-1 text-sm text-ink-800/70">{subtitle}</p>
      {/if}
    </div>
    <div class="flex items-center gap-2">
      <slot name="actions" />
    </div>
  </header>
  <div class="px-5 py-4">
    <slot />
  </div>
</section>
