export type NumericMention = { key: string; label: string };

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

const NUMERIC_UNITS = new Set([
  '%',
  'percent',
  'million',
  'billion',
  'trillion',
  'thousand',
  'hundred',
  'year',
  'years',
  'month',
  'months',
  'day',
  'days',
  'line',
  'lines',
  'point',
  'points',
  'dollar',
  'dollars',
  'usd',
  'aud',
  'eur',
  'gbp',
]);
const NUMERIC_SCALE_UNITS = new Set(['hundred', 'thousand', 'million', 'billion', 'trillion']);
const NUMERIC_CURRENCY_UNITS = new Set(['usd', 'aud', 'eur', 'gbp']);
const NUMERIC_SCALE_POW: Record<string, number> = { hundred: 2, thousand: 3, million: 6, billion: 9, trillion: 12 };

export function canonicalUnitToken(raw: string): string {
  const u = String(raw ?? '').toLowerCase();
  if (!u) return '';
  if (u === '%' || u === 'percentage' || u === 'percent') return 'percent';
  if (u === 'dollar' || u === 'dollars' || u === 'usd') return 'usd';
  if (u === 'years' || u === 'year') return 'year';
  if (u === 'months' || u === 'month') return 'month';
  if (u === 'days' || u === 'day') return 'day';
  if (u === 'lines' || u === 'line') return 'line';
  if (u === 'points' || u === 'point') return 'point';
  if (u === 'aud' || u === 'eur' || u === 'gbp') return u;
  return u;
}

export function scientificFromScaled(value: string, pow: number): string {
  const num = Number(value);
  if (!Number.isFinite(num)) return '';
  const scaled = num * Math.pow(10, pow);
  if (!Number.isFinite(scaled)) return '';
  if (scaled === 0) return '0';
  const exp = scaled.toExponential();
  const parts = exp.split('e');
  if (parts.length !== 2) return '';
  let mantissa = String(parts[0] ?? '');
  const exponent = Number.parseInt(String(parts[1] ?? ''), 10);
  if (!Number.isFinite(exponent)) return '';
  while (mantissa.includes('.') && mantissa.endsWith('0')) mantissa = mantissa.slice(0, -1);
  if (mantissa.endsWith('.')) mantissa = mantissa.slice(0, -1);
  return `${mantissa}e${exponent}`;
}

export function normalizeNumericMention(raw: string): string {
  const t = collapseWhitespace(String(raw ?? ''));
  if (!t) return '';
  const src = t.split(' ').filter(Boolean);
  const toks: string[] = [];
  for (let i = 0; i < src.length; i++) {
    const low = String(src[i] ?? '').toLowerCase();
    const next = i + 1 < src.length ? String(src[i + 1] ?? '').toLowerCase() : '';
    if (low === 'per' && next === 'cent') {
      toks.push('percent');
      i += 1;
    } else {
      toks.push(String(src[i] ?? ''));
    }
  }
  let currency = '';
  if (toks.length) {
    let first = String(toks[0] ?? '');
    const low = first.toLowerCase();
    if (low === '$') {
      currency = 'usd';
      toks.shift();
    } else if (low === 'us$') {
      currency = 'usd';
      toks.shift();
    } else if (low === 'a$') {
      currency = 'aud';
      toks.shift();
    } else if (low === '€') {
      currency = 'eur';
      toks.shift();
    } else if (low === '£') {
      currency = 'gbp';
      toks.shift();
    } else if (low === 'usd' || low === 'aud' || low === 'eur' || low === 'gbp') {
      currency = low;
      toks.shift();
    } else if (low.startsWith('$')) {
      currency = 'usd';
      first = first.slice(1);
      toks[0] = first;
    } else if (low.startsWith('us$')) {
      currency = 'usd';
      first = first.slice(3);
      toks[0] = first;
    } else if (low.startsWith('a$')) {
      currency = 'aud';
      first = first.slice(2);
      toks[0] = first;
    } else if (low.startsWith('€')) {
      currency = 'eur';
      first = first.slice(1);
      toks[0] = first;
    } else if (low.startsWith('£')) {
      currency = 'gbp';
      first = first.slice(1);
      toks[0] = first;
    }
  }
  if (!toks.length) return '';
  if (toks.length === 1) {
    const single = String(toks[0] ?? '');
    let j = 0;
    if (single[0] === '+' || single[0] === '-') j = 1;
    let seenDigit = false;
    let seenDot = false;
    for (; j < single.length; j++) {
      const ch = single[j] ?? '';
      const isDigit = ch >= '0' && ch <= '9';
      if (isDigit) {
        seenDigit = true;
        continue;
      }
      if (ch === ',' || (!seenDot && ch === '.')) {
        if (ch === '.') seenDot = true;
        continue;
      }
      break;
    }
    if (seenDigit && j < single.length) {
      const left = single.slice(0, j);
      const right = single.slice(j).toLowerCase();
      if (NUMERIC_UNITS.has(right)) return currency ? `${left} ${right} ${currency}` : `${left} ${right}`;
    }
  }
  for (let i = 1; i < toks.length; i++) {
    const u = canonicalUnitToken(String(toks[i] ?? ''));
    if (u) toks[i] = u;
  }
  if (currency) {
    const lowParts = new Set(toks.map((x) => String(x ?? '').toLowerCase()));
    if (!lowParts.has('usd') && !lowParts.has('aud') && !lowParts.has('eur') && !lowParts.has('gbp')) toks.push(currency);
  }
  return toks.join(' ');
}

export function parseNumericValueToken(raw: string): string {
  const compact = String(raw ?? '').trim().split(',').join('');
  if (!compact) return '';
  let i = 0;
  let sign = '';
  if (compact[0] === '+' || compact[0] === '-') {
    sign = compact[0];
    i = 1;
  }
  let seenDigit = false;
  let seenDot = false;
  let intPart = '';
  let fracPart = '';
  for (; i < compact.length; i++) {
    const ch = compact[i] ?? '';
    const isDigit = ch >= '0' && ch <= '9';
    if (isDigit) {
      seenDigit = true;
      if (seenDot) fracPart += ch;
      else intPart += ch;
      continue;
    }
    if (ch === '.' && !seenDot) {
      seenDot = true;
      continue;
    }
    return '';
  }
  if (!seenDigit) return '';

  while (intPart.startsWith('0') && intPart.length > 1) intPart = intPart.slice(1);
  while (fracPart.endsWith('0')) fracPart = fracPart.slice(0, -1);

  let value = fracPart ? `${intPart}.${fracPart}` : intPart;
  if (value === '0') sign = '';
  if (sign === '-') value = `-${value}`;
  return value;
}

export function numericKey(raw: string): string {
  const mention = normalizeNumericMention(raw);
  if (!mention) return '';
  const toks = mention.split(' ').filter(Boolean);
  if (!toks.length) return '';
  const value = parseNumericValueToken(toks[0] ?? '');
  if (!value) return '';
  const units = toks.slice(1).map((u) => canonicalUnitToken(u)).filter(Boolean);
  if (!units.length) return `${value}|`;
  const uniq = Array.from(new Set(units));
  if (uniq.some((u) => !NUMERIC_UNITS.has(u))) return '';
  let unit = '';
  let outValue = value;
  if (uniq.length === 1) {
    unit = uniq[0] ?? '';
  } else if (uniq.length === 2) {
    const scale = uniq.find((u) => NUMERIC_SCALE_UNITS.has(u)) ?? '';
    const ccy = uniq.find((u) => NUMERIC_CURRENCY_UNITS.has(u)) ?? '';
    if (!scale || !ccy) return '';
    const pow = NUMERIC_SCALE_POW[scale] ?? null;
    if (pow === null) return '';
    const sci = scientificFromScaled(value, pow);
    if (!sci) return '';
    outValue = sci;
    unit = ccy;
  } else {
    return '';
  }
  return `${outValue}|${unit}`;
}

export function numericMentionsFromValues(values: any[]): NumericMention[] {
  const byKey = new Map<string, string>();
  for (const raw of values ?? []) {
    const label = normalizeNumericMention(String(raw ?? ''));
    const key = numericKey(label);
    if (!label || !key) continue;
    if (!byKey.has(key)) byKey.set(key, label);
  }
  return Array.from(byKey.entries()).map(([key, label]) => ({ key, label }));
}

export function numericMentionsForEvent(e: any): NumericMention[] {
  const stepNums = Array.isArray((e as any)?.steps)
    ? uniqueStrings((e as any).steps.flatMap((s: any) => stepNumericObjects(s)))
    : [];
  const nums = stepNums.length ? stepNums : uniqueStrings(eventNumericObjects(e));
  return numericMentionsFromValues(nums);
}

export function numericLabelFromKey(key: string): string {
  const parts = String(key ?? '').split('|');
  const value = parts[0] ?? '';
  const unit = parts[1] ?? '';
  if (!value) return String(key ?? '');
  if (!unit) return value;
  if (unit === 'percent') return `${value} percent`;
  return `${value} ${unit}`;
}

export function numericSortValueFromKey(key: string): number | null {
  const raw = String(key ?? '').split('|')[0] ?? '';
  const n = Number(raw);
  if (!Number.isFinite(n)) return null;
  return n;
}

export function numericSortUnitFromKey(key: string): string {
  return String(key ?? '').split('|')[1] ?? '';
}

export function compareNumericLaneEntries(a: [string, number], b: [string, number]): number {
  const av = numericSortValueFromKey(a[0]);
  const bv = numericSortValueFromKey(b[0]);
  if (av !== null && bv !== null) {
    const ad = Math.abs(av);
    const bd = Math.abs(bv);
    if (bd !== ad) return bd - ad;
    if (bv !== av) return bv - av;
  } else if (av !== null) {
    return -1;
  } else if (bv !== null) {
    return 1;
  }

  const au = numericSortUnitFromKey(a[0]);
  const bu = numericSortUnitFromKey(b[0]);
  if (au !== bu) return au.localeCompare(bu);
  return a[0].localeCompare(b[0]);
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

export function stepNumericObjects(step: any): string[] {
  if (Array.isArray(step?.numeric_objects)) return step.numeric_objects.map((x: any) => String(x)).filter(Boolean);
  return [];
}

export function eventNumericObjects(e: any): string[] {
  if (Array.isArray(e?.numeric_objects)) return e.numeric_objects.map((x: any) => String(x)).filter(Boolean);
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
