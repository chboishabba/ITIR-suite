import path from 'node:path';
import { existsSync } from 'node:fs';

import { loadWikiTimeline } from '$lib/server/wikiTimeline';

const GWB_REL = path.join('SensibLaw', '.cache_local', 'wiki_timeline_gwb.json');
const HCA_REL = path.join('SensibLaw', '.cache_local', 'wiki_timeline_hca_s942025_aoo.json');
const LEGAL_REL = path.join('SensibLaw', 'demo', 'ingest', 'legal_principles_au_v1', 'wiki_timeline_legal_principles_au_v1.json');
const LEGAL_FOLLOW_REL = path.join(
  'SensibLaw',
  'demo',
  'ingest',
  'legal_principles_au_v1',
  'follow',
  'wiki_timeline_legal_principles_au_v1_follow.json'
);
const SOURCE_PATHS = { gwb: GWB_REL, hca: HCA_REL, legal: LEGAL_REL, legal_follow: LEGAL_FOLLOW_REL } as const;

function resolveRepoRoot(): string {
  const candidates = [path.resolve('.'), path.resolve('..')];
  for (const c of candidates) {
    if (existsSync(path.join(c, 'SensibLaw'))) return c;
  }
  return path.resolve('..');
}

export async function load({ url }: { url: URL }) {
  const repoRoot = resolveRepoRoot();
  const source = (url.searchParams.get('source') || 'gwb').toLowerCase();
  const rel = SOURCE_PATHS[source as keyof typeof SOURCE_PATHS] ?? GWB_REL;
  try {
    const payload = await loadWikiTimeline(repoRoot, rel);
    return { payload, relPath: rel, source, error: null as string | null };
  } catch (e) {
    return {
      payload: { snapshot: { title: null, wiki: null, revid: null, source_url: null }, events: [] },
      relPath: rel,
      source,
      error: e instanceof Error ? e.message : String(e)
    };
  }
}
