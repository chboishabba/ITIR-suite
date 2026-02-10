<script lang="ts">
  import Section from '$lib/ui/Section.svelte';

  export let warnings: string[] | undefined;
</script>

<Section title="Warnings" subtitle="Explicit warnings emitted by the compiler.">
  {#if warnings && warnings.length}
    <ul class="list-disc pl-5 text-sm text-ink-900/80">
      {#each warnings as w}
        <li>{w}</li>
      {/each}
    </ul>
  {:else}
    <div class="text-sm text-ink-800/70">No warnings.</div>
  {/if}
</Section>
