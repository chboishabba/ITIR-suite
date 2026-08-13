import type { PageServerLoad } from './$types';
import { loadFactReviewAcceptance, loadFactReviewDemoBundle, loadFactReviewWorkbench, listFactReviewSources } from '$lib/server/factReview';
import { classifyFactReviewErrorMessage } from '$lib/server/factReviewCli.js';

export const load: PageServerLoad = async ({ url }) => {
  const workflowKind = (url.searchParams.get('workflow') || 'transcript_semantic').trim();
  const workflowRunId = (url.searchParams.get('workflowRunId') || '').trim() || null;
  const sourceLabel = (url.searchParams.get('sourceLabel') || '').trim() || null;
  const view = (url.searchParams.get('view') || 'intake_triage').trim();
  const wave = (url.searchParams.get('wave') || 'wave1_legal').trim();
  try {
    const workbench = await loadFactReviewWorkbench({
      workflowKind,
      workflowRunId,
      sourceLabel
    });
    const [acceptanceResult, sourcesResult, demoBundleResult] = await Promise.allSettled([
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
      listFactReviewSources(workflowKind),
      workflowKind === 'au_semantic'
        ? loadFactReviewDemoBundle(
            {
              workflowKind,
              workflowRunId,
              sourceLabel
            },
            {
              wave,
              fixtureKind: 'unknown'
            }
          )
        : Promise.resolve(null)
    ]);
    const acceptance = acceptanceResult.status === 'fulfilled' ? acceptanceResult.value : null;
    const sources = sourcesResult.status === 'fulfilled' ? sourcesResult.value : [];
    const demoBundle = demoBundleResult.status === 'fulfilled' ? demoBundleResult.value : null;
    const resolvedWorkflowRunId =
      workflowRunId ??
      workbench.reopen_navigation?.query?.workflow_run_id ??
      workbench.reopen_navigation?.current?.workflow_run_id ??
      workbench.run.workflow_link?.workflow_run_id ??
      null;
    const resolvedSourceLabel =
      sourceLabel ??
      workbench.reopen_navigation?.query?.source_label ??
      workbench.reopen_navigation?.current?.source_label ??
      workbench.run.source_label ??
      null;
    return {
      workflowKind,
      workflowRunId: resolvedWorkflowRunId,
      sourceLabel: resolvedSourceLabel,
      view,
      wave,
      workbench,
      demoBundle,
      acceptance,
      sources,
      error: null as string | null,
      errorKind: null as string | null,
      errorTitle: null as string | null
    };
  } catch (error) {
    const info = classifyFactReviewErrorMessage(error instanceof Error ? error.message : String(error));
    return {
      workflowKind,
      workflowRunId,
      sourceLabel,
      view,
      wave,
      workbench: null,
      demoBundle: null,
      acceptance: null,
      sources: [],
      error: info.detail,
      errorKind: info.kind,
      errorTitle: info.title
    };
  }
};
