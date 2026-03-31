export {
  canonicalUnitToken,
  compareNumericLaneEntries,
  eventNumericObjects,
  numericKey,
  numericLabelFromKey,
  numericMentionsForEvent,
  numericMentionsFromValues,
  numericSortUnitFromKey,
  numericSortValueFromKey,
  normalizeNumericMention,
  parseNumericValueToken,
  scientificFromScaled,
  stepNumericObjects,
  type NumericMention,
} from './numeric';

export function pad2(n: number): string {
  return String(n).padStart(2, '0');
}

export function uniqueStrings(xs: any[]): string[] {
  const out = new Set<string>();
  for (const x of xs ?? []) {
    const s = String(x ?? '').trim();
    if (s) out.add(s);
  }
  return Array.from(out);
}

export function collapseWhitespace(raw: string): string {
  let out = '';
  let prevSpace = true;
  for (const ch of String(raw ?? '')) {
    const isSpace = ch.trim() === '';
    if (isSpace) {
      if (!prevSpace) out += ' ';
    } else {
      out += ch;
    }
    prevSpace = isSpace;
  }
  return out.trim();
}

export function actionLabel(action: string | null | undefined, negation?: { kind?: string | null }): string {
  const base = String(action ?? '').trim();
  if (!base) return '(no action matched)';
  if (String(negation?.kind ?? '').toLowerCase() === 'not') return `not_${base}`;
  return base;
}

export function stepEntityObjects(step: any): string[] {
  if (Array.isArray(step?.entity_objects)) return step.entity_objects.map((x: any) => String(x)).filter(Boolean);
  if (Array.isArray(step?.objects)) return step.objects.map((x: any) => String(x)).filter(Boolean);
  return [];
}

export function eventEntityObjects(e: any): string[] {
  if (Array.isArray(e?.entity_objects)) return e.entity_objects.map((x: any) => String(x)).filter(Boolean);
  if (Array.isArray(e?.objects)) return e.objects.map((o: any) => String(o?.title ?? '')).filter(Boolean);
  return [];
}

export function collectFollowProviders(rows: any[]): string[] {
  const out: string[] = [];
  for (const row of rows ?? []) {
    if (!row || typeof row !== 'object') continue;
    if (Array.isArray((row as any).follower_order)) {
      for (const x of (row as any).follower_order) out.push(String(x ?? '').trim());
    }
    if (Array.isArray((row as any).follow)) {
      for (const h of (row as any).follow) {
        const p = String((h as any)?.provider ?? '').trim();
        if (p) out.push(p);
      }
    }
  }
  return uniqueStrings(out);
}

export function evidenceLabelsFromEvent(e: any): string[] {
  const citationTexts = Array.isArray(e?.citations)
    ? (e.citations as any[])
        .map((c: any) => String(c?.text ?? '').trim())
        .filter(Boolean)
    : [];
  const slRefTexts = Array.isArray(e?.sl_references)
    ? (e.sl_references as any[])
        .map((r: any) => {
          const t = String(r?.text ?? '').trim();
          if (t) return t;
          const auth = String(r?.authority ?? '').trim();
          const ref = String(r?.ref_value ?? '').trim();
          return `${auth} ${ref}`.trim();
        })
        .filter(Boolean)
    : [];
  return uniqueStrings([...citationTexts, ...slRefTexts]);
}

export function sourceLabelsForEvent(e: any, payload: any): string[] {
  const out: string[] = [];
  const src = payload?.source_entity;
  if (src && typeof src === 'object') {
    const title = String(src.title ?? '').trim();
    const typ = String(src.type ?? '').trim();
    if (title && typ) out.push(`source:${title} (${typ})`);
    else if (title) out.push(`source:${title}`);
    else if (typ) out.push(`source_type:${typ}`);
  }
  const extraction = payload?.extraction_record;
  if (extraction && typeof extraction === 'object') {
    const parserVersion = String(extraction.parser_version ?? '').trim();
    if (parserVersion) out.push(`parser:${parserVersion}`);
  }
  const timeline = payload?.source_timeline;
  if (timeline && typeof timeline === 'object') {
    const p = String((timeline as any)?.path ?? '').trim();
    if (p) out.push(`timeline:${p.split('/').slice(-2).join('/')}`);
  }

  if (e && typeof e === 'object') {
    const actSrc = String((e as any)?.action_meta?.source ?? '').trim();
    if (actSrc) out.push(`action_meta:${actSrc}`);

    if (Array.isArray((e as any)?.actors)) {
      for (const a of (e as any).actors) {
        const s = String(a?.source ?? '').trim();
        if (s) out.push(`actor_source:${s}`);
      }
    }
    if (Array.isArray((e as any)?.objects)) {
      for (const o of (e as any).objects) {
        const s = String(o?.source ?? '').trim();
        if (s) out.push(`object_source:${s}`);
      }
    }
    if (Array.isArray((e as any)?.steps)) {
      for (const step of (e as any).steps) {
        const s = String(step?.action_meta?.source ?? '').trim();
        if (s) out.push(`step_action_meta:${s}`);
      }
    }
  }

  if (Array.isArray(e?.citations)) {
    for (const c of e.citations) {
      const kind = String((c as any)?.kind ?? '').trim().toLowerCase();
      const text = String((c as any)?.text ?? '').trim();
      if (kind === 'source_row' && text) out.push(`source_row:${text}`);
      const follow = Array.isArray((c as any)?.follow) ? (c as any).follow : [];
      for (const h of follow) {
        const url = String((h as any)?.url ?? '').trim();
        if (!url) continue;
        try {
          const host = new URL(url).host;
          if (host) out.push(`host:${host}`);
        } catch {
          // ignore invalid URLs
        }
      }
    }
  }
  const citationProviders = Array.isArray(e?.citations) ? collectFollowProviders(e.citations) : [];
  const slRefProviders = Array.isArray(e?.sl_references) ? collectFollowProviders(e.sl_references) : [];
  for (const p of uniqueStrings([...citationProviders, ...slRefProviders])) out.push(`provider:${p}`);
  return uniqueStrings(out);
}

export function lensLabelsForEvent(e: any, payload: any): string[] {
  const out: string[] = [];
  const profile = payload?.extraction_profile;
  if (profile && typeof profile === 'object') {
    const profileId = String(profile.profile_id ?? '').trim();
    const profileVersion = String(profile.profile_version ?? '').trim();
    const predicateClassifier = String(profile.predicate_classifier ?? '').trim();
    if (profileId && profileVersion) out.push(`profile:${profileId}@${profileVersion}`);
    else if (profileId) out.push(`profile:${profileId}`);
    if (predicateClassifier) out.push(`classifier:${predicateClassifier}`);
  }
  if ((e as any)?.claim_bearing === true) out.push('claim:claim_bearing');
  if (Array.isArray((e as any)?.steps)) {
    const claimBearingSteps = (e as any).steps.filter((s: any) => s?.claim_bearing === true).length;
    if (claimBearingSteps > 0) out.push(`claim_steps:${claimBearingSteps}`);
  }
  if (Array.isArray((e as any)?.sl_references)) {
    for (const r of (e as any).sl_references) {
      const lane = String((r as any)?.lane ?? '').trim();
      if (lane) out.push(`sl_lane:${lane}`);
    }
  }
  const markers = (e as any)?.legal_section_markers;
  if (markers && typeof markers === 'object' && Array.isArray(markers.sl_reference_lanes)) {
    for (const lane of markers.sl_reference_lanes) {
      const x = String(lane ?? '').trim();
      if (x) out.push(`sl_lane:${x}`);
    }
  }
  if (Array.isArray((e as any)?.timeline_facts) && (e as any).timeline_facts.length) out.push('fact:timeline');
  return uniqueStrings(out);
}

export function hasRequesterActor(e: any): boolean {
  return (e?.actors ?? []).some((a: any) => {
    if ((a?.role ?? '') !== 'requester') return false;
    return Boolean(String(a?.resolved ?? a?.label ?? '').trim());
  });
}

export function timeKeyForEvent(e: { anchor: { year: number; month: number | null; day: number | null } }, g: 'year' | 'month' | 'day'): string {
  const y = String(e.anchor.year || 0);
  if (g === 'year') return y;
  const m = e.anchor.month ?? null;
  if (!m) return y;
  const ym = `${y}-${pad2(m)}`;
  if (g === 'month') return ym;
  const d = e.anchor.day ?? null;
  if (!d) return ym;
  return `${ym}-${pad2(d)}`;
}

export function factAnchorKey(a: any): string {
  const y = String(a?.year ?? 0);
  const m = typeof a?.month === 'number' ? pad2(a.month) : '99';
  const d = typeof a?.day === 'number' ? pad2(a.day) : '99';
  return `${y}-${m}-${d}`;
}
