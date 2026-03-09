import { loadWikiRevisionMonitor } from '$lib/server/wikiRevisionMonitor';

export async function load({ url }: { url: URL }) {
  const packId = url.searchParams.get('pack') || 'wiki_revision_contested_v2';
  const runId = url.searchParams.get('run');
  const articleId = url.searchParams.get('article');
  try {
    const payload = await loadWikiRevisionMonitor({ packId, runId, articleId });
    return { payload, error: null as string | null };
  } catch (e) {
    return {
      payload: {
        db_path: '',
        packs: [],
        selected_pack_id: packId,
        runs: [],
        selected_run_id: runId,
        summary: null,
        selected_article_id: articleId,
        selected_graph: null
      },
      error: e instanceof Error ? e.message : String(e)
    };
  }
}
