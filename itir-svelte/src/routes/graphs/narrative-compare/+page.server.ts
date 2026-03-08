import { loadNarrativeComparison } from '$lib/server/narrativeCompare';

export async function load({ url }: { url: URL }) {
  const selectedFixture = (url.searchParams.get('fixture') || 'friendlyjordies_demo').trim() || 'friendlyjordies_demo';
  try {
    const payload = await loadNarrativeComparison(selectedFixture);
    return {
      selectedFixture,
      fixtureMeta: payload.fixture,
      comparison: payload.comparison,
      availableFixtures: payload.availableFixtures,
      error: null as string | null
    };
  } catch (e) {
    return {
      selectedFixture,
      fixtureMeta: null,
      comparison: null,
      availableFixtures: [{ key: 'friendlyjordies_demo', label: 'FriendlyJordies public-media demo' }],
      error: e instanceof Error ? e.message : String(e)
    };
  }
}
