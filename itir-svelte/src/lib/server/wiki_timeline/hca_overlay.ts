import fs from 'node:fs/promises';
import path from 'node:path';

import type { AooEvent, WikiTimelineAooPayload } from './types';
import { fileExists } from './runtime';
import { normalizePayloadObject } from './normalize';

function isObj(v: unknown): v is Record<string, unknown> {
  return Boolean(v) && typeof v === 'object';
}

function isMeaningfulActorList(value: unknown): boolean {
  return Array.isArray(value) && value.some((row) => isObj(row) && String((row as any).resolved ?? (row as any).label ?? '').trim());
}

function isMeaningfulObjectList(value: unknown): boolean {
  return Array.isArray(value) && value.some((row) => isObj(row) && String((row as any).title ?? '').trim());
}

export function needsHcaEventOverlay(events: AooEvent[]): boolean {
  if (!events.length) return true;
  const actorful = events.filter((e) => isMeaningfulActorList(e.actors)).length;
  const objectful = events.filter((e) => isMeaningfulObjectList(e.objects)).length;
  return actorful === 0 || objectful < Math.max(1, Math.floor(events.length * 0.5));
}

export function isHcaCanonicalRelPath(relPath: string): boolean {
  return path.basename(relPath) === 'wiki_timeline_hca_s942025_aoo.json';
}

export async function maybeOverlayHcaPayload(
  repoRoot: string,
  relPath: string,
  basePayload: WikiTimelineAooPayload,
): Promise<WikiTimelineAooPayload> {
  if (!isHcaCanonicalRelPath(relPath)) return basePayload;
  if (!needsHcaEventOverlay(basePayload.events)) return basePayload;

  const richPath = path.join(
    repoRoot,
    'SensibLaw',
    'demo',
    'ingest',
    'hca_case_s942025',
    'graph',
    'wiki_timeline_hca_s942025_aoo.json',
  );
  if (!(await fileExists(richPath))) return basePayload;

  try {
    const raw = JSON.parse(await fs.readFile(richPath, 'utf8'));
    const richPayload = normalizePayloadObject(raw);
    if (!richPayload.events.length) return basePayload;
    return {
      ...richPayload,
      source_entity: basePayload.source_entity ?? richPayload.source_entity,
      extraction_record: basePayload.extraction_record ?? richPayload.extraction_record,
      extraction_profile: basePayload.extraction_profile ?? richPayload.extraction_profile,
      requester_coverage: basePayload.requester_coverage ?? richPayload.requester_coverage,
      source_timeline: basePayload.source_timeline ?? richPayload.source_timeline,
      generated_at: basePayload.generated_at ?? richPayload.generated_at,
      run_id: basePayload.run_id ?? richPayload.run_id,
      __loaded_from_db: basePayload.__loaded_from_db || richPayload.__loaded_from_db,
    };
  } catch {
    return basePayload;
  }
}
