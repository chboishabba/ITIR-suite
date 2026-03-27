import type { PageServerLoad } from './$types';
import { loadMessengerMessages, loadMessengerRuns, loadMessengerSummary } from '$lib/server/corpora';

export const load: PageServerLoad = async ({ url }) => {
  const runId = (url.searchParams.get('runId') || '').trim() || null;
  const conversationHash = (url.searchParams.get('conversation') || '').trim() || null;
  const q = (url.searchParams.get('q') || '').trim() || null;
  const [runs, summary, messagePayload] = await Promise.all([
    loadMessengerRuns().catch(() => []),
    loadMessengerSummary(runId).catch(() => null),
    loadMessengerMessages({ runId, conversationHash, textQuery: q, limit: 150 }).catch(() => ({
      runId: null,
      messages: []
    }))
  ]);
  return {
    runId,
    conversationHash,
    q: q ?? '',
    runs,
    summary,
    activeRunId: messagePayload.runId,
    messages: messagePayload.messages
  };
};
