<script lang="ts">
  import Panel from '$lib/ui/Panel.svelte';
  import LayeredGraph, { type LayerNode, type LayeredEdge } from '$lib/ui/LayeredGraph.svelte';

  export let data: {
    payload: {
      root_actor: { label: string; surname: string };
      parser?: any;
      events: Array<{
        event_id: string;
        anchor: { year: number; month: number | null; day: number | null; precision: string; text: string; kind: string };
        section: string;
        text: string;
        actors: Array<{ label: string; resolved: string; role: string; source: string }>;
        action: string | null;
        negation?: { kind: string; scope?: string; source?: string };
        chains?: Array<{ from_step?: number; to_step?: number; to?: string; kind: string }>;
        entity_objects?: string[];
        numeric_objects?: string[];
        modifier_objects?: string[];
        span_candidates?: Array<{
          span_id: string;
          text: string;
          span_type: string;
          recurrence?: { seen_events: number };
          hygiene?: { view_score?: number; token_count?: number };
        }>;
        objects: Array<{
          title: string;
          source: string;
          resolver_hints?: Array<{ lane: string; kind: string; title: string; score: number }>;
        }>;
        purpose: string | null;
        warnings: string[];
        citations?: Array<{ text?: string }>;
        sl_references?: Array<{ text?: string; authority?: string; ref_value?: string }>;
        timeline_facts?: Array<{
          anchor?: { year?: number; month?: number | null; day?: number | null };
          subjects?: string[];
          action?: string | null;
          negation?: { kind?: string; scope?: string; source?: string };
          objects?: string[];
          numeric_objects?: string[];
        }>;
      }>;
    };
    relPath: string;
    source?: string;
    view?: string;
    error: string | null;
  };

  let selectedId: string | null = null;
  let selectedNodeId: string | null = null;
  let expandContextDetails = false;
  let showAllSpans = false;
  type LayoutMode = 'roles' | 'step_ribbon';
  let layoutMode: LayoutMode = 'step_ribbon';

  type TimeGranularity = 'auto' | 'year' | 'month' | 'day';
  let timeGranularity: TimeGranularity = 'auto';

  function viewTypeFromLayout(layout: LayoutMode): string {
    return layout === 'roles' ? 'roles' : 'step-ribbon';
  }

  function hrefFor(source: string, viewType: string): string {
    return `/graphs/wiki-timeline-aoo?source=${encodeURIComponent(source)}&view=${encodeURIComponent(viewType)}`;
  }

  $: layoutMode = data.view === 'roles' ? 'roles' : 'step_ribbon';

  function fmtTime(a: { year: number; month: number | null; day: number | null; precision: string }): string {
    const y = a.year || 0;
    const m = a.month ?? null;
    const d = a.day ?? null;
    if (a.precision === 'day' && m && d) return `${y}-${String(m).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
    if (a.precision === 'month' && m) return `${y}-${String(m).padStart(2, '0')}`;
    return String(y);
  }

  function timeLayersForEvent(
    eventId: string,
    a: { year: number; month: number | null; day: number | null; precision: string; text: string }
  ): { layers: Array<{ id: string; title: string; nodes: LayerNode[] }>; edges: LayeredEdge[]; attachId: string } {
    const y = a.year || 0;
    const m = a.month ?? null;
    const d = a.day ?? null;

    const want = (g: TimeGranularity): TimeGranularity => {
      if (g !== 'auto') return g;
      if (a.precision === 'day') return 'day';
      if (a.precision === 'month') return 'month';
      return 'year';
    };

    const g = want(timeGranularity);

    const yearNode = node(`time:${eventId}:y:${y}`, String(y), '#e8f4ff', a.text);
    const monthNode =
      m && (g === 'month' || g === 'day')
        ? node(`time:${eventId}:m:${y}-${String(m).padStart(2, '0')}`, `${y}-${String(m).padStart(2, '0')}`, '#e8f4ff', a.text)
        : null;
    const dayNode =
      m && d && g === 'day'
        ? node(
            `time:${eventId}:d:${y}-${String(m).padStart(2, '0')}-${String(d).padStart(2, '0')}`,
            `${y}-${String(m).padStart(2, '0')}-${String(d).padStart(2, '0')}`,
            '#e8f4ff',
            a.text
          )
        : null;

    const layers: Array<{ id: string; title: string; nodes: LayerNode[] }> = [{ id: 'year', title: 'Year', nodes: [yearNode] }];
    if (g === 'month' || g === 'day') layers.push({ id: 'month', title: 'Month', nodes: [monthNode ?? node('time:none:m', '(none)', '#ffffff')] });
    if (g === 'day') layers.push({ id: 'day', title: 'Day', nodes: [dayNode ?? node('time:none:d', '(none)', '#ffffff')] });

    const edges: LayeredEdge[] = [];
    if (monthNode) edges.push({ from: yearNode.id, to: monthNode.id, label: 'in' });
    if (monthNode && dayNode) edges.push({ from: monthNode.id, to: dayNode.id, label: 'on' });

    const attachId = dayNode?.id ?? monthNode?.id ?? yearNode.id;
    return { layers, edges, attachId };
  }

  $: events = data.payload.events ?? [];
  $: {
    const first = events[0];
    if (!selectedId && first) selectedId = first.event_id;
  }

  function handleNodeSelect(event: CustomEvent<{ nodeId: string }>) {
    const nodeId = event.detail.nodeId;
    selectedNodeId = nodeId;
    const m = /ev:\d+/.exec(nodeId);
    if (m) selectedId = m[0];
  }
  $: selected = selectedId ? events.find((e) => e.event_id === selectedId) ?? null : null;
  $: spanSorted =
    selected?.span_candidates?.slice().sort((a, b) => {
      const as = Number(a.hygiene?.view_score ?? 0);
      const bs = Number(b.hygiene?.view_score ?? 0);
      if (bs !== as) return bs - as;
      const ar = Number(a.recurrence?.seen_events ?? 0);
      const br = Number(b.recurrence?.seen_events ?? 0);
      if (br !== ar) return br - ar;
      const al = Number(a.hygiene?.token_count ?? 0);
      const bl = Number(b.hygiene?.token_count ?? 0);
      if (bl !== al) return bl - al;
      return String(a.text ?? '').localeCompare(String(b.text ?? ''));
    }) ?? [];
  $: spanShown = showAllSpans ? spanSorted : spanSorted.slice(0, 24);
  $: objectHintRows =
    selected?.objects?.map((o) => ({
      title: o.title,
      source: o.source,
      hints: (o.resolver_hints ?? []).slice().sort((a, b) => Number(b.score ?? 0) - Number(a.score ?? 0)).slice(0, 4)
    })) ?? [];

  function node(id: string, label: string, color: string, tooltip?: string): LayerNode {
    const short = label.length > 54 ? label.slice(0, 54) + '...' : label;
    return { id, label: short, fullLabel: label, color, tooltip: tooltip ?? label };
  }

  function actionLabel(action: string | null | undefined, negation?: { kind?: string | null }): string {
    const base = String(action ?? '').trim();
    if (!base) return '(no action matched)';
    if (String(negation?.kind ?? '').toLowerCase() === 'not') return `not_${base}`;
    return base;
  }

  function stepEntityObjects(step: any): string[] {
    if (Array.isArray(step?.entity_objects)) return step.entity_objects.map((x: any) => String(x)).filter(Boolean);
    if (Array.isArray(step?.objects)) return step.objects.map((x: any) => String(x)).filter(Boolean);
    return [];
  }

  function eventEntityObjects(ev: any): string[] {
    if (Array.isArray(ev?.entity_objects)) return ev.entity_objects.map((x: any) => String(x)).filter(Boolean);
    return (ev?.objects ?? []).map((o: any) => String(o?.title ?? '')).filter(Boolean);
  }

  function stepNumericObjects(step: any): string[] {
    if (Array.isArray(step?.numeric_objects)) return step.numeric_objects.map((x: any) => String(x)).filter(Boolean);
    return [];
  }

  function eventNumericObjects(ev: any): string[] {
    if (Array.isArray(ev?.numeric_objects)) return ev.numeric_objects.map((x: any) => String(x)).filter(Boolean);
    return [];
  }

  function nodeNeedle(nodeId: string): string {
    if (!nodeId) return '';
    if (nodeId.startsWith('num:')) {
      const key = nodeId.slice('num:'.length);
      return numericLabelByKey.get(key) ?? numericLabelFromKey(key);
    }
    if (nodeId.startsWith('sub:') || nodeId.startsWith('obj:') || nodeId.startsWith('req:')) {
      const parts = nodeId.split(':');
      return parts[parts.length - 1] ?? '';
    }
    return '';
  }

  function highlightParts(text: string, needle: string): Array<{ s: string; hit: boolean }> {
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

  function uniqueStrings(xs: any[]): string[] {
    const out = new Set<string>();
    for (const x of xs ?? []) {
      const s = String(x ?? '').trim();
      if (s) out.add(s);
    }
    return Array.from(out);
  }

  type NumericMention = { key: string; label: string };

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
  const NUMERIC_SCALE_POW: Record<string, number> = {
    hundred: 2,
    thousand: 3,
    million: 6,
    billion: 9,
    trillion: 12
  };

  function scientificFromScaled(value: string, pow: number): string {
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

  function canonicalUnitToken(raw: string): string {
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

  function parseNumericValueToken(raw: string): string {
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

  function normalizeNumericMention(raw: string): string {
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

  function numericKey(raw: string): string {
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

  function numericMentionsFromValues(values: any[]): NumericMention[] {
    const byKey = new Map<string, string>();
    for (const raw of values ?? []) {
      const label = normalizeNumericMention(String(raw ?? ''));
      const key = numericKey(label);
      if (!label || !key) continue;
      if (!byKey.has(key)) byKey.set(key, label);
    }
    return Array.from(byKey.entries()).map(([key, label]) => ({ key, label }));
  }

  function numericMentionsForEvent(ev: any): NumericMention[] {
    const stepNums = Array.isArray((ev as any)?.steps)
      ? uniqueStrings((ev as any).steps.flatMap((s: any) => stepNumericObjects(s)))
      : [];
    const nums = stepNums.length ? stepNums : uniqueStrings(eventNumericObjects(ev));
    return numericMentionsFromValues(nums);
  }

  function numericMentionsForStep(step: any): NumericMention[] {
    return numericMentionsFromValues(stepNumericObjects(step));
  }

  function numericLabelFromKey(key: string): string {
    const parts = String(key ?? '').split('|');
    const value = parts[0] ?? '';
    const unit = parts[1] ?? '';
    if (!value) return String(key ?? '');
    if (!unit) return value;
    if (unit === 'percent') return `${value} percent`;
    return `${value} ${unit}`;
  }

  function numericSortValueFromKey(key: string): number | null {
    const raw = String(key ?? '').split('|')[0] ?? '';
    const n = Number(raw);
    if (!Number.isFinite(n)) return null;
    return n;
  }

  function numericSortUnitFromKey(key: string): string {
    return String(key ?? '').split('|')[1] ?? '';
  }

  function compareNumericKeys(a: string, b: string): number {
    const av = numericSortValueFromKey(a);
    const bv = numericSortValueFromKey(b);
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

    const au = numericSortUnitFromKey(a);
    const bu = numericSortUnitFromKey(b);
    if (au !== bu) return au.localeCompare(bu);
    return a.localeCompare(b);
  }

  $: numericLabelByKey = (() => {
    const out = new Map<string, string>();
    for (const ev of events ?? []) {
      for (const m of numericMentionsForEvent(ev)) if (!out.has(m.key)) out.set(m.key, m.label);
    }
    return out;
  })();

  $: selectedContext = (() => {
    if (!selected) return null as null | { needle: string; summary: string[] };
    const steps = Array.isArray((selected as any).steps) ? ((selected as any).steps as Array<any>) : [];
    const subjects = Array.from(
      new Set(
        steps.length
          ? steps.flatMap((s) => (Array.isArray(s?.subjects) ? s.subjects : []))
          : selected.actors.filter((a) => a.role !== 'requester').map((a) => a.resolved ?? a.label)
      )
    ).filter(Boolean) as string[];
    const objects = Array.from(
      new Set(
        steps.length
          ? steps.flatMap((s) => stepEntityObjects(s))
          : eventEntityObjects(selected)
      )
    ).filter(Boolean) as string[];
    const numericMentions = steps.length
      ? numericMentionsFromValues(steps.flatMap((s) => stepNumericObjects(s)))
      : numericMentionsForEvent(selected);
    const actions = Array.from(new Set((steps.length ? steps.map((s) => actionLabel(s?.action, s?.negation)) : [actionLabel(selected.action, selected.negation)]).filter(Boolean)));
    const summary = [
      ...subjects.map((x) => `sub:${x}`),
      ...actions.map((x) => `act:${x}`),
      ...objects.map((x) => `obj:${x}`),
      ...numericMentions.map((x) => `num:${x.key}`)
    ];
    return { needle: selectedNodeId ? nodeNeedle(selectedNodeId) : '', summary };
  })();

  $: selectedContextDetails = (() => {
    if (!selected) {
      return {
        requesters: [] as string[],
        subjects: [] as string[],
        actions: [] as string[],
        objects: [] as string[],
        numerics: [] as string[],
        citations: [] as string[],
        slRefs: [] as string[],
        factRows: [] as string[],
        warnings: [] as string[]
      };
    }
    const steps = Array.isArray((selected as any).steps) ? ((selected as any).steps as Array<any>) : [];
    const requesters = uniqueStrings(
      (selected.actors ?? [])
        .filter((a) => a.role === 'requester')
        .map((a) => a.resolved ?? a.label)
    );
    const subjects = uniqueStrings(
      steps.length
        ? steps.flatMap((s) => (Array.isArray(s?.subjects) ? s.subjects : []))
        : (selected.actors ?? []).filter((a) => a.role !== 'requester').map((a) => a.resolved ?? a.label)
    );
    const actions = uniqueStrings(
      (steps.length ? steps.map((s) => actionLabel(s?.action, s?.negation)) : [actionLabel(selected.action, selected.negation)]).filter(Boolean)
    );
    const objects = uniqueStrings(
      steps.length
        ? steps.flatMap((s) => stepEntityObjects(s))
        : eventEntityObjects(selected)
    );
    const numerics = (steps.length
      ? numericMentionsFromValues(steps.flatMap((s) => stepNumericObjects(s)))
      : numericMentionsForEvent(selected))
      .slice()
      .sort((a, b) => compareNumericKeys(a.key, b.key))
      .map((m) => m.label);
    const citations = uniqueStrings(((selected as any).citations ?? []).map((c: any) => String(c?.text ?? '')));
    const slRefs = uniqueStrings(
      ((selected as any).sl_references ?? []).map((r: any) => String(r?.text ?? `${r?.authority ?? ''} ${r?.ref_value ?? ''}`.trim()))
    );
    const factRows = uniqueStrings(
      ((selected as any).timeline_facts ?? []).map((f: any) => {
        const y = Number(f?.anchor?.year ?? 0);
        const m = Number(f?.anchor?.month ?? 0);
        const d = Number(f?.anchor?.day ?? 0);
        const m2 = m > 0 ? String(m).padStart(2, '0') : '00';
        const d2 = d > 0 ? String(d).padStart(2, '0') : '00';
        const a = actionLabel(f?.action, f?.negation);
        const subs = Array.isArray(f?.subjects) ? f.subjects.join(', ') : '';
        const objs = Array.isArray(f?.objects) ? f.objects.join(', ') : '';
        const nums = Array.isArray(f?.numeric_objects) ? f.numeric_objects.join(', ') : '';
        return `${y}-${m2}-${d2} | ${subs}${a && a !== '(no action matched)' ? ' -> ' + a : ''}${objs ? ' -> ' + objs : ''}${nums ? ' -> #' + nums : ''}`.trim();
      })
    );
    const warnings = uniqueStrings((selected as any).warnings ?? []);
    return { requesters, subjects, actions, objects, numerics, citations, slRefs, factRows, warnings };
  })();

  $: graph = (() => {
    if (!selected) return { layers: [], edges: [] as LayeredEdge[] };

    const time = timeLayersForEvent(selected.event_id, selected.anchor);

    const requesters = selected.actors.filter((a) => a.role === 'requester');

    const requesterNodes = requesters.map((a) => node(`req:${a.resolved}`, a.resolved, '#e9d5ff', `source=${a.source}`));

    const steps = Array.isArray((selected as any).steps) && (selected as any).steps.length
      ? ((selected as any).steps as Array<{ action: string; negation?: { kind: string; scope?: string; source?: string }; subjects: string[]; objects: string[]; numeric_objects?: string[]; purpose: string | null }>)
      : [{
          action: selected.action ?? '(no action matched)',
          negation: selected.negation,
          subjects: selected.actors.filter((a) => a.role !== 'requester').map((a) => a.resolved),
          objects: eventEntityObjects(selected),
          numeric_objects: eventNumericObjects(selected),
          purpose: selected.purpose ?? null
        }];

    const stepSubjectSet = new Set<string>();
    for (const s of steps) for (const sub of s.subjects ?? []) if (sub) stepSubjectSet.add(String(sub));
    const subjectNodes = (() => {
      if (!stepSubjectSet.size) {
        return selected.actors
          .filter((a) => a.role !== 'requester')
          .map((a) => node(`sub:${a.resolved}`, a.resolved, '#bbf7d0', `source=${a.source}`));
      }
      const out: LayerNode[] = [];
      for (const sub of stepSubjectSet) out.push(node(`sub:${sub}`, sub, '#bbf7d0'));
      return out;
    })();

    const actionNodes = steps.map((s, i) =>
      node(`act:${selected.event_id}:${i}`, actionLabel(s.action, s.negation), '#fde68a')
    );

    // Objects/purpose are step-local when `steps[]` is present; fall back to legacy fields.
    const objSeen = new Set<string>();
    const objNodes: LayerNode[] = [];
    for (const s of steps) {
      for (const t of stepEntityObjects(s)) {
        const title = String(t ?? '').trim();
        if (!title || objSeen.has(title)) continue;
        objSeen.add(title);
        objNodes.push(node(`obj:${title}`, title, '#f6f6f6'));
      }
    }
    if (!objNodes.length) {
      for (const titleRaw of eventEntityObjects(selected)) {
        const title = String(titleRaw ?? '').trim();
        if (!title || objSeen.has(title)) continue;
        objSeen.add(title);
        objNodes.push(node(`obj:${title}`, title, '#f6f6f6'));
      }
    }

    const numByKey = new Map<string, string>();
    for (const s of steps) {
      for (const m of numericMentionsForStep(s)) if (!numByKey.has(m.key)) numByKey.set(m.key, m.label);
    }
    if (!numByKey.size) {
      for (const m of numericMentionsForEvent(selected)) if (!numByKey.has(m.key)) numByKey.set(m.key, m.label);
    }
    const numNodes: LayerNode[] = Array.from(numByKey.entries())
      .sort((a, b) => compareNumericKeys(a[0], b[0]))
      .map(([key, label]) => node(`num:${key}`, label, '#fee2e2', `key=${key}`));

    const purposeNodes: LayerNode[] = [];
    steps.forEach((s, i) => {
      if (s.purpose) purposeNodes.push(node(`pur:${selected.event_id}:${i}`, s.purpose, '#fef3c7'));
    });

    if (layoutMode === 'roles') {
      const layers = [...time.layers] as Array<{ id: string; title: string; nodes: LayerNode[] }>;
      if (requesterNodes.length) layers.push({ id: 'request', title: 'Requester', nodes: requesterNodes });
      layers.push({ id: 'subjects', title: 'Subjects', nodes: subjectNodes.length ? subjectNodes : [node('sub:none', '(none)', '#ffffff')] });
      layers.push({ id: 'action', title: 'Action', nodes: actionNodes.length ? actionNodes : [node('act:none', '(none)', '#ffffff')] });
      layers.push({ id: 'objects', title: 'Objects', nodes: objNodes.length ? objNodes : [node('obj:none', '(none)', '#ffffff')] });
      layers.push({ id: 'numeric', title: 'Numeric', nodes: numNodes.length ? numNodes : [node('num:none', '(none)', '#ffffff')] });
      layers.push({ id: 'purpose', title: 'Purpose', nodes: purposeNodes.length ? purposeNodes : [node('pur:none', '(none)', '#ffffff')] });

      const edges: LayeredEdge[] = [];
      const firstActionId = actionNodes[0]?.id ?? 'act:none';
      edges.push(...time.edges);
      edges.push({ from: time.attachId, to: firstActionId, label: 'at' });
      for (const r of requesterNodes) edges.push({ from: r.id, to: firstActionId, label: 'request' });

      // Step-local wiring: connect only the subjects/objects that belong to that step when possible.
      steps.forEach((st, i) => {
        const aid = actionNodes[i]?.id ?? firstActionId;
        // If step subjects are explicit resolved strings, connect those nodes when present; else connect all subjects.
        const subSet = new Set((st.subjects ?? []).map((x) => String(x)).filter(Boolean));
        const didOne = (() => {
          let ok = false;
          for (const s of subjectNodes) {
            if (!subSet.size || subSet.has(s.fullLabel ?? s.label)) {
              edges.push({ from: s.id, to: aid, label: 'do' });
              ok = true;
            }
          }
          return ok;
        })();
        if (!didOne) for (const s of subjectNodes) edges.push({ from: s.id, to: aid, label: 'do' });

        const objSet = new Set((st.objects ?? []).map((x) => String(x)).filter(Boolean));
        const numSet = new Set(numericMentionsForStep(st).map((m) => m.key));
        for (const o of objNodes) {
          const title = o.fullLabel ?? o.label;
          if (!objSet.size || objSet.has(title)) edges.push({ from: aid, to: o.id, label: 'object' });
        }
        for (const n of numNodes) {
          const key = String(n.id ?? '').startsWith('num:') ? String(n.id).slice('num:'.length) : '';
          if (!numSet.size || (key && numSet.has(key))) edges.push({ from: aid, to: n.id, label: 'numeric' });
        }
        if (st.purpose) edges.push({ from: aid, to: `pur:${selected.event_id}:${i}`, label: 'purpose' });
        const next = actionNodes[i + 1];
        if (next) edges.push({ from: aid, to: next.id, label: 'then' });
      });
      return { layers, edges };
    }

    // Step-ribbon layout: deterministic progression by step index.
    const layers: Array<{ id: string; title: string; nodes: LayerNode[] }> = [...time.layers];
    const edges: LayeredEdge[] = [];
    edges.push(...time.edges);
    if (requesterNodes.length) layers.push({ id: 'request', title: 'Requester', nodes: requesterNodes });

    const actionIds: string[] = [];
    steps.forEach((st, i) => {
      const sid = `${selected.event_id}:s${i}`;
      const actionId = `act:${sid}`;
      actionIds.push(actionId);

      const stepSubjects = Array.from(new Set((st.subjects ?? []).map((x) => String(x).trim()).filter(Boolean)));
      const stepObjects = Array.from(new Set(stepEntityObjects(st).map((x) => String(x).trim()).filter(Boolean)));
      const stepSubjectNodes = stepSubjects.length
        ? stepSubjects.map((s, j) => node(`sub:${sid}:${j}:${s}`, s, '#bbf7d0'))
        : [node(`sub:${sid}:none`, '(none)', '#ffffff')];
      const stepActionNode = node(actionId, actionLabel(st.action, st.negation), '#fde68a');
      const stepObjectNodes = stepObjects.length
        ? stepObjects.map((o, j) => node(`obj:${sid}:${j}:${o}`, o, '#f6f6f6'))
        : [node(`obj:${sid}:none`, '(none)', '#ffffff')];
      const stepNumbers = numericMentionsForStep(st);
      const stepNumberNodes = stepNumbers.length
        ? stepNumbers.map((n, j) => node(`num:${sid}:${j}:${n.key}`, n.label, '#fee2e2', `key=${n.key}`))
        : [node(`num:${sid}:none`, '(none)', '#ffffff')];
      const stepPurposeNodes = st.purpose ? [node(`pur:${sid}`, st.purpose, '#fef3c7')] : [];

      layers.push({ id: `step:${i}:sub`, title: `S${i + 1} Subjects`, nodes: stepSubjectNodes });
      layers.push({ id: `step:${i}:act`, title: `S${i + 1} Action`, nodes: [stepActionNode] });
      layers.push({ id: `step:${i}:obj`, title: `S${i + 1} Objects`, nodes: stepObjectNodes });
      layers.push({ id: `step:${i}:num`, title: `S${i + 1} Numeric`, nodes: stepNumberNodes });
      if (stepPurposeNodes.length) layers.push({ id: `step:${i}:pur`, title: `S${i + 1} Purpose`, nodes: stepPurposeNodes });

      for (const s of stepSubjectNodes) {
        if (!s.id.endsWith(':none')) edges.push({ from: s.id, to: actionId, label: 'do' });
      }
      for (const o of stepObjectNodes) {
        if (!o.id.endsWith(':none')) edges.push({ from: actionId, to: o.id, label: 'object' });
      }
      for (const n of stepNumberNodes) {
        if (!n.id.endsWith(':none')) edges.push({ from: actionId, to: n.id, label: 'numeric' });
      }
      const stepPurposeId = stepPurposeNodes[0]?.id;
      if (stepPurposeId) edges.push({ from: actionId, to: stepPurposeId, label: 'purpose' });
    });

    const firstActionId = actionIds[0] ?? 'act:none';
    edges.push({ from: time.attachId, to: firstActionId, label: 'at' });
    for (const r of requesterNodes) edges.push({ from: r.id, to: firstActionId, label: 'request' });
    for (let i = 0; i + 1 < actionIds.length; i++) {
      const from = actionIds[i];
      const to = actionIds[i + 1];
      if (from && to) edges.push({ from, to, label: 'then' });
    }

    return { layers, edges };
  })();

  $: graphWidth = (() => {
    if (!selected) return 1400;
    const cols = Array.isArray((graph as any)?.layers) ? (graph as any).layers.length : 10;
    // Deterministic: width derived from rendered column count + configured gap.
    // Keep headroom for expanded nodes and labels.
    const colGap = 760;
    const leftPad = 100;
    return Math.max(2000, leftPad * 2 + Math.max(0, cols - 1) * colGap + 620);
  })();
  // Reset only when the graph configuration meaningfully changes, not when the user clicks around.
  $: graphViewportKey = [
    String(data?.source ?? 'gwb'),
    String(layoutMode),
    String(timeGranularity),
    String(events?.length ?? 0),
  ].join('|');
</script>

<div class="space-y-4 p-6">
  <Panel>
    <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Wiki timeline: actor/action/object</div>
    <div class="mt-2 text-sm text-ink-950">
      Source: <span class="font-mono text-xs">{data.relPath}</span>
    </div>
    <div class="mt-2 text-xs text-ink-800/60">
      Sentence-local extraction. Non-causal. Non-authoritative.
    </div>
    <div class="mt-3 flex flex-wrap items-center gap-2 text-xs">
      <label class="flex items-center gap-2">
        <span class="text-ink-800/70">Dataset</span>
        <select
          class="rounded-md border border-ink-950/15 bg-white px-2 py-1 text-xs"
          value={data.source ?? 'gwb'}
          aria-label="Dataset source"
          on:change={(e) => {
            const v = (e.currentTarget as HTMLSelectElement).value;
            window.location.href = hrefFor(v, viewTypeFromLayout(layoutMode));
          }}
        >
          <option value="gwb">gwb</option>
          <option value="gwb_public_bios_v1">gwb_public_bios_v1</option>
          <option value="gwb_corpus_v1">gwb_corpus_v1</option>
          <option value="hca">hca</option>
          <option value="legal">legal</option>
          <option value="legal_follow">legal_follow</option>
        </select>
      </label>
      <a
        class="rounded-md border border-ink-950/15 px-2 py-1 text-xs text-ink-950 hover:border-ink-950/30 hover:bg-ink-950/[0.03]"
        href={`/graphs/wiki-timeline?source=${encodeURIComponent(data.source ?? 'gwb')}`}
      >
        Open Timeline
      </a>
      <a
        class="rounded-md border border-ink-950/15 px-2 py-1 text-xs text-ink-950 hover:border-ink-950/30 hover:bg-ink-950/[0.03]"
        href={`/graphs/wiki-timeline-aoo-all?source=${encodeURIComponent(data.source ?? 'gwb')}`}
      >
        Open AAO-all
      </a>
      <a
        class="rounded-md border border-ink-950/15 px-2 py-1 text-xs text-ink-950 hover:border-ink-950/30 hover:bg-ink-950/[0.03]"
        href={`/graphs/wiki-fact-timeline?source=${encodeURIComponent(data.source ?? 'gwb')}`}
      >
        Open Fact Timeline
      </a>
    </div>
  </Panel>

  {#if data.error}
    <Panel tone="danger">
      <div class="text-xs uppercase tracking-[0.28em] text-red-800/80">Load error</div>
      <pre class="mt-3 whitespace-pre-wrap font-mono text-xs text-ink-950">{data.error}</pre>
    </Panel>
  {/if}

  <div class="grid grid-cols-1 gap-4 lg:grid-cols-[360px_1fr]">
    <Panel>
      <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Events</div>
      <div class="mt-3 max-h-[560px] overflow-auto">
        {#each events as e (e.event_id)}
          <button
            class="mb-2 w-full rounded-lg border px-3 py-2 text-left text-xs transition hover:border-ink-950/30 hover:bg-ink-950/[0.02] {e.event_id===selectedId ? 'border-ink-950/35 bg-ink-950/[0.03]' : 'border-ink-950/10 bg-white'}"
            on:click={() => (selectedId = e.event_id)}
          >
            <div class="font-mono text-[10px] text-ink-800/60">{fmtTime(e.anchor)} {e.event_id}</div>
            <div class="mt-1 text-ink-950">{e.text.length > 140 ? e.text.slice(0, 140) + '...' : e.text}</div>
            {#if e.warnings?.length}
              <div class="mt-1 font-mono text-[10px] text-amber-900/70">warnings: {e.warnings.join(', ')}</div>
            {/if}
          </button>
        {/each}
      </div>
    </Panel>

    <div class="space-y-4">
      {#if selected}
        <Panel>
          <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Selected</div>
          <div class="mt-2 text-sm text-ink-950">{selected.text}</div>
          <div class="mt-2 text-xs text-ink-800/60">
            {selected.anchor.text} | section: <span class="font-mono">{selected.section}</span>
          </div>
          {#if selected.chains?.length}
            <div class="mt-2 text-xs text-ink-800/60 font-mono">
              chains:
              {#each selected.chains as c, i (i)}
                <span class="ml-2">{c.kind}({c.from_step ?? '-'}->{c.to_step ?? c.to ?? '-'})</span>
              {/each}
            </div>
          {/if}
          <div class="mt-4 flex flex-wrap items-center gap-2 text-xs text-ink-950">
            <div class="font-mono text-[10px] uppercase tracking-[0.20em] text-ink-800/70">Layout</div>
            <button
              class="rounded-md border px-2 py-1 font-mono text-[11px] {layoutMode==='step_ribbon' ? 'border-ink-950/40 bg-ink-950/[0.04]' : 'border-ink-950/10 bg-white hover:border-ink-950/25 hover:bg-ink-950/[0.02]'}"
              on:click={() => {
                window.location.href = hrefFor(data.source ?? 'gwb', 'step-ribbon');
              }}
            >
              step-ribbon
            </button>
            <button
              class="rounded-md border px-2 py-1 font-mono text-[11px] {layoutMode==='roles' ? 'border-ink-950/40 bg-ink-950/[0.04]' : 'border-ink-950/10 bg-white hover:border-ink-950/25 hover:bg-ink-950/[0.02]'}"
              on:click={() => {
                window.location.href = hrefFor(data.source ?? 'gwb', 'roles');
              }}
            >
              roles
            </button>
          </div>
          <div class="mt-2 text-[11px] text-ink-800/65">
            `step-ribbon` preserves sentence order (S1 -&gt; S2 ...) with explicit `then` edges; it is linearization only, not causality.
          </div>
          <div class="mt-4 flex flex-wrap items-center gap-2 text-xs text-ink-950">
            <div class="font-mono text-[10px] uppercase tracking-[0.20em] text-ink-800/70">Time view</div>
            <button
              class="rounded-md border px-2 py-1 font-mono text-[11px] {timeGranularity==='auto' ? 'border-ink-950/40 bg-ink-950/[0.04]' : 'border-ink-950/10 bg-white hover:border-ink-950/25 hover:bg-ink-950/[0.02]'}"
              on:click={() => (timeGranularity = 'auto')}
            >
              auto
            </button>
            <button
              class="rounded-md border px-2 py-1 font-mono text-[11px] {timeGranularity==='year' ? 'border-ink-950/40 bg-ink-950/[0.04]' : 'border-ink-950/10 bg-white hover:border-ink-950/25 hover:bg-ink-950/[0.02]'}"
              on:click={() => (timeGranularity = 'year')}
            >
              year
            </button>
            <button
              class="rounded-md border px-2 py-1 font-mono text-[11px] {timeGranularity==='month' ? 'border-ink-950/40 bg-ink-950/[0.04]' : 'border-ink-950/10 bg-white hover:border-ink-950/25 hover:bg-ink-950/[0.02]'}"
              on:click={() => (timeGranularity = 'month')}
            >
              month
            </button>
            <button
              class="rounded-md border px-2 py-1 font-mono text-[11px] {timeGranularity==='day' ? 'border-ink-950/40 bg-ink-950/[0.04]' : 'border-ink-950/10 bg-white hover:border-ink-950/25 hover:bg-ink-950/[0.02]'}"
              on:click={() => (timeGranularity = 'day')}
            >
              day
            </button>
          </div>
        </Panel>

        <LayeredGraph
          layers={graph.layers}
        edges={graph.edges}
        width={graphWidth}
        height={920}
        colGap={760}
        leftPad={100}
        fitToWidth={false}
        scrollWhenOverflow={true}
        viewportResetKey={graphViewportKey}
        on:nodeSelect={(e) => handleNodeSelect(e as CustomEvent<{ nodeId: string }>)}
      />

        <Panel>
          <div class="flex flex-wrap items-center justify-between gap-3">
            <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Context</div>
            <div class="text-[11px] font-mono text-ink-800/60">
              {#if selected}
                selected: {selected.event_id}{#if selectedNodeId} ({selectedNodeId}){/if}
                <button
                  class="ml-2 rounded border border-ink-950/10 bg-white px-2 py-0.5 text-[10px] hover:border-ink-950/25"
                  on:click={() => (expandContextDetails = !expandContextDetails)}
                >
                  {expandContextDetails ? 'collapse details' : 'expand details'}
                </button>
              {:else}
                click a node to inspect context
              {/if}
            </div>
          </div>
          {#if selected && selectedContext}
            <div class="mt-3 rounded-lg border border-ink-950/10 bg-white p-3">
              <div class="flex flex-wrap items-center justify-between gap-2">
                <div class="font-mono text-[10px] text-ink-800/60">{fmtTime(selected.anchor)} {selected.event_id}</div>
                <div class="font-mono text-[10px] text-ink-800/60">section={selected.section}</div>
              </div>
              <div class="mt-2 text-sm text-ink-950 leading-relaxed">
                {#each highlightParts(selected.text, selectedContext.needle) as p, i (i)}
                  {#if p.hit}
                    <mark class="rounded bg-amber-100 px-0.5">{p.s}</mark>
                  {:else}
                    <span>{p.s}</span>
                  {/if}
                {/each}
              </div>
              <div class="mt-2 text-[11px] text-ink-800/65 font-mono">
                connected {selectedContext.summary.join(' ')}
              </div>
              {#if expandContextDetails}
                <div class="mt-3 max-h-[280px] overflow-auto rounded border border-ink-950/10 bg-slate-50 p-2 text-[11px]">
                  {#if selectedContextDetails.requesters.length}
                    <div class="mb-1">
                      <span class="font-mono text-ink-800/60">requesters</span>
                      {#each selectedContextDetails.requesters as x (selected.event_id + ':req:' + x)}
                        <span class="ml-1 inline-block rounded bg-purple-100 px-1.5 py-0.5 font-mono">[{x}]</span>
                      {/each}
                    </div>
                  {/if}
                  {#if selectedContextDetails.subjects.length}
                    <div class="mb-1">
                      <span class="font-mono text-ink-800/60">subjects</span>
                      {#each selectedContextDetails.subjects as x (selected.event_id + ':sub:' + x)}
                        <span class="ml-1 inline-block rounded bg-emerald-100 px-1.5 py-0.5 font-mono">[{x}]</span>
                      {/each}
                    </div>
                  {/if}
                  {#if selectedContextDetails.actions.length}
                    <div class="mb-1">
                      <span class="font-mono text-ink-800/60">actions</span>
                      {#each selectedContextDetails.actions as x (selected.event_id + ':act:' + x)}
                        <span class="ml-1 inline-block rounded bg-amber-100 px-1.5 py-0.5 font-mono">[{x}]</span>
                      {/each}
                    </div>
                  {/if}
                  {#if selectedContextDetails.objects.length}
                    <div class="mb-1">
                      <span class="font-mono text-ink-800/60">objects</span>
                      {#each selectedContextDetails.objects as x (selected.event_id + ':obj:' + x)}
                        <span class="ml-1 inline-block rounded bg-slate-100 px-1.5 py-0.5 font-mono">[{x}]</span>
                      {/each}
                    </div>
                  {/if}
                  {#if selectedContextDetails.numerics.length}
                    <div class="mb-1">
                      <span class="font-mono text-ink-800/60">numeric</span>
                      {#each selectedContextDetails.numerics as x (selected.event_id + ':num:' + x)}
                        <span class="ml-1 inline-block rounded bg-rose-100 px-1.5 py-0.5 font-mono">[{x}]</span>
                      {/each}
                    </div>
                  {/if}
                  {#if selectedContextDetails.factRows.length}
                    <div class="mb-1">
                      <span class="font-mono text-ink-800/60">timeline_facts</span>
                      {#each selectedContextDetails.factRows.slice(0, 6) as x (selected.event_id + ':fact:' + x)}
                        <span class="ml-1 mt-1 inline-block rounded bg-lime-50 px-1.5 py-0.5 font-mono text-ink-900">{x}</span>
                      {/each}
                    </div>
                  {/if}
                  {#if selectedContextDetails.citations.length}
                    <div class="mb-1">
                      <span class="font-mono text-ink-800/60">citations</span>
                      {#each selectedContextDetails.citations.slice(0, 8) as x (selected.event_id + ':cit:' + x)}
                        <span class="ml-1 inline-block rounded bg-amber-50 px-1.5 py-0.5 font-mono text-ink-900">{x}</span>
                      {/each}
                    </div>
                  {/if}
                  {#if selectedContextDetails.slRefs.length}
                    <div class="mb-1">
                      <span class="font-mono text-ink-800/60">sl_refs</span>
                      {#each selectedContextDetails.slRefs.slice(0, 8) as x (selected.event_id + ':sl:' + x)}
                        <span class="ml-1 inline-block rounded bg-blue-50 px-1.5 py-0.5 font-mono text-ink-900">{x}</span>
                      {/each}
                    </div>
                  {/if}
                  {#if selectedContextDetails.warnings.length}
                    <div>
                      <span class="font-mono text-ink-800/60">warnings</span>
                      {#each selectedContextDetails.warnings as x (selected.event_id + ':warn:' + x)}
                        <span class="ml-1 inline-block rounded bg-rose-50 px-1.5 py-0.5 font-mono text-ink-900">{x}</span>
                      {/each}
                    </div>
                  {/if}
                </div>
              {/if}
            </div>
          {/if}
        </Panel>

        <Panel>
          <div class="flex flex-wrap items-center justify-between gap-2">
            <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Span candidates</div>
            <div class="font-mono text-[10px] text-ink-800/60">
              {#if data.payload.parser}
                parser={data.payload.parser.model ?? '(unknown)'}
              {:else}
                parser=(none)
              {/if}
            </div>
          </div>
          {#if selected.span_candidates?.length}
            <div class="mt-3 flex flex-wrap items-center gap-3 text-xs text-ink-950">
              <label class="flex items-center gap-2">
                <input type="checkbox" bind:checked={showAllSpans} />
                <span class="text-ink-800/70">show all</span>
              </label>
              <div class="font-mono text-[10px] text-ink-800/60">
                showing {spanShown.length} / {selected.span_candidates.length}
              </div>
            </div>
            <div class="mt-3 flex flex-wrap gap-2 text-[11px]">
              {#each spanShown as s (s.span_id)}
                <span class="rounded border border-ink-950/10 bg-white px-2 py-1 font-mono text-ink-950">
                  <span class="text-ink-800/70">{s.span_type}</span>
                  <span class="ml-2">{s.text}</span>
                  {#if s.hygiene?.view_score !== undefined}
                    <span class="ml-2 text-ink-800/60">score={Number(s.hygiene.view_score).toFixed(2)}</span>
                  {/if}
                  {#if s.recurrence?.seen_events}
                    <span class="ml-2 text-ink-800/60">seen={s.recurrence.seen_events}</span>
                  {/if}
                </span>
              {/each}
            </div>
          {:else}
            <div class="mt-3 text-xs text-ink-800/70">
              No span candidates emitted (model not installed, parsing disabled, or no noun chunks outside resolved entities).
            </div>
          {/if}
        </Panel>

        <Panel>
          <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Object resolver hints</div>
          {#if objectHintRows.length}
            <div class="mt-3 max-h-[260px] overflow-auto space-y-2">
              {#each objectHintRows as r (r.title + ':' + r.source)}
                <div class="rounded border border-ink-950/10 bg-white px-2 py-2">
                  <div class="font-mono text-[11px] text-ink-950">
                    [{r.source}] {r.title}
                  </div>
                  {#if r.hints.length}
                    <div class="mt-1 flex flex-wrap gap-2 text-[10px]">
                      {#each r.hints as h, i (r.title + ':' + i)}
                        <span class="rounded bg-slate-100 px-1.5 py-0.5 font-mono text-ink-900">
                          {h.kind}@{h.lane}: {h.title} ({Number(h.score).toFixed(2)})
                        </span>
                      {/each}
                    </div>
                  {:else}
                    <div class="mt-1 text-[11px] text-ink-800/70">no resolver hints</div>
                  {/if}
                </div>
              {/each}
            </div>
          {:else}
            <div class="mt-3 text-xs text-ink-800/70">No objects available for hinting in this event.</div>
          {/if}
        </Panel>
      {/if}
    </div>
  </div>
</div>
