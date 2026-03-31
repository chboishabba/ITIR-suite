import path from 'node:path';
import { existsSync } from 'node:fs';

import { loadWikiTimelineSourceDb, normalizeWikiTimelineSourceKey } from '$lib/server/wikiTimeline';

function resolveRepoRoot(): string {
  const candidates = [path.resolve('.'), path.resolve('..')];
  for (const c of candidates) {
    if (existsSync(path.join(c, 'SensibLaw'))) return c;
  }
  return path.resolve('..');
}

export async function load({ url }: { url: URL }) {
  const repoRoot = resolveRepoRoot();
  const requestedSource = url.searchParams.get('source');
  const sourceKey = normalizeWikiTimelineSourceKey(requestedSource, 'gwb');
  try {
    const loaded = await loadWikiTimelineSourceDb(repoRoot, sourceKey, {
      dbEnv: process.env.ITIR_DB_PATH ?? null
    });
    return {
      payload: loaded.payload,
      relPath: loaded.relPath,
      source: loaded.source,
      error: null as string | null,
      mode: 'db' as const
    };
  } catch (e) {
    return {
      payload: { snapshot: { title: null, wiki: null, revid: null, source_url: null }, events: [] },
      relPath: '',
      source: sourceKey,
      error: e instanceof Error ? e.message : String(e),
      mode: 'db'
    };
  }
}
