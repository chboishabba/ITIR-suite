import { fail } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';
import {
  addFeedbackReceipt,
  importFeedbackReceiptsFromJsonlText,
  loadFeedbackReceipts,
  loadPersonalProcessedOverview
} from '$lib/server/corpora';

export const load: PageServerLoad = async () => {
  const [overview, feedbackReceipts] = await Promise.all([
    loadPersonalProcessedOverview(),
    loadFeedbackReceipts(20)
  ]);
  return {
    overview,
    feedbackReceipts
  };
};

export const actions: Actions = {
  addFeedback: async ({ request }) => {
    const form = await request.formData();
    const feedbackClass = String(form.get('feedbackClass') ?? '').trim();
    const roleLabel = String(form.get('roleLabel') ?? '').trim();
    const taskLabel = String(form.get('taskLabel') ?? '').trim();
    const sourceKind = String(form.get('sourceKind') ?? '').trim();
    const summary = String(form.get('summary') ?? '').trim();
    const quoteText = String(form.get('quoteText') ?? '').trim();
    const severity = String(form.get('severity') ?? '').trim();
    if (!feedbackClass || !roleLabel || !taskLabel || !sourceKind || !summary || !quoteText || !severity) {
      return fail(400, {
        ok: false,
        error: 'Missing required feedback receipt fields.',
        values: {
          feedbackClass,
          roleLabel,
          taskLabel,
          sourceKind,
          summary,
          quoteText,
          severity,
          targetProduct: String(form.get('targetProduct') ?? ''),
          targetSurface: String(form.get('targetSurface') ?? ''),
          workflowLabel: String(form.get('workflowLabel') ?? ''),
          desiredOutcome: String(form.get('desiredOutcome') ?? ''),
          sentiment: String(form.get('sentiment') ?? ''),
          tagsText: String(form.get('tagsText') ?? ''),
          provenanceCollector: String(form.get('provenanceCollector') ?? ''),
          provenanceSourceRef: String(form.get('provenanceSourceRef') ?? ''),
          canonicalThreadId: String(form.get('canonicalThreadId') ?? ''),
          workflowKindRef: String(form.get('workflowKindRef') ?? ''),
          workflowRunIdRef: String(form.get('workflowRunIdRef') ?? ''),
          sourceLabelRef: String(form.get('sourceLabelRef') ?? '')
        }
      });
    }
    const tags = String(form.get('tagsText') ?? '')
      .split(',')
      .map((value) => value.trim())
      .filter(Boolean);
    const canonicalThreadId = String(form.get('canonicalThreadId') ?? '').trim();
    const workflowKindRef = String(form.get('workflowKindRef') ?? '').trim();
    const workflowRunIdRef = String(form.get('workflowRunIdRef') ?? '').trim();
    const sourceLabelRef = String(form.get('sourceLabelRef') ?? '').trim();
    const provenanceJson: Record<string, unknown> = {};
    if (canonicalThreadId) {
      provenanceJson.source_ref = canonicalThreadId;
      provenanceJson.canonical_thread_id = canonicalThreadId;
    }
    if (workflowKindRef) provenanceJson.workflow_kind = workflowKindRef;
    if (workflowRunIdRef) provenanceJson.workflow_run_id = workflowRunIdRef;
    if (sourceLabelRef) provenanceJson.source_label = sourceLabelRef;
    const result = await addFeedbackReceipt({
      feedbackClass,
      roleLabel,
      taskLabel,
      sourceKind,
      summary,
      quoteText,
      severity,
      capturedAt: String(form.get('capturedAt') ?? '').trim(),
      targetProduct: String(form.get('targetProduct') ?? '').trim(),
      targetSurface: String(form.get('targetSurface') ?? '').trim(),
      workflowLabel: String(form.get('workflowLabel') ?? '').trim(),
      desiredOutcome: String(form.get('desiredOutcome') ?? '').trim(),
      sentiment: String(form.get('sentiment') ?? '').trim(),
      provenanceCollector: String(form.get('provenanceCollector') ?? '').trim(),
      provenanceSourceRef: String(form.get('provenanceSourceRef') ?? '').trim(),
      provenanceJson,
      tags
    });
    return {
      ok: true,
      addedReceiptId: result.receiptId,
      addedFeedbackClass: result.feedbackClass
    };
  },
  importFeedback: async ({ request }) => {
    const form = await request.formData();
    const jsonlText = String(form.get('jsonlText') ?? '');
    if (!jsonlText.trim()) {
      return fail(400, { ok: false, error: 'Missing JSONL import text.', values: { jsonlText } });
    }
    const result = await importFeedbackReceiptsFromJsonlText(jsonlText);
    return {
      ok: true,
      importedCount: result.importedCount
    };
  }
};
