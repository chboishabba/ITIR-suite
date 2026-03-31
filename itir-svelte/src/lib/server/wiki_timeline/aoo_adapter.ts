import path from 'node:path';

import type { WikiTimelineSourceKey } from '$lib/server/wikiTimeline';

import type { WikiTimelineAooPayload } from './types';
import { normalizePayloadObject } from './normalize';
import { isHcaCanonicalRelPath, maybeOverlayHcaPayload } from './hca_overlay';
import { fileExists, loadFromDbCandidates, resolveItirDbPath, runPythonJson } from './runtime';

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

export async function loadWikiTimelineAooSource(
  repoRoot: string,
  sourceKey: WikiTimelineSourceKey,
  opts?: { variant?: 'aoo' | 'aoo_all' }
): Promise<{ source: WikiTimelineSourceKey; relPath: string; timelineSuffix: string; payload: WikiTimelineAooPayload }> {
  const dbPath = resolveItirDbPath(repoRoot);
  const raw = await runPythonJson(repoRoot, [
    '--db-path',
    dbPath,
    '--source-key',
    sourceKey,
    '--projection',
    'raw',
    '--with-source-meta',
    '--source-variant',
    opts?.variant ?? 'aoo'
  ]);
  if (!raw || typeof raw !== 'object') {
    throw new Error(`No AAO payload found for source ${sourceKey} in ${dbPath}`);
  }
  const row = raw as { source?: string; rel_path?: string; timeline_suffix?: string; payload?: unknown };
  if (!row.payload || typeof row.payload !== 'object') {
    throw new Error(`AAO payload envelope missing payload for source ${sourceKey} in ${dbPath}`);
  }
  const relPath = typeof row.rel_path === 'string' ? row.rel_path : '';
  const payload = normalizePayloadObject({ ...(row.payload as any), __loaded_from_db: true });
  const finalPayload = isHcaCanonicalRelPath(relPath) ? await maybeOverlayHcaPayload(repoRoot, relPath, payload) : payload;
  return {
    source: sourceKey,
    relPath,
    timelineSuffix: typeof row.timeline_suffix === 'string' ? row.timeline_suffix : '',
    payload: finalPayload
  };
}
