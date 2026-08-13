import type { PageServerLoad } from './$types';
import {
  loadArchiveNormalizedArtifact,
  loadCaptureNormalizedArtifact,
  loadConversationNormalizedArtifact,
  loadFactReviewNormalizedArtifact,
  loadResearchNormalizedArtifact,
  loadSbNormalizedArtifact,
  type NormalizedArtifactRef,
  type SuiteNormalizedArtifact
} from '$lib/server/normalizedArtifacts';
import {
  summarizeNormalizedArtifactConformance,
  type NormalizedArtifactConformanceStatus
} from '$lib/server/normalizedArtifactConformance';

type NormalizedArtifactCard = NormalizedArtifactRef & {
  conformance: NormalizedArtifactConformanceStatus;
};

function withConformance(ref: NormalizedArtifactRef | null): NormalizedArtifactCard | null {
  if (!ref) return null;
  return {
    ...ref,
    conformance: summarizeNormalizedArtifactConformance(ref.artifact as SuiteNormalizedArtifact | null)
  };
}

export const load: PageServerLoad = async ({ url }) => {
  const workflowKind = (url.searchParams.get('workflow') || 'au_semantic').trim();
  const workflowRunId = (url.searchParams.get('workflowRunId') || '').trim() || null;
  const sourceLabel = (url.searchParams.get('sourceLabel') || '').trim() || null;
  const sbDate = (url.searchParams.get('sbDate') || '').trim() || null;
  const archiveArtifact = (url.searchParams.get('archiveArtifact') || '').trim() || null;
  const captureArtifact = (url.searchParams.get('captureArtifact') || '').trim() || null;
  const researchArtifact = (url.searchParams.get('researchArtifact') || '').trim() || null;
  const conversationArtifact = (url.searchParams.get('conversationArtifact') || '').trim() || null;

  const [reviewArtifact, stateArtifact, archiveArtifactRef, captureArtifactRef, researchArtifactRef, conversationArtifactRef] = await Promise.all([
    loadFactReviewNormalizedArtifact(workflowKind, workflowRunId, sourceLabel),
    loadSbNormalizedArtifact(sbDate),
    loadArchiveNormalizedArtifact(archiveArtifact),
    loadCaptureNormalizedArtifact(captureArtifact),
    loadResearchNormalizedArtifact(researchArtifact),
    loadConversationNormalizedArtifact(conversationArtifact)
  ]);

  return {
    workflowKind,
    workflowRunId,
    sourceLabel,
    sbDate,
    archiveArtifact,
    captureArtifact,
    researchArtifact,
    conversationArtifact,
    reviewArtifact: withConformance(reviewArtifact),
    stateArtifact: withConformance(stateArtifact),
    archiveArtifactRef: withConformance(archiveArtifactRef),
    captureArtifactRef: withConformance(captureArtifactRef),
    researchArtifactRef: withConformance(researchArtifactRef),
    conversationArtifactRef: withConformance(conversationArtifactRef)
  };
};
