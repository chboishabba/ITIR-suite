<script lang="ts">
  import DashboardShell from '$lib/sb-dashboard/components/DashboardShell.svelte';
  import Panel from '$lib/ui/Panel.svelte';
  import Section from '$lib/ui/Section.svelte';

  export let data: {
    diagnostics: Array<{
      key: string;
      label: string;
      artifactPath: string;
      summaryLines: Array<{ label: string; value: string | number }>;
      sections: Array<{ key: string; label: string; stats: Array<{ label: string; value: string | number }> }>;
    }>;
  };
</script>

<DashboardShell title="Broader Diagnostics">
  <Section
    title="Broader Diagnostics"
    subtitle="Browse the wider timeline-family and corpus-diagnostic artifacts that sit beyond the default semantic report."
  >
    <div class="text-sm text-ink-800/75">
      This is where the broader GWB and AU diagnostics live, including family-level breakdowns like <span class="font-mono">public_bios_timeline</span> versus <span class="font-mono">corpus_book_timeline</span>.
    </div>
  </Section>

  <div class="grid gap-4 lg:grid-cols-2">
    {#each data.diagnostics as diagnostic}
      <Panel>
        <div class="text-xs uppercase tracking-[0.28em] text-ink-800/60">{diagnostic.label}</div>
        <div class="mt-2 font-mono text-[11px] text-ink-800/65 break-all">{diagnostic.artifactPath}</div>
        <div class="mt-3 text-sm">
          <a class="underline decoration-ink-950/20 underline-offset-4 hover:decoration-ink-950/50" href={`/corpora/processed/broader/${diagnostic.key}`}>
            Open details
          </a>
        </div>

        <div class="mt-4 space-y-2">
          {#each diagnostic.summaryLines as line}
            <div class="rounded-lg bg-paper-100 px-3 py-2 ring-1 ring-ink-900/10">
              <div class="text-[10px] uppercase tracking-widest text-ink-800/60">{line.label}</div>
              <div class="mt-1 text-sm text-ink-950">{line.value}</div>
            </div>
          {/each}
        </div>

        {#if diagnostic.sections.length}
          <div class="mt-4 space-y-3">
            {#each diagnostic.sections as section}
              <div class="rounded-xl bg-paper-50 px-3 py-3 ring-1 ring-ink-900/10">
                <div class="text-sm text-ink-950">{section.label}</div>
                <div class="mt-2 flex flex-wrap gap-2">
                  {#each section.stats as stat}
                    <span class="inline-flex items-center rounded-full bg-paper-100 px-2 py-1 text-[10px] font-mono uppercase tracking-widest text-ink-900 ring-1 ring-ink-900/10">
                      {stat.label}: {stat.value}
                    </span>
                  {/each}
                </div>
              </div>
            {/each}
          </div>
        {/if}
      </Panel>
    {/each}
  </div>
</DashboardShell>
