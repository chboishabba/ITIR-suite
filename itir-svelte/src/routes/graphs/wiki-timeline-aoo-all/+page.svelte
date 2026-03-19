<script lang="ts">
  import Panel from '$lib/ui/Panel.svelte';
  import LayeredGraph, { type LayerNode, type LayeredEdge } from '$lib/ui/LayeredGraph.svelte';
  import { afterUpdate } from 'svelte';

  type RequesterCoverage = {
    request_signal_events?: number;
    requester_events?: number;
    total_events?: number;
    missing_requester_event_ids?: string[];
  };

  export let data: {
    payload: {
      root_actor: { label: string; surname: string };
      requester_coverage?: RequesterCoverage;
      source_entity?: {
        id?: string;
        type?: string;
        title?: string;
        url?: string;
        publication_date?: string;
        version_hash?: string;
      };
      extraction_record?: {
        id?: string;
        source_entity_id?: string;
        parser_version?: string;
        extraction_timestamp?: string;
        confidence_score?: number;
      };
      extraction_profile?: {
        profile_id?: string;
        profile_version?: string;
        predicate_classifier?: string;
        path?: string;
      };
      run_id?: string;
      generated_at?: string;
      __loaded_from_db?: boolean;
      source_timeline?: { path?: string; snapshot?: any } | null;
      events: Array<{
        event_id: string;
        anchor: { year: number; month: number | null; day: number | null; precision: string; text: string; kind: string };
        section: string;
        text: string;
        actors: Array<{ label: string; resolved: string; role: string; source: string }>;
        action: string | null;
        negation?: { kind: string; scope?: string; source?: string };
        objects: Array<{ title: string; source: string }>;
        entity_objects?: string[];
        numeric_objects?: string[];
        modifier_objects?: string[];
        steps?: Array<{
          action: string;
          claim_bearing?: boolean;
          negation?: { kind: string; scope?: string; source?: string };
          subjects?: string[];
          entity_objects?: string[];
          numeric_objects?: string[];
          modifier_objects?: string[];
          objects?: string[];
          purpose?: string | null;
        }>;
        citations?: Array<{
          text: string;
          kind?: string;
          follower_order?: string[];
          follow?: Array<{ provider?: string; mode?: string; url?: string; path?: string; script?: string }>;
        }>;
        sl_references?: Array<{
          text?: string;
          lane?: string;
          authority?: string;
          ref_value?: string;
          follower_order?: string[];
          follow?: Array<{ provider?: string; mode?: string; url?: string; path?: string; script?: string }>;
        }>;
        party?: string;
        toc_context?: Array<{ node_type?: string; identifier?: string; title?: string; path?: string }>;
        legal_section_markers?: {
          citation_prefixes?: string[];
          sl_reference_lanes?: string[];
          provision_stable_ids?: string[];
          rule_atom_stable_ids?: string[];
        };
        timeline_facts?: Array<{
          fact_id: string;
          anchor: { year: number; month: number | null; day: number | null; precision: string; text: string; kind: string };
          subjects?: string[];
          action?: string | null;
          negation?: { kind: string; scope?: string; source?: string };
          objects?: string[];
          numeric_objects?: string[];
          party?: string;
        }>;
        purpose: string | null;
        claim_bearing?: boolean;
        warnings: string[];
      }>;
    };
    relPath: string;
    source?: string;
    corpusDocs?: Array<{ relPath: string; name: string; bytes: number; ext: string }>;
    error: string | null;
  };

  type TimeGranularity = 'year' | 'month' | 'day';
  let timeGranularity: TimeGranularity = 'month';
  let limitEvents = 80;
  let maxSubjects = 120;
  let maxObjects = 160;
  let maxNumbers = 120;
  let maxSources = 80;
  let maxLenses = 120;
  let maxEvidence = 140;
  let includeSources = true;
  let includeLenses = true;
  let includeRequesters = true;
  let includePurpose = false;
  let includeEvidence = false;
  let orderByFactDate = false;
  let showAllContextRows = false;

  let selectedNodeId: string | null = null;
  let contextBox: HTMLDivElement | null = null;
  let lastScrollKey = '';
  // Wider lane spacing for readability in dense AAO-all layouts.
  const GRAPH_HEIGHT = 900;
  const GRAPH_COL_GAP = 800;
  const GRAPH_LEFT_PAD = 100;
  // Reset the viewport only when the graph layout meaningfully changes (dataset/filters),
  // not when the user clicks around selecting nodes.
  $: graphViewportKey = [
    String(data?.source ?? 'gwb'),
    String(timeGranularity),
    String(limitEvents),
    String(maxSubjects),
    String(maxObjects),
    String(maxNumbers),
    includeSources ? `src:${maxSources}` : 'src:off',
    includeLenses ? `lens:${maxLenses}` : 'lens:off',
    includeEvidence ? `evd:${maxEvidence}` : 'evd:off',
    includeRequesters ? 'req:on' : 'req:off',
    includePurpose ? 'purpose:on' : 'purpose:off',
    orderByFactDate ? 'fact_date:on' : 'fact_date:off',
    String(graphEvents?.length ?? 0)
  ].join('|');
  $: graphWidth = Math.max(
    3600,
    GRAPH_LEFT_PAD * 2 + Math.max(0, (graph as any)?.layers?.length ? (graph as any).layers.length - 1 : 8) * GRAPH_COL_GAP + 720
  );

  function node(id: string, label: string, color: string, tooltip?: string): LayerNode {
    const short = label.length > 54 ? label.slice(0, 54) + '...' : label;
    return { id, label: short, fullLabel: label, color, tooltip: tooltip ?? label };
  }

  function pad2(n: number): string {
    return String(n).padStart(2, '0');
  }

  function fmtBytes(n: number): string {
    const v = Number(n);
    if (!Number.isFinite(v) || v <= 0) return '0 B';
    const units = ['B', 'KB', 'MB', 'GB'];
    let u = 0;
    let x = v;
    while (x >= 1024 && u < units.length - 1) {
      x /= 1024;
      u += 1;
    }
    const digits = u === 0 ? 0 : u === 1 ? 1 : 2;
    return `${x.toFixed(digits)} ${units[u]}`;
  }

  function referencedCorpusPaths(): Set<string> {
    const out = new Set<string>();
    for (const e of eventsAll ?? []) {
      const cits = Array.isArray((e as any).citations) ? (e as any).citations : [];
      for (const c of cits) {
        const follow = Array.isArray(c?.follow) ? c.follow : [];
        for (const f of follow) {
          const p = String(f?.path ?? '').trim();
          const u = String(f?.url ?? '').trim();
          if (p) out.add(p);
          if (u) out.add(u);
        }
      }
      const refs = Array.isArray((e as any).sl_references) ? (e as any).sl_references : [];
      for (const r of refs) {
        const follow = Array.isArray(r?.follow) ? r.follow : [];
        for (const f of follow) {
          const p = String(f?.path ?? '').trim();
          const u = String(f?.url ?? '').trim();
          if (p) out.add(p);
          if (u) out.add(u);
        }
      }
    }
    return out;
  }

  function refHasDoc(ref: Set<string>, relPath: string, name: string): boolean {
    const relNorm = String(relPath || '').replaceAll('\\', '/');
    const nameNorm = String(name || '').trim();
    if (!relNorm && !nameNorm) return false;
    for (const raw of ref) {
      const x = String(raw || '').replaceAll('\\', '/');
      if (!x) continue;
      if (relNorm && (x === relNorm || x.endsWith('/' + relNorm))) return true;
      if (nameNorm && (x === nameNorm || x.endsWith('/' + nameNorm))) return true;
    }
    return false;
  }

  function fmtYM(a: { year: number; month: number | null }): string {
    const y = a.year || 0;
    const m = a.month ?? null;
    if (!m) return String(y);
    return `${y}-${pad2(m)}`;
  }

  function fmtYMD(a: { year: number; month: number | null; day: number | null }): string {
    const y = a.year || 0;
    const m = a.month ?? null;
    const d = a.day ?? null;
    if (!m) return String(y);
    if (!d) return `${y}-${pad2(m)}`;
    return `${y}-${pad2(m)}-${pad2(d)}`;
  }

  $: eventsAll = data.payload.events ?? [];
  $: graphEvents = eventsAll.slice(0, Math.max(10, Math.min(eventsAll.length, Math.floor(limitEvents))));
  $: contextEvents = eventsAll;
  $: requesterCoverage = ((data.payload as any)?.requester_coverage ?? null) as RequesterCoverage | null;
  $: missingRequesterEventIds = Array.isArray(requesterCoverage?.missing_requester_event_ids)
    ? requesterCoverage.missing_requester_event_ids.map((x) => String(x ?? '')).filter(Boolean)
    : [];
  $: missingRequesterEventIdSet = new Set<string>(missingRequesterEventIds);

  type CtxRow = {
    key: string;
    // Disambiguates duplicate event_ids in some merged/union datasets.
    // This keeps Svelte keyed {#each} stable and prevents runtime crashes.
    instance: number;
    event_id: string;
    time: string;
    section: string;
    text: string;
    requesters: string[];
    subjects: string[];
    action: string | null;
    negation?: { kind: string; scope?: string; source?: string };
    actions: string[];
    objects: string[];
    numerics: string[];
    numericClaims: string[];
    sources: string[];
    lenses: string[];
    citations: string[];
    checkNext: string[];
    slRefs: string[];
    party: string;
    tocContext: string[];
    legalMarkers: string[];
    factRows: string[];
    sortTime: string;
    connected: string[];
    purpose: string | null;
  };

  type RequesterCoverageSnapshot = {
    requestSignalEvents: number;
    requesterEvents: number;
    totalEvents: number;
    missingRequesterEventIds: string[];
  };

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

  function numericMentionsForEvent(e: any): NumericMention[] {
    const stepNums = Array.isArray((e as any)?.steps)
      ? uniqueStrings((e as any).steps.flatMap((s: any) => stepNumericObjects(s)))
      : [];
    const nums = stepNums.length ? stepNums : uniqueStrings(eventNumericObjects(e));
    return numericMentionsFromValues(nums);
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

  function compareNumericLaneEntries(a: [string, number], b: [string, number]): number {
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

  function eventEntityObjects(e: any): string[] {
    if (Array.isArray(e?.entity_objects)) return e.entity_objects.map((x: any) => String(x)).filter(Boolean);
    if (Array.isArray(e?.objects)) return e.objects.map((o: any) => String(o?.title ?? '')).filter(Boolean);
    return [];
  }

  function stepNumericObjects(step: any): string[] {
    if (Array.isArray(step?.numeric_objects)) return step.numeric_objects.map((x: any) => String(x)).filter(Boolean);
    return [];
  }

  function eventNumericObjects(e: any): string[] {
    if (Array.isArray(e?.numeric_objects)) return e.numeric_objects.map((x: any) => String(x)).filter(Boolean);
    return [];
  }

  function sourceLabelsForEvent(e: any): string[] {
    const out: string[] = [];
    const src = (data.payload as any)?.source_entity;
    if (src && typeof src === 'object') {
      const title = String(src.title ?? '').trim();
      const typ = String(src.type ?? '').trim();
      if (title && typ) out.push(`source:${title} (${typ})`);
      else if (title) out.push(`source:${title}`);
      else if (typ) out.push(`source_type:${typ}`);
    }
    const extraction = (data.payload as any)?.extraction_record;
    if (extraction && typeof extraction === 'object') {
      const parserVersion = String(extraction.parser_version ?? '').trim();
      if (parserVersion) out.push(`parser:${parserVersion}`);
    }
    const timeline = (data.payload as any)?.source_timeline;
    if (timeline && typeof timeline === 'object') {
      const p = String((timeline as any)?.path ?? '').trim();
      if (p) out.push(`timeline:${p.split('/').slice(-2).join('/')}`);
    }

    // Always show per-event extraction provenance signals (even when citations are empty),
    // otherwise the Source lane collapses to "(none)" for the wiki datasets.
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

    // For source-pack timelines, each row is its own source-ish artifact. Preserve
    // the row title and any follow URL host so sources are visible per-event.
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

  function lensLabelsForEvent(e: any): string[] {
    const out: string[] = [];
    const profile = (data.payload as any)?.extraction_profile;
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

  function hasRequesterActor(e: any): boolean {
    return (e?.actors ?? []).some((a: any) => {
      if ((a?.role ?? '') !== 'requester') return false;
      return Boolean(String(a?.resolved ?? a?.label ?? '').trim());
    });
  }

  function asCount(raw: any): number {
    const n = Number(raw);
    if (!Number.isFinite(n)) return 0;
    if (n <= 0) return 0;
    return Math.floor(n);
  }

  $: requesterCoverageGlobal = (() => {
    if (!requesterCoverage) return null as RequesterCoverageSnapshot | null;
    return {
      requestSignalEvents: asCount(requesterCoverage.request_signal_events),
      requesterEvents: asCount(requesterCoverage.requester_events),
      totalEvents: asCount(requesterCoverage.total_events ?? eventsAll.length),
      missingRequesterEventIds: uniqueStrings(requesterCoverage.missing_requester_event_ids ?? [])
    } as RequesterCoverageSnapshot;
  })();

  $: requesterCoverageWindow = (() => {
    const missingRequesterEventIds: string[] = [];
    let requestSignalEvents = 0;
    let requesterEvents = 0;
    for (const e of graphEvents ?? []) {
      const eventId = String((e as any)?.event_id ?? '');
      const hasRequester = hasRequesterActor(e);
      const missingRequester = eventId ? missingRequesterEventIdSet.has(eventId) : false;
      if (hasRequester) requesterEvents += 1;
      if (hasRequester || missingRequester) requestSignalEvents += 1;
      if (missingRequester && eventId) missingRequesterEventIds.push(eventId);
    }
    return {
      requestSignalEvents,
      requesterEvents,
      totalEvents: graphEvents.length,
      missingRequesterEventIds
    } as RequesterCoverageSnapshot;
  })();

  $: requesterCoverageWindowGap = requesterCoverageWindow.requestSignalEvents > requesterCoverageWindow.requesterEvents;
  $: requesterCoverageGlobalGap = requesterCoverageGlobal
    ? requesterCoverageGlobal.requestSignalEvents > requesterCoverageGlobal.requesterEvents
    : false;

  $: numericLabelByKey = (() => {
    const out = new Map<string, string>();
    for (const e of contextEvents ?? []) {
      for (const m of numericMentionsForEvent(e)) if (!out.has(m.key)) out.set(m.key, m.label);
    }
    return out;
  })();

  const DEFAULT_FOLLOW_ORDER = ['wikipedia', 'wiki_connector', 'austlii', 'jade', 'source_document', 'source_pdf'];

  function collectFollowProviders(rows: any[]): string[] {
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

  function evidenceLabelsFromEvent(e: any): string[] {
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

  function keyFromNodeId(id: string): { kind: string; key: string } {
    const m = /^([a-z]+):(.+)$/.exec(id);
    if (!m) return { kind: 'other', key: id };
    const kind = m[1] ?? 'other';
    const key = m[2] ?? id;
    return { kind, key };
  }

  function timeKeyForEvent(e: { anchor: { year: number; month: number | null; day: number | null } }, g: TimeGranularity): string {
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

  function factAnchorKey(a: any): string {
    const y = String(a?.year ?? 0);
    const m = typeof a?.month === 'number' ? pad2(a.month) : '99';
    const d = typeof a?.day === 'number' ? pad2(a.day) : '99';
    return `${y}-${m}-${d}`;
  }

  function eventMatchesNode(e: any, nodeId: string): boolean {
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
      return numericMentionsForEvent(e).some((m: NumericMention) => m.key === key);
    }
    if (nodeId.startsWith('evd:')) {
      const key = nodeId.slice('evd:'.length);
      return evidenceLabelsFromEvent(e).includes(key);
    }
    if (nodeId.startsWith('src:')) {
      const key = nodeId.slice('src:'.length);
      return sourceLabelsForEvent(e).includes(key);
    }
    if (nodeId.startsWith('lens:')) {
      const key = nodeId.slice('lens:'.length);
      return lensLabelsForEvent(e).includes(key);
    }

    if (nodeId.startsWith('time:y:')) {
      const key = nodeId.slice('time:y:'.length);
      return String(e.anchor?.year ?? 0) === key;
    }
    if (nodeId.startsWith('time:m:')) {
      const key = nodeId.slice('time:m:'.length);
      const y = String(e.anchor?.year ?? 0);
      const m = e.anchor?.month ?? null;
      const ym = m ? `${y}-${pad2(m)}` : y;
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

  $: contextRows = (() => {
    if (!selectedNodeId) return [] as CtxRow[];
    const { kind, key } = keyFromNodeId(selectedNodeId);
    const rows: CtxRow[] = [];
    const eventIdCounts = new Map<string, number>();
    for (const e of contextEvents) {
      if (!eventMatchesNode(e, selectedNodeId)) continue;
      const eventId = String(e.event_id ?? '');
      const instance = (eventIdCounts.get(eventId) ?? 0) + 1;
      eventIdCounts.set(eventId, instance);
      const reqs = (e.actors ?? []).filter((a: any) => (a.role ?? '') === 'requester').map((a: any) => String(a.resolved ?? a.label ?? '')).filter(Boolean);
      const stepSubs = Array.isArray((e as any).steps)
        ? uniqueStrings((e as any).steps.flatMap((s: any) => (Array.isArray(s?.subjects) ? s.subjects : [])))
        : [];
      const subs = stepSubs.length
        ? stepSubs
        : (e.actors ?? []).filter((a: any) => (a.role ?? '') !== 'requester').map((a: any) => String(a.resolved ?? a.label ?? '')).filter(Boolean);
      const stepObjs = Array.isArray((e as any).steps)
        ? uniqueStrings((e as any).steps.flatMap((s: any) => stepEntityObjects(s)))
        : [];
      const objs = stepObjs.length
        ? stepObjs
        : eventEntityObjects(e);
      const numMentions = numericMentionsForEvent(e);
      const nums = numMentions.map((m) => m.label);
      const numKeys = numMentions.map((m) => m.key);
      const srcs = sourceLabelsForEvent(e);
      const lenses = lensLabelsForEvent(e);
      const numericClaims = Array.isArray((e as any).numeric_claims)
        ? uniqueStrings(
            (e as any).numeric_claims.map((c: any) => {
              const key = String(c?.key ?? '').trim();
              const role = String(c?.role ?? '').trim();
              const exprScale = String(c?.normalized?.expression?.scale_word ?? '').trim();
              const exprExp = c?.normalized?.expression?.exponent_from_scale;
              const surfSpacing = String(c?.normalized?.surface?.spacing_pattern ?? '').trim();
              const years = Array.isArray(c?.time_years) ? c.time_years.map((x: any) => String(x ?? '').trim()).filter(Boolean).join(',') : '';
              const ta = c?.time_anchor && typeof c.time_anchor === 'object'
                ? [c.time_anchor.year, c.time_anchor.month, c.time_anchor.day]
                    .filter((x: any) => x !== null && x !== undefined && String(x).trim() !== '')
                    .map((x: any) => String(x))
                    .join('-')
                : '';
              const bits = [
                key,
                role ? `role=${role}` : '',
                exprScale ? `scale=${exprScale}` : '',
                Number.isFinite(exprExp) ? `exp=${String(exprExp)}` : '',
                surfSpacing ? `spacing=${surfSpacing}` : '',
                years ? `years=${years}` : '',
                ta ? `anchor=${ta}` : ''
              ]
                .filter(Boolean)
                .join(' ');
              return bits;
            })
          )
        : [];
      const stepActs = Array.isArray((e as any).steps)
        ? uniqueStrings((e as any).steps.map((s: any) => actionLabel(s?.action, s?.negation)).filter(Boolean))
        : [];
      const citations = Array.isArray((e as any).citations)
        ? uniqueStrings((e as any).citations.map((c: any) => String(c?.text ?? '')).filter(Boolean))
        : [];
      const citationFollowers = Array.isArray((e as any).citations) ? collectFollowProviders((e as any).citations) : [];
      const slRefs = Array.isArray((e as any).sl_references)
        ? uniqueStrings(
            (e as any).sl_references
              .map((r: any) => String(r?.text ?? `${r?.authority ?? ''} ${r?.ref_value ?? ''}`.trim()))
              .filter(Boolean)
          )
        : [];
      const slRefFollowers = Array.isArray((e as any).sl_references) ? collectFollowProviders((e as any).sl_references) : [];
      const party = String((e as any).party ?? '').trim();
      const tocContext = Array.isArray((e as any).toc_context)
        ? uniqueStrings(
            (e as any).toc_context
              .map((t: any) => String(t?.path ?? `${t?.identifier ?? ''} ${t?.title ?? ''}`.trim()))
              .filter(Boolean)
          )
        : [];
      const legalMarkers = (() => {
        const m = (e as any).legal_section_markers;
        if (!m || typeof m !== 'object') return [] as string[];
        return uniqueStrings([
          ...((Array.isArray(m.citation_prefixes) ? m.citation_prefixes : []).map((x: any) => `cit:${String(x)}`)),
          ...((Array.isArray(m.sl_reference_lanes) ? m.sl_reference_lanes : []).map((x: any) => `lane:${String(x)}`)),
          ...((Array.isArray(m.provision_stable_ids) ? m.provision_stable_ids : []).map((x: any) => `prov:${String(x)}`)),
          ...((Array.isArray(m.rule_atom_stable_ids) ? m.rule_atom_stable_ids : []).map((x: any) => `atom:${String(x)}`))
        ]);
      })();
      const hasLegalSignals = legalMarkers.length > 0 || slRefs.length > 0;
      const checkNext = uniqueStrings([
        ...citationFollowers,
        ...slRefFollowers,
        ...(citations.length || slRefs.length ? ['wikipedia', 'wiki_connector', 'source_document', 'source_pdf'] : []),
        ...(hasLegalSignals ? ['austlii', 'jade'] : []),
        ...(citations.length || slRefs.length ? DEFAULT_FOLLOW_ORDER : [])
      ]);
      const factRows = Array.isArray((e as any).timeline_facts)
        ? uniqueStrings(
            (e as any).timeline_facts.map((f: any) => {
              const fa = factAnchorKey(f?.anchor);
              const subs = Array.isArray(f?.subjects) ? f.subjects.join(', ') : '';
              const act = actionLabel(f?.action, f?.negation);
              const objs = Array.isArray(f?.objects) ? f.objects.join(', ') : '';
              const nums = Array.isArray(f?.numeric_objects) ? f.numeric_objects.join(', ') : '';
              return `${fa} | ${subs}${act && act !== '(no action matched)' ? ' -> ' + act : ''}${objs ? ' -> ' + objs : ''}${nums ? ' -> #' + nums : ''}`.trim();
            })
          )
        : [];
      const firstFactTime = Array.isArray((e as any).timeline_facts) && (e as any).timeline_facts.length
        ? factAnchorKey((e as any).timeline_facts[0]?.anchor)
        : '';
      const connected = uniqueStrings([
        ...reqs.map((x: string) => `req:${x}`),
        ...subs.map((x: string) => `sub:${x}`),
        ...stepActs.map((x: string) => `act:${x}`),
        ...objs.map((x: string) => `obj:${x}`),
        ...numKeys.map((x: string) => `num:${x}`),
        ...evidenceLabelsFromEvent(e).map((x: string) => `evd:${x}`),
        ...srcs.map((x: string) => `src:${x}`),
        ...lenses.map((x: string) => `lens:${x}`)
      ]);
      rows.push({
        key: `${selectedNodeId}:${eventId}:${instance}`,
        instance,
        event_id: eventId,
        time: timeKeyForEvent(e, 'day'),
        section: e.section ?? '',
        text: e.text ?? '',
        requesters: reqs,
        subjects: subs,
        action: typeof e.action === 'string' ? e.action : null,
        negation: (e as any).negation && typeof (e as any).negation.kind === 'string' ? (e as any).negation : undefined,
        actions: stepActs,
        objects: objs,
        numerics: nums,
        numericClaims,
        sources: srcs,
        lenses: lenses,
        citations,
        checkNext,
        slRefs,
        party,
        tocContext,
        legalMarkers,
        factRows,
        sortTime: firstFactTime || timeKeyForEvent(e, 'day'),
        connected,
        purpose: typeof e.purpose === 'string' ? e.purpose : null
      });
    }
    // Keep chronological-ish by time bucket, then event_id.
    if (orderByFactDate) {
      rows.sort((a, b) => a.sortTime.localeCompare(b.sortTime) || a.event_id.localeCompare(b.event_id));
    } else {
      rows.sort((a, b) => a.time.localeCompare(b.time) || a.event_id.localeCompare(b.event_id));
    }
    return rows;
  })();

  $: contextRowsShown = showAllContextRows ? contextRows : contextRows.slice(0, 80);

  $: contextNeedle = (() => {
    const id = selectedNodeId ?? '';
    if (!id) return '';
    if (id.startsWith('time:')) return id.split(':').slice(-1)[0] ?? '';
    if (id.startsWith('act:')) return '';
    if (id.startsWith('sub:')) return id.slice('sub:'.length);
    if (id.startsWith('req:')) return id.slice('req:'.length);
    if (id.startsWith('obj:')) return id.slice('obj:'.length);
    if (id.startsWith('num:')) {
      const key = id.slice('num:'.length);
      return numericLabelByKey.get(key) ?? numericLabelFromKey(key);
    }
    if (id.startsWith('evd:')) return id.slice('evd:'.length);
    if (id.startsWith('src:')) return id.slice('src:'.length);
    if (id.startsWith('lens:')) return id.slice('lens:'.length);
    return '';
  })();

  afterUpdate(() => {
    if (!contextBox || !selectedNodeId) return;
    const k = `${selectedNodeId}:${contextRowsShown[0]?.event_id ?? ''}`;
    if (!k || k === lastScrollKey) return;
    lastScrollKey = k;
    const first = contextRowsShown[0];
    if (!first) return;
    const el = contextBox.querySelector(`[data-ctx-id="${first.event_id}"]`);
    if (el && 'scrollIntoView' in el) (el as HTMLElement).scrollIntoView({ block: 'center' });
  });

  $: graph = (() => {
    const yearNodes = new Map<string, LayerNode>();
    const monthNodes = new Map<string, LayerNode>();
    const dayNodes = new Map<string, LayerNode>();

    const subjectCount = new Map<string, number>();
    const objectCount = new Map<string, number>();
    const numericCount = new Map<string, number>();
    const sourceCount = new Map<string, number>();
    const lensCount = new Map<string, number>();
    const requesterCount = new Map<string, number>();
    const evidenceCount = new Map<string, number>();

    for (const e of graphEvents) {
      const y = String(e.anchor.year || 0);
      yearNodes.set(y, node(`time:y:${y}`, y, '#e8f4ff', 'Year bucket (non-authoritative)'));
      if (timeGranularity !== 'year' && e.anchor.month) {
        const ym = fmtYM(e.anchor);
        monthNodes.set(ym, node(`time:m:${ym}`, ym, '#e8f4ff', 'Month bucket (non-authoritative)'));
      }
      if (timeGranularity === 'day' && e.anchor.month && e.anchor.day) {
        const ymd = fmtYMD(e.anchor);
        dayNodes.set(ymd, node(`time:d:${ymd}`, ymd, '#e8f4ff', 'Day bucket (non-authoritative)'));
      }

      for (const a of e.actors ?? []) {
        const key = a.resolved || a.label;
        if (!key) continue;
        if (a.role === 'requester') requesterCount.set(key, (requesterCount.get(key) ?? 0) + 1);
      }
      const stepSubs = Array.isArray((e as any).steps)
        ? uniqueStrings((e as any).steps.flatMap((s: any) => (Array.isArray(s?.subjects) ? s.subjects : [])))
        : [];
      const uniqueSubs = stepSubs.length
        ? stepSubs
        : uniqueStrings((e.actors ?? []).filter((a: any) => (a.role ?? '') !== 'requester').map((a: any) => a.resolved ?? a.label));
      for (const key of uniqueSubs) subjectCount.set(key, (subjectCount.get(key) ?? 0) + 1);
      const stepObjsForCounts = Array.isArray((e as any).steps)
        ? uniqueStrings((e as any).steps.flatMap((s: any) => stepEntityObjects(s)))
        : [];
      const objKeys = stepObjsForCounts.length
        ? stepObjsForCounts
        : uniqueStrings(eventEntityObjects(e));
      for (const key of objKeys) objectCount.set(key, (objectCount.get(key) ?? 0) + 1);
      for (const m of numericMentionsForEvent(e)) numericCount.set(m.key, (numericCount.get(m.key) ?? 0) + 1);
      for (const src of sourceLabelsForEvent(e)) sourceCount.set(src, (sourceCount.get(src) ?? 0) + 1);
      for (const lens of lensLabelsForEvent(e)) lensCount.set(lens, (lensCount.get(lens) ?? 0) + 1);
      for (const ev of evidenceLabelsFromEvent(e)) evidenceCount.set(ev, (evidenceCount.get(ev) ?? 0) + 1);
    }

    const top = (m: Map<string, number>, n: number) =>
      Array.from(m.entries())
        .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
        .slice(0, Math.max(0, Math.floor(n)));

    const topSubjects = top(subjectCount, maxSubjects);
    const topObjects = top(objectCount, maxObjects);
    const topNumbers = top(numericCount, maxNumbers).sort(compareNumericLaneEntries);
    const topSources = includeSources ? top(sourceCount, Math.max(10, maxSources)) : [];
    const topLenses = includeLenses ? top(lensCount, Math.max(10, maxLenses)) : [];
    const topRequesters = includeRequesters ? top(requesterCount, Math.min(60, maxSubjects)) : [];
    const topEvidence = includeEvidence ? top(evidenceCount, maxEvidence) : [];

    const subjectSet = new Set(topSubjects.map(([k]) => k));
    const objectSet = new Set(topObjects.map(([k]) => k));
    const numericSet = new Set(topNumbers.map(([k]) => k));
    const sourceSet = new Set(topSources.map(([k]) => k));
    const lensSet = new Set(topLenses.map(([k]) => k));
    const requesterSet = new Set(topRequesters.map(([k]) => k));
    const evidenceSet = new Set(topEvidence.map(([k]) => k));

    const missingRequesterIdsInWindow = uniqueStrings(
      (graphEvents ?? [])
        .map((e: any) => String(e?.event_id ?? ''))
        .filter((eventId: string) => Boolean(eventId) && missingRequesterEventIdSet.has(eventId))
    );
    const requesterNodes = topRequesters.map(([k, c]) => node(`req:${k}`, `${k} (${c})`, '#e9d5ff'));
    const subjectNodes = topSubjects.map(([k, c]) => node(`sub:${k}`, `${k} (${c})`, '#bbf7d0'));
    const objectNodes = topObjects.map(([k, c]) => node(`obj:${k}`, `${k} (${c})`, '#f6f6f6'));
    const numericNodes = topNumbers.map(([k, c]) => {
      const label = numericLabelByKey.get(k) ?? numericLabelFromKey(k);
      return node(`num:${k}`, `${label} (${c})`, '#fee2e2', `key=${k}`);
    });
    const sourceNodes = topSources.map(([k, c]) => node(`src:${k}`, `${k} (${c})`, '#d1fae5'));
    const lensNodes = topLenses.map(([k, c]) => node(`lens:${k}`, `${k} (${c})`, '#ede9fe'));
    const evidenceNodes = topEvidence.map(([k, c]) => node(`evd:${k}`, `${k} (${c})`, '#dbeafe'));

    const actionNodes: LayerNode[] = [];
    const purposeNodes: LayerNode[] = [];

    const edges: LayeredEdge[] = [];

    // Time chain edges (unique, no per-event duplication).
    if (timeGranularity !== 'year') {
      for (const ym of monthNodes.keys()) {
        const y = ym.split('-')[0] ?? ym;
        edges.push({ from: `time:y:${y}`, to: `time:m:${ym}`, kind: 'sequence' });
      }
    }
    if (timeGranularity === 'day') {
      for (const ymd of dayNodes.keys()) {
        const ym = ymd.slice(0, 7);
        edges.push({ from: `time:m:${ym}`, to: `time:d:${ymd}`, kind: 'sequence' });
      }
    }

    for (const e of graphEvents) {
      const actionText = actionLabel(e.action, (e as any).negation);
      const snippet = e.text.length > 58 ? e.text.slice(0, 58) + '...' : e.text;
      const actId = `act:${e.event_id}`;
      const stepActs = Array.isArray((e as any).steps)
        ? (e as any).steps.map((s: any) => actionLabel(s?.action, s?.negation)).filter(Boolean)
        : [];
      const actionPathLabel = stepActs.length > 1 ? stepActs.join(' -> ') : actionText;
      actionNodes.push(node(actId, `${actionPathLabel}: ${snippet}`, '#fde68a', `${e.event_id} | ${e.anchor.text} | section=${e.section}`));

      // Time -> action (attach at most specific available for selected granularity).
      const y = String(e.anchor.year || 0);
      const ym = fmtYM(e.anchor);
      const ymd = fmtYMD(e.anchor);
      const t =
        timeGranularity === 'day' && e.anchor.month && e.anchor.day
          ? `time:d:${ymd}`
          : timeGranularity !== 'year' && e.anchor.month
            ? `time:m:${ym}`
            : `time:y:${y}`;
      edges.push({ from: t, to: actId, kind: 'sequence' });

      // Requester/subjects -> action (filtered by top sets for UI sanity).
      for (const a of e.actors ?? []) {
        const key = a.resolved || a.label;
        if (!key) continue;
        if (a.role === 'requester') {
          if (includeRequesters && requesterSet.has(key)) edges.push({ from: `req:${key}`, to: actId, kind: 'role' });
        }
      }
      const edgeSubs = Array.isArray((e as any).steps)
        ? uniqueStrings((e as any).steps.flatMap((s: any) => (Array.isArray(s?.subjects) ? s.subjects : [])))
        : [];
      const uniqueEdgeSubs = edgeSubs.length
        ? edgeSubs
        : uniqueStrings((e.actors ?? []).filter((a: any) => (a.role ?? '') !== 'requester').map((a: any) => a.resolved ?? a.label));
      for (const key of uniqueEdgeSubs) if (subjectSet.has(key)) edges.push({ from: `sub:${key}`, to: actId, kind: 'role' });

      // Action -> objects (frame/step-scoped first; event-global fallback only when steps absent).
      const edgeObjs = Array.isArray((e as any).steps)
        ? uniqueStrings((e as any).steps.flatMap((s: any) => stepEntityObjects(s)))
        : [];
      const edgeObjKeys = edgeObjs.length
        ? edgeObjs
        : uniqueStrings(eventEntityObjects(e));
      for (const key of edgeObjKeys) if (objectSet.has(key)) edges.push({ from: actId, to: `obj:${key}`, kind: 'role' });
      for (const m of numericMentionsForEvent(e)) if (numericSet.has(m.key)) edges.push({ from: actId, to: `num:${m.key}`, kind: 'role' });
      if (includeSources) {
        for (const src of sourceLabelsForEvent(e)) {
          if (sourceSet.has(src)) edges.push({ from: `src:${src}`, to: actId, kind: 'context' });
        }
      }
      if (includeLenses) {
        for (const lens of lensLabelsForEvent(e)) {
          if (lensSet.has(lens)) edges.push({ from: `lens:${lens}`, to: actId, kind: 'context' });
        }
      }

      if (includeEvidence) {
        const evidenceKeys = evidenceLabelsFromEvent(e);
        for (const key of evidenceKeys) {
          if (!evidenceSet.has(key)) continue;
          edges.push({ from: actId, to: `evd:${key}`, kind: 'evidence' });
        }
      }

      if (includePurpose && e.purpose) {
        const pid = `pur:${e.event_id}`;
        purposeNodes.push(node(pid, e.purpose, '#fef3c7'));
        edges.push({ from: actId, to: pid, kind: 'role' });
      }
    }

    const layers: Array<{ id: string; title: string; nodes: LayerNode[] }> = [
      { id: 'year', title: 'Year', nodes: Array.from(yearNodes.values()).sort((a, b) => a.id.localeCompare(b.id)) }
    ];
    if (timeGranularity !== 'year') {
      layers.push({ id: 'month', title: 'Month', nodes: Array.from(monthNodes.values()).sort((a, b) => a.id.localeCompare(b.id)) });
    }
    if (timeGranularity === 'day') {
      layers.push({ id: 'day', title: 'Day', nodes: Array.from(dayNodes.values()).sort((a, b) => a.id.localeCompare(b.id)) });
    }
    if (includeSources) layers.push({ id: 'src', title: 'Source', nodes: sourceNodes.length ? sourceNodes : [node('src:none', '(none)', '#ffffff')] });
    if (includeLenses) layers.push({ id: 'lens', title: 'Lens', nodes: lensNodes.length ? lensNodes : [node('lens:none', '(none)', '#ffffff')] });
    if (includeRequesters) {
      const reqLane: LayerNode[] = [];
      if (requesterNodes.length) reqLane.push(...requesterNodes);
      if (missingRequesterEventIdSet.size) {
        const ids = Array.from(missingRequesterEventIdSet.values());
        const sample = ids.slice(0, 30).join(', ');
        const suffix = ids.length > 30 ? ` (+${ids.length - 30} more)` : '';
        reqLane.push(
          node(
            'req:missing',
            `(missing requester: ${missingRequesterEventIdSet.size})`,
            '#fff7ed',
            ids.length ? `Request-signal events missing requester: ${sample}${suffix}` : 'Request-signal events missing requester'
          )
        );
      }
      if (reqLane.length) layers.push({ id: 'req', title: 'Requester', nodes: reqLane });
    }
    layers.push({ id: 'sub', title: 'Subjects', nodes: subjectNodes.length ? subjectNodes : [node('sub:none', '(none)', '#ffffff')] });
    layers.push({ id: 'act', title: 'Action', nodes: actionNodes.length ? actionNodes : [node('act:none', '(none)', '#ffffff')] });
    layers.push({ id: 'obj', title: 'Objects', nodes: objectNodes.length ? objectNodes : [node('obj:none', '(none)', '#ffffff')] });
    layers.push({ id: 'num', title: 'Numeric', nodes: numericNodes.length ? numericNodes : [node('num:none', '(none)', '#ffffff')] });
    if (includeEvidence) layers.push({ id: 'evd', title: 'Evidence', nodes: evidenceNodes.length ? evidenceNodes : [node('evd:none', '(none)', '#ffffff')] });
    if (includePurpose) layers.push({ id: 'pur', title: 'Purpose', nodes: purposeNodes.length ? purposeNodes : [node('pur:none', '(none)', '#ffffff')] });

    return { layers, edges };
  })();
</script>

<div class="space-y-4 p-6">
  <Panel>
    <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Wiki timeline AAO: whole-article combined</div>
    <div class="mt-2 text-sm text-ink-950">
      Timeline input: <span class="font-mono text-xs">{data.relPath}</span>
    </div>
    <div class="mt-2 text-xs text-ink-800/60">
      DB run: <span class="font-mono break-all">{data.payload.run_id ?? '(unknown)'}</span>
      <span class="mx-2">|</span>
      stored timeline_path: <span class="font-mono break-all">{(data.payload.source_timeline as any)?.path ?? '(unknown)'}</span>
      <span class="mx-2">|</span>
      loaded_from_db: <span class="font-mono">{data.payload.__loaded_from_db ? 'true' : 'false'}</span>
    </div>
    <div class="mt-2 text-xs text-ink-800/60">
      Union graph over many sentence-local AAO extractions. Non-causal. Non-authoritative.
    </div>

    <div class="mt-4 flex flex-wrap items-center gap-3 text-sm">
      <label class="flex items-center gap-2">
        <span class="text-ink-800/70">Dataset</span>
        <select
          class="rounded-md border border-ink-950/15 bg-white px-2 py-1 text-sm"
          value={data.source ?? 'gwb'}
          aria-label="Dataset source"
          on:change={(e) => {
            const v = (e.currentTarget as HTMLSelectElement).value;
            window.location.href = `/graphs/wiki-timeline-aoo-all?source=${encodeURIComponent(v)}`;
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
      <label class="flex items-center gap-2">
        <span class="text-ink-800/70">Time</span>
        <select bind:value={timeGranularity} class="rounded-md border border-ink-950/15 bg-white px-2 py-1 text-sm" aria-label="Time granularity">
          <option value="year">Year</option>
          <option value="month">Month</option>
          <option value="day">Day</option>
        </select>
      </label>
      <label class="flex items-center gap-2">
        <span class="text-ink-800/70">Events</span>
        <input
          type="number"
          min="10"
          max={eventsAll.length}
          step="5"
          bind:value={limitEvents}
          class="w-24 rounded-md border border-ink-950/15 px-2 py-1 font-mono text-xs"
          aria-label="Max events"
        />
      </label>
      <label class="flex items-center gap-2">
        <span class="text-ink-800/70">Max subjects</span>
        <input type="number" min="10" max="400" step="10" bind:value={maxSubjects} class="w-24 rounded-md border border-ink-950/15 px-2 py-1 font-mono text-xs" aria-label="Max subjects" />
      </label>
      <label class="flex items-center gap-2">
        <span class="text-ink-800/70">Max objects</span>
        <input type="number" min="10" max="600" step="10" bind:value={maxObjects} class="w-24 rounded-md border border-ink-950/15 px-2 py-1 font-mono text-xs" aria-label="Max objects" />
      </label>
      <label class="flex items-center gap-2">
        <span class="text-ink-800/70">Max numeric</span>
        <input type="number" min="10" max="600" step="10" bind:value={maxNumbers} class="w-24 rounded-md border border-ink-950/15 px-2 py-1 font-mono text-xs" aria-label="Max numeric values" />
      </label>
      <label class="flex items-center gap-2">
        <input type="checkbox" bind:checked={includeSources} aria-label="Show source lane" />
        <span class="text-ink-800/70">Source lane</span>
      </label>
      {#if includeSources}
        <label class="flex items-center gap-2">
          <span class="text-ink-800/70">Max sources</span>
          <input type="number" min="10" max="400" step="10" bind:value={maxSources} class="w-24 rounded-md border border-ink-950/15 px-2 py-1 font-mono text-xs" aria-label="Max sources" />
        </label>
      {/if}
      <label class="flex items-center gap-2">
        <input type="checkbox" bind:checked={includeLenses} aria-label="Show lens lane" />
        <span class="text-ink-800/70">Lens lane</span>
      </label>
      {#if includeLenses}
        <label class="flex items-center gap-2">
          <span class="text-ink-800/70">Max lenses</span>
          <input type="number" min="10" max="500" step="10" bind:value={maxLenses} class="w-24 rounded-md border border-ink-950/15 px-2 py-1 font-mono text-xs" aria-label="Max lenses" />
        </label>
      {/if}
      <label class="flex items-center gap-2">
        <input type="checkbox" bind:checked={includeEvidence} aria-label="Show evidence lane" />
        <span class="text-ink-800/70">Evidence lane</span>
      </label>
      {#if includeEvidence}
        <label class="flex items-center gap-2">
          <span class="text-ink-800/70">Max evidence</span>
          <input type="number" min="10" max="400" step="10" bind:value={maxEvidence} class="w-24 rounded-md border border-ink-950/15 px-2 py-1 font-mono text-xs" aria-label="Max evidence" />
        </label>
      {/if}
      <label class="flex items-center gap-2">
        <input type="checkbox" bind:checked={includeRequesters} aria-label="Show requesters" />
        <span class="text-ink-800/70">Requesters</span>
      </label>
      <label class="flex items-center gap-2">
        <input type="checkbox" bind:checked={includePurpose} aria-label="Show purpose" />
        <span class="text-ink-800/70">Purpose</span>
      </label>
      <label class="flex items-center gap-2">
        <input type="checkbox" bind:checked={orderByFactDate} />
        <span class="text-ink-800/70">Fact-date order</span>
      </label>
      <a
        class="rounded-md border border-ink-950/15 px-2 py-1 text-xs text-ink-950 hover:border-ink-950/30 hover:bg-ink-950/[0.03]"
        href={`/graphs/wiki-timeline?source=${encodeURIComponent(data.source ?? 'gwb')}`}
      >
        Open Timeline
      </a>
      <a
        class="rounded-md border border-ink-950/15 px-2 py-1 text-xs text-ink-950 hover:border-ink-950/30 hover:bg-ink-950/[0.03]"
        href={`/graphs/wiki-timeline-aoo?source=${encodeURIComponent(data.source ?? 'gwb')}`}
      >
        Open AAO
      </a>
      <a
        class="rounded-md border border-ink-950/15 px-2 py-1 text-xs text-ink-950 hover:border-ink-950/30 hover:bg-ink-950/[0.03]"
        href={`/graphs/wiki-timeline-aoo?source=${encodeURIComponent(data.source ?? 'gwb')}&view=step-ribbon`}
      >
        Open Step-Ribbon
      </a>
      <a
        class="rounded-md border border-ink-950/15 px-2 py-1 text-xs text-ink-950 hover:border-ink-950/30 hover:bg-ink-950/[0.03]"
        href={`/graphs/wiki-fact-timeline?source=${encodeURIComponent(data.source ?? 'gwb')}`}
      >
        Open Fact Timeline
      </a>
    </div>
  </Panel>

  {#if (data.corpusDocs ?? []).length}
    {@const ref = referencedCorpusPaths()}
    {@const refCount = ref.size}
    <Panel>
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div>
          <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Corpus docs</div>
          <div class="mt-1 text-xs text-ink-800/60">
            root: <span class="font-mono">SensibLaw/demo/ingest/gwb</span> | files:{' '}
            <span class="font-mono">{(data.corpusDocs ?? []).length}</span>
            <span class="mx-2">|</span>
            follow_hints_in_run: <span class="font-mono">{refCount}</span>
          </div>
        </div>
      </div>
      {#if refCount === 0}
        <div class="mt-2 text-xs text-ink-800/70">
          This selected dataset/run emitted no citation/sl_ref follow hints, so everything below will show as <span class="font-mono">unreferenced</span>.
          If you want the corpus files to appear as sources, switch Dataset to <span class="font-mono">gwb_corpus_v1</span>.
        </div>
      {/if}
      <div class="mt-3 flex flex-wrap gap-2 text-[11px]">
        {#each data.corpusDocs ?? [] as d (d.relPath)}
          {@const isRef = refHasDoc(ref, d.relPath, d.name)}
          <span
            class={`inline-flex items-center gap-2 rounded ring-1 ring-ink-900/10 px-2 py-1 ${
              isRef ? 'bg-emerald-50' : 'bg-paper-100'
            }`}
          >
            <span class="font-mono text-ink-900">{d.name}</span>
            <span class="font-mono text-ink-800/60">{d.ext}</span>
            <span class="font-mono text-ink-800/60">{fmtBytes(d.bytes)}</span>
            <span
              class={`rounded px-1.5 py-0.5 font-mono ${
                isRef ? 'bg-emerald-200/60 text-emerald-900' : 'bg-ink-950/5 text-ink-800/70'
              }`}
              title={d.relPath}
            >
              {isRef ? 'referenced' : 'unreferenced'}
            </span>
          </span>
        {/each}
      </div>
      <div class="mt-2 text-xs text-ink-800/60">
        \"Referenced\" means the current AAO run emitted a citation/sl_ref follow hint pointing at that file path/URL. It does not guarantee we extracted semantic events from the doc content.
      </div>
    </Panel>
  {/if}

  {#if data.error}
    <Panel tone="danger">
      <div class="text-xs uppercase tracking-[0.28em] text-red-800/80">Load error</div>
      <pre class="mt-3 whitespace-pre-wrap font-mono text-xs text-ink-950">{data.error}</pre>
    </Panel>
  {/if}

  <LayeredGraph
    layers={graph.layers}
    edges={graph.edges}
    width={graphWidth}
    height={GRAPH_HEIGHT}
    colGap={GRAPH_COL_GAP}
    leftPad={GRAPH_LEFT_PAD}
    fitToWidth={false}
    scrollWhenOverflow={true}
    viewportResetKey={graphViewportKey}
    on:nodeSelect={(e) => (selectedNodeId = (e as CustomEvent<{ nodeId: string }>).detail.nodeId)}
  />

  <Panel>
    <div class="flex flex-wrap items-center justify-between gap-3">
      <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Context</div>
      <div class="flex flex-wrap items-center gap-3 text-[11px] font-mono text-ink-800/60">
        {#if selectedNodeId}
          <span>selected: {selectedNodeId}</span>
          {#if contextRows.length > 80}
            <label class="inline-flex items-center gap-1 rounded border border-ink-950/10 bg-white px-2 py-0.5">
              <input type="checkbox" bind:checked={showAllContextRows} />
              <span>all rows ({contextRows.length})</span>
            </label>
          {:else}
            <span>rows: {contextRows.length}</span>
          {/if}
        {:else}
          <span>click a node to preview the relevant extracted timeline text</span>
        {/if}
      </div>
    </div>

    <div class="mt-3 max-h-[320px] overflow-auto rounded-lg border border-ink-950/10 bg-white" bind:this={contextBox}>
      {#if !selectedNodeId}
        <div class="p-3 text-xs text-ink-800/70">
          This panel shows sentence-local timeline evidence for the selected node (from the extracted timeline substrate, not the full Wikipedia article).
        </div>
      {:else}
        {#if selectedNodeId === 'req:missing'}
          <div class="border-b border-ink-950/10 bg-amber-50/40 p-3 text-[11px]">
            <div class="font-mono text-ink-900">
              requester_window: signal={requesterCoverageWindow.requestSignalEvents} requester={requesterCoverageWindow.requesterEvents}
              missing={requesterCoverageWindow.missingRequesterEventIds.length} total={requesterCoverageWindow.totalEvents}
            </div>
            {#if requesterCoverageGlobal}
              <div class="mt-1 font-mono text-ink-900">
                requester_global: signal={requesterCoverageGlobal.requestSignalEvents} requester={requesterCoverageGlobal.requesterEvents}
                missing={requesterCoverageGlobal.missingRequesterEventIds.length} total={requesterCoverageGlobal.totalEvents}
              </div>
            {:else}
              <div class="mt-1 font-mono text-ink-800/70">requester_global: unavailable (payload missing requester_coverage)</div>
            {/if}
            <div class="mt-2 flex flex-wrap gap-2 font-mono">
              {#if requesterCoverageWindowGap}
                <span class="rounded bg-red-100 px-1.5 py-0.5 text-red-900">window_gap: request-signal events exceed requester-tagged events</span>
              {:else}
                <span class="rounded bg-emerald-100 px-1.5 py-0.5 text-emerald-900">window_gap: none</span>
              {/if}
              {#if requesterCoverageGlobalGap}
                <span class="rounded bg-red-100 px-1.5 py-0.5 text-red-900">global_gap: request-signal events exceed requester-tagged events</span>
              {:else if requesterCoverageGlobal}
                <span class="rounded bg-emerald-100 px-1.5 py-0.5 text-emerald-900">global_gap: none</span>
              {/if}
            </div>
            {#if requesterCoverageWindow.missingRequesterEventIds.length}
              <div class="mt-2">
                <span class="font-mono text-ink-800/60">window_missing_ids</span>
                {#each requesterCoverageWindow.missingRequesterEventIds as x (x)}
                  <span class="ml-1 inline-block rounded bg-red-50 px-1.5 py-0.5 font-mono text-red-900">{x}</span>
                {/each}
              </div>
            {:else if requesterCoverageGlobal?.missingRequesterEventIds.length}
              <div class="mt-2">
                <span class="font-mono text-ink-800/60">global_missing_ids</span>
                {#each requesterCoverageGlobal.missingRequesterEventIds.slice(0, 24) as x (x)}
                  <span class="ml-1 inline-block rounded bg-red-50 px-1.5 py-0.5 font-mono text-red-900">{x}</span>
                {/each}
              </div>
            {/if}
          </div>
        {/if}
        {#if !contextRows.length}
          <div class="p-3 text-xs text-ink-800/70">No matching extracted timeline rows for this node in the current event window.</div>
        {:else}
          {#each contextRowsShown as r (r.key)}
            <div class="border-b border-ink-950/10 p-3 last:border-b-0" data-ctx-id={r.event_id}>
            <div class="flex flex-wrap items-center justify-between gap-2">
              <div class="font-mono text-[10px] text-ink-800/60">{r.time} {r.event_id}</div>
              <div class="font-mono text-[10px] text-ink-800/60">section={r.section}</div>
            </div>
            <div class="mt-2 flex flex-wrap items-center gap-2 text-[11px] text-ink-950">
              {#if r.requesters.length}
                {#each r.requesters as x (r.event_id + ':req:' + x)}
                  <span class="rounded bg-purple-100 px-1.5 py-0.5 font-mono">[{x}]</span>
                {/each}
                <span class="font-mono text-ink-800/50">request</span>
              {/if}
              {#if r.subjects.length}
                {#each r.subjects as x (r.event_id + ':sub:' + x)}
                  <span class="rounded bg-emerald-100 px-1.5 py-0.5 font-mono">[{x}]</span>
                {/each}
                <span class="font-mono text-ink-800/50">do</span>
              {/if}
              {#if r.actions.length}
                {#each r.actions as a (r.event_id + ':act:' + a)}
                  <span class="rounded bg-amber-100 px-1.5 py-0.5 font-mono">[{a}]</span>
                {/each}
              {:else}
                <span class="rounded bg-amber-100 px-1.5 py-0.5 font-mono">[{actionLabel(r.action, r.negation)}]</span>
              {/if}
              {#if r.objects.length}
                <span class="font-mono text-ink-800/50">object</span>
                {#each r.objects as x (r.event_id + ':obj:' + x)}
                  <span class="rounded bg-slate-100 px-1.5 py-0.5 font-mono">[{x}]</span>
                {/each}
              {/if}
              {#if r.numerics.length}
                <span class="font-mono text-ink-800/50">numeric</span>
                {#each r.numerics as x (r.event_id + ':num:' + x)}
                  <span class="rounded bg-rose-100 px-1.5 py-0.5 font-mono">[{x}]</span>
                {/each}
              {/if}
              {#if r.purpose}
                <span class="font-mono text-ink-800/50">purpose</span>
                <span class="rounded bg-yellow-50 px-1.5 py-0.5 font-mono">[{r.purpose}]</span>
              {/if}
            </div>
            {#if r.connected.length}
              <div class="mt-2 text-[11px]">
                <span class="font-mono text-ink-800/50">connected</span>
                {#each r.connected as x (r.event_id + ':conn:' + x)}
                  <span class="ml-1 inline-block rounded bg-slate-50 px-1.5 py-0.5 font-mono text-ink-900">{x}</span>
                {/each}
              </div>
            {/if}
            {#if r.numericClaims.length}
              <div class="mt-2 text-[11px]">
                <span class="font-mono text-ink-800/50">numeric_claims</span>
                {#each r.numericClaims.slice(0, 8) as x (r.event_id + ':nclaim:' + x)}
                  <span class="ml-1 inline-block rounded bg-rose-50 px-1.5 py-0.5 font-mono text-ink-900">{x}</span>
                {/each}
              </div>
            {/if}
            {#if r.sources.length}
              <div class="mt-2 text-[11px]">
                <span class="font-mono text-ink-800/50">sources</span>
                {#each r.sources.slice(0, 8) as x (r.event_id + ':src:' + x)}
                  <span class="ml-1 inline-block rounded bg-emerald-50 px-1.5 py-0.5 font-mono text-ink-900">{x}</span>
                {/each}
              </div>
            {/if}
            {#if r.lenses.length}
              <div class="mt-2 text-[11px]">
                <span class="font-mono text-ink-800/50">lenses</span>
                {#each r.lenses.slice(0, 8) as x (r.event_id + ':lens:' + x)}
                  <span class="ml-1 inline-block rounded bg-violet-50 px-1.5 py-0.5 font-mono text-ink-900">{x}</span>
                {/each}
              </div>
            {/if}
            {#if r.slRefs.length}
              <div class="mt-2 text-[11px]">
                <span class="font-mono text-ink-800/50">sl_refs</span>
                {#each r.slRefs.slice(0, 6) as x (r.event_id + ':sl:' + x)}
                  <span class="ml-1 inline-block rounded bg-blue-50 px-1.5 py-0.5 font-mono text-ink-900">{x}</span>
                {/each}
              </div>
            {/if}
            {#if r.checkNext.length}
              <div class="mt-2 text-[11px]">
                <span class="font-mono text-ink-800/50">check_next</span>
                {#each r.checkNext as x (r.event_id + ':next:' + x)}
                  <span class="ml-1 inline-block rounded bg-violet-50 px-1.5 py-0.5 font-mono text-ink-900">{x}</span>
                {/each}
              </div>
            {/if}
            {#if r.party}
              <div class="mt-2 text-[11px]">
                <span class="font-mono text-ink-800/50">party</span>
                <span class="ml-1 inline-block rounded bg-emerald-50 px-1.5 py-0.5 font-mono text-ink-900">{r.party}</span>
              </div>
            {/if}
            {#if r.tocContext.length}
              <div class="mt-2 text-[11px]">
                <span class="font-mono text-ink-800/50">toc</span>
                {#each r.tocContext.slice(0, 4) as x (r.event_id + ':toc:' + x)}
                  <span class="ml-1 inline-block rounded bg-slate-50 px-1.5 py-0.5 font-mono text-ink-900">{x}</span>
                {/each}
              </div>
            {/if}
            {#if r.legalMarkers.length}
              <div class="mt-2 text-[11px]">
                <span class="font-mono text-ink-800/50">legal_markers</span>
                {#each r.legalMarkers.slice(0, 8) as x (r.event_id + ':lm:' + x)}
                  <span class="ml-1 inline-block rounded bg-indigo-50 px-1.5 py-0.5 font-mono text-ink-900">{x}</span>
                {/each}
              </div>
            {/if}
            {#if r.factRows.length}
              <div class="mt-2 text-[11px]">
                <span class="font-mono text-ink-800/50">timeline_facts</span>
                {#each r.factRows.slice(0, 4) as x (r.event_id + ':fact:' + x)}
                  <span class="ml-1 inline-block rounded bg-lime-50 px-1.5 py-0.5 font-mono text-ink-900">{x}</span>
                {/each}
              </div>
            {/if}
            {#if r.citations.length}
              <div class="mt-2 text-[11px]">
                <span class="font-mono text-ink-800/50">citations</span>
                {#each r.citations.slice(0, 6) as x (r.event_id + ':cit:' + x)}
                  <span class="ml-1 inline-block rounded bg-amber-50 px-1.5 py-0.5 font-mono text-ink-900">{x}</span>
                {/each}
              </div>
            {/if}
            <div class="mt-2 text-sm text-ink-950">
              {#if contextNeedle}
                {#each highlightParts(r.text, contextNeedle) as part, i (r.event_id + ':' + i)}
                  {#if part.hit}
                    <span class="rounded bg-amber-200/60 px-1">{part.s}</span>
                  {:else}
                    {part.s}
                  {/if}
                {/each}
              {:else}
                {r.text}
              {/if}
            </div>
            </div>
          {/each}
        {/if}
      {/if}
    </div>
  </Panel>
</div>
