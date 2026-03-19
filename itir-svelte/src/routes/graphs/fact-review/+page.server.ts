import type { PageServerLoad } from './$types';
import { loadFactReviewAcceptance, loadFactReviewWorkbench, listFactReviewSources } from '$lib/server/factReview';

export const load: PageServerLoad = async ({ url }) => {
  const workflowKind = (url.searchParams.get('workflow') || 'transcript_semantic').trim();
  const workflowRunId = (url.searchParams.get('workflowRunId') || '').trim() || null;
  const sourceLabel = (url.searchParams.get('sourceLabel') || '').trim() || null;
  const view = (url.searchParams.get('view') || 'intake_triage').trim();
  const wave = (url.searchParams.get('wave') || 'wave1_legal').trim();
  try {
    const [workbench, acceptance, sources] = await Promise.all([
      loadFactReviewWorkbench({
        workflowKind,
        workflowRunId,
        sourceLabel
      }),
      loadFactReviewAcceptance(
        {
          workflowKind,
          workflowRunId,
          sourceLabel
        },
        {
          wave,
          fixtureKind: 'unknown'
        }
      ),
      listFactReviewSources(workflowKind)
    ]);
    return {
      workflowKind,
      workflowRunId,
      sourceLabel,
      view,
      wave,
      workbench,
      acceptance,
      sources,
      error: null as string | null
    };
  } catch (error) {
    return {
      workflowKind,
      workflowRunId,
      sourceLabel,
      view,
      wave,
      workbench: null,
      acceptance: null,
      sources: [],
      error: error instanceof Error ? error.message : String(error)
    };
  }
};
