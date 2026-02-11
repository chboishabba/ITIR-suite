import path from 'node:path';

import { loadWikiTimeline } from '$lib/server/wikiTimeline';

export async function load() {
  const repoRoot = path.resolve('..');
  const rel = path.join('SensibLaw', '.cache_local', 'wiki_timeline_gwb.json');
  try {
    const payload = await loadWikiTimeline(repoRoot, rel);
    return { payload, relPath: rel, error: null as string | null };
  } catch (e) {
    return {
      payload: { snapshot: { title: null, wiki: null, revid: null, source_url: null }, events: [] },
      relPath: rel,
      error: e instanceof Error ? e.message : String(e)
    };
  }
}

