<script lang="ts">
  import DashboardShell from '$lib/sb-dashboard/components/DashboardShell.svelte';
  import Panel from '$lib/ui/Panel.svelte';
  import Section from '$lib/ui/Section.svelte';

  export let data: {
    overview: {
      runs: Array<{
        sourceLabel: string;
        runId: string;
        workflowKind: string;
        workflowRunId: string;
        createdAt: string;
        notes: string;
        counts: {
          sourceCount: number;
          statementCount: number;
          factCount: number;
          observationCount: number;
          eventCount: number;
          reviewCount: number;
          contestationCount: number;
        };
        summary: Record<string, number>;
        operatorViews: string[];
        acceptanceSummary: {
          storyCount: number;
          passCount: number;
          partialCount: number;
          failCount: number;
        } | null;
        rawSourceHref: string;
        workbenchHref: string;
      }>;
      affidavits: Array<{
        key: string;
        label: string;
        artifactPath: string;
        origin: 'fixture' | 'live';
        affidavitPath: string;
        sourcePath: string;
        summary: {
          affidavitPropositionCount: number;
          coveredCount: number;
          partialCount: number;
          unsupportedAffidavitCount: number;
          missingReviewCount: number;
          substantiveResponseCount: number;
          affidavitSupportedRatio: number;
          substantiveResponseRatio: number;
        };
      }>;
    };
  };
</script>

<DashboardShell title="Personal Processed Results">
  <Section
    title="Personal Processed Results"
    subtitle="Browse the outputs over your real transcript, AU, Messenger-adjacent, and affidavit corpora rather than only generic demo semantic reports."
  >
    <div class="text-sm text-ink-800/75">
      This view foregrounds persisted <span class="font-mono">:real_</span> fact-review runs and the affidavit review artifacts currently available in the repo or live temp outputs.
    </div>
  </Section>

  <Section
    title="Fact Review Runs"
    subtitle="Live persisted personal runs from the canonical ITIR DB, with operator-view and acceptance summaries when available."
  >
    <div class="grid gap-4 lg:grid-cols-2">
      {#each data.overview.runs as run}
        <Panel>
          <div class="flex items-start justify-between gap-3">
            <div>
              <div class="text-xs uppercase tracking-[0.28em] text-ink-800/60">{run.workflowKind || 'fact review'}</div>
              <div class="mt-2 text-sm text-ink-950">{run.sourceLabel}</div>
              <div class="mt-1 font-mono text-[11px] text-ink-800/65 break-all">{run.runId}</div>
            </div>
            <div class="flex flex-col items-end gap-2 text-sm">
              <a class="underline decoration-ink-950/20 underline-offset-4 hover:decoration-ink-950/50" href={run.workbenchHref}>
                Open workbench
              </a>
              <a class="underline decoration-ink-950/20 underline-offset-4 hover:decoration-ink-950/50" href={run.rawSourceHref}>
                Open source lane
              </a>
            </div>
          </div>

          <div class="mt-3 text-[11px] text-ink-800/70">{run.createdAt}</div>
          {#if run.notes}
            <div class="mt-2 text-sm text-ink-800/85">{run.notes}</div>
          {/if}

          <div class="mt-4 grid gap-2 sm:grid-cols-2">
            <div class="rounded-xl bg-paper-100 px-3 py-2 ring-1 ring-ink-900/10">
              <div class="text-[10px] uppercase tracking-widest text-ink-800/60">Counts</div>
              <div class="mt-1 text-[11px] text-ink-800/75">{run.counts.factCount.toLocaleString()} facts</div>
              <div class="text-[11px] text-ink-800/75">{run.counts.observationCount.toLocaleString()} observations</div>
              <div class="text-[11px] text-ink-800/75">{run.counts.statementCount.toLocaleString()} statements</div>
              <div class="text-[11px] text-ink-800/75">{run.counts.sourceCount.toLocaleString()} sources</div>
            </div>
            <div class="rounded-xl bg-paper-100 px-3 py-2 ring-1 ring-ink-900/10">
              <div class="text-[10px] uppercase tracking-widest text-ink-800/60">Pressure</div>
              <div class="mt-1 text-[11px] text-ink-800/75">{run.summary.review_queue_count?.toLocaleString?.() ?? 0} review queue</div>
              <div class="text-[11px] text-ink-800/75">{run.summary.contested_item_count?.toLocaleString?.() ?? run.counts.contestationCount.toLocaleString()} contested</div>
              <div class="text-[11px] text-ink-800/75">{run.summary.missing_actor_review_queue_count?.toLocaleString?.() ?? 0} missing actor</div>
              <div class="text-[11px] text-ink-800/75">{run.summary.missing_date_review_queue_count?.toLocaleString?.() ?? 0} missing date</div>
            </div>
          </div>

          {#if run.acceptanceSummary}
            <div class="mt-4">
              <div class="text-[10px] uppercase tracking-widest text-ink-800/60">Acceptance</div>
              <div class="mt-2 flex flex-wrap gap-2">
                <span class="inline-flex items-center rounded-full bg-paper-100 px-2 py-1 text-[10px] font-mono uppercase tracking-widest text-ink-900 ring-1 ring-ink-900/10">
                  stories: {run.acceptanceSummary.storyCount}
                </span>
                <span class="inline-flex items-center rounded-full bg-paper-100 px-2 py-1 text-[10px] font-mono uppercase tracking-widest text-ink-900 ring-1 ring-ink-900/10">
                  pass: {run.acceptanceSummary.passCount}
                </span>
                <span class="inline-flex items-center rounded-full bg-paper-100 px-2 py-1 text-[10px] font-mono uppercase tracking-widest text-ink-900 ring-1 ring-ink-900/10">
                  partial: {run.acceptanceSummary.partialCount}
                </span>
                <span class="inline-flex items-center rounded-full bg-paper-100 px-2 py-1 text-[10px] font-mono uppercase tracking-widest text-ink-900 ring-1 ring-ink-900/10">
                  fail: {run.acceptanceSummary.failCount}
                </span>
              </div>
            </div>
          {/if}

          {#if run.operatorViews.length}
            <div class="mt-4">
              <div class="text-[10px] uppercase tracking-widest text-ink-800/60">Operator views</div>
              <div class="mt-2 flex flex-wrap gap-2">
                {#each run.operatorViews as view}
                  <span class="inline-flex items-center rounded-full bg-paper-50 px-2 py-1 text-[10px] font-mono text-ink-900 ring-1 ring-ink-900/10">
                    {view}
                  </span>
                {/each}
              </div>
            </div>
          {/if}
        </Panel>
      {/each}
    </div>
  </Section>

  <Section
    title="Affidavit Reviews"
    subtitle="Coverage/rebuttal summaries over the affidavit-style corpora, including the latest live contested Google Docs output when present."
  >
    <div class="grid gap-4 lg:grid-cols-2">
      {#each data.overview.affidavits as affidavit}
        <Panel>
          <div class="flex items-start justify-between gap-3">
            <div>
              <div class="text-xs uppercase tracking-[0.28em] text-ink-800/60">{affidavit.label}</div>
              <div class="mt-2 font-mono text-[11px] text-ink-800/65 break-all">{affidavit.artifactPath}</div>
            </div>
            <span class="inline-flex items-center rounded-full bg-paper-100 px-2 py-1 text-[10px] font-mono uppercase tracking-widest text-ink-900 ring-1 ring-ink-900/10">
              {affidavit.origin}
            </span>
          </div>

          <div class="mt-4 grid gap-2 sm:grid-cols-2">
            <div class="rounded-xl bg-paper-100 px-3 py-2 ring-1 ring-ink-900/10">
              <div class="text-[10px] uppercase tracking-widest text-ink-800/60">Coverage</div>
              <div class="mt-1 text-[11px] text-ink-800/75">{affidavit.summary.affidavitPropositionCount.toLocaleString()} propositions</div>
              <div class="text-[11px] text-ink-800/75">{affidavit.summary.coveredCount.toLocaleString()} covered</div>
              <div class="text-[11px] text-ink-800/75">{affidavit.summary.partialCount.toLocaleString()} partial</div>
              <div class="text-[11px] text-ink-800/75">{affidavit.summary.unsupportedAffidavitCount.toLocaleString()} unsupported</div>
            </div>
            <div class="rounded-xl bg-paper-100 px-3 py-2 ring-1 ring-ink-900/10">
              <div class="text-[10px] uppercase tracking-widest text-ink-800/60">Response</div>
              <div class="mt-1 text-[11px] text-ink-800/75">{affidavit.summary.missingReviewCount.toLocaleString()} review queue only</div>
              <div class="text-[11px] text-ink-800/75">{affidavit.summary.substantiveResponseCount.toLocaleString()} substantive responses</div>
              <div class="text-[11px] text-ink-800/75">support ratio {affidavit.summary.affidavitSupportedRatio.toFixed(3)}</div>
              <div class="text-[11px] text-ink-800/75">substantive ratio {affidavit.summary.substantiveResponseRatio.toFixed(3)}</div>
            </div>
          </div>

          {#if affidavit.affidavitPath}
            <div class="mt-4 text-[11px] text-ink-800/75 break-all">
              affidavit: {affidavit.affidavitPath}
            </div>
          {/if}
          {#if affidavit.sourcePath}
            <div class="mt-1 text-[11px] text-ink-800/75 break-all">
              source: {affidavit.sourcePath}
            </div>
          {/if}
        </Panel>
      {/each}
    </div>
  </Section>
</DashboardShell>
