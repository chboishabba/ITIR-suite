import type { PageServerLoad } from './$types';
import { loadOpenRecallCaptures, loadOpenRecallRuns, loadOpenRecallSummary } from '$lib/server/corpora';

export const load: PageServerLoad = async ({ url }) => {
  const importRunId = (url.searchParams.get('importRunId') || '').trim() || null;
  const appName = (url.searchParams.get('app') || '').trim() || null;
  const date = (url.searchParams.get('date') || '').trim() || null;
  const q = (url.searchParams.get('q') || '').trim() || null;
  const [runs, summary, captures] = await Promise.all([
    loadOpenRecallRuns().catch(() => []),
    loadOpenRecallSummary({ importRunId, appName, date }).catch(() => null),
    loadOpenRecallCaptures({ importRunId, appName, date, textQuery: q, limit: 120 }).catch(() => [])
  ]);
  return {
    importRunId,
    appName,
    date,
    q: q ?? '',
    runs,
    summary,
    captures
  };
};
