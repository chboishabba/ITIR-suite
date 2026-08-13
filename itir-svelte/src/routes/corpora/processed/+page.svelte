<script lang="ts">
  import DashboardShell from '$lib/sb-dashboard/components/DashboardShell.svelte';
  import Panel from '$lib/ui/Panel.svelte';
  import Section from '$lib/ui/Section.svelte';

  export let data: {
    corpora: Array<{
      key: string;
      label: string;
      runId: string;
      summary: {
        entityCount: number;
        relationCandidateCount: number;
        promotedRelationCount: number;
        candidateOnlyRelationCount: number;
        abstainedRelationCandidateCount: number;
        unresolvedMentionCount: number;
      };
      semanticBasisCounts: Record<string, number>;
      topPredicates: Array<{ predicateKey: string; displayLabel: string; totalCount: number }>;
      href: string;
    }>;
  };
</script>

<DashboardShell title="Processed Results">
  <Section
    title="Processed Results"
    subtitle="Browse the extracted semantic/report outputs rather than only the raw source corpora."
  >
    <div class="text-sm text-ink-800/75">
      This is the quick operator view for things like promoted relation counts, abstentions, semantic basis mix, and the dominant extracted predicates per corpus.
    </div>
    <div class="mt-3 text-sm">
      <a class="mr-4 underline decoration-ink-950/20 underline-offset-4 hover:decoration-ink-950/50" href="/corpora/processed/personal">
        Open personal corpus results
      </a>
      <a class="underline decoration-ink-950/20 underline-offset-4 hover:decoration-ink-950/50" href="/corpora/processed/broader">
        Open broader diagnostics
      </a>
    </div>
  </Section>

  <div class="grid gap-4 lg:grid-cols-3">
    {#each data.corpora as corpus}
      <Panel>
        <div class="flex items-start justify-between gap-3">
          <div>
            <div class="text-xs uppercase tracking-[0.28em] text-ink-800/60">{corpus.label}</div>
            <div class="mt-2 font-mono text-[11px] text-ink-800/65 break-all">{corpus.runId || 'no run id'}</div>
          </div>
          <a class="text-sm underline decoration-ink-950/20 underline-offset-4 hover:decoration-ink-950/50" href={corpus.href}>
            Open full report
          </a>
        </div>

        <div class="mt-4 grid gap-2 sm:grid-cols-2">
          <div class="rounded-xl bg-paper-100 px-3 py-2 ring-1 ring-ink-900/10">
            <div class="text-[10px] uppercase tracking-widest text-ink-800/60">Relations</div>
            <div class="mt-1 text-sm text-ink-950">{corpus.summary.relationCandidateCount.toLocaleString()} candidates</div>
            <div class="text-[11px] text-ink-800/70">{corpus.summary.promotedRelationCount.toLocaleString()} promoted</div>
            <div class="text-[11px] text-ink-800/70">{corpus.summary.candidateOnlyRelationCount.toLocaleString()} candidate-only</div>
          </div>
          <div class="rounded-xl bg-paper-100 px-3 py-2 ring-1 ring-ink-900/10">
            <div class="text-[10px] uppercase tracking-widest text-ink-800/60">Quality</div>
            <div class="mt-1 text-[11px] text-ink-800/70">{corpus.summary.abstainedRelationCandidateCount.toLocaleString()} abstained</div>
            <div class="text-[11px] text-ink-800/70">{corpus.summary.unresolvedMentionCount.toLocaleString()} unresolved mentions</div>
            <div class="text-[11px] text-ink-800/70">{corpus.summary.entityCount.toLocaleString()} entities</div>
          </div>
        </div>

        <div class="mt-4">
          <div class="text-[10px] uppercase tracking-widest text-ink-800/60">Semantic basis</div>
          {#if Object.keys(corpus.semanticBasisCounts).length}
            <div class="mt-2 flex flex-wrap gap-2">
              {#each Object.entries(corpus.semanticBasisCounts) as [basis, count]}
                <span class="inline-flex items-center rounded-full bg-paper-100 px-2 py-1 text-[10px] font-mono uppercase tracking-widest text-ink-900 ring-1 ring-ink-900/10">
                  {basis}: {count.toLocaleString()}
                </span>
              {/each}
            </div>
          {:else}
            <div class="mt-2 text-sm text-ink-800/70">No semantic basis counts emitted for this corpus.</div>
          {/if}
        </div>

        <div class="mt-4">
          <div class="text-[10px] uppercase tracking-widest text-ink-800/60">Top predicates</div>
          {#if corpus.topPredicates.length}
            <div class="mt-2 space-y-2">
              {#each corpus.topPredicates as predicate}
                <div class="flex items-center justify-between gap-3 rounded-lg bg-paper-100 px-3 py-2 ring-1 ring-ink-900/10">
                  <div class="min-w-0">
                    <div class="text-sm text-ink-950 truncate">{predicate.displayLabel}</div>
                    <div class="font-mono text-[10px] text-ink-800/65 truncate">{predicate.predicateKey}</div>
                  </div>
                  <div class="font-mono text-xs text-ink-950">{predicate.totalCount.toLocaleString()}</div>
                </div>
              {/each}
            </div>
          {:else}
            <div class="mt-2 text-sm text-ink-800/70">No promoted/candidate predicate rows found.</div>
          {/if}
        </div>
      </Panel>
    {/each}
  </div>
</DashboardShell>
