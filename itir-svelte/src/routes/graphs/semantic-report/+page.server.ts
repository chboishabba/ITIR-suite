import { fail, redirect } from '@sveltejs/kit';
import { listSemanticCorpora, loadSemanticComparison, loadSemanticReport } from '$lib/server/semanticReport';
import {
  buildCorrectionRecord,
  CorrectionValidationError,
  parseCorrectionForm,
  readCorrectionRecords,
  submitCorrectionRecord
} from '$lib/server/semantic-report/corrections';

export async function load({ url }: { url: URL }) {
  const source = (url.searchParams.get('source') || 'gwb').toLowerCase();
  const available = listSemanticCorpora();
  try {
    const [payload, comparison] = await Promise.all([loadSemanticReport(source), loadSemanticComparison()]);
    const corrections = await readCorrectionRecords(source, payload.report?.run_id);
    return {
      ...payload,
      comparison,
      graphGate: comparison.graphGate,
      semanticGraph: comparison.semanticGraph,
      tokenArcDebug: payload.tokenArcDebug,
      corrections,
      available,
      error: null as string | null
    };
  } catch (e) {
    return {
      source,
      label: available.find((item) => item.key === source)?.label ?? source,
      report: null,
      comparison: null,
      graphGate: null,
      semanticGraph: null,
      tokenArcDebug: { events: [], unavailableReason: null },
      corrections: [],
      available,
      error: e instanceof Error ? e.message : String(e)
    };
  }
}

export const actions = {
  submitCorrection: async ({ request, url }: { request: Request; url: URL }) => {
    try {
      const fields = parseCorrectionForm(await request.formData());
      const record = buildCorrectionRecord(fields);
      await submitCorrectionRecord(record);
      const next = new URL(url);
      next.searchParams.set('source', fields.source);
      next.searchParams.set('submitted', '1');
      throw redirect(303, next.toString());
    } catch (error) {
      if (error instanceof CorrectionValidationError) {
        return fail(400, { ok: false, error: error.message });
      }
      throw error;
    }
  }
};
