import path from 'node:path';
import { existsSync } from 'node:fs';
import fs from 'node:fs/promises';

import { loadWikiTimelineAoo } from '$lib/server/wikiTimelineAoo';

const GWB_REL = path.join('SensibLaw', '.cache_local', 'wiki_timeline_gwb.json');
const GWB_PUBLIC_BIOS_REL = path.join(
  'SensibLaw',
  'demo',
  'ingest',
  'gwb',
  'public_bios_v1',
  'wiki_timeline_gwb_public_bios_v1.json'
);
const GWB_CORPUS_REL = path.join('SensibLaw', 'demo', 'ingest', 'gwb', 'corpus_v1', 'wiki_timeline_gwb_corpus_v1.json');
const HCA_REL = path.join('SensibLaw', '.cache_local', 'wiki_timeline_hca_s942025_aoo.json');
const LEGAL_REL = path.join(
  'SensibLaw',
  'demo',
  'ingest',
  'legal_principles_au_v1',
  'wiki_timeline_legal_principles_au_v1.json'
);
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
  gwb_corpus_v1: GWB_CORPUS_REL,
  hca: HCA_REL,
  legal: LEGAL_REL,
  legal_follow: LEGAL_FOLLOW_REL
} as const;

type CorpusDoc = {
  relPath: string;
  name: string;
  bytes: number;
  ext: string;
};

function resolveRepoRoot(): string {
  const candidates = [path.resolve('.'), path.resolve('..')];
  for (const c of candidates) {
    if (existsSync(path.join(c, 'SensibLaw'))) return c;
  }
  return path.resolve('..');
}

async function listCorpusDocs(repoRoot: string, source: string): Promise<CorpusDoc[]> {
  // For now, only the GWB demo ingest has local corpus artifacts (PDF/EPUB/etc).
  if (source !== 'gwb' && source !== 'gwb_public_bios_v1' && source !== 'gwb_corpus_v1') return [];
  const baseRel = path.join('SensibLaw', 'demo', 'ingest', 'gwb');
  const baseAbs = path.join(repoRoot, baseRel);

  const exts = new Set(['.pdf', '.epub', '.html', '.htm']);
  const out: CorpusDoc[] = [];

  async function walk(dirAbs: string, dirRelFromRepo: string): Promise<void> {
    let entries: Array<import('node:fs').Dirent> = [];
    try {
      entries = await fs.readdir(dirAbs, { withFileTypes: true });
    } catch {
      return;
    }
    for (const ent of entries) {
      // Skip huge raw trees we don't need right now.
      if (ent.isDirectory() && ent.name === 'raw') continue;
      const abs = path.join(dirAbs, ent.name);
      const rel = path.join(dirRelFromRepo, ent.name);
      if (ent.isDirectory()) {
        await walk(abs, rel);
        continue;
      }
      const ext = path.extname(ent.name).toLowerCase();
      if (!exts.has(ext)) continue;
      try {
        const st = await fs.stat(abs);
        out.push({ relPath: rel, name: ent.name, bytes: st.size, ext });
      } catch {
        // ignore stat failures
      }
    }
  }

  await walk(baseAbs, baseRel);
  out.sort((a, b) => a.relPath.localeCompare(b.relPath));
  return out;
}

export async function load({ url }: { url: URL }) {
  const repoRoot = resolveRepoRoot();
  const source = (url.searchParams.get('source') || 'gwb').toLowerCase();
  const rel = SOURCE_PATHS[source as keyof typeof SOURCE_PATHS] ?? GWB_REL;
  try {
    const payload = await loadWikiTimelineAoo(repoRoot, rel);
    const corpusDocs = await listCorpusDocs(repoRoot, source);
    return { payload, relPath: rel, source, corpusDocs, error: null as string | null };
  } catch (e) {
    return {
      payload: { root_actor: { label: '', surname: '' }, events: [] },
      relPath: rel,
      source,
      corpusDocs: [] as CorpusDoc[],
      error: e instanceof Error ? e.message : String(e)
    };
  }
}
