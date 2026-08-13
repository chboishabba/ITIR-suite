import { eventEntityObjects, evidenceLabelsFromEvent, lensLabelsForEvent, numericMentionsForEvent, sourceLabelsForEvent, stepEntityObjects, timeKeyForEvent, uniqueStrings } from './graph';

export function keyFromNodeId(id: string): { kind: string; key: string } {
  const m = /^([a-z]+):(.+)$/.exec(id);
  if (!m) return { kind: 'other', key: id };
  const kind = m[1] ?? 'other';
  const key = m[2] ?? id;
  return { kind, key };
}

export function eventMatchesNode(
  e: any,
  nodeId: string,
  payload: any,
  missingRequesterEventIdSet: Set<string>,
): boolean {
  if (!nodeId) return false;
  if (nodeId.startsWith('act:')) return nodeId === `act:${e.event_id}`;

  if (nodeId.startsWith('sub:')) {
    const key = nodeId.slice('sub:'.length);
    const stepSubs = Array.isArray((e as any).steps)
      ? (e as any).steps.flatMap((s: any) => (Array.isArray(s?.subjects) ? s.subjects : []))
      : [];
    if (stepSubs.length) return stepSubs.some((x: any) => String(x) === key);
    return (e.actors ?? []).some((a: any) => (a.role ?? '') !== 'requester' && (a.resolved ?? a.label) === key);
  }
  if (nodeId.startsWith('req:')) {
    const key = nodeId.slice('req:'.length);
    if (key === 'missing') return missingRequesterEventIdSet.has(String((e as any)?.event_id ?? ''));
    return (e.actors ?? []).some((a: any) => (a.role ?? '') === 'requester' && (a.resolved ?? a.label) === key);
  }
  if (nodeId.startsWith('obj:')) {
    const key = nodeId.slice('obj:'.length);
    const stepObjs = Array.isArray((e as any).steps)
      ? (e as any).steps.flatMap((s: any) => stepEntityObjects(s))
      : [];
    if (stepObjs.length) return stepObjs.some((x: any) => String(x) === key);
    return eventEntityObjects(e).some((x: any) => String(x) === key);
  }
  if (nodeId.startsWith('num:')) {
    const key = nodeId.slice('num:'.length);
    return numericMentionsForEvent(e).some((m: any) => m.key === key);
  }
  if (nodeId.startsWith('evd:')) {
    const key = nodeId.slice('evd:'.length);
    return evidenceLabelsFromEvent(e).includes(key);
  }
  if (nodeId.startsWith('src:')) {
    const key = nodeId.slice('src:'.length);
    return sourceLabelsForEvent(e, payload).includes(key);
  }
  if (nodeId.startsWith('lens:')) {
    const key = nodeId.slice('lens:'.length);
    return lensLabelsForEvent(e, payload).includes(key);
  }

  if (nodeId.startsWith('time:y:')) {
    const key = nodeId.slice('time:y:'.length);
    return String(e.anchor?.year ?? 0) === key;
  }
  if (nodeId.startsWith('time:m:')) {
    const key = nodeId.slice('time:m:'.length);
    const y = String(e.anchor?.year ?? 0);
    const m = e.anchor?.month ?? null;
    const ym = m ? `${y}-${String(m).padStart(2, '0')}` : y;
    return ym === key;
  }
  if (nodeId.startsWith('time:d:')) {
    const key = nodeId.slice('time:d:'.length);
    const ymd = timeKeyForEvent(e, 'day');
    return ymd === key;
  }

  if (nodeId.startsWith('pur:')) return nodeId === `pur:${e.event_id}`;
  return false;
}

export function highlightParts(text: string, needle: string): Array<{ s: string; hit: boolean }> {
  const t = String(text ?? '');
  const n = String(needle ?? '').trim();
  if (!n) return [{ s: t, hit: false }];
  const lower = t.toLowerCase();
  const nl = n.toLowerCase();
  const out: Array<{ s: string; hit: boolean }> = [];
  let i = 0;
  while (i < t.length) {
    const j = lower.indexOf(nl, i);
    if (j < 0) {
      out.push({ s: t.slice(i), hit: false });
      break;
    }
    if (j > i) out.push({ s: t.slice(i, j), hit: false });
    out.push({ s: t.slice(j, j + n.length), hit: true });
    i = j + n.length;
  }
  return out.length ? out : [{ s: t, hit: false }];
}

export function top(map: Map<string, number>, limit: number): Array<[string, number]> {
  return Array.from(map.entries())
    .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
    .slice(0, limit);
}

export function countLabels(events: any[], payload: any): {
  sources: Map<string, number>;
  lenses: Map<string, number>;
  evidence: Map<string, number>;
} {
  const sourceCount = new Map<string, number>();
  const lensCount = new Map<string, number>();
  const evidenceCount = new Map<string, number>();
  for (const e of events) {
    for (const src of sourceLabelsForEvent(e, payload)) sourceCount.set(src, (sourceCount.get(src) ?? 0) + 1);
    for (const lens of lensLabelsForEvent(e, payload)) lensCount.set(lens, (lensCount.get(lens) ?? 0) + 1);
    for (const ev of evidenceLabelsFromEvent(e)) evidenceCount.set(ev, (evidenceCount.get(ev) ?? 0) + 1);
  }
  return { sources: sourceCount, lenses: lensCount, evidence: evidenceCount };
}

export function defaultFollowOrder(): string[] {
  return ['wikipedia', 'wiki_connector', 'austlii', 'jade', 'source_document', 'source_pdf'];
}

export function requesterFlags(events: any[], missingRequesterEventIdSet: Set<string>): {
  requestSignalEvents: number;
  requesterEvents: number;
  missingRequesterEventIds: string[];
} {
  const missingRequesterEventIds: string[] = [];
  let requestSignalEvents = 0;
  let requesterEvents = 0;
  for (const e of events ?? []) {
    const eventId = String((e as any)?.event_id ?? '');
    const hasRequester = hasRequesterActor(e);
    const missingRequester = eventId ? missingRequesterEventIdSet.has(eventId) : false;
    if (hasRequester) requesterEvents += 1;
    if (hasRequester || missingRequester) requestSignalEvents += 1;
    if (missingRequester && eventId) missingRequesterEventIds.push(eventId);
  }
  return { requestSignalEvents, requesterEvents, missingRequesterEventIds };
}

export function hasRequesterActor(e: any): boolean {
  return (e?.actors ?? []).some((a: any) => {
    if ((a?.role ?? '') !== 'requester') return false;
    return Boolean(String(a?.resolved ?? a?.label ?? '').trim());
  });
}
