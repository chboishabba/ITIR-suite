import { loadNarrativeComparison } from '$lib/server/narrativeCompare';

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
      error: e instanceof Error ? e.message : String(e)
    };
  }
}
