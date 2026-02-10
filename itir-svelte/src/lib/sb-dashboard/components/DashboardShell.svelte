<script lang="ts">
  export let title = 'ITIR UI';
</script>

<div class="min-h-dvh">
  <div class="mx-auto max-w-[1200px] px-4 py-6">
    <header class="mb-6">
      <div class="text-xs uppercase tracking-[0.28em] text-ink-800/60">{title}</div>
      <div class="mt-2 h-px w-full bg-gradient-to-r from-ink-900/20 via-ink-900/5 to-transparent"></div>
    </header>
    <main class="space-y-5">
      <slot />
    </main>
  </div>
</div>
