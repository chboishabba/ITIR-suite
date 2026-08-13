import path from 'node:path';

import type { WikiTimelineAooPayload } from './types';
import { normalizePayloadObject } from './normalize';
import { isHcaCanonicalRelPath, maybeOverlayHcaPayload } from './hca_overlay';
import { fileExists, loadFromDbCandidates, resolveItirDbPath } from './runtime';

function timelineSuffixCandidates(relPath: string): string[] {
  const base = path.basename(relPath);
  const candidates = new Set<string>([base]);
  if (base.endsWith('_aoo.json')) {
    candidates.add(`${base.slice(0, -'_aoo.json'.length)}.json`);
  }
  return Array.from(candidates).filter(Boolean);
}

export async function loadWikiTimelineAoo(repoRoot: string, relPath: string): Promise<WikiTimelineAooPayload> {
  const dbPath = resolveItirDbPath(repoRoot);
  const suffixes = timelineSuffixCandidates(relPath);

  if (await fileExists(dbPath)) {
    try {
      const raw = await loadFromDbCandidates(repoRoot, dbPath, suffixes);
      if (raw && typeof raw === 'object') {
        const payload = normalizePayloadObject({ ...(raw as any), __loaded_from_db: true });
        if (isHcaCanonicalRelPath(relPath)) {
          return maybeOverlayHcaPayload(repoRoot, relPath, payload);
        }
        return payload;
      }
    } catch {
      // fall through to error
    }
  }

  throw new Error(
    [
      'No AAO payload found in the canonical store.',
      `DB path checked: ${dbPath}`,
      `timeline suffix candidates: ${suffixes.join(', ')}`,
      'Fix: rerun wiki_timeline_aoo_extract with DB persistence, or set ITIR_DB_PATH to the canonical sqlite path.',
    ].join(' '),
  );
}
