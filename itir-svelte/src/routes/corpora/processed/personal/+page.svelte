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
        artifactPath: string | null;
        origin: 'fixture' | 'live' | 'persisted';
        reviewRunId: string | null;
        storageBasis: 'sqlite' | 'artifact';
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
    feedbackReceipts: Array<{
      receiptId: string;
      feedbackClass: string;
      roleLabel: string;
      taskLabel: string;
      targetProduct: string | null;
      targetSurface: string | null;
      workflowLabel: string | null;
      sourceKind: string;
      summary: string;
      quoteText: string;
      severity: string;
      desiredOutcome: string | null;
      sentiment: string | null;
      capturedAt: string;
      tags: string[];
      createdAt: string;
      provenance: Record<string, unknown>;
      drillInHref: string | null;
      drillInLabel: string | null;
    }>;
  };
  export let form:
    | {
        ok?: boolean;
        error?: string;
        addedReceiptId?: string;
        addedFeedbackClass?: string;
        importedCount?: number;
        values?: Record<string, string>;
      }
    | undefined;
</script>

<DashboardShell title="Personal Processed Results">
  <Section
    title="Personal Processed Results"
    subtitle="Browse the outputs over your real transcript, AU, Messenger-adjacent, and affidavit corpora rather than only generic demo semantic reports."
  >
    <div class="text-sm text-ink-800/75">
      This view is DB-first for persisted <span class="font-mono">:real_</span> fact-review runs and now prefers the canonical sqlite contested-review receiver for affidavit coverage where available. Artifact cards remain as fallback projections.
    </div>
  </Section>

  <Section
    title="Feedback Receipts"
    subtitle="Capture actual frustrations, delight signals, and competitor pain points into the canonical receiver without dropping to raw CLI or sqlite."
  >
    {#if form?.error}
      <div class="rounded-2xl bg-amber-100 px-4 py-3 text-sm text-ink-950 ring-1 ring-amber-900/15">
        {form.error}
      </div>
    {:else if form?.addedReceiptId}
      <div class="rounded-2xl bg-paper-100 px-4 py-3 text-sm text-ink-950 ring-1 ring-ink-900/10">
        Added feedback receipt <span class="font-mono">{form.addedReceiptId}</span> ({form.addedFeedbackClass}).
      </div>
    {:else if form?.importedCount}
      <div class="rounded-2xl bg-paper-100 px-4 py-3 text-sm text-ink-950 ring-1 ring-ink-900/10">
        Imported {form.importedCount} feedback receipts.
      </div>
    {/if}

    <div class="grid gap-4 lg:grid-cols-2">
      <Panel>
        <form method="POST" action="?/addFeedback" class="space-y-3">
          <div class="text-xs uppercase tracking-[0.28em] text-ink-800/60">Add one receipt</div>
          <div class="grid gap-3 sm:grid-cols-2">
            <label class="text-sm text-ink-900">
              Class
              <select name="feedbackClass" class="mt-1 w-full rounded-xl border border-ink-900/15 bg-paper px-3 py-2 text-sm">
                <option value="suite_frustration" selected={form?.values?.feedbackClass === 'suite_frustration'}>suite_frustration</option>
                <option value="competitor_frustration" selected={form?.values?.feedbackClass === 'competitor_frustration'}>competitor_frustration</option>
                <option value="delight_signal" selected={form?.values?.feedbackClass === 'delight_signal'}>delight_signal</option>
              </select>
            </label>
            <label class="text-sm text-ink-900">
              Severity
              <select name="severity" class="mt-1 w-full rounded-xl border border-ink-900/15 bg-paper px-3 py-2 text-sm">
                <option value="medium" selected={form?.values?.severity === 'medium'}>medium</option>
                <option value="low" selected={form?.values?.severity === 'low'}>low</option>
                <option value="high" selected={form?.values?.severity === 'high'}>high</option>
                <option value="critical" selected={form?.values?.severity === 'critical'}>critical</option>
              </select>
            </label>
            <label class="text-sm text-ink-900">
              Role
              <input name="roleLabel" value={form?.values?.roleLabel ?? ''} class="mt-1 w-full rounded-xl border border-ink-900/15 bg-paper px-3 py-2 text-sm" />
            </label>
            <label class="text-sm text-ink-900">
              Task
              <input name="taskLabel" value={form?.values?.taskLabel ?? ''} class="mt-1 w-full rounded-xl border border-ink-900/15 bg-paper px-3 py-2 text-sm" />
            </label>
            <label class="text-sm text-ink-900">
              Source kind
              <select name="sourceKind" class="mt-1 w-full rounded-xl border border-ink-900/15 bg-paper px-3 py-2 text-sm">
                <option value="interview" selected={form?.values?.sourceKind === 'interview'}>interview</option>
                <option value="usability_session" selected={form?.values?.sourceKind === 'usability_session'}>usability_session</option>
                <option value="chat_thread" selected={form?.values?.sourceKind === 'chat_thread'}>chat_thread</option>
                <option value="operator_note" selected={form?.values?.sourceKind === 'operator_note'}>operator_note</option>
                <option value="story_proxy" selected={form?.values?.sourceKind === 'story_proxy'}>story_proxy</option>
              </select>
            </label>
            <label class="text-sm text-ink-900">
              Sentiment
              <select name="sentiment" class="mt-1 w-full rounded-xl border border-ink-900/15 bg-paper px-3 py-2 text-sm">
                <option value="">(optional)</option>
                <option value="negative" selected={form?.values?.sentiment === 'negative'}>negative</option>
                <option value="neutral" selected={form?.values?.sentiment === 'neutral'}>neutral</option>
                <option value="positive" selected={form?.values?.sentiment === 'positive'}>positive</option>
              </select>
            </label>
          </div>
          <label class="block text-sm text-ink-900">
            Summary
            <input name="summary" value={form?.values?.summary ?? ''} class="mt-1 w-full rounded-xl border border-ink-900/15 bg-paper px-3 py-2 text-sm" />
          </label>
          <label class="block text-sm text-ink-900">
            Quote
            <textarea name="quoteText" rows="3" class="mt-1 w-full rounded-xl border border-ink-900/15 bg-paper px-3 py-2 text-sm">{form?.values?.quoteText ?? ''}</textarea>
          </label>
          <div class="grid gap-3 sm:grid-cols-2">
            <label class="text-sm text-ink-900">
              Target product
              <input name="targetProduct" value={form?.values?.targetProduct ?? ''} class="mt-1 w-full rounded-xl border border-ink-900/15 bg-paper px-3 py-2 text-sm" />
            </label>
            <label class="text-sm text-ink-900">
              Target surface
              <input name="targetSurface" value={form?.values?.targetSurface ?? ''} class="mt-1 w-full rounded-xl border border-ink-900/15 bg-paper px-3 py-2 text-sm" />
            </label>
            <label class="text-sm text-ink-900">
              Workflow label
              <input name="workflowLabel" value={form?.values?.workflowLabel ?? ''} class="mt-1 w-full rounded-xl border border-ink-900/15 bg-paper px-3 py-2 text-sm" />
            </label>
            <label class="text-sm text-ink-900">
              Tags
              <input name="tagsText" value={form?.values?.tagsText ?? ''} placeholder="navigation, workflow, trust" class="mt-1 w-full rounded-xl border border-ink-900/15 bg-paper px-3 py-2 text-sm" />
            </label>
          </div>
          <label class="block text-sm text-ink-900">
            Desired outcome
            <input name="desiredOutcome" value={form?.values?.desiredOutcome ?? ''} class="mt-1 w-full rounded-xl border border-ink-900/15 bg-paper px-3 py-2 text-sm" />
          </label>
          <div class="grid gap-3 sm:grid-cols-2">
            <label class="text-sm text-ink-900">
              Provenance collector
              <input name="provenanceCollector" value={form?.values?.provenanceCollector ?? ''} class="mt-1 w-full rounded-xl border border-ink-900/15 bg-paper px-3 py-2 text-sm" />
            </label>
            <label class="text-sm text-ink-900">
              Provenance source ref
              <input name="provenanceSourceRef" value={form?.values?.provenanceSourceRef ?? ''} class="mt-1 w-full rounded-xl border border-ink-900/15 bg-paper px-3 py-2 text-sm" />
            </label>
          </div>
          <div class="grid gap-3 sm:grid-cols-2">
            <label class="text-sm text-ink-900">
              Canonical thread id
              <input name="canonicalThreadId" value={form?.values?.canonicalThreadId ?? ''} class="mt-1 w-full rounded-xl border border-ink-900/15 bg-paper px-3 py-2 font-mono text-[12px]" />
            </label>
            <label class="text-sm text-ink-900">
              Workflow kind ref
              <input name="workflowKindRef" value={form?.values?.workflowKindRef ?? ''} class="mt-1 w-full rounded-xl border border-ink-900/15 bg-paper px-3 py-2 text-sm" />
            </label>
            <label class="text-sm text-ink-900">
              Workflow run id ref
              <input name="workflowRunIdRef" value={form?.values?.workflowRunIdRef ?? ''} class="mt-1 w-full rounded-xl border border-ink-900/15 bg-paper px-3 py-2 font-mono text-[12px]" />
            </label>
            <label class="text-sm text-ink-900">
              Source label ref
              <input name="sourceLabelRef" value={form?.values?.sourceLabelRef ?? ''} class="mt-1 w-full rounded-xl border border-ink-900/15 bg-paper px-3 py-2 text-sm" />
            </label>
          </div>
          <button type="submit" class="inline-flex items-center rounded-full bg-ink-950 px-4 py-2 text-sm text-paper shadow-sm">Add receipt</button>
        </form>
      </Panel>

      <Panel>
        <form method="POST" action="?/importFeedback" class="space-y-3">
          <div class="text-xs uppercase tracking-[0.28em] text-ink-800/60">Import JSONL</div>
          <div class="text-sm text-ink-800/75">
            Paste one JSON object per line using the <span class="font-mono">feedback.receipt.v1</span> field names. Missing <span class="font-mono">schema_version</span> and <span class="font-mono">captured_at</span> are filled conservatively.
          </div>
          <label class="block text-sm text-ink-900">
            JSONL batch
            <textarea name="jsonlText" rows="15" class="mt-1 w-full rounded-xl border border-ink-900/15 bg-paper px-3 py-2 font-mono text-[12px] leading-5">{form?.values?.jsonlText ?? ''}</textarea>
          </label>
          <button type="submit" class="inline-flex items-center rounded-full bg-paper-100 px-4 py-2 text-sm text-ink-950 ring-1 ring-ink-900/10 shadow-sm">Import receipts</button>
        </form>
      </Panel>
    </div>

    <div class="mt-6 grid gap-4 lg:grid-cols-2">
      {#each data.feedbackReceipts as receipt}
        <Panel>
          <div class="flex items-start justify-between gap-3">
            <div>
              <div class="text-xs uppercase tracking-[0.28em] text-ink-800/60">{receipt.feedbackClass}</div>
              <div class="mt-2 text-sm text-ink-950">{receipt.summary}</div>
              <div class="mt-1 font-mono text-[11px] text-ink-800/65 break-all">{receipt.receiptId}</div>
            </div>
            <span class="inline-flex items-center rounded-full bg-paper-100 px-2 py-1 text-[10px] font-mono uppercase tracking-widest text-ink-900 ring-1 ring-ink-900/10">
              {receipt.severity}
            </span>
          </div>
          <div class="mt-3 text-[11px] text-ink-800/70">{receipt.roleLabel} · {receipt.taskLabel} · {receipt.sourceKind}</div>
          {#if receipt.provenance?.source_ref}
            <div class="mt-1 font-mono text-[11px] text-ink-800/65 break-all">
              source ref: {String(receipt.provenance.source_ref)}
            </div>
          {/if}
          {#if receipt.provenance?.workflow_kind || receipt.provenance?.workflow_run_id || receipt.provenance?.source_label}
            <div class="mt-1 font-mono text-[11px] text-ink-800/65 break-all">
              selector:
              {String(receipt.provenance.workflow_kind ?? '')}
              {#if receipt.provenance?.workflow_run_id}
                {" / "}{String(receipt.provenance.workflow_run_id)}
              {/if}
              {#if receipt.provenance?.source_label}
                {" / "}{String(receipt.provenance.source_label)}
              {/if}
            </div>
          {/if}
          <blockquote class="mt-3 rounded-xl bg-paper-50 px-3 py-3 text-sm text-ink-900 ring-1 ring-ink-900/10">
            {receipt.quoteText}
          </blockquote>
          {#if receipt.desiredOutcome}
            <div class="mt-3 text-sm text-ink-800/85">
              desired outcome: {receipt.desiredOutcome}
            </div>
          {/if}
          {#if receipt.drillInHref}
            <div class="mt-3">
              <a class="underline decoration-ink-950/20 underline-offset-4 hover:decoration-ink-950/50 text-sm" href={receipt.drillInHref}>
                {receipt.drillInLabel ?? 'Open related surface'}
              </a>
            </div>
          {/if}
          <div class="mt-3 flex flex-wrap gap-2">
            {#if receipt.targetProduct}
              <span class="inline-flex items-center rounded-full bg-paper-50 px-2 py-1 text-[10px] font-mono text-ink-900 ring-1 ring-ink-900/10">
                product: {receipt.targetProduct}
              </span>
            {/if}
            {#if receipt.targetSurface}
              <span class="inline-flex items-center rounded-full bg-paper-50 px-2 py-1 text-[10px] font-mono text-ink-900 ring-1 ring-ink-900/10">
                surface: {receipt.targetSurface}
              </span>
            {/if}
            {#if receipt.workflowLabel}
              <span class="inline-flex items-center rounded-full bg-paper-50 px-2 py-1 text-[10px] font-mono text-ink-900 ring-1 ring-ink-900/10">
                workflow: {receipt.workflowLabel}
              </span>
            {/if}
            {#each receipt.tags as tag}
              <span class="inline-flex items-center rounded-full bg-paper-50 px-2 py-1 text-[10px] font-mono text-ink-900 ring-1 ring-ink-900/10">
                {tag}
              </span>
            {/each}
          </div>
          <div class="mt-3 text-[11px] text-ink-800/70">{receipt.capturedAt}</div>
        </Panel>
      {/each}
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
    subtitle="Coverage/rebuttal summaries over affidavit-style corpora, preferring persisted contested-review runs and falling back to artifact projections when needed."
  >
    <div class="grid gap-4 lg:grid-cols-2">
      {#each data.overview.affidavits as affidavit}
        <Panel>
          <div class="flex items-start justify-between gap-3">
            <div>
              <div class="text-xs uppercase tracking-[0.28em] text-ink-800/60">{affidavit.label}</div>
              {#if affidavit.reviewRunId}
                <div class="mt-2 font-mono text-[11px] text-ink-800/65 break-all">{affidavit.reviewRunId}</div>
              {:else if affidavit.artifactPath}
                <div class="mt-2 font-mono text-[11px] text-ink-800/65 break-all">{affidavit.artifactPath}</div>
              {/if}
            </div>
            <div class="flex flex-col items-end gap-2">
              <span class="inline-flex items-center rounded-full bg-paper-100 px-2 py-1 text-[10px] font-mono uppercase tracking-widest text-ink-900 ring-1 ring-ink-900/10">
                {affidavit.origin}
              </span>
              <span class="inline-flex items-center rounded-full bg-paper-50 px-2 py-1 text-[10px] font-mono uppercase tracking-widest text-ink-900 ring-1 ring-ink-900/10">
                {affidavit.storageBasis}
              </span>
            </div>
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
