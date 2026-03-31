export type NumericMention = { key: string; label: string };

function uniqueStrings(xs: any[]): string[] {
  const out = new Set<string>();
  for (const x of xs ?? []) {
    const s = String(x ?? '').trim();
    if (s) out.add(s);
  }
  return Array.from(out);
}

function collapseWhitespace(raw: string): string {
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
  'gbp'
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

export function stepNumericObjects(step: any): string[] {
  if (Array.isArray(step?.numeric_objects)) return step.numeric_objects.map((x: any) => String(x)).filter(Boolean);
  return [];
}

export function eventNumericObjects(e: any): string[] {
  if (Array.isArray(e?.numeric_objects)) return e.numeric_objects.map((x: any) => String(x)).filter(Boolean);
  return [];
}

export function numericMentionsFromValues(values: any[]): NumericMention[] {
  const byKey = new Map<string, string>();
  for (const raw of values ?? []) {
    const text = String(raw ?? '').trim();
    if (!text) continue;
    // Python-owned projections may provide canonical key literals directly.
    if (!text.includes(' ') && text.includes('|')) {
      const keyLiteral = text;
      if (!byKey.has(keyLiteral)) byKey.set(keyLiteral, numericLabelFromKey(keyLiteral));
      continue;
    }
    const label = normalizeNumericMention(text);
    const key = numericKey(label);
    if (!label || !key) continue;
    if (!byKey.has(key)) byKey.set(key, label);
  }
  return Array.from(byKey.entries()).map(([key, label]) => ({ key, label }));
}

function projectedNumericMentions(value: any): NumericMention[] {
  if (!Array.isArray(value?.numeric_mentions)) return [];
  const out: NumericMention[] = [];
  for (const item of value.numeric_mentions) {
    if (!item || typeof item !== 'object') continue;
    const key = String((item as any).key ?? '').trim();
    const label = String((item as any).label ?? '').trim();
    if (!key || !label) continue;
    out.push({ key, label });
  }
  return out;
}

export function numericMentionsForEvent(e: any): NumericMention[] {
  const projectedEventMentions = projectedNumericMentions(e);
  if (projectedEventMentions.length) return projectedEventMentions;
  if (Array.isArray((e as any)?.steps)) {
    const fromSteps = uniqueStrings(
      (e as any).steps.flatMap((step: any) => projectedNumericMentions(step).map((m) => m.label)),
    );
    if (fromSteps.length) return numericMentionsFromValues(fromSteps);
  }
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
