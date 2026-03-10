import { loadWikiRevisionMonitor } from '$lib/server/wikiRevisionMonitor';
import { wikiContestedReviewState } from '$lib/workbench/reviewState';

function computeStateReason(payload: any, hasError: boolean) {
  const summary = payload?.summary ?? {};
  const articles = summary?.articles ?? [];
  const selectedArticle = articles.find((row: any) => row.article_id === payload?.selected_article_id) ?? articles[0] ?? null;
  const packs = payload?.packs ?? [];
  const selectedPack = packs.find((row: any) => row.pack_id === payload?.selected_pack_id) ?? null;
  const graphSummary = payload?.selected_graph?.summary ?? selectedArticle?.contested_graph_summary ?? null;
  return wikiContestedReviewState({
    hasLoadError: hasError,
    selectedArticleStatus: String(selectedArticle?.status ?? '').toLowerCase(),
    packGraphEnabled: Boolean(selectedPack?.graph_enabled),
    selectedArticleExists: Boolean(selectedArticle),
    selectedArticleGraphAvailable: Boolean(selectedArticle?.contested_graph_available),
    hasGraphPayload: Boolean(graphSummary)
  });
}

export async function load({ url }: { url: URL }) {
  const packId = url.searchParams.get('pack') || 'wiki_revision_contested_v2';
  const runId = url.searchParams.get('run');
  const articleId = url.searchParams.get('article');
  try {
    const payload = await loadWikiRevisionMonitor({ packId, runId, articleId });
    return {
      payload,
      stateReason: computeStateReason(payload, false),
      error: null as string | null
    };
  } catch (e) {
    const payload = {
      db_path: '',
      packs: [],
      selected_pack_id: packId,
      runs: [],
      selected_run_id: runId,
      summary: null,
      selected_article_id: articleId,
      selected_graph: null
    };
    return {
      payload,
      stateReason: computeStateReason(payload, true),
      error: e instanceof Error ? e.message : String(e)
    };
  }
}
