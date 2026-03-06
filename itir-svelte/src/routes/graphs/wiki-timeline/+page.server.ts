import path from 'node:path';
import { existsSync } from 'node:fs';

import { loadWikiTimelineDb } from '$lib/server/wikiTimeline';

const GWB_REL = path.join('SensibLaw', '.cache_local', 'wiki_timeline_gwb.json');
const GWB_PUBLIC_BIOS_REL = path.join(
  'SensibLaw',
  'demo',
  'ingest',
  'gwb',
  'public_bios_v1',
  'wiki_timeline_gwb_public_bios_v1.json'
);
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
const SOURCE_PATHS = {
  gwb: GWB_REL,
  gwb_public_bios_v1: GWB_PUBLIC_BIOS_REL,
  hca: HCA_REL,
  legal: LEGAL_REL,
  legal_follow: LEGAL_FOLLOW_REL
} as const;

const TIMELINE_SUFFIX = {
  gwb: 'wiki_timeline_gwb.json',
  gwb_public_bios_v1: 'wiki_timeline_gwb_public_bios_v1.json',
  hca: 'wiki_timeline_hca_s942025_aoo.json',
  legal: 'wiki_timeline_legal_principles_au_v1.json',
  legal_follow: 'wiki_timeline_legal_principles_au_v1_follow.json'
} as const;

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
  const suffix = TIMELINE_SUFFIX[source as keyof typeof TIMELINE_SUFFIX] ?? TIMELINE_SUFFIX.gwb;
  try {
    const payload = await loadWikiTimelineDb(repoRoot, { dbEnv: process.env.ITIR_DB_PATH ?? null, timelineSuffix: suffix });
    return { payload, relPath: rel, source, error: null as string | null, mode: 'db' as const };
  } catch (e) {
    return {
      payload: { snapshot: { title: null, wiki: null, revid: null, source_url: null }, events: [] },
      relPath: rel,
      source,
      error: e instanceof Error ? e.message : String(e),
      mode: 'db'
    };
  }
}
