import path from 'node:path';
import { existsSync } from 'node:fs';
import fs from 'node:fs/promises';

import { normalizeWikiTimelineSourceKey } from '$lib/server/wikiTimeline';
import { loadWikiTimelineAooSource } from '$lib/server/wikiTimelineAoo';

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
  const source = normalizeWikiTimelineSourceKey(url.searchParams.get('source'), 'gwb');
  try {
    const loaded = await loadWikiTimelineAooSource(repoRoot, source, { variant: 'aoo_all' });
    const payload = loaded.payload;
    const corpusDocs = await listCorpusDocs(repoRoot, source);
    return { payload, relPath: loaded.relPath, source, corpusDocs, error: null as string | null };
  } catch (e) {
    return {
      payload: { root_actor: { label: '', surname: '' }, events: [] },
      relPath: '',
      source,
      corpusDocs: [] as CorpusDoc[],
      error: e instanceof Error ? e.message : String(e)
    };
  }
}
