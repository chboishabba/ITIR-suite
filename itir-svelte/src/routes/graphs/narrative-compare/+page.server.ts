import { loadNarrativeComparison } from '$lib/server/narrativeCompare';
import { narrativeCompareReviewState } from '$lib/workbench/reviewState';

export async function load({ url }: { url: URL }) {
  const selectedFixture = (url.searchParams.get('fixture') || 'friendlyjordies_demo').trim() || 'friendlyjordies_demo';
  const threadId = (url.searchParams.get('threadId') || '').trim() || null;
  const threadTitle = (url.searchParams.get('threadTitle') || '').trim() || null;
  try {
    const payload = await loadNarrativeComparison(selectedFixture, { threadId, threadTitle });
    return {
      selectedFixture,
      threadId,
      threadTitle,
      fixtureMeta: payload.fixture,
      comparison: payload.comparison,
      availableFixtures: payload.availableFixtures,
      stateReason: narrativeCompareReviewState(null, (payload.comparison?.shared_propositions?.length ?? 0)
        + (payload.comparison?.disputed_propositions?.length ?? 0)
        + Object.values(payload.comparison?.source_only_propositions ?? {}).reduce((acc: number, rows: any) => acc + ((rows as any[])?.length ?? 0), 0)),
      error: null as string | null
    };
  } catch (e) {
    return {
      selectedFixture,
      threadId,
      threadTitle,
      fixtureMeta: null,
      comparison: null,
      availableFixtures: [{ key: 'friendlyjordies_demo', label: 'FriendlyJordies public-media demo' }],
      stateReason: narrativeCompareReviewState(e instanceof Error ? e.message : String(e), 0),
      error: e instanceof Error ? e.message : String(e)
    };
  }
}
