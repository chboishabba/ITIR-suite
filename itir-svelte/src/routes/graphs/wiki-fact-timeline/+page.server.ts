import path from 'node:path';
import { existsSync } from 'node:fs';

import { resolveItirDbPath, runPythonJson } from '$lib/server/wiki_timeline/runtime';
import { normalizeWikiTimelineSourceKey } from '$lib/server/wikiTimeline';

function resolveRepoRoot(): string {
  const candidates = [path.resolve('.'), path.resolve('..')];
  for (const c of candidates) {
    if (existsSync(path.join(c, 'SensibLaw'))) return c;
  }
  return path.resolve('..');
}

export async function load({ url }: { url: URL }) {
  const repoRoot = resolveRepoRoot();
  const source = normalizeWikiTimelineSourceKey(url.searchParams.get('source'), 'hca');
  try {
    const dbPath = resolveItirDbPath(repoRoot);
    const projection = await runPythonJson(repoRoot, [
      '--db-path',
      dbPath,
      '--source-key',
      source,
      '--projection',
      'fact_timeline',
      '--with-source-meta'
    ]) as {
      source?: string;
      rel_path?: string;
      timeline_suffix?: string;
      payload?: {
        root_actor?: { label?: string; surname?: string };
        parser?: unknown;
        facts?: unknown[];
        propositions?: unknown[];
        proposition_links?: unknown[];
        diagnostics?: {
          event_count?: number;
          fact_row_source?: string;
          raw_fact_rows?: number;
          output_fact_rows?: number;
        };
      };
    } | null;
    const payload = projection?.payload;
    if (!projection || typeof projection !== 'object' || !payload || typeof payload !== 'object') {
      throw new Error(`No fact timeline projection found for source ${source} in ${dbPath}`);
    }

    return {
      payload: {
        root_actor: payload.root_actor ?? { label: '', surname: '' },
        parser: payload.parser ?? null,
        facts: Array.isArray(payload.facts) ? payload.facts : [],
        propositions: Array.isArray(payload.propositions) ? payload.propositions : [],
        proposition_links: Array.isArray(payload.proposition_links) ? payload.proposition_links : [],
        diagnostics: payload.diagnostics ?? {
          event_count: 0,
          fact_row_source: 'native_fact_timeline',
          raw_fact_rows: 0,
          output_fact_rows: 0
        }
      },
      relPath: typeof projection.rel_path === 'string' ? projection.rel_path : '',
      source,
      error: null as string | null
    };
  } catch (e) {
    return {
      payload: {
        root_actor: { label: '', surname: '' },
        parser: null,
        facts: [],
        propositions: [],
        proposition_links: [],
        diagnostics: {
          event_count: 0,
          fact_row_source: 'native_fact_timeline',
          raw_fact_rows: 0,
          output_fact_rows: 0
        }
      },
      relPath: '',
      source,
      error: e instanceof Error ? e.message : String(e)
    };
  }
}
