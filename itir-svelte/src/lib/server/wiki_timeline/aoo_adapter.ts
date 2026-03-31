import type { WikiTimelineSourceKey } from '$lib/server/wikiTimeline';

import type { WikiTimelineAooPayload } from './types';
import { normalizePayloadObject } from './normalize';
import { isHcaCanonicalRelPath, maybeOverlayHcaPayload } from './hca_overlay';
import { runPythonJson } from './runtime';

export async function loadWikiTimelineAoo(repoRoot: string, relPath: string): Promise<WikiTimelineAooPayload> {
  const raw = await runPythonJson(repoRoot, ['--rel-path', relPath, '--projection', 'raw']);
  if (!raw || typeof raw !== 'object') {
    throw new Error(`No AAO payload found in the canonical store for ${relPath}`);
  }
  const row = raw as { payload?: unknown };
  if (!row.payload || typeof row.payload !== 'object') {
    throw new Error(`AAO payload envelope missing payload for ${relPath}`);
  }
  const payload = normalizePayloadObject({ ...(row.payload as any), __loaded_from_db: true });
  return isHcaCanonicalRelPath(relPath) ? maybeOverlayHcaPayload(repoRoot, relPath, payload) : payload;
}

export async function loadWikiTimelineAooSource(
  repoRoot: string,
  sourceKey: WikiTimelineSourceKey,
  opts?: { variant?: 'aoo' | 'aoo_all' }
): Promise<{ source: WikiTimelineSourceKey; relPath: string; timelineSuffix: string; payload: WikiTimelineAooPayload }> {
  const raw = await runPythonJson(repoRoot, [
    '--source-key',
    sourceKey,
    '--projection',
    'raw',
    '--with-source-meta',
    '--source-variant',
    opts?.variant ?? 'aoo'
  ]);
  if (!raw || typeof raw !== 'object') {
    throw new Error(`No AAO payload found for source ${sourceKey}`);
  }
  const row = raw as { source?: string; rel_path?: string; timeline_suffix?: string; payload?: unknown };
  if (!row.payload || typeof row.payload !== 'object') {
    throw new Error(`AAO payload envelope missing payload for source ${sourceKey}`);
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
